#!/usr/bin/env python3
"""
تحديث دالة عرض الأرشيف لاستخدام القالب المصحح
"""

import os

def update_windows_explorer_view():
    """تحديث ملف windows_explorer_view.py لاستخدام القالب المصحح"""
    file_path = 'rental/windows_explorer_view.py'
    
    if not os.path.exists(file_path):
        print("❌ ملف windows_explorer_view.py غير موجود")
        return False
    
    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()
    
    # استبدال اسم القالب في دالة admin_archive_windows
    if 'windows_explorer_enhanced.html' in content:
        updated_content = content.replace(
            'windows_explorer_enhanced.html', 
            'direct_fix.html'
        )
        
        with open(file_path, 'w', encoding='utf-8') as file:
            file.write(updated_content)
        
        print("✅ تم تحديث دالة عرض الأرشيف لاستخدام القالب المصحح")
        return True
    else:
        print("❌ لم يتم العثور على استدعاء القالب في الملف")
        return False

# تنفيذ التحديث
if __name__ == "__main__":
    update_windows_explorer_view()
