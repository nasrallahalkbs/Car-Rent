"""
إضافة فئات الفحص المهمة المطلوبة للنظام

هذا السكريبت يضيف الفئات الأربع المهمة المطلوبة وبعض العناصر المهمة والمكلفة والحرجة
لاستخدامها في نموذج فحص السيارة.
"""

import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'car_rental_project.settings')
django.setup()

from rental.models import CarInspectionCategory, CarInspectionItem
from django.db.models import Q

# قائمة الفئات المهمة المطلوبة
important_categories = [
    'الهيكل الخارجي',  # يتضمن عناصر مكلفة ومهمة للفحص
    'المحرك ومكونات أسفل غطاء المحرك',  # فئة حرجة وأساسية للفحص
    'الإطارات والعجلات',  # مكلفة ومتعلقة بالسلامة
    'أنظمة السلامة والتشغيل'  # حرجة وتؤثر على السلامة
]

def add_important_categories():
    """إضافة الفئات المهمة الأربع"""
    print("📝 بدء إضافة فئات الفحص المهمة...")
    
    # التحقق من الفئات الموجودة
    existing_categories = CarInspectionCategory.objects.filter(name__in=important_categories)
    existing_names = [cat.name for cat in existing_categories]
    
    print(f"✓ الفئات الموجودة بالفعل: {len(existing_names)}")
    for name in existing_names:
        print(f"  - {name}")
    
    # إضافة الفئات الغير موجودة
    categories_to_add = [name for name in important_categories if name not in existing_names]
    print(f"⏳ فئات سيتم إضافتها: {len(categories_to_add)}")
    
    new_categories = []
    display_order = CarInspectionCategory.objects.count() + 1
    
    for name in categories_to_add:
        print(f"  + إضافة فئة: {name}")
        category = CarInspectionCategory(
            name=name,
            description=f"فئة فحص مهمة: {name}",
            display_order=display_order,
            is_active=True
        )
        category.save()
        new_categories.append(category)
        display_order += 1
    
    return existing_categories.union(CarInspectionCategory.objects.filter(pk__in=[cat.pk for cat in new_categories]))
    
def add_important_items():
    """إضافة بعض العناصر المهمة لكل فئة"""
    print("\n📋 بدء إضافة عناصر الفحص المهمة...")
    
    # الحصول على الفئات
    categories = CarInspectionCategory.objects.filter(name__in=important_categories)
    
    for category in categories:
        print(f"\n✓ إضافة عناصر لفئة: {category.name}")
        
        # التحقق من العناصر الموجودة
        existing_items = CarInspectionItem.objects.filter(category=category).count()
        print(f"  - عدد العناصر الموجودة حاليًا: {existing_items}")
        
        if existing_items > 0:
            print("  - تخطي الإضافة لوجود عناصر بالفعل")
            continue
            
        # إضافة العناصر حسب الفئة
        items_to_add = []
        if category.name == 'الهيكل الخارجي':
            items_to_add = [
                {'name': 'غطاء المحرك', 'is_important': True, 'is_expensive': True, 'is_critical': False},
                {'name': 'الأبواب', 'is_important': True, 'is_expensive': True, 'is_critical': False},
                {'name': 'السقف', 'is_important': True, 'is_expensive': True, 'is_critical': False},
                {'name': 'المصابيح الأمامية', 'is_important': True, 'is_expensive': True, 'is_critical': False},
            ]
        elif category.name == 'المحرك ومكونات أسفل غطاء المحرك':
            items_to_add = [
                {'name': 'المحرك', 'is_important': True, 'is_expensive': True, 'is_critical': True},
                {'name': 'ناقل الحركة', 'is_important': True, 'is_expensive': True, 'is_critical': True},
                {'name': 'نظام التبريد', 'is_important': True, 'is_expensive': False, 'is_critical': True},
            ]
        elif category.name == 'الإطارات والعجلات':
            items_to_add = [
                {'name': 'الإطارات', 'is_important': True, 'is_expensive': True, 'is_critical': True},
                {'name': 'الجنوط', 'is_important': False, 'is_expensive': True, 'is_critical': False},
            ]
        elif category.name == 'أنظمة السلامة والتشغيل':
            items_to_add = [
                {'name': 'نظام الفرامل', 'is_important': True, 'is_expensive': True, 'is_critical': True},
                {'name': 'الوسائد الهوائية', 'is_important': True, 'is_expensive': True, 'is_critical': True},
                {'name': 'حزام الأمان', 'is_important': True, 'is_expensive': False, 'is_critical': True},
            ]
        
        # إضافة العناصر
        display_order = 1
        for item_data in items_to_add:
            print(f"  + إضافة عنصر: {item_data['name']}")
            item = CarInspectionItem(
                category=category,
                name=item_data['name'],
                description=f"عنصر فحص: {item_data['name']}",
                display_order=display_order,
                is_active=True,
                is_important=item_data['is_important'],
                is_expensive=item_data['is_expensive'],
                is_critical=item_data['is_critical'],
                is_required=True
            )
            item.save()
            display_order += 1
            
def main():
    """الدالة الرئيسية"""
    try:
        categories = add_important_categories()
        add_important_items()
        
        # عرض ملخص نهائي
        print("\n✅ تم الانتهاء من إضافة فئات وعناصر الفحص المهمة!")
        print(f"📊 إجمالي عدد الفئات: {CarInspectionCategory.objects.filter(is_active=True).count()}")
        for category in CarInspectionCategory.objects.filter(is_active=True):
            items_count = CarInspectionItem.objects.filter(category=category, is_active=True).count()
            important_items = CarInspectionItem.objects.filter(
                category=category, 
                is_active=True
            ).filter(
                Q(is_important=True) | Q(is_expensive=True) | Q(is_critical=True)
            ).count()
            print(f"  - {category.name}: {items_count} عنصر ({important_items} مهم/مكلف/حرج)")
            
    except Exception as e:
        print(f"❌ حدث خطأ: {str(e)}")
        
if __name__ == "__main__":
    main()