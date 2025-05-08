"""
تطبيق القالب الجديد لصفحة الحجوزات

هذا السكريبت يقوم بتحديث دالة admin_reservations في ملف admin_views.py
لاستخدام القالب الجديد الذي يطابق الصورة المرجعية للعميل.
"""

import os
import re

def apply_new_template():
    """
    تطبيق قالب الحجوزات الجديد الذي يطابق الصورة المرجعية
    """
    # ملف العرض الذي يحتاج للتعديل
    views_file = 'rental/admin_views.py'
    
    if not os.path.exists(views_file):
        print(f"خطأ: الملف {views_file} غير موجود")
        return False
    
    # قراءة محتوى الملف
    with open(views_file, 'r', encoding='utf-8') as file:
        content = file.read()
    
    # البحث عن دالة admin_reservations
    admin_res_pattern = r'def admin_reservations\(request\):(.*?)(?=def |$)'
    admin_res_match = re.search(admin_res_pattern, content, re.DOTALL)
    
    if not admin_res_match:
        print("خطأ: لم يتم العثور على دالة admin_reservations")
        return False
    
    # محتوى الدالة الحالي
    current_function = admin_res_match.group(0)
    
    # البحث عن سطر إرجاع القالب
    template_pattern = r'return render\(request, [\'"]([^\'"]+)[\'"],'
    template_match = re.search(template_pattern, current_function)
    
    if not template_match:
        print("خطأ: لم يتم العثور على سطر إرجاع القالب")
        return False
    
    # القالب الحالي
    current_template = template_match.group(1)
    
    # القالب الجديد
    new_template = 'admin/reservations_new.html'
    
    # استبدال القالب القديم بالجديد
    updated_function = current_function.replace(
        f'return render(request, \'{current_template}\'',
        f'return render(request, \'{new_template}\''
    )
    
    # تحديث محتوى الملف
    updated_content = content.replace(current_function, updated_function)
    
    # حفظ التغييرات
    with open(views_file, 'w', encoding='utf-8') as file:
        file.write(updated_content)
    
    print(f"✅ تم تحديث دالة admin_reservations لاستخدام القالب الجديد: {new_template}")
    return True

if __name__ == "__main__":
    apply_new_template()