"""
إصلاح تنسيق التاريخ وترجمة عناصر واجهة المستخدم في ملف payments_django.html
"""

def fix_payments_page():
    try:
        with open('templates/admin/payments_django.html', 'r', encoding='utf-8') as file:
            content = file.read()
        
        # تحديث تنسيق التاريخ على أساس اللغة
        content = content.replace(
            '<div>{{ payment.created_at|date:"d/m/Y" }}</div>',
            '<div>{% if is_english %}{{ payment.created_at|date:"m/d/Y" }}{% else %}{{ payment.created_at|date:"Y/m/d" }}{% endif %}</div>'
        )
        
        # ترجمة عناصر واجهة المستخدم
        content = content.replace(
            '<label for="date_from" class="form-label">من تاريخ</label>',
            '<label for="date_from" class="form-label">{% if is_english %}From Date{% else %}من تاريخ{% endif %}</label>'
        )
        
        content = content.replace(
            '<label for="date_to" class="form-label">إلى تاريخ</label>',
            '<label for="date_to" class="form-label">{% if is_english %}To Date{% else %}إلى تاريخ{% endif %}</label>'
        )
        
        # حفظ التغييرات
        with open('templates/admin/payments_django.html', 'w', encoding='utf-8') as file:
            file.write(content)
        
        print("تم إصلاح تنسيق التاريخ وترجمة عناصر واجهة المستخدم في ملف payments_django.html")
    
    except FileNotFoundError:
        print("ملف payments_django.html غير موجود. تحقق من المسار الصحيح.")

if __name__ == "__main__":
    fix_payments_page()
