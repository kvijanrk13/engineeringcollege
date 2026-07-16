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


@register.filter
def first_book_title(value):
    if not value:
        return ""
    parts = re.split(r"[\n/]+", str(value))
    for part in parts:
        t = re.sub(r"^\s*\d+[\.\)]\s*", "", part.strip())
        t = t.split(",")[0].strip()
        t = re.sub(r"\s+", " ", t)
        if t:
            return t
    return ""


@register.filter
def textbooks_only(value):
    if not value:
        return "-"
    parts = re.split(r"[\n/]+", str(value))
    kept = []
    for part in parts:
        p = part.strip()
        if re.match(r"^1[\.\)]", p):
            kept.append(p)
    kept = [k for k in kept if k]
    if not kept:
        return "-"
    return mark_safe("<br>".join(escape(k) for k in kept))
