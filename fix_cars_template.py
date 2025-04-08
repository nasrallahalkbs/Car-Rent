#!/usr/bin/env python3

import re

def fix_cars_template():
    with open('templates/cars_django.html', 'r', encoding='utf-8') as file:
        content = file.read()
    
    # 1. Fix view details button
    content = re.sub(
        r'<a href="{% url \'car_detail\' car_id=car.id %}" class="btn-view-details">\s*عرض التفاصيل <i class="fas fa-arrow-left ms-1></i>\s*</a>',
        r'<a href="{% url \'car_detail\' car_id=car.id %}" class="btn-view-details">{% if is_english %}View Details <i class="fas fa-arrow-right me-1"></i>{% else %}عرض التفاصيل <i class="fas fa-arrow-left ms-1"></i>{% endif %}</a>',
        content
    )
    
    # 2. Fix add to favorites button
    content = re.sub(
        r'<button class="btn-add-favorite" type="button" title="إضافة للمفضلة">\s*<i class="far fa-heart" ms-1></i>',
        r'<button class="btn-add-favorite" type="button" title="{% if is_english %}Add to Favorites{% else %}إضافة للمفضلة{% endif %}"><i class="far fa-heart {% if is_english %}me-1{% else %}ms-1{% endif %}"></i>',
        content
    )
    
    # 3. Fix car title for proper language display
    content = re.sub(
        r'<h5 class="car-title">{{ car.make }} {{ car.model }} {{ car.year }}</h5>',
        r'<h5 class="car-title">{{ car.make }} {{ car.model }} {{ car.year }}</h5>',
        content
    )
    
    # 4. Ensure correct CSS for RTL/LTR
    # Check margin-left style
    content = re.sub(
        r'margin-left: 6px;',
        r'{% if is_english %}margin-right: 6px;{% else %}margin-left: 6px;{% endif %}',
        content
    )
    
    # 5. Make sure right/left positioning is language-aware
    content = re.sub(
        r'right: 0;',
        r'{% if is_english %}left: 0;{% else %}right: 0;{% endif %}',
        content
    )
    
    content = re.sub(
        r'left: 12px;',
        r'{% if is_english %}right: 12px;{% else %}left: 12px;{% endif %}',
        content
    )
    
    content = re.sub(
        r'right: 12px;',
        r'{% if is_english %}left: 12px;{% else %}right: 12px;{% endif %}',
        content
    )
    
    # 6. Fix border-right for price display
    content = re.sub(
        r'border-right: 4px solid var\(--primary-color\);',
        r'{% if is_english %}border-left: 4px solid var(--primary-color);{% else %}border-right: 4px solid var(--primary-color);{% endif %}',
        content
    )
    
    # Fix any other issues with button text and icons
    content = re.sub(
        r'<i class="fas fa-([a-z-]+)" ms-1></i>',
        r'<i class="fas fa-\1 {% if is_english %}me-1{% else %}ms-1{% endif %}"></i>',
        content
    )
    
    # Make empty state message bilingual if it exists
    content = re.sub(
        r'<h3 class="empty-title">لا توجد سيارات متاحة</h3>',
        r'<h3 class="empty-title">{% if is_english %}No Cars Available{% else %}لا توجد سيارات متاحة{% endif %}</h3>',
        content
    )
    
    content = re.sub(
        r'<p class="empty-message">لم نتمكن من العثور على سيارات تطابق معايير البحث المحددة. يرجى تعديل معايير البحث والمحاولة مرة أخرى.</p>',
        r'<p class="empty-message">{% if is_english %}We couldn\'t find any cars matching your search criteria. Please adjust your search criteria and try again.{% else %}لم نتمكن من العثور على سيارات تطابق معايير البحث المحددة. يرجى تعديل معايير البحث والمحاولة مرة أخرى.{% endif %}</p>',
        content
    )

    # Write the updated content back to the file
    with open('templates/cars_django.html', 'w', encoding='utf-8') as file:
        file.write(content)
    
    print("Cars template has been fixed for bilingual support.")

if __name__ == "__main__":
    fix_cars_template()
