from django import template

register = template.Library()

@register.filter
def get_item(dictionary, key):
    """
    فلتر مخصص للحصول على عنصر من قاموس باستخدام المفتاح
    يمكن استخدامه في قوالب Django للوصول إلى عناصر القاموس بالمفتاح
    مثال: {{ my_dict|get_item:key_var }}
    """
    if dictionary is None:
        return None
    
    # محاولة الحصول على العنصر بالمفتاح
    try:
        return dictionary.get(key)
    except (AttributeError, KeyError, TypeError):
        return None