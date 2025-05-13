#!/usr/bin/env python
"""
استبدال فئة "الهيكل الخارجي" بفئة مهمة جداً جديدة

هذا السكريبت يقوم بإجراء التغييرات التالية:
1. إزالة فئة "الهيكل الخارجي" من الفئات المستخدمة في التقارير
2. إضافة فئة مهمة جداً جديدة بعناصر فحص حرجة ومهمة
3. تحديث العناصر وإعادة تنظيمها
"""

import os
import django
import sys
from datetime import datetime

# إعداد بيئة Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'car_rental_project.settings')
django.setup()

from rental.models import CarInspectionCategory, CarInspectionItem
from django.db import transaction

@transaction.atomic
def replace_exterior_category():
    """استبدال فئة الهيكل الخارجي بفئة مهمة جداً جديدة"""
    
    print('\n✅ بدء استبدال فئة الهيكل الخارجي بفئة جديدة مهمة جداً...')
    
    # الحصول على جميع الفئات المتاحة
    all_categories = CarInspectionCategory.objects.all()
    print(f"📋 جميع الفئات المتاحة في قاعدة البيانات: {all_categories.count()}")
    for cat in all_categories:
        print(f"  - {cat.name} (ID: {cat.id})")
    
    # 1. تغيير اسم فئة الهيكل الخارجي
    try:
        exterior_category = CarInspectionCategory.objects.filter(name__icontains="الهيكل الخارجي").first()
        if exterior_category:
            # احتفظ بمعرف الفئة القديمة
            old_exterior_id = exterior_category.id
            
            # تغيير اسم الفئة
            new_name = "أجزاء السيارة الرئيسية"
            exterior_category.name = new_name
            exterior_category.description = "الأجزاء الرئيسية والمهمة جداً في السيارة"
            exterior_category.display_order = 1  # جعل الفئة في المرتبة الأولى
            exterior_category.save()
            
            print(f"✅ تم تغيير اسم فئة 'الهيكل الخارجي' (ID: {old_exterior_id}) إلى '{new_name}'")
        else:
            print("⚠️ لم يتم العثور على فئة 'الهيكل الخارجي'")
            # إنشاء فئة جديدة
            new_category = CarInspectionCategory.objects.create(
                name="أجزاء السيارة الرئيسية",
                description="الأجزاء الرئيسية والمهمة جداً في السيارة",
                display_order=1
            )
            old_exterior_id = new_category.id
            print(f"✅ تم إنشاء فئة جديدة 'أجزاء السيارة الرئيسية' (ID: {old_exterior_id})")
    except Exception as e:
        print(f"❌ خطأ أثناء تغيير فئة 'الهيكل الخارجي': {str(e)}")
        return
        
    # 2. تحديد العناصر المهمة جداً للفئة الجديدة
    critical_items = [
        {"name": "المحرك", "description": "حالة المحرك العامة", "is_critical": True},
        {"name": "نظام الفرامل", "description": "حالة ومستوى سائل الفرامل", "is_critical": True},
        {"name": "الإطارات", "description": "حالة الإطارات ومستوى التآكل", "is_critical": True},
        {"name": "نظام التوجيه", "description": "سلاسة وحساسية نظام التوجيه", "is_critical": True},
        {"name": "البطارية", "description": "حالة وقوة البطارية", "is_critical": True},
        {"name": "نظام التعليق", "description": "حالة نظام التعليق", "is_critical": True},
        {"name": "الوسائد الهوائية", "description": "فحص نظام الوسائد الهوائية", "is_critical": True},
        {"name": "أحزمة الأمان", "description": "حالة وعمل أحزمة الأمان", "is_critical": True},
        {"name": "صندوق المحركات", "description": "النظافة وعدم وجود تسريبات", "is_critical": False},
        {"name": "نظام العادم", "description": "حالة نظام العادم", "is_critical": False},
    ]
    
    # 3. إزالة العناصر القديمة من الفئة (اختياري)
    confirm_delete = True
    if confirm_delete:
        try:
            # احتفظ بالعناصر الموجودة في قائمة
            existing_items = list(CarInspectionItem.objects.filter(category_id=old_exterior_id).values_list('name', flat=True))
            # احذف العناصر القديمة
            delete_count = CarInspectionItem.objects.filter(category_id=old_exterior_id).delete()[0]
            print(f"✅ تم حذف {delete_count} عنصر من الفئة القديمة")
            print(f"📋 العناصر المحذوفة: {', '.join(existing_items)}")
        except Exception as e:
            print(f"⚠️ حدث خطأ أثناء حذف العناصر القديمة: {str(e)}")
    
    # 4. إضافة العناصر الجديدة المهمة جداً
    for i, item_data in enumerate(critical_items):
        try:
            # التحقق مما إذا كان العنصر موجود بالفعل
            existing_item = CarInspectionItem.objects.filter(
                category_id=old_exterior_id,
                name__iexact=item_data["name"]
            ).first()
            
            if existing_item:
                # تحديث العنصر الموجود
                existing_item.description = item_data["description"]
                existing_item.display_order = i + 1
                existing_item.is_active = True
                existing_item.is_required = True
                existing_item.is_important = True
                existing_item.is_expensive = True
                existing_item.is_critical = item_data["is_critical"]
                existing_item.save()
                print(f"✅ تحديث العنصر الموجود: {existing_item.name} (ID: {existing_item.id})")
            else:
                # إنشاء عنصر جديد
                new_item = CarInspectionItem.objects.create(
                    category_id=old_exterior_id,
                    name=item_data["name"],
                    description=item_data["description"],
                    display_order=i + 1,
                    is_active=True,
                    is_required=True,
                    is_important=True,
                    is_expensive=True,
                    is_critical=item_data["is_critical"]
                )
                print(f"✅ إضافة العنصر الجديد: {new_item.name} (ID: {new_item.id})")
        except Exception as e:
            print(f"❌ خطأ في إضافة العنصر '{item_data['name']}': {str(e)}")
    
    # 5. عرض ملخص للنتائج النهائية
    category_items = CarInspectionItem.objects.filter(category_id=old_exterior_id).order_by('display_order')
    print(f"\n✅ تم استبدال فئة 'الهيكل الخارجي' بالفئة الجديدة 'أجزاء السيارة الرئيسية'")
    print(f"📋 العناصر الجديدة في الفئة ({len(category_items)} عنصر):")
    
    for i, item in enumerate(category_items, 1):
        critical_mark = "🔴" if item.is_critical else "🔶"
        print(f"  {i}. {critical_mark} {item.name}")

def main():
    """تنفيذ الوظائف الرئيسية للبرنامج"""
    replace_exterior_category()
    print("\n✅ تم الانتهاء من استبدال فئة 'الهيكل الخارجي' بفئة مهمة جداً جديدة")

if __name__ == "__main__":
    main()