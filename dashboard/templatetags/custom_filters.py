from django import template

register = template.Library()

@register.filter(name='split')
def split(value, key):
    """
    Returns the value split by the given key.
    """
    if value:
        return value.split(key)
    return []