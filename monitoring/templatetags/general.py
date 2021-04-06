from django import template

from monitoring import events
from siteroot import settings

register = template.Library()


@register.simple_tag
def events_clear(request):
    events.clear(request)
    return ""


@register.simple_tag
def media(url):
    if settings.DEBUG:
        return "/static/" + url
    return "/media/" + url


@register.simple_tag
def logo():
    return "GAMEMONITORINGSITE"
