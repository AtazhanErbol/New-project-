from django.contrib import admin
from unfold.admin import ModelAdmin
from django.utils.safestring import mark_safe
from .models import PortfolioItem


@admin.register(PortfolioItem)
class PortfolioAdmin(ModelAdmin):
    list_display = ['thumbnail', 'alt_text', 'category', 'master', 'created_at']
    list_filter = ['category', 'master']
    search_fields = ['alt_text']

    def thumbnail(self, obj):
        if obj.image:
            return mark_safe(f'<img src="{obj.image.url}" style="width:60px;height:60px;border-radius:8px;object-fit:cover">')
        return '-'
    thumbnail.short_description = 'Фото'
