from django.core.management.base import BaseCommand

from apps.booking.models import Master, generate_slots_for_master


class Command(BaseCommand):
    help = 'Создаёт TimeSlot на ближайшие 14 дней для всех активных мастеров. Запускать по cron, чтобы сетка записи не "обрывалась".'

    def handle(self, *args, **options):
        total = 0
        for master in Master.objects.filter(is_active=True):
            total += generate_slots_for_master(master)
        self.stdout.write(self.style.SUCCESS(f'Создано {total} новых слотов.'))
