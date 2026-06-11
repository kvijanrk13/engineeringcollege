from django import template

register = template.Library()

@register.filter(name="dict_get")
def dict_get(value, key):
    if isinstance(value, dict):
        return value.get(key, [])
    return []

@register.filter(name='get_item')
def get_item(dictionary, key):
    if isinstance(dictionary, dict):
        return dictionary.get(key)
    return None
