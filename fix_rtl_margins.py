#!/usr/bin/env python3

"""
Fix template RTL margin issues.
This script replaces 'me-X' with 'ms-X' in the Arabic templates.
"""

import os

# List of templates to fix (Arabic templates)
templates_to_fix = [
    'templates/confirmation.html',
    'templates/cart_django.html',
    'templates/car_detail_django.html',
    'templates/profile.html',
    'templates/my_reservations.html',
    'templates/cars_django.html'
]

for template_path in templates_to_fix:
    # Skip if file doesn't exist
    if not os.path.exists(template_path):
        print(f"Skipping {template_path}: File does not exist")
        continue
        
    try:
        with open(template_path, 'r', encoding='utf-8') as file:
            content = file.read()
            
        # Replace me-X with ms-X for RTL support in Arabic templates
        for i in range(1, 6):
            # For clarity: me = margin-end, ms = margin-start
            # In RTL (Arabic), we need margin-start (ms) where English templates use margin-end (me)
            content = content.replace(f'me-{i}"', f'ms-{i}"')
            content = content.replace(f'me-{i} ', f'ms-{i} ')
            
        with open(template_path, 'w', encoding='utf-8') as file:
            file.write(content)
            
        print(f"Fixed margin classes in {template_path}")
    except Exception as e:
        print(f"Error fixing {template_path}: {e}")

print("RTL margin fix completed!")