"""
إصلاح تنسيق التاريخ في قالب الحجوزات
هذا السكريبت يحدث تنسيق التاريخ ليكون متوافقًا مع اللغة المحددة
"""

def fix_date_format():
    with open('templates/my_reservations_django.html', 'r') as file:
        content = file.read()
    
    # استبدال تنسيق التواريخ
    content = content.replace(
        '<div>{{ reservation.start_date|date:"d/m/Y" }} - {{ reservation.end_date|date:"d/m/Y" }}</div>',
        '<div>{% if is_english %}{{ reservation.start_date|date:"m/d/Y" }} - {{ reservation.end_date|date:"m/d/Y" }}{% else %}{{ reservation.start_date|date:"d/m/Y" }} - {{ reservation.end_date|date:"d/m/Y" }}{% endif %}</div>'
    )
    
    # حفظ الملف بعد التحديث
    with open('templates/my_reservations_django.html', 'w') as file:
        file.write(content)
    
    print("تم تحديث تنسيق التاريخ في ملف الحجوزات بنجاح.")

if __name__ == "__main__":
    fix_date_format()
