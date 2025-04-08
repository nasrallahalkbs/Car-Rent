#!/usr/bin/env python3

import re

def update_car_features():
    """Update car features in cars_django.html to be language-aware"""
    with open('templates/cars_django.html', 'r', encoding='utf-8') as file:
        content = file.read()
    
    # Fix missing quotes in availability badges
    content = re.sub(
        r'<i class="fas fa-check-circle ms-1></i> متاحة',
        '<i class="fas fa-check-circle {% if is_english %}me-1{% else %}ms-1{% endif %}"></i> {% if is_english %}Available{% else %}متاحة{% endif %}',
        content
    )
    
    content = re.sub(
        r'<i class="fas fa-times-circle ms-1></i> غير متاحة',
        '<i class="fas fa-times-circle {% if is_english %}me-1{% else %}ms-1{% endif %}"></i> {% if is_english %}Unavailable{% else %}غير متاحة{% endif %}',
        content
    )
    
    # Add language support for mid-size, compact and truck categories
    compact_badge = '''
                                {% elif car.category == 'Compact' %}
                                <div class="car-badge badge-compact">
                                    <i class="fas fa-car-side {% if is_english %}me-1{% else %}ms-1{% endif %}"></i> {% if is_english %}Compact{% else %}مدمجة{% endif %}
                                </div>'''
    
    midsize_badge = '''
                                {% elif car.category == 'Mid-size' %}
                                <div class="car-badge badge-midsize">
                                    <i class="fas fa-car {% if is_english %}me-1{% else %}ms-1{% endif %}"></i> {% if is_english %}Mid-size{% else %}متوسطة{% endif %}
                                </div>'''
    
    truck_badge = '''
                                {% elif car.category == 'Truck' %}
                                <div class="car-badge badge-truck">
                                    <i class="fas fa-truck-pickup {% if is_english %}me-1{% else %}ms-1{% endif %}"></i> {% if is_english %}Truck{% else %}شاحنات{% endif %}
                                </div>'''
    
    # Add CSS for new badges
    badge_css = '''
    .badge-compact {
        background: linear-gradient(45deg, #0d9488, #5eead4);
        color: white;
    }
    
    .badge-midsize {
        background: linear-gradient(45deg, #0369a1, #7dd3fc);
        color: white;
    }
    
    .badge-truck {
        background: linear-gradient(45deg, #b91c1c, #f87171);
        color: white;
    }'''
    
    # Insert new badge CSS after last badge class
    if '.badge-suv {' in content:
        content = content.replace('.badge-suv {', badge_css + '\n\n    .badge-suv {')
    
    # Add badge HTML for new categories
    if '{% elif car.category == \'SUV\' %}' in content:
        content = content.replace('{% elif car.category == \'SUV\' %}', 
                                 compact_badge + midsize_badge + truck_badge + '\n                                {% elif car.category == \'SUV\' %}')
    
    # Write the changes back
    with open('templates/cars_django.html', 'w', encoding='utf-8') as file:
        file.write(content)
    
    print("Car features updated with language conditionals.")

update_car_features()
