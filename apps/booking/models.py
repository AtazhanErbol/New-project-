from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
import math
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
    email = models.EmailField(blank=True, verbose_name='Email для уведомлений о записях')
    user = models.OneToOneField(
        'auth.User', on_delete=models.SET_NULL, null=True, blank=True,
        related_name='master_profile', verbose_name='Аккаунт для входа в кабинет',
    )
    specialization = models.CharField(max_length=300, blank=True, verbose_name='Специализация')
    photo = models.ImageField(upload_to='masters/', blank=True, verbose_name='Фото')
    description = models.TextField(blank=True, verbose_name='Описание')
    is_active = models.BooleanField(default=True, verbose_name='Активен')
    work_start = models.TimeField(default=datetime.time(9, 0), verbose_name='Начало рабочего дня')
    work_end = models.TimeField(default=datetime.time(21, 0), verbose_name='Конец рабочего дня')
    work_days = models.CharField(
        max_length=20, default='0,1,2,3,4,5,6', verbose_name='Рабочие дни',
        help_text='Дни недели через запятую: 0=Пн, 1=Вт, 2=Ср, 3=Чт, 4=Пт, 5=Сб, 6=Вс',
    )
    buffer_minutes = models.PositiveIntegerField(default=0, verbose_name='Буфер между записями (мин)')

    class Meta:
        verbose_name = 'Мастер'
        verbose_name_plural = 'Мастера'

    def __str__(self):
        return self.name

    @property
    def working_weekdays(self):
        out = set()
        for p in (self.work_days or '').split(','):
            p = p.strip()
            if p.isdigit():
                out.add(int(p))
        return out

    @property
    def buffer_slots(self):
        return math.ceil(self.buffer_minutes / 30) if self.buffer_minutes else 0

    def is_off(self, date):
        return self.time_off.filter(date_from__lte=date, date_to__gte=date).exists()

    def works_on(self, date):
        wd = self.working_weekdays
        if wd and date.weekday() not in wd:
            return False
        return not self.is_off(date)

    def fits_working_hours(self, start_time, duration_minutes):
        """Помещается ли услуга длительностью N минут в рабочие часы мастера."""
        base = datetime.date.today()
        start_dt = datetime.datetime.combine(base, start_time)
        end_dt = start_dt + datetime.timedelta(minutes=duration_minutes)
        ws = datetime.datetime.combine(base, self.work_start)
        we = datetime.datetime.combine(base, self.work_end)
        return ws <= start_dt and end_dt <= we


class MasterTimeOff(models.Model):
    REASON_CHOICES = [
        ('vacation', 'Отпуск'),
        ('sick', 'Больничный'),
        ('dayoff', 'Выходной'),
        ('other', 'Другое'),
    ]
    master = models.ForeignKey('Master', on_delete=models.CASCADE, related_name='time_off', verbose_name='Мастер')
    date_from = models.DateField(verbose_name='С')
    date_to = models.DateField(verbose_name='По')
    reason = models.CharField(max_length=20, choices=REASON_CHOICES, default='dayoff', verbose_name='Причина')
    comment = models.CharField(max_length=300, blank=True, verbose_name='Комментарий')

    class Meta:
        ordering = ['-date_from']
        verbose_name = 'Отсутствие мастера'
        verbose_name_plural = 'Отсутствия мастеров'

    def __str__(self):
        return f'{self.master.name}: {self.date_from}–{self.date_to} ({self.get_reason_display()})'


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

    @property
    def slot_count(self):
        """Сколько 30-минутных слотов занимает услуга."""
        return max(1, math.ceil(self.duration_minutes / 30))


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


class Client(models.Model):
    name = models.CharField(max_length=200, verbose_name='Имя')
    phone = models.CharField(max_length=20, verbose_name='Телефон')
    email = models.EmailField(blank=True, verbose_name='Email')
    notes = models.TextField(blank=True, verbose_name='Комментарий администратора')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Создан')

    class Meta:
        ordering = ['name']
        verbose_name = 'Клиент'
        verbose_name_plural = 'Клиенты'

    def __str__(self):
        return f'{self.name} ({self.phone})'

    @property
    def visits_count(self):
        return self.bookings.count()

    @classmethod
    def get_or_create_for_booking(cls, name, phone, email=''):
        """Найти клиента по телефону или создать нового; обновить контакты."""
        client = cls.objects.filter(phone=phone).first()
        if client is None:
            return cls.objects.create(name=name, phone=phone, email=email)
        changed = False
        if name and client.name != name:
            client.name = name
            changed = True
        if email and client.email != email:
            client.email = email
            changed = True
        if changed:
            client.save()
        return client


class Booking(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Ожидает'),
        ('confirmed', 'Подтверждена'),
        ('cancelled', 'Отменена'),
        ('completed', 'Завершена'),
    ]
    service = models.ForeignKey(Service, on_delete=models.CASCADE, related_name='bookings', verbose_name='Услуга')
    master = models.ForeignKey(Master, on_delete=models.SET_NULL, null=True, blank=True, related_name='bookings', verbose_name='Мастер')
    client = models.ForeignKey('Client', on_delete=models.SET_NULL, null=True, blank=True, related_name='bookings', verbose_name='Клиент')
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

    def get_reserved_slots(self):
        """Слоты, занятые записью: длительность услуги + буфер мастера."""
        m = self.master or self.slot.master
        total = self.service.slot_count + (m.buffer_slots if m else 0)
        return TimeSlot.objects.filter(
            date=self.slot.date, master=self.slot.master, time__gte=self.slot.time
        ).order_by('time')[:total]

    def release_slots(self):
        for s in self.get_reserved_slots():
            s.is_booked = False
            s.save(update_fields=['is_booked'])


def slots_are_contiguous(slots):
    """Проверяет, что слоты идут подряд без пропусков по 30 минут."""
    if not slots:
        return False
    expected = slots[0].time
    for s in slots:
        if s.time != expected:
            return False
        expected = (datetime.datetime.combine(s.date, expected) + datetime.timedelta(minutes=30)).time()
    return True


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


def ensure_slots_for_date(master, date):
    """Лениво создаёт слоты мастера на конкретную дату, если их ещё нет.

    Позволяет не генерировать слоты вручную: при выборе любой даты в форме
    записи недостающие слоты создаются автоматически.
    """
    if TimeSlot.objects.filter(master=master, date=date).exists():
        return
    times = [datetime.time(h, m) for h in range(9, 22) for m in (0, 30)]
    TimeSlot.objects.bulk_create(
        [TimeSlot(master=master, date=date, time=t) for t in times],
        ignore_conflicts=True,
    )


@receiver(post_save, sender=Master)
def auto_generate_slots(sender, instance, created, **kwargs):
    if created and instance.is_active:
        generate_slots_for_master(instance)
