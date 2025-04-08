#!/usr/bin/env python3

import re

def update_car_detail_template():
    """Update car detail template to be language-aware for transmission and fuel type"""
    with open('templates/car_detail_django.html', 'r', encoding='utf-8') as file:
        content = file.read()
    
    # Update transmission in car feature cards
    content = re.sub(
        r'<i class="fas fa-cog {% if is_english %}me-2{% else %}ms-2{% endif %}"></i> {{ car.transmission }}',
        '<i class="fas fa-cog {% if is_english %}me-2{% else %}ms-2{% endif %}"></i> '
        '{% if is_english %}'
        '{% if car.transmission == "Automatic" %}Automatic{% elif car.transmission == "Manual" %}Manual{% else %}{{ car.transmission }}{% endif %}'
        '{% else %}'
        '{% if car.transmission == "Automatic" %}أوتوماتيك{% elif car.transmission == "Manual" %}يدوي{% else %}{{ car.transmission }}{% endif %}'
        '{% endif %}',
        content
    )
    
    # Update fuel type in car feature cards
    content = re.sub(
        r'<i class="fas fa-gas-pump {% if is_english %}me-2{% else %}ms-2{% endif %}"></i> {{ car.fuel_type }}',
        '<i class="fas fa-gas-pump {% if is_english %}me-2{% else %}ms-2{% endif %}"></i> '
        '{% if is_english %}'
        '{% if car.fuel_type == "Gas" %}Gas{% elif car.fuel_type == "Diesel" %}Diesel{% elif car.fuel_type == "Electric" %}Electric{% elif car.fuel_type == "Hybrid" %}Hybrid{% else %}{{ car.fuel_type }}{% endif %}'
        '{% else %}'
        '{% if car.fuel_type == "Gas" %}بنزين{% elif car.fuel_type == "Diesel" %}ديزل{% elif car.fuel_type == "Electric" %}كهربائي{% elif car.fuel_type == "Hybrid" %}هجين{% else %}{{ car.fuel_type }}{% endif %}'
        '{% endif %}',
        content
    )
    
    # Update transmission in specifications section
    content = re.sub(
        r'<div class="spec-value">{{ car.transmission }}</div>',
        '<div class="spec-value">'
        '{% if is_english %}'
        '{% if car.transmission == "Automatic" %}Automatic{% elif car.transmission == "Manual" %}Manual{% else %}{{ car.transmission }}{% endif %}'
        '{% else %}'
        '{% if car.transmission == "Automatic" %}أوتوماتيك{% elif car.transmission == "Manual" %}يدوي{% else %}{{ car.transmission }}{% endif %}'
        '{% endif %}'
        '</div>',
        content
    )
    
    # Update fuel type in specifications section
    content = re.sub(
        r'<div class="spec-value">{{ car.fuel_type }}</div>',
        '<div class="spec-value">'
        '{% if is_english %}'
        '{% if car.fuel_type == "Gas" %}Gas{% elif car.fuel_type == "Diesel" %}Diesel{% elif car.fuel_type == "Electric" %}Electric{% elif car.fuel_type == "Hybrid" %}Hybrid{% else %}{{ car.fuel_type }}{% endif %}'
        '{% else %}'
        '{% if car.fuel_type == "Gas" %}بنزين{% elif car.fuel_type == "Diesel" %}ديزل{% elif car.fuel_type == "Electric" %}كهربائي{% elif car.fuel_type == "Hybrid" %}هجين{% else %}{{ car.fuel_type }}{% endif %}'
        '{% endif %}'
        '</div>',
        content
    )
    
    # Write the changes back
    with open('templates/car_detail_django.html', 'w', encoding='utf-8') as file:
        file.write(content)
    
    print("Car detail template updated with language conditionals.")

update_car_detail_template()
