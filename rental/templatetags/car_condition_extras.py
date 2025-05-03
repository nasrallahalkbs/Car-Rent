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