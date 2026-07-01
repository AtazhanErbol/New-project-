import logging

from django.shortcuts import redirect, get_object_or_404
from django.http import JsonResponse
from django.contrib import messages
from django.core.signing import TimestampSigner, BadSignature, SignatureExpired
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings
from django.db import transaction
from django.utils import timezone
from django_ratelimit.decorators import ratelimit
from .models import TimeSlot, Booking, Master, Service, Client, slots_are_contiguous, ensure_slots_for_date
from .forms import BookingForm
import datetime

logger = logging.getLogger(__name__)


@ratelimit(key='ip', rate='20/m', block=True)
def get_available_slots(request):
    date_str = request.GET.get('date')
    master_id = request.GET.get('master_id')
    service_id = request.GET.get('service_id')
    if not date_str:
        return JsonResponse({'slots': []})
    try:
        date = datetime.date.fromisoformat(date_str)
    except ValueError:
        return JsonResponse({'slots': []})

    appt = 1
    if service_id:
        try:
            appt = Service.objects.get(id=service_id).slot_count
        except Service.DoesNotExist:
            pass

    master = Master.objects.filter(id=master_id).first() if master_id else None
    # Мастер не работает в этот день (выходной / отпуск / больничный) — слотов нет.
    if master and not master.works_on(date):
        return JsonResponse({'slots': []})
    # Авто-создание слотов на выбранную дату (горизонт 90 дней) — без ручной генерации.
    if master and timezone.localdate() <= date <= timezone.localdate() + datetime.timedelta(days=90):
        ensure_slots_for_date(master, date)

    buf = master.buffer_slots if master else 0

    now = timezone.localtime().replace(tzinfo=None)
    slots = TimeSlot.objects.filter(date=date)
    if master_id:
        slots = slots.filter(master_id=master_id)
    slots = list(slots.order_by('time'))

    data = []
    for i, s in enumerate(slots):
        slot_dt = datetime.datetime.combine(s.date, s.time)
        if slot_dt <= now:
            continue
        # вне рабочих часов мастера — не показываем вовсе
        if master and not (master.work_start <= s.time < master.work_end):
            continue

        window = slots[i:i + appt]
        fits = (
            len(window) == appt
            and not any(w.is_booked for w in window)
            and slots_are_contiguous(window)
        )
        # услуга целиком должна влезать в рабочие часы
        if fits and master and not master.fits_working_hours(s.time, appt * 30):
            fits = False
        # буфер: слоты сразу после записи (которые существуют) должны быть свободны
        if fits and buf:
            after = slots[i + appt:i + appt + buf]
            if any(w.is_booked for w in after):
                fits = False

        data.append({
            'id': s.id,
            'time': s.time.strftime('%H:%M'),
            'booked': s.is_booked,
            'available': fits,
        })
    return JsonResponse({'slots': data})


@ratelimit(key='ip', rate='20/m', block=True)
def get_masters(request):
    service_id = request.GET.get('service_id')
    masters = Master.objects.filter(is_active=True)
    if service_id:
        masters = masters.filter(services__id=service_id)
    data = [{'id': m.id, 'name': m.name, 'specialization': m.specialization} for m in masters]
    return JsonResponse({'masters': data})


@ratelimit(key='ip', rate='20/m', block=True)
def get_services(request):
    master_id = request.GET.get('master_id')
    services = Service.objects.filter(is_active=True)
    if master_id:
        master = get_object_or_404(Master, id=master_id)
        if master.services.exists():
            services = services.filter(masters=master)
    data = [{'id': s.id, 'name': s.name, 'price_from': str(s.price_from), 'duration_minutes': s.duration_minutes} for s in services]
    return JsonResponse({'services': data})


@ratelimit(key='ip', rate='5/m', block=True)
def submit_booking(request):
    if request.method != 'POST':
        return redirect('/')
    form = BookingForm(request.POST)
    slot_id = request.POST.get('slot_id')
    master_id = request.POST.get('master_id')
    if not slot_id:
        messages.error(request, 'Выберите время')
        return redirect('/#booking')
    if not form.is_valid():
        messages.error(request, 'Исправьте ошибки в форме.')
        return redirect('/#booking')

    service = form.cleaned_data['service']
    master = None
    if master_id:
        master = get_object_or_404(Master, id=master_id)
        if service.masters.exists() and not service.masters.filter(id=master.id).exists():
            messages.error(request, 'Выбранный мастер не оказывает эту услугу.')
            return redirect('/#booking')

    now = timezone.localtime().replace(tzinfo=None)
    try:
        with transaction.atomic():
            slot = TimeSlot.objects.select_for_update().get(id=slot_id, is_booked=False)
            slot_dt = datetime.datetime.combine(slot.date, slot.time)
            if slot_dt <= now:
                messages.error(request, 'Это время уже прошло, выберите другое.')
                return redirect('/#booking')

            sched_master = master or slot.master
            if sched_master and not sched_master.works_on(slot.date):
                messages.error(request, 'Мастер не работает в выбранный день, выберите другое время.')
                return redirect('/#booking')

            needed = service.slot_count
            window = list(
                TimeSlot.objects.select_for_update()
                .filter(date=slot.date, master=slot.master, time__gte=slot.time)
                .order_by('time')[:needed]
            )
            if len(window) < needed or any(w.is_booked for w in window) or not slots_are_contiguous(window):
                messages.error(request, 'Недостаточно времени для этой услуги в выбранный слот, выберите другое время.')
                return redirect('/#booking')
            if sched_master and not sched_master.fits_working_hours(slot.time, needed * 30):
                messages.error(request, 'Услуга не помещается в рабочие часы мастера, выберите другое время.')
                return redirect('/#booking')

            # Блокируем слоты записи + буфер мастера (существующие слоты после).
            buf = sched_master.buffer_slots if sched_master else 0
            block = list(
                TimeSlot.objects.select_for_update()
                .filter(date=slot.date, master=slot.master, time__gte=slot.time)
                .order_by('time')[:needed + buf]
            )
            for w in block:
                if not w.is_booked:
                    w.is_booked = True
                    w.save(update_fields=['is_booked'])

            booking = form.save(commit=False)
            booking.slot = slot
            booking.master = master or slot.master
            booking.consent_given_at = timezone.now()
            booking.client = Client.get_or_create_for_booking(
                booking.client_name, booking.client_phone, booking.client_email
            )
            booking.save()
    except TimeSlot.DoesNotExist:
        messages.error(request, 'Это время уже занято.')
        return redirect('/#booking')

    _send_confirmation_email(booking)
    return redirect('/?booking=ok')


def cancel_booking(request, signed_token):
    signer = TimestampSigner()
    try:
        token = signer.unsign(signed_token, max_age=7 * 86400)
    except (BadSignature, SignatureExpired):
        messages.error(request, 'Ссылка недействительна или истекла.')
        return redirect('/')
    booking = get_object_or_404(Booking, cancel_token=token)
    if booking.status == 'cancelled':
        messages.info(request, 'Запись уже отменена.')
        return redirect('/')
    with transaction.atomic():
        booking.status = 'cancelled'
        booking.save()
        booking.release_slots()
    messages.success(request, 'Ваша запись отменена.')
    return redirect('/')


def _from_email():
    return settings.DEFAULT_FROM_EMAIL or settings.EMAIL_HOST_USER or 'noreply@beauty.kz'


def _notify_recipients(booking):
    """Кому уходит уведомление о новой записи: мастер + email салона + ADMIN_EMAIL."""
    from apps.core.models import SiteSettings
    recipients = []
    if booking.master and booking.master.email:
        recipients.append(booking.master.email)
    try:
        site_email = (SiteSettings.load().email or '').strip()
    except Exception:
        site_email = ''
    for extra in (site_email, getattr(settings, 'ADMIN_EMAIL', '')):
        if extra and extra not in recipients:
            recipients.append(extra)
    return recipients


def _send_confirmation_email(booking):
    """При создании записи: клиенту — 'заявка принята', мастеру и салону — уведомление."""
    from_email = _from_email()
    client_sent = False
    try:
        html = render_to_string('emails/booking_confirmation_client.html', {'booking': booking, 'confirmed': False})
        send_mail('Заявка на запись принята', '', from_email, [booking.client_email], html_message=html)
        client_sent = True
    except Exception:
        logger.exception('Не удалось отправить письмо клиенту для booking id=%s', booking.id)

    recipients = _notify_recipients(booking)
    if recipients:
        try:
            html_admin = render_to_string('emails/booking_notification_admin.html', {'booking': booking})
            send_mail('Новая запись', '', from_email, recipients, html_message=html_admin)
        except Exception:
            logger.exception('Не удалось отправить уведомление мастеру/салону для booking id=%s', booking.id)

    booking.email_sent = client_sent
    booking.save(update_fields=['email_sent'])


def send_client_confirmation_email(booking):
    """Письмо клиенту при подтверждении записи мастером/админом."""
    try:
        html = render_to_string('emails/booking_confirmation_client.html', {'booking': booking, 'confirmed': True})
        send_mail('Ваша запись подтверждена', '', _from_email(), [booking.client_email], html_message=html)
        return True
    except Exception:
        logger.exception('Не удалось отправить подтверждение клиенту для booking id=%s', booking.id)
        return False
