#!/usr/bin/env python
"""
تحديث كود عرض نموذج الفحص ليظهر جميع الفئات المهمة

هذا السكريبت يقوم بتعديل كود العرض ليعرض عناصر الفئات الجديدة وجميع العناصر المهمة
في نموذج فحص السيارة.
"""

import os
import django
import sys
from datetime import datetime
import shutil

# إعداد بيئة Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'car_rental_project.settings')
django.setup()

from rental.models import CarInspectionCategory, CarInspectionItem
from django.db import transaction

def backup_view_file():
    """إنشاء نسخة احتياطية من ملف العرض الرئيسي"""
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

@transaction.atomic
def update_important_categories():
    """تحديث الفئات المهمة في قاعدة البيانات لتشمل أجزاء السيارة الرئيسية"""
    
    # الحصول على فئة "أجزاء السيارة الرئيسية"
    main_parts_category = CarInspectionCategory.objects.filter(name="أجزاء السيارة الرئيسية").first()
    if main_parts_category:
        # تعيين الفئة كفئة مهمة
        print(f"✅ تعيين فئة 'أجزاء السيارة الرئيسية' (ID: {main_parts_category.id}) كفئة مهمة")
        
        # تجهيز جميع عناصر هذه الفئة كعناصر مهمة
        items = CarInspectionItem.objects.filter(category=main_parts_category)
        for item in items:
            item.is_important = True
            item.save()
            print(f"  ✓ تعيين العنصر '{item.name}' كعنصر مهم")
    else:
        print("⚠️ لم يتم العثور على فئة 'أجزاء السيارة الرئيسية'")

def update_car_condition_view():
    """تحديث ملف car_condition_views.py لعرض جميع الفئات المهمة"""
    file_path = "rental/car_condition_views.py"
    
    try:
        # قراءة محتوى الملف
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()
        
        # البحث عن كود استرجاع الفئات المهمة وتحديثه
        important_categories_code = """
            # استرجاع جميع فئات الفحص المهمة
            important_categories = []
            
            # البحث عن فئات الفحص المهمة
            for category_name in ["المحرك ومكونات أسفل غطاء المحرك", "الإطارات والعجلات", "أنظمة السلامة والتشغيل"]:
                category = CarInspectionCategory.objects.filter(name__icontains=category_name).first()
                if category:
                    important_categories.append(category)
        """
        
        # الكود المحدث الذي سيظهر جميع الفئات المهمة
        updated_code = """
            # استرجاع جميع فئات الفحص المهمة
            important_categories = []
            
            # إضافة فئة أجزاء السيارة الرئيسية
            main_parts_category = CarInspectionCategory.objects.filter(name__icontains="أجزاء السيارة الرئيسية").first()
            if main_parts_category:
                important_categories.append(main_parts_category)
            
            # البحث عن فئات الفحص المهمة
            for category_name in ["المحرك ومكونات أسفل غطاء المحرك", "الإطارات والعجلات", "أنظمة السلامة والتشغيل"]:
                category = CarInspectionCategory.objects.filter(name__icontains=category_name).first()
                if category:
                    important_categories.append(category)
        """
        
        # استبدال الكود القديم بالكود الجديد
        if important_categories_code.strip() in content:
            content = content.replace(important_categories_code.strip(), updated_code.strip())
            with open(file_path, 'w', encoding='utf-8') as file:
                file.write(content)
            print("✅ تم تحديث كود استرجاع الفئات المهمة")
        else:
            print("⚠️ لم يتم العثور على كود استرجاع الفئات المهمة بالصيغة المتوقعة")
            
            # البحث عن جزئيات من الكود
            search_code = 'important_categories = []'
            if search_code in content:
                print(f"  وجدنا '{search_code}' في الملف")
                
                # استخراج الكتلة البرمجية حول هذا السطر
                lines = content.split('\n')
                for i, line in enumerate(lines):
                    if search_code in line:
                        context_start = max(0, i - 10)
                        context_end = min(len(lines), i + 10)
                        print("  سياق الكود:")
                        for j in range(context_start, context_end):
                            print(f"    {j+1}: {lines[j]}")
                
                # محاولة تحديد الكود يدوياً باستخدام أنماط
                print("\n⚠️ جاري محاولة تحديد كود استرجاع الفئات بشكل يدوي...")
                
                # البحث عن نمط محدد
                target_pattern = "for category_name in"
                if target_pattern in content:
                    start_index = content.find(search_code)
                    if start_index != -1:
                        # البحث عن نهاية الكتلة البرمجية (عادة تنتهي بمسافة بيضاء جديدة)
                        end_search = content[start_index:].find("\n\n")
                        if end_search != -1:
                            end_index = start_index + end_search + 1
                            code_block = content[start_index:end_index]
                            
                            # كود جديد مع إضافة فئة أجزاء السيارة الرئيسية
                            new_code = search_code + "\n            \n            # إضافة فئة أجزاء السيارة الرئيسية\n            main_parts_category = CarInspectionCategory.objects.filter(name__icontains=\"أجزاء السيارة الرئيسية\").first()\n            if main_parts_category:\n                important_categories.append(main_parts_category)"
                            
                            # استبدال الكود القديم بالكود الجديد
                            modified_content = content.replace(search_code, new_code)
                            
                            with open(file_path, 'w', encoding='utf-8') as file:
                                file.write(modified_content)
                            print("✅ تم تحديث كود استرجاع الفئات المهمة يدوياً")
    except Exception as e:
        print(f"❌ خطأ أثناء تحديث ملف العرض: {str(e)}")

def update_category_filter():
    """تحديث فلتر عرض العناصر ليشمل جميع العناصر المهمة والحرجة والمكلفة"""
    file_path = "rental/car_condition_views.py"
    
    try:
        # قراءة محتوى الملف
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()
        
        # البحث عن الكود المسؤول عن فلترة العناصر
        old_filter_code = """
            # تصفية العناصر لإظهار المهمة والمكلفة والحرجة فقط
            important_items = CarInspectionItem.objects.filter(is_important=True, is_active=True)
            expensive_items = CarInspectionItem.objects.filter(is_expensive=True, is_active=True)
            critical_items = CarInspectionItem.objects.filter(is_critical=True, is_active=True)
        """
        
        # عرض جميع العناصر المهمة دون تصفية
        new_filter_code = """
            # تصفية العناصر لإظهار المهمة والمكلفة والحرجة فقط
            important_items = CarInspectionItem.objects.filter(is_important=True, is_active=True)
            expensive_items = CarInspectionItem.objects.filter(is_expensive=True, is_active=True)
            critical_items = CarInspectionItem.objects.filter(is_critical=True, is_active=True)
            
            # للتأكد من ظهور جميع العناصر المهمة في الفئات الأربع
            for category in important_categories:
                for item in CarInspectionItem.objects.filter(category=category, is_active=True):
                    item.is_important = True
                    item.save()
        """
        
        # استبدال الكود القديم بالكود الجديد
        if old_filter_code.strip() in content:
            content = content.replace(old_filter_code.strip(), new_filter_code.strip())
            with open(file_path, 'w', encoding='utf-8') as file:
                file.write(content)
            print("✅ تم تحديث كود فلترة العناصر المهمة")
        else:
            print("⚠️ لم يتم العثور على كود فلترة العناصر المهمة بالصيغة المتوقعة")
            
            # البحث عن جزئيات من الكود
            search_code = 'important_items = CarInspectionItem.objects.filter(is_important=True'
            if search_code in content:
                print(f"  وجدنا جزءاً من كود فلترة العناصر")
                
                # محاولة تحديد موقع الكود
                start_index = content.find(search_code)
                if start_index != -1:
                    # محاولة العثور على نهاية الكتلة البرمجية
                    end_search = content[start_index:].find("critical_items = ")
                    if end_search != -1:
                        # العثور على نهاية السطر
                        line_end = content[start_index + end_search:].find('\n')
                        if line_end != -1:
                            end_index = start_index + end_search + line_end + 1
                            
                            # إضافة الكود الجديد
                            additional_code = "\n            \n            # للتأكد من ظهور جميع العناصر المهمة في الفئات الأربع\n            for category in important_categories:\n                for item in CarInspectionItem.objects.filter(category=category, is_active=True):\n                    item.is_important = True\n                    item.save()"
                            
                            modified_content = content[:end_index] + additional_code + content[end_index:]
                            
                            with open(file_path, 'w', encoding='utf-8') as file:
                                file.write(modified_content)
                            print("✅ تم تحديث كود فلترة العناصر المهمة يدوياً")
    except Exception as e:
        print(f"❌ خطأ أثناء تحديث فلتر العناصر: {str(e)}")

def main():
    """تنفيذ الوظائف الرئيسية للبرنامج"""
    print("\n✅ بدء تحديث كود العرض ليظهر جميع الفئات المهمة بما فيها فئة أجزاء السيارة الرئيسية...")
    
    # 1. إنشاء نسخة احتياطية
    if backup_view_file():
        # 2. تحديث الفئات المهمة في قاعدة البيانات
        update_important_categories()
        
        # 3. تحديث ملف العرض
        update_car_condition_view()
        
        # 4. تحديث فلتر عرض العناصر
        update_category_filter()
    
    print("\n✅ تم الانتهاء من تحديث كود العرض ليظهر جميع الفئات والعناصر المهمة")

if __name__ == "__main__":
    main()