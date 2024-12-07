from django import template

register = template.Library()

@register.filter
def get_item(dictionary, key):
    """
    Custom filter to retrieve a value from a dictionary using a key.
    """
    try:
        return dictionary.get(key)
    except (TypeError, AttributeError):
        return None
    
@register.filter
def dict_key(d, key):
    return d.get(key, '')