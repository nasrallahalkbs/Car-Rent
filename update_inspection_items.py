#!/usr/bin/env python
import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "car_rental_project.settings")
django.setup()

from rental.models import CarInspectionItem

# قواميس تحدد العناصر المهمة والمكلفة والحرجة بناءً على الكلمات المفتاحية
important_keywords = {
    'محرك': True,
    'فرامل': True,
    'نظام التعليق': True,
    'ناقل الحركة': True, 
    'توجيه': True,
    'كهرباء': True,
    'بطارية': True,
    'مكيف': True,
}

expensive_keywords = {
    'محرك': True,
    'ناقل الحركة': True,
    'نظام التعليق': True,
    'مكيف': True,
    'رادييتر': True,
    'بطارية': True,
    'كمبيوتر': True,
}

critical_keywords = {
    'فرامل': True,
    'توجيه': True,
    'وسائد هوائية': True,
    'سلامة': True,
    'أمان': True,
    'إطارات': True,
}

# الحصول على جميع عناصر الفحص
inspection_items = CarInspectionItem.objects.all()
print(f"عدد عناصر الفحص الموجودة: {inspection_items.count()}")

# تحديث كل عنصر بناءً على الكلمات المفتاحية
for item in inspection_items:
    item_name = item.name
    
    # تحديد ما إذا كان العنصر مهمًا
    item.is_important = False
    for keyword in important_keywords:
        if keyword in item_name:
            item.is_important = True
            print(f"تعيين العنصر '{item_name}' كعنصر مهم")
            break
    
    # تحديد ما إذا كان العنصر مكلفًا
    item.is_expensive = False
    for keyword in expensive_keywords:
        if keyword in item_name:
            item.is_expensive = True
            print(f"تعيين العنصر '{item_name}' كعنصر مكلف")
            break
    
    # تحديد ما إذا كان العنصر حرجًا
    item.is_critical = False
    for keyword in critical_keywords:
        if keyword in item_name:
            item.is_critical = True
            print(f"تعيين العنصر '{item_name}' كعنصر حرج")
            break
    
    # حفظ التغييرات
    item.save()

print("تم الانتهاء من تحديث عناصر الفحص!")