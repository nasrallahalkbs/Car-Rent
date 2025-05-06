from django import template

register = template.Library()

@register.filter
def get_item(dictionary, key):
    """
    فلتر مخصص للوصول إلى عناصر القاموس باستخدام المفتاح
    Usage: {{ dictionary|get_item:key }}
    """
    return dictionary.get(key, '')