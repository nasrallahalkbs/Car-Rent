from django import template
register = template.Library()

@register.filter
def get_item(dictionary, key):
    """
    مرشح مخصص للوصول إلى عناصر القاموس بواسطة المفتاح في قوالب Django
    """
    if not dictionary:
        return None
    return dictionary.get(key)