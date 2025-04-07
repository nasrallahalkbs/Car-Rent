#!/usr/bin/env python3
import re

with open('templates/cart_django.html', 'r') as file:
    content = file.read()

# Replace the total_days calculation with our new variable
pattern = re.compile(r'''<div class="cart-summary-item">\s*<span>مجموع الأيام</span>\s*<span>\s*{% with total_days=0 %}.*?{% endwith %}\s*</span>\s*</div>''', re.DOTALL)
replacement = '<div class="cart-summary-item">\n                    <span>مجموع الأيام</span>\n                    <span>{{ total_days }} يوم</span>\n                </div>'

new_content = pattern.sub(replacement, content)

with open('templates/cart_django.html', 'w') as file:
    file.write(new_content)

print("Template updated successfully!")
