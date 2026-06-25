from django.shortcuts import redirect, get_object_or_404
from django.http import JsonResponse
from django.contrib import messages
from django.core.signing import TimestampSigner, BadSignature, SignatureExpired
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings
from django.db import transaction
from .models import TimeSlot, Booking, Master
from .forms import BookingForm
import datetime


def get_available_slots(request):
    date_str = request.GET.get('date')
    master_id = request.GET.get('master_id')
    if not date_str:
        return JsonResponse({'slots': []})
    try:
        date = datetime.date.fromisoformat(date_str)
    except ValueError:
        return JsonResponse({'slots': []})
    now = datetime.datetime.now()
    slots = TimeSlot.objects.filter(date=date, is_booked=False)
    if master_id:
        slots = slots.filter(master_id=master_id)
    elif master_id == '' or master_id is None:
        pass
    slots = slots.order_by('time')
    data = []
    for s in slots:
        slot_dt = datetime.datetime.combine(s.date, s.time)
        if slot_dt > now:
            data.append({'id': s.id, 'time': s.time.strftime('%H:%M'), 'master': s.master.name if s.master else ''})
    return JsonResponse({'slots': data})


def get_masters(request):
    from apps.booking.models import Master
    masters = Master.objects.filter(is_active=True)
    data = [{'id': m.id, 'name': m.name, 'specialization': m.specialization} for m in masters]
    return JsonResponse({'masters': data})


def submit_booking(request):
    if request.method != 'POST':
        return redirect('/')
    form = BookingForm(request.POST)
    slot_id = request.POST.get('slot_id')
    master_id = request.POST.get('master_id')
    if not slot_id:
        messages.error(request, 'Выберите время')
        return redirect('/#booking')
    if form.is_valid():
        try:
            slot = TimeSlot.objects.select_for_update().get(id=slot_id, is_booked=False)
        except TimeSlot.DoesNotExist:
            messages.error(request, 'Это время уже занято.')
            return redirect('/#booking')
        with transaction.atomic():
            slot.is_booked = True
            slot.save()
            booking = form.save(commit=False)
            booking.slot = slot
            if master_id:
                booking.master = get_object_or_404(Master, id=master_id)
            elif slot.master:
                booking.master = slot.master
            booking.save()
        _send_confirmation_email(booking)
        return redirect('/?booking=ok')
    messages.error(request, 'Исправьте ошибки в форме.')
    return redirect('/#booking')


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
        booking.slot.is_booked = False
        booking.slot.save()
    messages.success(request, 'Ваша запись отменена.')
    return redirect('/')


def _send_confirmation_email(booking):
    from_email = settings.DEFAULT_FROM_EMAIL or settings.EMAIL_HOST_USER or 'noreply@beauty.kz'
    try:
        subject = 'Подтверждение записи'
        html = render_to_string('emails/booking_confirmation_client.html', {'booking': booking})
        send_mail(subject, '', from_email, [booking.client_email], html_message=html)
        admin_email = getattr(settings, 'ADMIN_EMAIL', '')
        if admin_email:
            html_admin = render_to_string('emails/booking_notification_admin.html', {'booking': booking})
            send_mail('Новая запись', '', from_email, [admin_email], html_message=html_admin)
        booking.email_sent = True
        booking.save(update_fields=['email_sent'])
    except Exception:
        booking.email_sent = False
        booking.save(update_fields=['email_sent'])
