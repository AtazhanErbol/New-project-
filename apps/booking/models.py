from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
import secrets
import datetime


CATEGORY_CHOICES = [
    ('manicure', 'Маникюр'),
    ('pedicure', 'Педикюр'),
    ('design', 'Дизайн'),
    ('care', 'Уход'),
]


class Master(models.Model):
    name = models.CharField(max_length=200, verbose_name='Имя мастера')
    specialization = models.CharField(max_length=300, blank=True, verbose_name='Специализация')
    photo = models.ImageField(upload_to='masters/', blank=True, verbose_name='Фото')
    description = models.TextField(blank=True, verbose_name='Описание')
    is_active = models.BooleanField(default=True, verbose_name='Активен')

    class Meta:
        verbose_name = 'Мастер'
        verbose_name_plural = 'Мастера'

    def __str__(self):
        return self.name


class Service(models.Model):
    name = models.CharField(max_length=200, verbose_name='Название')
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, verbose_name='Категория')
    description = models.TextField(verbose_name='Описание')
    duration_minutes = models.PositiveIntegerField(verbose_name='Длительность (мин)')
    price_from = models.DecimalField(max_digits=10, decimal_places=0, verbose_name='Цена от (тг)')
    image = models.ImageField(upload_to='services/', blank=True, verbose_name='Фото')
    is_active = models.BooleanField(default=True, verbose_name='Активна')
    order = models.PositiveIntegerField(default=0, verbose_name='Порядок')
    masters = models.ManyToManyField(Master, blank=True, related_name='services', verbose_name='Мастера')

    class Meta:
        ordering = ['order', 'name']
        verbose_name = 'Услуга'
        verbose_name_plural = 'Услуги'

    def __str__(self):
        return f'{self.name} — от {self.price_from} тг'


class TimeSlot(models.Model):
    date = models.DateField(verbose_name='Дата')
    time = models.TimeField(verbose_name='Время')
    is_booked = models.BooleanField(default=False, verbose_name='Занято')
    master = models.ForeignKey(Master, on_delete=models.SET_NULL, related_name='timeslots', null=True, blank=True, verbose_name='Мастер')

    class Meta:
        unique_together = ('date', 'time', 'master')
        ordering = ['date', 'time']
        verbose_name = 'Слот времени'
        verbose_name_plural = 'Слоты времени'

    def __str__(self):
        return f'{self.date} {self.time}'

    def is_past(self):
        now = datetime.datetime.now()
        slot_dt = datetime.datetime.combine(self.date, self.time)
        return slot_dt < now


class Booking(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Ожидает'),
        ('confirmed', 'Подтверждена'),
        ('cancelled', 'Отменена'),
        ('completed', 'Завершена'),
    ]
    service = models.ForeignKey(Service, on_delete=models.CASCADE, related_name='bookings', verbose_name='Услуга')
    master = models.ForeignKey(Master, on_delete=models.SET_NULL, null=True, blank=True, related_name='bookings', verbose_name='Мастер')
    slot = models.OneToOneField(TimeSlot, on_delete=models.CASCADE, related_name='booking', verbose_name='Слот')
    client_name = models.CharField(max_length=200, verbose_name='Имя клиента')
    client_phone = models.CharField(max_length=20, verbose_name='Телефон')
    client_email = models.EmailField(verbose_name='Email')
    comment = models.TextField(blank=True, verbose_name='Комментарий')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name='Статус')
    cancel_token = models.CharField(max_length=64, unique=True)
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Создано')
    email_sent = models.BooleanField(default=False, verbose_name='Email отправлен')
    consent_given_at = models.DateTimeField(null=True, blank=True, verbose_name='Согласие на обработку ПД дано')

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Запись'
        verbose_name_plural = 'Записи'

    def __str__(self):
        return f'{self.client_name} — {self.service.name}'

    def save(self, *args, **kwargs):
        if not self.cancel_token:
            self.cancel_token = secrets.token_hex(32)
        super().save(*args, **kwargs)

    def get_cancel_url(self):
        from django.core.signing import TimestampSigner
        signer = TimestampSigner()
        signed = signer.sign(self.cancel_token)
        return f'/booking/cancel/{signed}/'


def generate_slots_for_master(master):
    today = datetime.date.today()
    times = [datetime.time(h, m) for h in range(9, 22) for m in (0, 30)]
    count = 0
    for day_offset in range(14):
        date = today + datetime.timedelta(days=day_offset)
        for t in times:
            _, created = TimeSlot.objects.get_or_create(date=date, time=t, master=master)
            if created:
                count += 1
    return count


@receiver(post_save, sender=Master)
def auto_generate_slots(sender, instance, created, **kwargs):
    if created and instance.is_active:
        generate_slots_for_master(instance)
