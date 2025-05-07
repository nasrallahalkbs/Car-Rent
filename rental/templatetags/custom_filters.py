"""
فلاتر قوالب مخصصة للنظام
"""

from django import template
from django.template.defaultfilters import stringfilter

register = template.Library()

@register.filter(name='get_item')
def get_item(dictionary, key):
    """
    فلتر للحصول على عنصر من قاموس باستخدام المفتاح
    
    الاستخدام في القوالب:
    {{ my_dict|get_item:some_key }}
    """
    if dictionary is None:
        return None
    
    # تحويل المفتاح إلى نص إذا كان ضرورياً
    if not isinstance(key, str):
        key = str(key)
    
    # محاولة الحصول على العنصر
    try:
        return dictionary.get(key)
    except (AttributeError, KeyError, TypeError):
        return None