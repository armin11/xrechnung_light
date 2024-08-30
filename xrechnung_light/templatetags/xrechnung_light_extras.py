from django import template
from django.template.defaultfilters import stringfilter

register = template.Library()

@register.filter
@stringfilter
def lower(value):
    return value.lower()

@register.filter
@stringfilter
def exchange_comma_with_point(value):
    return value.replace(',', '.')