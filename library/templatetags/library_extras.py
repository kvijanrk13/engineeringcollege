from django import template
from django.utils.html import escape
from django.utils.safestring import mark_safe

import re

register = template.Library()


@register.filter
def split_lines(value):
    if not value:
        return "-"
    parts = re.split(r"[\n,;/]+|\s/\s", str(value))
    parts = [p.strip() for p in parts if p.strip()]
    if not parts:
        return "-"
    return mark_safe("<br>".join(escape(p) for p in parts))


@register.filter
def isbn_digits(value):
    if not value:
        return ""
    return re.sub(r"[^0-9Xx]", "", str(value)).upper()
