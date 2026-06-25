from django.db import models


class SiteSettings(models.Model):
    site_name = models.CharField(max_length=200, default='Beauty by Kabylova', verbose_name='Название сайта')
    logo_text = models.CharField(max_length=100, default='by Kabylova', verbose_name='Текст логотипа')
    phone = models.CharField(max_length=30, blank=True, verbose_name='Телефон')
    address = models.CharField(max_length=200, blank=True, verbose_name='Адрес')
    working_hours = models.CharField(max_length=100, blank=True, verbose_name='Режим работы')
    promo_text = models.CharField(max_length=300, blank=True, verbose_name='Текст акции')
    instagram_url = models.URLField(blank=True, verbose_name='Instagram')
    whatsapp = models.CharField(max_length=30, blank=True, verbose_name='WhatsApp (номер)')
    telegram = models.CharField(max_length=100, blank=True, verbose_name='Telegram (@username или ссылка)')
    vk_url = models.URLField(blank=True, verbose_name='VK')
    facebook_url = models.URLField(blank=True, verbose_name='Facebook')
    tiktok_url = models.URLField(blank=True, verbose_name='TikTok')
    youtube_url = models.URLField(blank=True, verbose_name='YouTube')
    hero_image = models.ImageField(upload_to='hero/', blank=True, verbose_name='Фото героя')
    about_image = models.ImageField(upload_to='about/', blank=True, verbose_name='Фото о мастере')
    bio = models.TextField(blank=True, verbose_name='Bio / Описание')
    years_experience = models.PositiveIntegerField(default=0, verbose_name='Лет опыта')
    clients_count = models.PositiveIntegerField(default=0, verbose_name='Клиентов')
    works_count = models.PositiveIntegerField(default=0, verbose_name='Работ')
    email = models.EmailField(blank=True, verbose_name='Email для связи')
    footer_text = models.CharField(max_length=300, blank=True, default='Все права защищены', verbose_name='Текст в футере')

    class Meta:
        verbose_name = 'Настройки сайта'
        verbose_name_plural = 'Настройки сайта'

    def __str__(self):
        return self.site_name

    def save(self, *args, **kwargs):
        self.pk = 1
        super().save(*args, **kwargs)

    @classmethod
    def load(cls):
        obj, created = cls.objects.get_or_create(pk=1)
        return obj

    def whatsapp_link(self):
        if self.whatsapp:
            num = self.whatsapp.replace('+', '').replace(' ', '').replace('-', '').replace('(', '').replace(')', '')
            return f'https://wa.me/{num}'
        return ''

    def telegram_link(self):
        if self.telegram:
            if self.telegram.startswith('http'):
                return self.telegram
            return f'https://t.me/{self.telegram.lstrip("@")}'
        return ''

    def has_social(self):
        return any([self.instagram_url, self.whatsapp, self.telegram, self.vk_url, self.facebook_url, self.tiktok_url, self.youtube_url])
