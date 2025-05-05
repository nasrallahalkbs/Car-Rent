from django import template
from django.utils.html import mark_safe

register = template.Library()

@register.filter
def star_rating(value, max_stars=5):
    """عرض تقييم النجوم بشكل رسومي"""
    if not value:
        value = 0
    
    try:
        value = float(value)
    except (TypeError, ValueError):
        return ""
    
    # التأكد من أن القيمة ضمن النطاق المسموح
    value = max(0, min(value, max_stars))
    
    full_stars = int(value)
    half_star = False
    
    # التحقق مما إذا كان يجب عرض نصف نجمة
    if value - full_stars >= 0.5:
        half_star = True
    
    # إنشاء HTML للنجوم
    html = []
    
    # النجوم الكاملة
    for i in range(full_stars):
        html.append('<i class="fas fa-star text-warning"></i>')
    
    # نصف نجمة
    if half_star:
        html.append('<i class="fas fa-star-half-alt text-warning"></i>')
        empty_stars = max_stars - full_stars - 1
    else:
        empty_stars = max_stars - full_stars
    
    # النجوم الفارغة
    for i in range(empty_stars):
        html.append('<i class="far fa-star text-muted"></i>')
    
    return mark_safe(''.join(html))

@register.filter
def get_item(dictionary, key):
    """الحصول على قيمة من قاموس باستخدام مفتاح"""
    if dictionary is None:
        return None
    return dictionary.get(key)

@register.filter
def sub(value, arg):
    """طرح قيمة من قيمة أخرى"""
    try:
        return value - arg
    except (ValueError, TypeError):
        return 0
