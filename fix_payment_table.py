"""
إصلاح تنسيق التاريخ في ملف payment_table_django.html
"""

def fix_payment_table():
    with open('templates/admin/payment_table_django.html', 'r') as file:
        content = file.read()
    
    # تحديث تنسيق التاريخ على أساس اللغة
    content = content.replace(
        '<div>{{ payment.date|date:"Y/m/d" }}</div>',
        '<div>{% if is_english %}{{ payment.date|date:"m/d/Y" }}{% else %}{{ payment.date|date:"Y/m/d" }}{% endif %}</div>'
    )
    
    content = content.replace(
        '<small class="text-muted">{{ payment.date|date:"H:i" }}</small>',
        '<small class="text-muted">{% if is_english %}{{ payment.date|date:"h:i A" }}{% else %}{{ payment.date|date:"H:i" }}{% endif %}</small>'
    )
    
    # حفظ التغييرات
    with open('templates/admin/payment_table_django.html', 'w') as file:
        file.write(content)
    
    print("تم إصلاح تنسيق التاريخ في ملف payment_table_django.html")

if __name__ == "__main__":
    fix_payment_table()
