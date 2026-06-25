from django import template
register = template.Library()

@register.simple_tag
def site_settings():
    from ..models import SiteSettings
    return SiteSettings.load()
