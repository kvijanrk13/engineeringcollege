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
    s = str(value)
    # Drop "ISBN", "ISBN-13:", "ISBN10:" etc. (incl. the optional 13/10 number)
    s = re.sub(r"(?i)ISBN[-\s]*(?:13|10)?\D*", "", s)
    s = re.sub(r"[^\d]", "", s)  # keep only digits
    m = re.search(r"\d{13}", s)
    if m:
        return m.group(0)
    m = re.search(r"\d{10}", s)
    if m:
        return m.group(0)
    return ""


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
    text = str(value)
    parts = text.split('/')
    text_part = parts[0] if parts else text
    entries = re.split(r"[\n]+", text_part)
    kept = []
    for entry in entries:
        p = entry.strip()
        if p:
            clean = re.sub(r"^\d+[\.\)]\s*", "", p).strip()
            if clean:
                kept.append(clean)
    kept = [k for k in kept if k]
    if not kept:
        return "-"
    return mark_safe("<br>".join(escape(k) for k in kept))


@register.filter
def textbook_entries(value):
    if not value:
        return []
    text = str(value)
    parts = text.split('/')
    text_part = parts[0] if parts else text
    entries = re.split(r"[\n]+", text_part)
    out = []
    for entry in entries:
        p = entry.strip()
        if p:
            clean = re.sub(r"^1[\.\)]\s*", "", p).strip()
            if clean:
                out.append(clean)
    return out


@register.filter
def reference_books(value):
    if not value:
        return "-"
    text = str(value)
    parts = text.split('/')
    if len(parts) < 2:
        ref_part = parts[0] if parts else text
        entries = re.split(r"[\n]+", ref_part)
        kept = []
        for entry in entries:
            p = entry.strip()
            if p:
                clean = re.sub(r"^\d+[\.\)]\s*", "", p).strip()
                if clean:
                    kept.append(clean)
        kept = [k for k in kept if k]
        if not kept:
            return "-"
        return mark_safe("<br>".join(escape(k) for k in kept))
    
    ref_part = parts[1]
    ref_entries = re.split(r"[\n]+", ref_part)
    kept = []
    for entry in ref_entries:
        p = entry.strip()
        if p:
            clean = re.sub(r"^\d+[\.\)]\s*", "", p).strip()
            if clean:
                kept.append(clean)
    kept = [k for k in kept if k]
    if not kept:
        return "-"
    return mark_safe("<br>".join(escape(k) for k in kept))
