"""
إصلاح تنسيق التاريخ في ملف payment_detail_django.html
"""

def fix_payment_detail():
    with open('templates/admin/payment_detail_django.html', 'r', encoding='utf-8') as file:
        content = file.read()
    
    # تحديث تنسيق التاريخ على أساس اللغة
    content = content.replace(
        '{{ payment.date|date:"d/m/Y H:i" }}',
        '{% if is_english %}{{ payment.date|date:"m/d/Y h:i A" }}{% else %}{{ payment.date|date:"Y/m/d H:i" }}{% endif %}'
    )
    
    content = content.replace(
        '<div class="fw-bold">{{ payment.date|date:"d/m/Y" }}</div>',
        '<div class="fw-bold">{% if is_english %}{{ payment.date|date:"m/d/Y" }}{% else %}{{ payment.date|date:"Y/m/d" }}{% endif %}</div>'
    )
    
    content = content.replace(
        '<div class="fw-bold">{{ payment.start_date|date:"d/m/Y" }}</div>',
        '<div class="fw-bold">{% if is_english %}{{ payment.start_date|date:"m/d/Y" }}{% else %}{{ payment.start_date|date:"Y/m/d" }}{% endif %}</div>'
    )
    
    content = content.replace(
        '<div class="fw-bold">{{ payment.end_date|date:"d/m/Y" }}</div>',
        '<div class="fw-bold">{% if is_english %}{{ payment.end_date|date:"m/d/Y" }}{% else %}{{ payment.end_date|date:"Y/m/d" }}{% endif %}</div>'
    )
    
    # حفظ التغييرات
    with open('templates/admin/payment_detail_django.html', 'w', encoding='utf-8') as file:
        file.write(content)
    
    print("تم إصلاح تنسيق التاريخ في ملف payment_detail_django.html")

if __name__ == "__main__":
    try:
        fix_payment_detail()
    except FileNotFoundError:
        print("ملف payment_detail_django.html غير موجود. تحقق من المسار الصحيح.")
