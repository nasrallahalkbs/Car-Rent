#!/usr/bin/env python
import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "car_rental_project.settings")
django.setup()

from rental.models import CarInspectionCategory, CarInspectionItem

# إنشاء فئات فحص السيارة
categories = {
    'الهيكل الخارجي': 'العناصر المتعلقة بالهيكل الخارجي للسيارة',
    'المحرك': 'العناصر المتعلقة بمحرك السيارة ومكوناته',
    'نظام الفرامل': 'العناصر المتعلقة بنظام الفرامل',
    'نظام التعليق': 'العناصر المتعلقة بنظام التعليق والتوجيه',
    'الأنظمة الكهربائية': 'العناصر المتعلقة بالأنظمة الكهربائية',
    'المقصورة الداخلية': 'العناصر المتعلقة بالمقصورة الداخلية للسيارة',
    'أنظمة السلامة': 'العناصر المتعلقة بأنظمة السلامة والأمان'
}

# إنشاء قوائم العناصر لكل فئة
inspection_items = {
    'الهيكل الخارجي': [
        'الأبواب',
        'غطاء المحرك',
        'صندوق الأمتعة',
        'المصابيح الأمامية',
        'المصابيح الخلفية',
        'الزجاج الأمامي',
        'الزجاج الخلفي',
        'المرايا الجانبية',
        'الصدام الأمامي',
        'الصدام الخلفي',
        'الإطارات',
        'الجنوط'
    ],
    'المحرك': [
        'محرك السيارة',
        'نظام التبريد',
        'رادييتر التبريد',
        'مضخة الماء',
        'خزان الزيت',
        'فلتر الهواء',
        'البطارية',
        'ناقل الحركة',
        'مضخة الوقود',
        'حساسات المحرك'
    ],
    'نظام الفرامل': [
        'الفرامل الأمامية',
        'الفرامل الخلفية',
        'فرامل اليد',
        'سائل الفرامل',
        'اسطوانة الفرامل الرئيسية',
        'أقراص الفرامل'
    ],
    'نظام التعليق': [
        'نظام التعليق الأمامي',
        'نظام التعليق الخلفي',
        'المساعدات الأمامية',
        'المساعدات الخلفية',
        'نظام التوجيه',
        'عمود التوجيه'
    ],
    'الأنظمة الكهربائية': [
        'المولد الكهربائي (الدينامو)',
        'مارش التشغيل',
        'نظام إشعال المحرك',
        'مكيف الهواء',
        'نظام الصوت',
        'الأسلاك الكهربائية',
        'كمبيوتر السيارة',
        'فتحة السقف الكهربائية'
    ],
    'المقصورة الداخلية': [
        'لوحة العدادات',
        'المقاعد',
        'حزام الأمان',
        'عجلة القيادة',
        'النوافذ الكهربائية',
        'مرآة الرؤية الخلفية',
        'فتحات التكييف',
        'دواسة الوقود',
        'دواسة الفرامل',
        'دواسة الكلتش'
    ],
    'أنظمة السلامة': [
        'الوسائد الهوائية',
        'نظام ABS للفرامل',
        'نظام التحكم الإلكتروني بالثبات',
        'نظام مراقبة ضغط الإطارات',
        'أقفال أمان الأطفال',
        'أحزمة الأمان',
        'إنذار السيارة',
        'نظام مكافحة السرقة'
    ]
}

# إنشاء الفئات
created_categories = {}
for cat_name, cat_desc in categories.items():
    category, created = CarInspectionCategory.objects.get_or_create(
        name=cat_name,
        defaults={
            'description': cat_desc,
            'display_order': list(categories.keys()).index(cat_name)
        }
    )
    created_categories[cat_name] = category
    if created:
        print(f"تم إنشاء فئة: {cat_name}")
    else:
        print(f"تم العثور على فئة موجودة: {cat_name}")

# إنشاء عناصر الفحص
created_items_count = 0
for cat_name, items in inspection_items.items():
    category = created_categories[cat_name]
    for i, item_name in enumerate(items):
        item, created = CarInspectionItem.objects.get_or_create(
            name=item_name,
            category=category,
            defaults={
                'description': f'وصف {item_name}',
                'display_order': i,
                'is_required': True,
                # تعيين الحقول الجديدة بناءً على الكلمات المفتاحية
                'is_important': any(keyword in item_name for keyword in ['محرك', 'فرامل', 'نظام التعليق', 'ناقل الحركة', 'توجيه', 'كهرباء', 'بطارية', 'مكيف']),
                'is_expensive': any(keyword in item_name for keyword in ['محرك', 'ناقل الحركة', 'نظام التعليق', 'مكيف', 'رادييتر', 'بطارية', 'كمبيوتر']),
                'is_critical': any(keyword in item_name for keyword in ['فرامل', 'توجيه', 'وسائد هوائية', 'سلامة', 'أمان', 'إطارات'])
            }
        )
        if created:
            created_items_count += 1
            print(f"تم إنشاء عنصر فحص: {item_name} في فئة {cat_name}")
            # طباعة الخصائص الخاصة بالعنصر
            if item.is_important:
                print(f"  - مهم: نعم")
            if item.is_expensive:
                print(f"  - مكلف: نعم")
            if item.is_critical:
                print(f"  - حرج: نعم")

print(f"تم إنشاء {created_items_count} عنصر فحص جديد")