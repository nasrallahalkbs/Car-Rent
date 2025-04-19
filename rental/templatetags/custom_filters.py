from django import template

register = template.Library()

@register.filter
def get_item(dictionary, key):
    """
    Get an item from a dictionary using the key.
    This filter is useful for accessing dictionary items where the key is a variable.
    
    Usage: {{ dictionary|get_item:key }}
    """
    if dictionary is None:
        return None
    
    # If key is an integer string, convert it to int
    if isinstance(key, str) and key.isdigit():
        key = int(key)
    
    # Try to get from dictionary with the key, or return 0 if not found
    return dictionary.get(key, 0)

@register.filter
def abs(value):
    """
    Returns the absolute value of a number.
    
    Usage: {{ value|abs }}
    """
    try:
        return abs(value)
    except (ValueError, TypeError):
        return value