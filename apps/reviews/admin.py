from django.contrib import admin
from django.utils.safestring import mark_safe
from .models import Review


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ['client_name', 'stars', 'master', 'is_published', 'created_at']
    list_filter = ['is_published', 'rating', 'master']
    search_fields = ['client_name', 'text']
    list_editable = ['is_published']

    def stars(self, obj):
        return mark_safe(f'<span style="color:#C9A96E">{"★" * obj.rating}{"☆" * (5 - obj.rating)}</span>')
    stars.short_description = 'Рейтинг'
