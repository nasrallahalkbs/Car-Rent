#!/usr/bin/env python3

def fix_cars_template():
    with open('templates/cars_django.html', 'r', encoding='utf-8') as file:
        content = file.read()
    
    # Fix the escaped single quotes in url tags
    content = content.replace("{% url \\'car_detail\\'", "{% url 'car_detail'")
    
    # Write the updated content back to the file
    with open('templates/cars_django.html', 'w', encoding='utf-8') as file:
        file.write(content)
    
    print("Fixed escaped quotes in cars template.")

fix_cars_template()
