def site_settings(request):
    from .models import SiteSettings
    return {'site_settings': SiteSettings.load()}
