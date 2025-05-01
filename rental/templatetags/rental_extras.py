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


@register.filter
def contains(value, arg):
    """
    فحص إذا كانت السلسلة النصية تحتوي على الوسيطة المعطاة
    مثال: {% if description|contains:"صورة أمامية" %}
    """
    return arg in value if value else False


@register.filter
def split(value, arg):
    """
    تقسيم السلسلة النصية باستخدام المحدد المعطى
    مثال: {{ description|split:"-" }}
    """
    return value.split(arg) if value else []


@register.filter
def trim(value):
    """
    إزالة المسافات الزائدة من بداية ونهاية السلسلة النصية
    مثال: {{ text|trim }}
    """
    return value.strip() if value else ""


@register.filter
def first_item(value):
    """
    إرجاع العنصر الأول من قائمة
    مثال: {{ my_list|first_item }}
    """
    if value and len(value) > 0:
        return value[0]
    return None


@register.filter
def selectattr(value, attr):
    """
    تصفية قائمة من العناصر التي تحتوي على العبارة المعطاة في الخاصية المحددة
    مثال: {{ images|selectattr:"description"|selectattr:"صورة أمامية"|first }}
    """
    if not value:
        return []
    
    result = []
    for item in value:
        if hasattr(item, 'description') and attr in getattr(item, 'description', ''):
            result.append(item)
    return result