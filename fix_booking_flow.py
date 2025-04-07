#!/usr/bin/env python

"""
إصلاح تدفق الحجز - إعادة التوجيه إلى صفحة الحجز بدلاً من السلة
هذا السكربت يصلح وظيفة add_to_cart لإعادة التوجيه إلى صفحة الحجز بدلاً من السلة
"""

import re
import os

def process_file():
    """Process the views.py file"""
    views_path = "rental/views.py"
    
    # Make sure the file exists
    if not os.path.exists(views_path):
        print(f"Error: {views_path} does not exist")
        return False
    
    # Read the file
    with open(views_path, "r", encoding="utf-8") as file:
        content = file.read()
    
    # Fix add_to_cart function
    updated_content = fix_add_to_cart(content)
    
    # Write the changes back to the file
    with open(views_path, "w", encoding="utf-8") as file:
        file.write(updated_content)
    
    print(f"Successfully updated {views_path}")
    return True

def fix_add_to_cart(content):
    """Update add_to_cart function to redirect to book_car instead of cart"""
    # Find the add_to_cart function
    add_to_cart_pattern = r"@login_required\s+def add_to_cart\(request\):.*?return redirect\('cart'\)"
    
    # Find the function in the content
    add_to_cart_match = re.search(add_to_cart_pattern, content, re.DOTALL)
    
    if not add_to_cart_match:
        print("add_to_cart function not found")
        return content
    
    old_function = add_to_cart_match.group(0)
    
    # Replace the redirect at the end of the function
    new_function = old_function.replace("return redirect('cart')", "return redirect('book_car', car_id=car_id)")
    
    # Update the content
    return content.replace(old_function, new_function)

if __name__ == "__main__":
    process_file()
