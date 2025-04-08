#!/usr/bin/env python3

import re

"""
Translate profile.html to Arabic.
"""

def translate_profile():
    with open('templates/profile.html', 'r', encoding='utf-8') as file:
        content = file.read()
    
    # Fix the date format to be language-aware
    content = re.sub(
        r'{{ user.date_joined\|date:"d b Y" }}',
        r'{% if is_english %}{{ user.date_joined|date:"d M Y" }}{% else %}{{ user.date_joined|date:"d M Y" }}{% endif %}',
        content
    )
    
    # Write the changes back
    with open('templates/profile.html', 'w', encoding='utf-8') as file:
        file.write(content)
    
    print("Profile template updated with proper date formatting.")

translate_profile()
