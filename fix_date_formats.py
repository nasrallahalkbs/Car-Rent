#!/usr/bin/env python3

"""
Fix date formatting in Arabic templates.
This script replaces English date formats with Arabic date formats.
"""

import os

# List of templates to fix (Arabic templates)
templates_to_fix = [
    'templates/profile.html',
    'templates/my_reservations.html',
    'templates/confirmation.html',
    'templates/cart_django.html'
]

for template_path in templates_to_fix:
    # Skip if file doesn't exist
    if not os.path.exists(template_path):
        print(f"Skipping {template_path}: File does not exist")
        continue
        
    try:
        with open(template_path, 'r', encoding='utf-8') as file:
            content = file.read()
            
        # Replace date formats for Arabic display
        # Replacing Y-m-d with custom format
        content = content.replace('|date:"Y-m-d"', '|date:"d F Y"')
        
        # Replace the direct date displays to use Arabic locale format
        # This format works with Django's date filter to output dates in Arabic format
        content = content.replace('{{ reservation.start_date }}', '{{ reservation.start_date|date:"d F Y" }}')
        content = content.replace('{{ reservation.end_date }}', '{{ reservation.end_date|date:"d F Y" }}')
        content = content.replace('{{ current_user.date_joined }}', '{{ current_user.date_joined|date:"d F Y" }}')
        
        with open(template_path, 'w', encoding='utf-8') as file:
            file.write(content)
            
        print(f"Fixed date formats in {template_path}")
    except Exception as e:
        print(f"Error fixing {template_path}: {e}")

print("Date format fix completed!")