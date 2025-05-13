#!/usr/bin/env python
"""
تعديل طريقة عرض تفاصيل الفحص لإظهار عناصر الهيكل الخارجي

هذا السكريبت يقوم بتعديل ملف car_condition_views.py لإزالة الشرط الذي يتخطى
عناصر الهيكل الخارجي في تقارير فحص السيارة.
"""

import os
import re
import fileinput
import django
import sys
import shutil
from datetime import datetime

# إعداد بيئة Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'car_rental_project.settings')
django.setup()

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

def modify_views_file():
    """تعديل ملف car_condition_views.py لإظهار عناصر الهيكل الخارجي"""
    
    file_path = "rental/car_condition_views.py"
    
    # الأنماط التي سنبحث عنها ونعدلها
    patterns = [
        (r"# تخطي عناصر \"الهيكل الخارجي\" لأننا نستخدم الصور بدلاً منها\s+if inspection_item\.category\.name == ['\"]+الهيكل الخارجي['\"]+:\s+continue", 
         "# تم تعديل السلوك ليشمل عناصر الهيكل الخارجي\n# if inspection_item.category.name == 'الهيكل الخارجي':\n#     continue"),
        
        (r"# تخطي عناصر الهيكل الخارجي \(نستخدم الصور بدلًا منها\)\s+if item\.category\.name == ['\"]+الهيكل الخارجي['\"]+:\s+print\(.*\)\s+continue", 
         "# تم تعديل السلوك ليشمل عناصر الهيكل الخارجي\n# if item.category.name == 'الهيكل الخارجي':\n#     print(f\"⏭️ تخطي عنصر هيكل خارجي: {item.name}\")\n#     continue"),
    ]
    
    modifications_count = 0
    
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()
        
        modified_content = content
        for pattern, replacement in patterns:
            modified_content, count = re.subn(pattern, replacement, modified_content, flags=re.MULTILINE)
            modifications_count += count
        
        if modifications_count > 0:
            with open(file_path, 'w', encoding='utf-8') as file:
                file.write(modified_content)
            
            print(f"✅ تم تعديل {modifications_count} موقع في ملف {file_path}")
            return True
        else:
            print(f"⚠️ لم يتم العثور على أنماط للتعديل في ملف {file_path}")
            
            # البحث اليدوي عن هذه العبارات
            exterior_checks = []
            
            with open(file_path, 'r', encoding='utf-8') as file:
                for i, line in enumerate(file):
                    if "الهيكل الخارجي" in line and "continue" in line:
                        exterior_checks.append((i+1, line.strip()))
            
            if exterior_checks:
                print("🔍 عمليات تخطي الهيكل الخارجي التي تم العثور عليها:")
                for line_num, line_text in exterior_checks:
                    print(f"  خط {line_num}: {line_text}")
                
                print("\n⚠️ يجب تعديل هذه الأسطر يدوياً بتعليقها باستخدام # في بداية السطر")
            
            return False
    except Exception as e:
        print(f"❌ خطأ أثناء تعديل الملف: {str(e)}")
        return False

def check_inspection_view_code():
    """التحقق من كود عرض تفاصيل الفحص"""
    
    file_path = "rental/car_condition_views.py"
    try:
        # البحث عن دالة عرض تفاصيل الفحص
        view_function_pattern = r"def car_inspection_detail\(request, report_id\):"
        
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()
        
        match = re.search(view_function_pattern, content)
        if match:
            print(f"✅ تم العثور على دالة عرض تفاصيل الفحص car_inspection_detail في السطر {content[:match.start()].count(chr(10)) + 1}")
            
            # التحقق من وجود تصفية لعناصر الهيكل الخارجي في دالة عرض التفاصيل
            view_function_text = content[match.start():]
            view_function_text = view_function_text[:view_function_text.find("\n\ndef ")] if "\n\ndef " in view_function_text else view_function_text
            
            if "الهيكل الخارجي" in view_function_text:
                print("⚠️ يوجد فلترة لعناصر الهيكل الخارجي في دالة عرض التفاصيل")
            else:
                print("✅ لا يوجد فلترة لعناصر الهيكل الخارجي في دالة عرض التفاصيل")
        else:
            print("❌ لم يتم العثور على دالة عرض تفاصيل الفحص")
    except Exception as e:
        print(f"❌ خطأ أثناء التحقق من كود العرض: {str(e)}")

def main():
    """تنفيذ الوظائف الرئيسية للبرنامج"""
    
    print("✅ بدء تعديل طريقة عرض تفاصيل الفحص لإظهار عناصر الهيكل الخارجي")
    
    # التحقق من دالة عرض تفاصيل الفحص
    check_inspection_view_code()
    
    # إنشاء نسخة احتياطية
    backup_created = backup_views_file()
    
    if backup_created:
        # تعديل ملف car_condition_views.py
        modified = modify_views_file()
        
        if modified:
            print("✅ تم تعديل الكود بنجاح. الآن ستظهر عناصر الهيكل الخارجي في تقارير الفحص")
        else:
            print("⚠️ لم يتم تعديل الكود. قد تحتاج إلى تعديله يدوياً")
    
    print("\n✅ تعليمات إضافية:")
    print("1. قم بإعادة تشغيل الخادم لتطبيق التغييرات")
    print("2. اختبر إنشاء تقرير فحص جديد للتأكد من ظهور عناصر الهيكل الخارجي")
    print("3. إذا لم تظهر العناصر، تحقق من ملف car_condition_views.py وابحث عن عمليات التخطي الأخرى")

if __name__ == "__main__":
    main()