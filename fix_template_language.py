#!/usr/bin/env python3

def update_template_function():
    with open('rental/views.py', 'r', encoding='utf-8') as file:
        content = file.read()
    
    # Find the get_template_by_language function
    start = content.find("def get_template_by_language")
    if start == -1:
        print("Function not found!")
        return
    
    # Find the end of the function
    end = content.find("def", start + 1)
    if end == -1:
        print("End of function not found!")
        return
    
    old_function = content[start:end]
    
    # Create the new function
    new_function = """def get_template_by_language(request, base_template):
    \"\"\"Helper function to choose the appropriate template based on language setting\"\"\"
    # Always use the Arabic design template regardless of language
    
    # For cars.html
    if base_template == 'cars.html':
        return 'cars_django.html'
    
    # For index.html - always use Arabic design template
    if base_template == 'index.html':
        return 'index_arabic.html'
    
    # For profile.html - always use Arabic design template
    if base_template == 'profile.html':
        return 'profile_arabic.html'
    
    # For car detail - always use Arabic design template
    if base_template == 'car_detail.html':
        return 'car_detail_django.html'
    
    # Handle templates with _django suffix for all languages
    if base_template.endswith('.html'):
        base_name = base_template[:-5]
        # Check if *_django.html exists (used for templates with Arabic design)
        django_template = f"{base_name}_django.html"
        if django_template in ['login_django.html', 'register_django.html', 'checkout_django.html', 'confirmation_django.html']:
            return django_template
    
    # Default fallback - use the base template unchanged
    return base_template

"""
    
    # Replace the old function with the new one
    updated_content = content.replace(old_function, new_function)
    
    with open('rental/views.py', 'w', encoding='utf-8') as file:
        file.write(updated_content)
    
    print("Template function has been updated to always use Arabic design.")

update_template_function()
