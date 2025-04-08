#!/usr/bin/env python3

import re

def update_toggle_button():
    with open('templates/layout_django.html', 'r', encoding='utf-8') as file:
        content = file.read()
    
    # Pattern for language toggle button
    pattern = r'(<li class="nav-item">\s*<a class="nav-link btn btn-sm btn-outline-primary mx-2 px-3" href="\{% url \'toggle_language\' %\}">\s*<i class="fas fa-language ms-1"></i>.*?Switch to English\s*</a>)'
    
    # New content with conditional language
    replacement = '''<li class="nav-item">
                        <a class="nav-link btn btn-sm btn-outline-primary mx-2 px-3" href="{% url 'toggle_language' %}">
                            <i class="fas fa-language {% if is_english %}me-1{% else %}ms-1{% endif %}"></i> 
                            {% if is_english %}التحويل إلى العربية{% else %}Switch to English{% endif %}
                        </a>'''
    
    # Replace in content
    updated = re.sub(pattern, replacement, content, flags=re.DOTALL)
    
    with open('templates/layout_django.html', 'w', encoding='utf-8') as file:
        file.write(updated)
    
    print("Toggle language button has been updated to be dynamic based on current language.")

update_toggle_button()
