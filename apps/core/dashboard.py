"""Данные для дашборда админки (Unfold)."""
from datetime import timedelta

from django.db.models import Count
from django.utils import timezone


def dashboard_callback(request, context):
    from apps.booking.models import Booking, Master, Service, Client

    today = timezone.localdate()
    tomorrow = today + timedelta(days=1)

    active = Booking.objects.exclude(status='cancelled')

    upcoming = (
        active.filter(slot__date__gte=today)
        .select_related('service', 'master', 'slot')
        .order_by('slot__date', 'slot__time')[:8]
    )
    popular_services = Service.objects.annotate(n=Count('bookings')).order_by('-n')[:5]
    popular_masters = Master.objects.annotate(n=Count('bookings')).order_by('-n')[:5]

    context.update({
        'stats': [
            {'label': 'Записей сегодня', 'value': active.filter(slot__date=today).count()},
            {'label': 'Записей завтра', 'value': active.filter(slot__date=tomorrow).count()},
            {'label': 'Ожидают подтверждения', 'value': active.filter(status='pending').count()},
            {'label': 'Клиентов', 'value': Client.objects.count()},
        ],
        'upcoming_bookings': upcoming,
        'popular_services': popular_services,
        'popular_masters': popular_masters,
    })
    return context
