#!/usr/bin/env python3

import re

def update_car_detail_badges():
    """Update car category badge in car detail template to be language-aware"""
    with open('templates/car_detail_django.html', 'r', encoding='utf-8') as file:
        content = file.read()
    
    # Update category badge
    content = re.sub(
        r'<i class="fas fa-car {% if is_english %}me-2{% else %}ms-2{% endif %}"></i> {{ car.category }}',
        '<i class="fas fa-car {% if is_english %}me-2{% else %}ms-2{% endif %}"></i> '
        '{% if is_english %}'
        '{% if car.category == "Economy" %}Economy{% elif car.category == "Compact" %}Compact{% elif car.category == "Mid-size" %}Mid-size{% elif car.category == "Luxury" %}Luxury{% elif car.category == "SUV" %}SUV{% elif car.category == "Truck" %}Truck{% else %}{{ car.category }}{% endif %}'
        '{% else %}'
        '{% if car.category == "Economy" %}اقتصادية{% elif car.category == "Compact" %}مدمجة{% elif car.category == "Mid-size" %}متوسطة{% elif car.category == "Luxury" %}فاخرة{% elif car.category == "SUV" %}دفع رباعي{% elif car.category == "Truck" %}شاحنات{% else %}{{ car.category }}{% endif %}'
        '{% endif %}',
        content
    )
    
    # Fix seats information
    content = re.sub(
        r'<div class="spec-value">{{ car.seats }}</div>',
        '<div class="spec-value">{{ car.seats }} {% if is_english %}Seats{% else %}مقاعد{% endif %}</div>',
        content
    )
    
    # Fix category in specifications section
    content = re.sub(
        r'<div class="spec-value">{{ car.category }}</div>',
        '<div class="spec-value">'
        '{% if is_english %}'
        '{% if car.category == "Economy" %}Economy{% elif car.category == "Compact" %}Compact{% elif car.category == "Mid-size" %}Mid-size{% elif car.category == "Luxury" %}Luxury{% elif car.category == "SUV" %}SUV{% elif car.category == "Truck" %}Truck{% else %}{{ car.category }}{% endif %}'
        '{% else %}'
        '{% if car.category == "Economy" %}اقتصادية{% elif car.category == "Compact" %}مدمجة{% elif car.category == "Mid-size" %}متوسطة{% elif car.category == "Luxury" %}فاخرة{% elif car.category == "SUV" %}دفع رباعي{% elif car.category == "Truck" %}شاحنات{% else %}{{ car.category }}{% endif %}'
        '{% endif %}'
        '</div>',
        content
    )
    
    # Write the changes back
    with open('templates/car_detail_django.html', 'w', encoding='utf-8') as file:
        file.write(content)
    
    print("Car detail badges updated with language conditionals.")

update_car_detail_badges()
