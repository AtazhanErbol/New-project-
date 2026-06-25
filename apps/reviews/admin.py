from django.contrib import admin
from .models import Review


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ['client_name', 'rating', 'master', 'is_published', 'created_at']
    list_filter = ['is_published', 'rating', 'master']
    list_editable = ['is_published']
