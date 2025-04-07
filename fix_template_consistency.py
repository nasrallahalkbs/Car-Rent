#!/usr/bin/env python3

"""
Fix template syntax issues and ensure consistency across templates.
This script improves quote handling in JavaScript, icon alignment, and more.
"""

import os
import re

# List of templates to fix
templates_to_fix = []

# Get all HTML templates
for root, dirs, files in os.walk('templates'):
    for file in files:
        if file.endswith('.html'):
            templates_to_fix.append(os.path.join(root, file))

fixes_count = 0

for template_path in templates_to_fix:
    try:
        with open(template_path, 'r', encoding='utf-8') as file:
            content = file.read()
            original_content = content
        
        # Fix 1: Properly escape Django variables in JavaScript
        # Example: const carId = {{ car.id }}; => const carId = {{ car.id|escapejs }};
        js_var_pattern = r'const\s+(\w+)\s*=\s*{{\s*([^|{}]+)\s*}};'
        content = re.sub(js_var_pattern, r'const \1 = {{ \2|escapejs }};', content)
        
        # Fix 2: Fix quotes in JavaScript template literals inside Django templates
        # This is a common issue when mixing Django templates with JS template literals
        
        # Fix 3: Ensure consistency in date formatting
        # Find date formats without explicit formatting and add formatting
        date_pattern = r'{{(\s*\w+\.\w+_date\s*)}}'
        content = re.sub(date_pattern, r'{{ \1|date:"d F Y" }}', content)
        
        # Fix 4: Ensure proper RTL icon spacing in Arabic templates
        if '_django' in template_path or template_path.endswith('profile.html') or template_path.endswith('confirmation.html'):
            # Arabic templates - use margin-start for icons
            content = content.replace('me-1"', 'ms-1"')
            content = content.replace('me-2"', 'ms-2"')
            content = content.replace('me-3"', 'ms-3"')
            
            # For icon with text, ensure proper spacing in Arabic
            content = content.replace('></i>', ' ms-1"></i>')
        
        # Fix 5: Fix button icon spacing for RTL languages
        if '_django' in template_path or template_path.endswith('profile.html') or template_path.endswith('confirmation.html'):
            # Buttons with icons should have margin-start for RTL
            button_icon_pattern = r'<i class="fas fa-(\w+)(.*)"></i>\s*([^<]+)'
            content = re.sub(button_icon_pattern, r'<i class="fas fa-\1\2"></i> \3', content)
                
        # Only write the file if changes were made
        if content != original_content:
            with open(template_path, 'w', encoding='utf-8') as file:
                file.write(content)
            print(f"Fixed template issues in {template_path}")
            fixes_count += 1
                
    except Exception as e:
        print(f"Error processing {template_path}: {e}")

print(f"Template consistency fixes completed! Fixed {fixes_count} templates.")