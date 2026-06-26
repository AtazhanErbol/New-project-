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
from .models import TimeSlot, Booking, Master, Service, slots_are_contiguous
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

    needed = 1
    if service_id:
        try:
            needed = Service.objects.get(id=service_id).slot_count
        except Service.DoesNotExist:
            pass

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
        window = slots[i:i + needed]
        fits = (
            len(window) == needed
            and not any(w.is_booked for w in window)
            and slots_are_contiguous(window)
        )
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

            needed = service.slot_count
            window = list(
                TimeSlot.objects.select_for_update()
                .filter(date=slot.date, master=slot.master, time__gte=slot.time)
                .order_by('time')[:needed]
            )
            if len(window) < needed or any(w.is_booked for w in window) or not slots_are_contiguous(window):
                messages.error(request, 'Недостаточно времени для этой услуги в выбранный слот, выберите другое время.')
                return redirect('/#booking')

            for w in window:
                w.is_booked = True
                w.save(update_fields=['is_booked'])

            booking = form.save(commit=False)
            booking.slot = slot
            booking.master = master or slot.master
            booking.consent_given_at = timezone.now()
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


def _send_confirmation_email(booking):
    from_email = settings.DEFAULT_FROM_EMAIL or settings.EMAIL_HOST_USER or 'noreply@beauty.kz'
    client_sent = False
    try:
        html = render_to_string('emails/booking_confirmation_client.html', {'booking': booking})
        send_mail('Подтверждение записи', '', from_email, [booking.client_email], html_message=html)
        client_sent = True
    except Exception:
        logger.exception('Не удалось отправить письмо клиенту для booking id=%s', booking.id)

    admin_email = getattr(settings, 'ADMIN_EMAIL', '')
    if admin_email:
        try:
            html_admin = render_to_string('emails/booking_notification_admin.html', {'booking': booking})
            send_mail('Новая запись', '', from_email, [admin_email], html_message=html_admin)
        except Exception:
            logger.exception('Не удалось отправить письмо администратору для booking id=%s', booking.id)

    booking.email_sent = client_sent
    booking.save(update_fields=['email_sent'])
