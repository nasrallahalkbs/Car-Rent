#!/usr/bin/env python
"""
إضافة عناصر فحص مهمة جداً بدلاً من فئة الهيكل الخارجي

هذا السكريبت يقوم بإضافة عناصر فحص مهمة جداً لتوثيق حالة السيارة، وذلك
باستخدام الفئات المهمة وإضافة عناصر حيوية لكل فئة.
"""

import os
import django
import sys

# إعداد بيئة Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'car_rental_project.settings')
django.setup()

from rental.models import CarInspectionCategory, CarInspectionItem
from django.db import transaction

@transaction.atomic
def add_critical_inspection_items():
    """إضافة عناصر فحص مهمة جداً لتوثيق حالة السيارة"""
    
    print('✅ تعيين العناصر المهمة جداً للفحص...')
    
    # تحديد الفئات المهمة - الفئات الأربع المتاحة في النظام
    important_categories = [
        "الهيكل الخارجي",
        "المحرك ومكونات أسفل غطاء المحرك",
        "الإطارات والعجلات",
        "أنظمة السلامة والتشغيل",
    ]
    
    # الحصول على جميع الفئات المتاحة وطباعتها للتشخيص
    all_categories = CarInspectionCategory.objects.all()
    print(f"📋 جميع الفئات المتاحة في قاعدة البيانات: {all_categories.count()}")
    for cat in all_categories:
        print(f"  - {cat.name} (ID: {cat.id})")

    # تحديد الفئات المهمة من قاعدة البيانات
    important_category_objects = []
    for cat_name in important_categories:
        try:
            category = CarInspectionCategory.objects.filter(name__icontains=cat_name).first()
            if category:
                important_category_objects.append(category)
        except Exception as e:
            print(f"❌ خطأ في العثور على الفئة '{cat_name}': {str(e)}")
    
    # ملاحظة: لا داعي لإضافة فئة "الهيكل الخارجي" هنا لأنها ستكون موجودة في القائمة important_categories
    
    print(f"🔍 الفئات المهمة التي تم العثور عليها: {len(important_category_objects)}")
    for cat in important_category_objects:
        print(f"  + {cat.name} (ID: {cat.id})")
    
    # تحديد العناصر المهمة جداً لكل فئة
    critical_items = {
        "الهيكل الخارجي": ["غطاء المحرك", "الأبواب", "المصدات", "الزجاج الأمامي"],
        "المحرك ومكونات أسفل غطاء المحرك": ["المحرك", "زيت المحرك", "نظام التبريد", "البطارية"],
        "الإطارات والعجلات": ["الإطارات", "الجنوط", "ضغط الهواء", "حالة المداس"],
        "أنظمة السلامة والتشغيل": ["نظام الفرامل", "الوسائد الهوائية", "نظام ABS", "حزام الأمان"],
    }
    
    # طباعة ملخص للعناصر المهمة جداً
    print(f"✅ تم تحديد {sum(len(items) for items in critical_items.values())} عنصر مهم جداً للفحص:")
    for cat, items in critical_items.items():
        print(f"  - فئة ({cat}): {len(items)} عناصر")
        print(f"    * {', '.join(items)}")
    
    # تعيين العناصر الموجودة كعناصر مهمة وحرجة
    for category in important_category_objects:
        for item in CarInspectionItem.objects.filter(category=category):
            # تحقق مما إذا كان العنصر مهماً جداً
            for items_list in critical_items.values():
                if any(critical_name.lower() in item.name.lower() for critical_name in items_list):
                    item.is_important = True
                    item.is_critical = True
                    item.save()
                    print(f"✅ تعيين العنصر '{item.name}' كعنصر مهم وحرج")

    # إنشاء عناصر جديدة مهمة جداً إذا لم تكن موجودة
    for category in important_category_objects:
        cat_name = category.name
        items_to_check = []
        
        # تحديد العناصر المطلوبة لهذه الفئة
        for key, items in critical_items.items():
            if key.lower() in cat_name.lower() or cat_name.lower() in key.lower():
                items_to_check = items
                break
        
        # إضافة العناصر المهمة إذا لم تكن موجودة
        for item_name in items_to_check:
            existing_item = CarInspectionItem.objects.filter(
                category=category,
                name__icontains=item_name
            ).first()
            
            if not existing_item:
                # إنشاء عنصر جديد
                try:
                    new_item = CarInspectionItem.objects.create(
                        category=category,
                        name=item_name,
                        description=f"فحص {item_name}",
                        display_order=0,  # سيتم تعديله لاحقاً
                        is_active=True,
                        is_required=True,
                        is_important=True,
                        is_expensive=True,
                        is_critical=True
                    )
                    print(f"✅ إضافة العنصر المهم جداً: {item_name} (ID: {new_item.id})")
                except Exception as e:
                    print(f"❌ خطأ في إنشاء العنصر '{item_name}': {str(e)}")
            else:
                # تحديث العنصر الموجود
                existing_item.is_important = True
                existing_item.is_critical = True
                existing_item.is_required = True
                existing_item.save()
                print(f"✅ تحديث العنصر الموجود: {existing_item.name} (ID: {existing_item.id})")
    
    # إعادة ترتيب العناصر داخل كل فئة
    for category in important_category_objects:
        items = CarInspectionItem.objects.filter(category=category).order_by('id')
        for i, item in enumerate(items):
            item.display_order = i + 1
            item.save()

    # إظهار ملخص للنتائج النهائية
    print(f"✅ عدد فئات الفحص: {len(important_category_objects)}")
    for category in important_category_objects:
        item_count = CarInspectionItem.objects.filter(
            category=category, 
            is_active=True,
            is_important=True
        ).count()
        print(f"✅ فئة {category.name}: {item_count} عنصر")

def remove_skip_exterior_items():
    """تعديل الكود لعدم تخطي عناصر الهيكل الخارجي"""
    
    # هذه الدالة ستقوم فقط بعرض معلومات توضيحية حول العناصر المهمة
    # ولن تقوم بتعديل الكود فعلياً، فهذا يتطلب تعديل ملفات المشروع الأصلية
    
    print("\n✅ كيفية تعديل الكود لعدم تخطي عناصر الهيكل الخارجي:")
    print("1. افتح ملف rental/car_condition_views.py")
    print("2. ابحث عن الشرط الذي يتخطى عناصر الهيكل الخارجي:")
    print('   if inspection_item.category.name == "الهيكل الخارجي":')
    print('       continue')
    print("3. قم بتعليق أو إزالة هذا الشرط لتمكين معالجة عناصر الهيكل الخارجي\n")
    
    # يمكن إضافة المزيد من التعليمات هنا حسب الحاجة

def main():
    """تنفيذ الوظائف الرئيسية للبرنامج"""
    add_critical_inspection_items()
    remove_skip_exterior_items()
    print("\n✅ تم الانتهاء من إضافة العناصر المهمة جداً لتوثيق حالة السيارة")

if __name__ == "__main__":
    main()