"""
إصلاح تنسيق التاريخ ومشكلة علامة ms-1 في ملف reservation_table_django.html
"""

def fix_reservation_table():
    with open('templates/admin/reservation_table_django.html', 'r') as file:
        content = file.read()
    
    # إصلاح مشكلة علامة ms-1 غير المغلقة
    content = content.replace(
        '<i class="fas fa-calendar-alt me-1 text-muted" ms-1></i>',
        '<i class="fas fa-calendar-alt {% if is_english %}me-1{% else %}ms-1{% endif %} text-muted"></i>'
    )
    
    content = content.replace(
        '<i class="fas fa-clock ms-1></i>',
        '<i class="fas fa-clock {% if is_english %}me-1{% else %}ms-1{% endif %}"></i>'
    )
    
    # تحديث تنسيق التاريخ حسب اللغة
    content = content.replace(
        '{{ item.reservation.start_date|date:"Y/m/d" }}',
        '{% if is_english %}{{ item.reservation.start_date|date:"m/d/Y" }}{% else %}{{ item.reservation.start_date|date:"Y/m/d" }}{% endif %}'
    )
    
    content = content.replace(
        '{{ item.reservation.end_date|date:"Y/m/d" }}',
        '{% if is_english %}{{ item.reservation.end_date|date:"m/d/Y" }}{% else %}{{ item.reservation.end_date|date:"Y/m/d" }}{% endif %}'
    )
    
    content = content.replace(
        '{{ item.reservation.created_at|date:"Y/m/d H:i" }}',
        '{% if is_english %}{{ item.reservation.created_at|date:"m/d/Y h:i A" }}{% else %}{{ item.reservation.created_at|date:"Y/m/d H:i" }}{% endif %}'
    )
    
    # حفظ التغييرات
    with open('templates/admin/reservation_table_django.html', 'w') as file:
        file.write(content)
    
    print("تم إصلاح تنسيق التاريخ ومشكلة علامة ms-1 في ملف reservation_table_django.html")

if __name__ == "__main__":
    fix_reservation_table()
