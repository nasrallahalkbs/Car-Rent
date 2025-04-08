"""
إصلاح أيقونات واجهة المستخدم في قالب car_detail_django.html
"""

def fix_icons():
    with open('templates/car_detail_django.html', 'r') as file:
        content = file.read()
    
    # أنماط الاستبدال للأيقونات
    content = content.replace(
        '<i class="fas fa-car {% if is_english %}me-2{% else %}ms-2{% endif %}">',
        '<i class="fas fa-car {% if is_english %}me-2{% else %}ms-2{% endif %}">'
    )
    
    content = content.replace(
        '<i class="fas fa-cog {% if is_english %}me-2{% else %}ms-2{% endif %}">',
        '<i class="fas fa-cog {% if is_english %}me-2{% else %}ms-2{% endif %}">'
    )
    
    content = content.replace(
        '<i class="fas fa-gas-pump {% if is_english %}me-2{% else %}ms-2{% endif %}">',
        '<i class="fas fa-gas-pump {% if is_english %}me-2{% else %}ms-2{% endif %}">'
    )
    
    content = content.replace(
        '<i class="fas fa-check-circle {% if is_english %}me-2{% else %}ms-2{% endif %}">',
        '<i class="fas fa-check-circle {% if is_english %}me-2{% else %}ms-2{% endif %}">'
    )
    
    content = content.replace(
        '<i class="fas fa-times-circle {% if is_english %}me-2{% else %}ms-2{% endif %}">',
        '<i class="fas fa-times-circle {% if is_english %}me-2{% else %}ms-2{% endif %}">'
    )
    
    content = content.replace(
        '<i class="fas fa-info-circle {% if is_english %}me-2{% else %}ms-2{% endif %}">',
        '<i class="fas fa-info-circle {% if is_english %}me-2{% else %}ms-2{% endif %}">'
    )
    
    content = content.replace(
        '<i class="fas fa-list {% if is_english %}me-2{% else %}ms-2{% endif %}">',
        '<i class="fas fa-list {% if is_english %}me-2{% else %}ms-2{% endif %}">'
    )
    
    content = content.replace(
        '<i class="fas fa-calendar-times {% if is_english %}me-2{% else %}ms-2{% endif %}">',
        '<i class="fas fa-calendar-times {% if is_english %}me-2{% else %}ms-2{% endif %}">'
    )
    
    content = content.replace(
        '<i class="fas fa-calendar-check {% if is_english %}me-2{% else %}ms-2{% endif %}">',
        '<i class="fas fa-calendar-check {% if is_english %}me-2{% else %}ms-2{% endif %}">'
    )
    
    # حفظ الملف بعد التحديث
    with open('templates/car_detail_django.html', 'w') as file:
        file.write(content)
    
    print("تم إصلاح أيقونات القالب بنجاح.")

if __name__ == "__main__":
    fix_icons()
