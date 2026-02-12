from django import template

register = template.Library()

@register.filter(name="get_item")
def get_item(value, key):
    try:
        return value.get(key)
    except Exception:
        return None
