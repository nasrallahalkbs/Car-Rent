"""
تحديث نص الشعار البديل في admin_layout.html ليتناسب مع اللغة
"""

def fix_admin_logo():
    with open('templates/admin_layout.html', 'r') as file:
        content = file.read()
    
    # تحديث نص الشعار البديل
    content = content.replace(
        'alt="كاررنتال - شعار"',
        'alt="{% if is_english %}CarRental - Logo{% else %}كاررنتال - شعار{% endif %}"'
    )
    
    # حفظ التغييرات
    with open('templates/admin_layout.html', 'w') as file:
        file.write(content)
    
    print("تم تحديث نص الشعار البديل في admin_layout.html")

if __name__ == "__main__":
    fix_admin_logo()
