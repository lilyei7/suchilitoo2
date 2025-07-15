from django import template

register = template.Library()

@register.filter
def get_item(dictionary, key):
    """
    Gets an item from a dictionary using the key as a variable
    Usage: {{ mydict|get_item:my_key_var }}
    """
    try:
        return dictionary.get(key)
    except (KeyError, AttributeError):
        return None
