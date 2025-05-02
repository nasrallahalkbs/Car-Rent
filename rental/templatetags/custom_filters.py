from django import template
from django.utils.translation import gettext as _
from django.utils.timezone import now
import datetime

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
        # Use Python's built-in abs function, not recursively calling this function
        return __builtins__['abs'](value)
    except (ValueError, TypeError):
        return value

@register.filter(name='sub')
def sub(value, arg):
    """
    طرح قيمة من أخرى
    
    Usage: {{ value|sub:arg }}
    """
    try:
        return int(value) - int(arg)
    except (ValueError, TypeError):
        return 0
        
@register.filter(name='percentage_change')
def percentage_change(new_value, old_value):
    """
    حساب نسبة التغيير بين قيمتين
    
    Usage: {{ new_value|percentage_change:old_value }}
    """
    try:
        new_value = float(new_value)
        old_value = float(old_value)
        if old_value == 0:
            return 100  # تغيير من الصفر يعتبر زيادة بنسبة 100%
        
        change = ((new_value - old_value) / old_value) * 100
        return int(change)
    except (ValueError, TypeError, ZeroDivisionError):
        return 0

@register.filter(name='fuel_level_to_percent')
def fuel_level_to_percent(level):
    """
    تحويل مستوى الوقود إلى نسبة مئوية
    
    Usage: {{ fuel_level|fuel_level_to_percent }}
    """
    fuel_levels = {
        'empty': 5,
        'quarter': 25,
        'half': 50, 
        'three_quarters': 75,
        'full': 100
    }
    
    return fuel_levels.get(level, 0)
    
@register.filter(name='condition_value')
def condition_value(condition):
    """
    تحويل حالة السيارة إلى قيمة رقمية للمقارنة
    
    Usage: {{ car_condition|condition_value }}
    """
    condition_values = {
        'excellent': 5,
        'good': 4,
        'fair': 3,
        'poor': 2,
        'damaged': 1
    }
    
    return condition_values.get(condition, 0)