#!/usr/bin/env python3

import re

"""
Fix template RTL margin issues.
This script replaces 'me-X' with 'ms-X' in the Arabic templates.
"""

def fix_rtl_margins():
    with open('templates/layout.html', 'r', encoding='utf-8') as file:
        content = file.read()
    
    # Fix fixed me-X margins in Arabic section 
    # Arabic navbar uses ms-X for right margins
    content = re.sub(
        r'<i class="fas fa-language me-1"></i> تبديل إلى العربية',
        '<i class="fas fa-language {% if is_english %}me-1{% else %}ms-1{% endif %}"></i> تبديل إلى العربية',
        content
    )
    
    # Fix fixed ms-X margins in English section
    # English navbar uses me-X for right margins
    content = re.sub(
        r'class="dropdown me-3"',
        'class="dropdown {% if is_english %}me-3{% else %}ms-3{% endif %}"',
        content
    )
    
    content = re.sub(
        r'<a href="{% url \'cart\' %}" class="me-3 position-relative">',
        '<a href="{% url \'cart\' %}" class="{% if is_english %}me-3{% else %}ms-3{% endif %} position-relative">',
        content
    )
    
    # Write the changes back
    with open('templates/layout.html', 'w', encoding='utf-8') as file:
        file.write(content)
    
    print("Fixed RTL margin issues in layout.html.")

fix_rtl_margins()
