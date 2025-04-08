"""
إصلاح تعريب قالب السلة (cart_django.html) لدعم اللغتين العربية والإنجليزية
"""

def fix_cart_template():
    with open('templates/cart_django.html', 'r', encoding='utf-8') as file:
        content = file.read()
    
    # تحديث عنوان الصفحة
    content = content.replace(
        '{% block title %}سلة التسوق - كاررنتال{% endblock %}',
        '{% block title %}{% if is_english %}Shopping Cart - CarRental{% else %}سلة التسوق - كاررنتال{% endif %}{% endblock %}'
    )
    
    # تحديث عنوان سلة التسوق
    content = content.replace(
        '<i class="fas fa-shopping-cart ms-2"></i> سلة التسوق',
        '<i class="fas fa-shopping-cart {% if is_english %}me-2{% else %}ms-2{% endif %}"></i> {% if is_english %}Shopping Cart{% else %}سلة التسوق{% endif %}'
    )
    
    # تحديث عدد العناصر في السلة
    content = content.replace(
        '<span class="cart-count">{{ cart_items|length }} عنصر</span>',
        '<span class="cart-count">{{ cart_items|length }} {% if is_english %}item(s){% else %}عنصر{% endif %}</span>'
    )
    
    # تحديث رسالة تأكيد حذف عنصر من السلة
    content = content.replace(
        "return confirm('هل أنت متأكد من إزالة هذه السيارة من سلة التسوق؟')",
        "return confirm('{% if is_english %}Are you sure you want to remove this car from your cart?{% else %}هل أنت متأكد من إزالة هذه السيارة من سلة التسوق؟{% endif %}')"
    )
    
    # تحديث رسالة السلة الفارغة
    content = content.replace(
        '<h3 class="empty-cart-title">سلة التسوق فارغة</h3>',
        '<h3 class="empty-cart-title">{% if is_english %}Your Cart is Empty{% else %}سلة التسوق فارغة{% endif %}</h3>'
    )
    
    content = content.replace(
        '<p class="empty-cart-text">يبدو أنك لم تضف أي سيارات إلى سلة التسوق بعد. يمكنك استعراض السيارات المتاحة والبدء في اختيار السيارة المناسبة لاحتياجاتك.</p>',
        '<p class="empty-cart-text">{% if is_english %}It looks like you haven\'t added any cars to your cart yet. You can browse available cars and start choosing the right car for your needs.{% else %}يبدو أنك لم تضف أي سيارات إلى سلة التسوق بعد. يمكنك استعراض السيارات المتاحة والبدء في اختيار السيارة المناسبة لاحتياجاتك.{% endif %}</p>'
    )
    
    # تحديث الأزرار والروابط
    content = content.replace(
        '<a href="{% url \'cars\' %}" class="btn btn-primary mt-3">استعراض السيارات</a>',
        '<a href="{% url \'cars\' %}" class="btn btn-primary mt-3">{% if is_english %}Browse Cars{% else %}استعراض السيارات{% endif %}</a>'
    )
    
    # تحديث زر المتابعة للدفع
    content = content.replace(
        '<a href="{% url \'checkout\' %}" class="btn btn-primary btn-lg w-100 mb-3">متابعة للدفع</a>',
        '<a href="{% url \'checkout\' %}" class="btn btn-primary btn-lg w-100 mb-3">{% if is_english %}Proceed to Checkout{% else %}متابعة للدفع{% endif %}</a>'
    )
    
    # تحديث مدة الإيجار
    content = content.replace(
        '<div class="duration-badge bg-light border">مدة الإيجار: {{ item.days }} يوم</div>',
        '<div class="duration-badge bg-light border">{% if is_english %}Rental Duration: {{ item.days }} day(s){% else %}مدة الإيجار: {{ item.days }} يوم{% endif %}</div>'
    )
    
    # تحديث نص التفاصيل في السلة
    content = content.replace(
        '<div class="fw-bold text-primary mb-1">{{ item.car.make }} {{ item.car.model }} {{ item.car.year }}</div>',
        '<div class="fw-bold text-primary mb-1">{{ item.car.make }} {{ item.car.model }} {{ item.car.year }}</div>'
    )
    
    # مزيد من التحديثات للنصوص الأخرى
    content = content.replace(
        '<div class="fs-4 text-primary fw-bold">المجموع: {{ cart_total }} ريال</div>',
        '<div class="fs-4 text-primary fw-bold">{% if is_english %}Total: {{ cart_total }} SAR{% else %}المجموع: {{ cart_total }} ريال{% endif %}</div>'
    )
    
    # حفظ التغييرات
    with open('templates/cart_django.html', 'w', encoding='utf-8') as file:
        file.write(content)
    
    print("تم تحديث قالب السلة بنجاح")

if __name__ == "__main__":
    fix_cart_template()
