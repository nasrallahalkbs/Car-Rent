"""
إصلاح تنسيق التاريخ في ملف payment_receipt_django.html
"""

def fix_payment_receipt():
    try:
        with open('templates/admin/payment_receipt_django.html', 'r', encoding='utf-8') as file:
            content = file.read()
        
        # تحديث تنسيق التاريخ على أساس اللغة
        content = content.replace(
            '<div class="text-muted">{{ payment.date|date:"d/m/Y H:i" }}</div>',
            '<div class="text-muted">{% if is_english %}{{ payment.date|date:"m/d/Y h:i A" }}{% else %}{{ payment.date|date:"Y/m/d H:i" }}{% endif %}</div>'
        )
        
        content = content.replace(
            '<div>{{ payment.date|date:"d/m/Y" }}</div>',
            '<div>{% if is_english %}{{ payment.date|date:"m/d/Y" }}{% else %}{{ payment.date|date:"Y/m/d" }}{% endif %}</div>'
        )
        
        content = content.replace(
            '<div>من: {{ payment.reservation.start_date|date:"d/m/Y" }}</div>',
            '<div>{% if is_english %}From: {{ payment.reservation.start_date|date:"m/d/Y" }}{% else %}من: {{ payment.reservation.start_date|date:"Y/m/d" }}{% endif %}</div>'
        )
        
        content = content.replace(
            '<div>إلى: {{ payment.reservation.end_date|date:"d/m/Y" }}</div>',
            '<div>{% if is_english %}To: {{ payment.reservation.end_date|date:"m/d/Y" }}{% else %}إلى: {{ payment.reservation.end_date|date:"Y/m/d" }}{% endif %}</div>'
        )
        
        content = content.replace(
            '<div>{{ current_datetime|date:"d/m/Y H:i" }}</div>',
            '<div>{% if is_english %}{{ current_datetime|date:"m/d/Y h:i A" }}{% else %}{{ current_datetime|date:"Y/m/d H:i" }}{% endif %}</div>'
        )
        
        # حفظ التغييرات
        with open('templates/admin/payment_receipt_django.html', 'w', encoding='utf-8') as file:
            file.write(content)
        
        print("تم إصلاح تنسيق التاريخ في ملف payment_receipt_django.html")
    
    except FileNotFoundError:
        print("ملف payment_receipt_django.html غير موجود. تحقق من المسار الصحيح.")

if __name__ == "__main__":
    fix_payment_receipt()
