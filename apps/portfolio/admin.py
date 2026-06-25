from django.contrib import admin
from .models import PortfolioItem


@admin.register(PortfolioItem)
class PortfolioAdmin(admin.ModelAdmin):
    list_display = ['alt_text', 'category', 'master', 'created_at']
    list_filter = ['category', 'master']
    search_fields = ['alt_text']
