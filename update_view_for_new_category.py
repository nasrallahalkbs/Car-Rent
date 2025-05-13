#!/usr/bin/env python
"""
تحديث كود العرض ليعمل مع الفئة الجديدة "أجزاء السيارة الرئيسية"

هذا السكريبت يقوم بتحديث أي إشارات إلى "الهيكل الخارجي" في ملف car_condition_views.py
ليتم استبدالها بـ "أجزاء السيارة الرئيسية"
"""

import os
import re
import shutil
from datetime import datetime

def backup_views_file():
    """إنشاء نسخة احتياطية من ملف car_condition_views.py"""
    
    source_file = "rental/car_condition_views.py"
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_file = f"rental/car_condition_views_backup_{timestamp}.py"
    
    try:
        shutil.copy2(source_file, backup_file)
        print(f"✅ تم إنشاء نسخة احتياطية: {backup_file}")
        return True
    except Exception as e:
        print(f"❌ خطأ في إنشاء نسخة احتياطية: {str(e)}")
        return False

def update_views_file():
    """تحديث ملف car_condition_views.py"""
    
    file_path = "rental/car_condition_views.py"
    
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()
        
        # البحث عن جميع إشارات "الهيكل الخارجي" واستبدالها
        old_name = "الهيكل الخارجي"
        new_name = "أجزاء السيارة الرئيسية"
        
        # استبدال الاسم في التعليقات
        modified_content = content.replace(f"# تخطي عناصر \"{old_name}\"", f"# لم نعد نتخطى عناصر \"{new_name}\"")
        modified_content = modified_content.replace(f"# تخطي عناصر {old_name}", f"# لم نعد نتخطى عناصر {new_name}")
        
        # استبدال أي إشارات أخرى للاسم
        modified_content = modified_content.replace(f"if inspection_item.category.name == '{old_name}':", 
                                                  f"# لم نعد نتخطى عناصر '{new_name}'\n# if inspection_item.category.name == '{new_name}':")
        
        modified_content = modified_content.replace(f"if item.category.name == '{old_name}':", 
                                                  f"# لم نعد نتخطى عناصر '{new_name}'\n# if item.category.name == '{new_name}':")
        
        # تحديث مخصصات الصور
        modified_content = modified_content.replace(f"'exterior_images': [],  # قائمة فارغة لصور {old_name}", 
                                                  f"'exterior_images': [],  # قائمة فارغة لصور {new_name}")
        
        # البحث عن أنماط معقدة
        pattern = r"(if\s+(?:inspection_item|item)\.category\.name\s*==\s*['\"])الهيكل الخارجي(['\"]\s*:)"
        replacement = r"# لم نعد نتخطى عناصر 'أجزاء السيارة الرئيسية'\n# \1أجزاء السيارة الرئيسية\2"
        modified_content = re.sub(pattern, replacement, modified_content)
        
        # حفظ التغييرات
        with open(file_path, 'w', encoding='utf-8') as file:
            file.write(modified_content)
        
        print(f"✅ تم تحديث ملف {file_path} لاستخدام الفئة الجديدة")
        return True
    except Exception as e:
        print(f"❌ خطأ أثناء تحديث الملف: {str(e)}")
        return False

def verify_update():
    """التحقق من التحديثات"""
    
    file_path = "rental/car_condition_views.py"
    search_terms = [
        "أجزاء السيارة الرئيسية",
        "لم نعد نتخطى عناصر"
    ]
    
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()
        
        found_terms = {}
        for term in search_terms:
            occurrences = content.count(term)
            found_terms[term] = occurrences
            print(f"✅ تم العثور على '{term}' {occurrences} مرة")
        
        if all(count > 0 for count in found_terms.values()):
            print("✅ تم التحقق من التحديثات بنجاح")
            return True
        else:
            print("⚠️ بعض المصطلحات لم يتم تحديثها")
            return False
    except Exception as e:
        print(f"❌ خطأ أثناء التحقق من التحديثات: {str(e)}")
        return False

def main():
    """الدالة الرئيسية"""
    print("\n✅ بدء تحديث كود العرض ليعمل مع الفئة الجديدة...")
    
    # إنشاء نسخة احتياطية
    if backup_views_file():
        # تحديث الملف
        if update_views_file():
            # التحقق من التحديثات
            verify_update()
    
    print("\n✅ تم الانتهاء من تحديث كود العرض للعمل مع الفئة الجديدة 'أجزاء السيارة الرئيسية'")

if __name__ == "__main__":
    main()