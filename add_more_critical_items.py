#!/usr/bin/env python
"""
إضافة المزيد من العناصر المهمة جداً لفئات الفحص

هذا السكريبت يقوم بإضافة عناصر فحص إضافية مهمة وحرجة لفئات الفحص المهمة الحالية
لتعزيز شمولية وفعالية تقارير فحص السيارة.
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
def add_more_critical_items():
    """إضافة المزيد من العناصر المهمة جداً لفئات الفحص"""
    
    print('\n✅ بدء إضافة المزيد من العناصر المهمة جداً لفئات الفحص...')
    
    # الحصول على جميع الفئات المتاحة
    all_categories = CarInspectionCategory.objects.all()
    print(f"📋 جميع الفئات المتاحة في قاعدة البيانات: {all_categories.count()}")
    for cat in all_categories:
        print(f"  - {cat.name} (ID: {cat.id})")
    
    # تعريف العناصر الجديدة لكل فئة
    new_items_by_category = {
        # أجزاء السيارة الرئيسية
        "أجزاء السيارة الرئيسية": [
            {"name": "نظام الكمبيوتر الرئيسي", "description": "فحص كمبيوتر السيارة الرئيسي", "is_critical": True},
            {"name": "عداد السرعة والمسافة", "description": "فحص عداد السرعة والمسافة", "is_critical": True},
            {"name": "المفتاح الذكي", "description": "فحص نظام المفتاح الذكي والتشغيل", "is_critical": True},
            {"name": "الأجهزة الكهربائية", "description": "فحص عمل الأجهزة الكهربائية الرئيسية", "is_critical": True},
            {"name": "حساسات الأمان", "description": "فحص حساسات الأمان والتحذير", "is_critical": True},
        ],
        
        # المحرك ومكونات أسفل غطاء المحرك
        "المحرك ومكونات أسفل غطاء المحرك": [
            {"name": "مضخة المياه", "description": "فحص مضخة المياه", "is_critical": True},
            {"name": "مضخة الزيت", "description": "فحص مضخة الزيت", "is_critical": True},
            {"name": "خراطيم التبريد", "description": "فحص خراطيم التبريد", "is_critical": True},
            {"name": "جهاز الإشعال", "description": "فحص جهاز الإشعال وعمله", "is_critical": True},
            {"name": "علبة المرشحات", "description": "فحص المرشحات وعلبها", "is_critical": False},
        ],
        
        # الإطارات والعجلات
        "الإطارات والعجلات": [
            {"name": "الإطار الاحتياطي", "description": "فحص الإطار الاحتياطي وعدته", "is_critical": True},
            {"name": "تآكل الإطارات", "description": "فحص نمط تآكل الإطارات", "is_critical": True},
            {"name": "توازن العجلات", "description": "فحص توازن العجلات", "is_critical": True},
            {"name": "محاذاة العجلات", "description": "فحص محاذاة العجلات", "is_critical": True},
            {"name": "براغي العجلات", "description": "فحص براغي العجلات وإحكامها", "is_critical": True},
        ],
        
        # أنظمة السلامة والتشغيل
        "أنظمة السلامة والتشغيل": [
            {"name": "نظام ESP", "description": "فحص نظام التحكم الإلكتروني بالثبات", "is_critical": True},
            {"name": "نظام ASR", "description": "فحص نظام التحكم بتماسك العجلات", "is_critical": True},
            {"name": "مساعد الفرامل", "description": "فحص نظام مساعد الفرامل", "is_critical": True},
            {"name": "كاميرا الرجوع للخلف", "description": "فحص كاميرا الرجوع للخلف", "is_critical": False},
            {"name": "حساسات الركن", "description": "فحص حساسات المساعدة في الركن", "is_critical": False},
        ],
    }
    
    # إضافة العناصر الجديدة لكل فئة
    for category_name, items in new_items_by_category.items():
        try:
            # البحث عن الفئة باستخدام الاسم
            category = CarInspectionCategory.objects.filter(name__icontains=category_name).first()
            
            if category:
                print(f"\n✅ إضافة عناصر جديدة للفئة: {category.name} (ID: {category.id})")
                
                # الحصول على العناصر الموجودة حالياً في الفئة
                existing_items = list(CarInspectionItem.objects.filter(category=category).values_list('name', flat=True))
                print(f"  📋 العناصر الموجودة حالياً: {len(existing_items)}")
                
                # الحصول على أعلى قيمة ترتيب حالية
                max_display_order = CarInspectionItem.objects.filter(category=category).order_by('-display_order').first()
                next_display_order = 1
                if max_display_order:
                    next_display_order = max_display_order.display_order + 1
                
                # إضافة العناصر الجديدة
                added_count = 0
                for item_data in items:
                    # التحقق مما إذا كان العنصر موجوداً بالفعل
                    if item_data["name"] not in existing_items:
                        new_item = CarInspectionItem.objects.create(
                            category=category,
                            name=item_data["name"],
                            description=item_data["description"],
                            display_order=next_display_order,
                            is_active=True,
                            is_required=True,
                            is_important=True,
                            is_expensive=True,
                            is_critical=item_data["is_critical"]
                        )
                        critical_mark = "🔴" if item_data["is_critical"] else "🔶"
                        print(f"  {critical_mark} تمت إضافة: {new_item.name} (ID: {new_item.id})")
                        next_display_order += 1
                        added_count += 1
                    else:
                        print(f"  ⏭️ تم تخطي {item_data['name']} (موجود بالفعل)")
                
                print(f"  ✅ تمت إضافة {added_count} عنصر جديد للفئة {category.name}")
            else:
                print(f"⚠️ لم يتم العثور على الفئة: {category_name}")
        except Exception as e:
            print(f"❌ خطأ أثناء إضافة عناصر للفئة '{category_name}': {str(e)}")
    
    # عرض ملخص نهائي
    print("\n📊 ملخص العناصر بعد الإضافة:")
    for category in CarInspectionCategory.objects.all().order_by('display_order'):
        items_count = CarInspectionItem.objects.filter(category=category, is_active=True).count()
        critical_items_count = CarInspectionItem.objects.filter(category=category, is_active=True, is_critical=True).count()
        print(f"  - {category.name}: {items_count} عنصر ({critical_items_count} عنصر حرج)")

def main():
    """تنفيذ الوظائف الرئيسية للبرنامج"""
    add_more_critical_items()
    print("\n✅ تم الانتهاء من إضافة العناصر المهمة جداً الإضافية لفئات الفحص")

if __name__ == "__main__":
    main()