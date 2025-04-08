"""
إصلاح تنسيق التاريخ في قالب سلة التسوق
هذا السكريبت يحدث تنسيق التاريخ ليكون متوافقًا مع اللغة المحددة
"""

def fix_date_format():
    with open('templates/cart_django.html', 'r') as file:
        content = file.read()
    
    # استبدال تنسيق تاريخ البداية
    content = content.replace(
        '<div class="cart-date-value">{{ item.start_date|date:"d F Y" }}</div>',
        '<div class="cart-date-value">{% if is_english %}{{ item.start_date|date:"F d, Y" }}{% else %}{{ item.start_date|date:"d F Y" }}{% endif %}</div>'
    )
    
    # استبدال تنسيق تاريخ النهاية
    content = content.replace(
        '<div class="cart-date-value">{{ item.end_date|date:"d F Y" }}</div>',
        '<div class="cart-date-value">{% if is_english %}{{ item.end_date|date:"F d, Y" }}{% else %}{{ item.end_date|date:"d F Y" }}{% endif %}</div>'
    )
    
    # حفظ الملف بعد التحديث
    with open('templates/cart_django.html', 'w') as file:
        file.write(content)
    
    print("تم تحديث تنسيق التاريخ في ملف سلة التسوق بنجاح.")

if __name__ == "__main__":
    fix_date_format()
