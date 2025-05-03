from django import template

register = template.Library()

@register.filter
def get_item(dictionary, key):
    """
    مرشح قالب للوصول إلى قيمة في قاموس باستخدام المفتاح
    مثال الاستخدام: {{ my_dict|get_item:item_id }}
    """
    try:
        return dictionary.get(key)
    except (KeyError, AttributeError):
        return None

@register.filter
def subtract(value, arg):
    """
    مرشح قالب لحساب الفرق بين قيمتين
    مثال الاستخدام: {{ value|subtract:arg }}
    """
    try:
        return int(value) - int(arg)
    except (ValueError, TypeError):
        return 0