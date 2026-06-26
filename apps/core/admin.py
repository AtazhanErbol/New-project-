from django.contrib import admin
from .models import SiteSettings

admin.site.site_header = 'Beauty by Kabylova — Админ-панель'
admin.site.site_title = 'Beauty by Kabylova'
admin.site.index_title = 'Управление сайтом'


@admin.register(SiteSettings)
class SiteSettingsAdmin(admin.ModelAdmin):
    fieldsets = [
        ('Основное', {'fields': ['site_name', 'logo_text', 'hero_image', 'about_image', 'bio']}),
        ('Контакты', {'fields': ['phone', 'email', 'address', 'working_hours']}),
        ('Акция', {'fields': ['promo_text']}),
        ('Статистика', {'fields': ['years_experience', 'clients_count', 'works_count']}),
        ('Соцсети', {'fields': ['instagram_url', 'whatsapp', 'telegram', 'vk_url', 'facebook_url', 'tiktok_url', 'youtube_url']}),
        ('Футер', {'fields': ['footer_text']}),
    ]
    verbose_name = 'Настройки сайта'
    verbose_name_plural = 'Настройки сайта'

    def has_add_permission(self, request):
        return not SiteSettings.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False
