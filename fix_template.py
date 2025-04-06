#!/usr/bin/env python3
# Fix the car detail template

import re

# Read the file
with open('templates/car_detail_django.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Fix the double quotes issue
fixed = content.replace(
    'unavailableDatesContainer.innerHTML = "<p class="text-danger mb-0 text-center py-4"><i class="fas fa-exclamation-circle ms-2"></i>حدث خطأ أثناء تحميل التواريخ المحجوزة</p>";',
    'unavailableDatesContainer.innerHTML = \'<p class="text-danger mb-0 text-center py-4"><i class="fas fa-exclamation-circle ms-2"></i>حدث خطأ أثناء تحميل التواريخ المحجوزة</p>\';'
)

# Write the file back
with open('templates/car_detail_django.html', 'w', encoding='utf-8') as f:
    f.write(fixed)

print("Template fixed successfully")
