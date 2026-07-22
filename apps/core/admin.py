from django.contrib import admin
from unfold.admin import ModelAdmin
from .models import SiteSettings

admin.site.site_header = 'Aurora Beauty Studio — Админ-панель'
admin.site.site_title = 'Aurora Beauty Studio'
admin.site.index_title = 'Управление сайтом'


@admin.register(SiteSettings)
class SiteSettingsAdmin(ModelAdmin):
    fieldsets = [
        ('Название и логотип', {'fields': ['site_name', 'logo_text', 'logo_image']}),
        ('Главный экран (hero)', {
            'description': 'Текст и фото самого первого блока на сайте — то, что видит клиент, открыв сайт.',
            'fields': ['hero_eyebrow', 'hero_title', 'hero_typeline', 'service_tags', 'hero_image'],
        }),
        ('О мастере / студии', {'fields': ['about_image', 'bio']}),
        ('Контакты', {'fields': ['phone', 'email', 'address', 'working_hours']}),
        ('Акция', {'fields': ['promo_text']}),
        ('Статистика (цифры на сайте)', {'fields': ['years_experience', 'clients_count', 'works_count']}),
        ('Соцсети', {'fields': ['instagram_url', 'whatsapp', 'telegram', 'vk_url', 'facebook_url', 'tiktok_url', 'youtube_url']}),
        ('Футер', {'fields': ['footer_text']}),
    ]
    verbose_name = 'Настройки сайта'
    verbose_name_plural = 'Настройки сайта'

    def has_add_permission(self, request):
        return not SiteSettings.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False
