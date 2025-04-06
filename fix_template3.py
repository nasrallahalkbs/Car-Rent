#!/usr/bin/env python3
# Fix the car detail template

import re

# Read the file
with open('templates/car_detail_django.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Fix the double quotes issue (third instance)
fixed = content.replace(
    'unavailableDatesContainer.innerHTML = "<p class="text-success mb-0 text-center py-4"><i class="fas fa-check-circle ms-2"></i>لا توجد تواريخ محجوزة حالياً!</p>";',
    'unavailableDatesContainer.innerHTML = \'<p class="text-success mb-0 text-center py-4"><i class="fas fa-check-circle ms-2"></i>لا توجد تواريخ محجوزة حالياً!</p>\';'
)

# Write the file back
with open('templates/car_detail_django.html', 'w', encoding='utf-8') as f:
    f.write(fixed)

print("Template fixed successfully")
