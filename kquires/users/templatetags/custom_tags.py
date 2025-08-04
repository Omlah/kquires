from django import template
from django.urls import reverse

register = template.Library()

@register.simple_tag(takes_context=True)
def is_active(context, url_name):
    request = context['request']
    return request.path == reverse(url_name)