# myapps/website/templatetags/custom_filters.py
from django import template

register = template.Library()

@register.filter
def format_decimal(value, digits=6):
    try:
        return f"{value:.{digits}f}"
    except (ValueError, TypeError):
        return value