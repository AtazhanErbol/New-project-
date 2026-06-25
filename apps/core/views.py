from django.shortcuts import render
from apps.booking.models import Service, Master
from apps.portfolio.models import PortfolioItem
from apps.reviews.models import Review
from .models import SiteSettings


def index(request):
    settings_obj = SiteSettings.load()
    services = Service.objects.filter(is_active=True)
    portfolio = PortfolioItem.objects.all()[:12]
    reviews = Review.objects.filter(is_published=True)
    masters = Master.objects.filter(is_active=True)
    return render(request, 'index.html', {
        'site_settings': settings_obj,
        'services': services,
        'portfolio': portfolio,
        'reviews': reviews,
        'masters': masters,
    })
