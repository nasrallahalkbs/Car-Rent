"""
سكريبت لإنشاء فئات وعناصر الفحص الافتراضية لنظام توثيق حالة السيارات
"""

import os
import django

# إعداد البيئة
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'car_rental_project.settings')
django.setup()

from rental.models import CarInspectionCategory, CarInspectionItem
from django.utils.translation import gettext_lazy as _

# التحقق من وجود فئات سابقة
if CarInspectionCategory.objects.count() == 0:
    print("بدء إنشاء فئات وعناصر الفحص الافتراضية...")
    
    # قائمة بفئات الفحص الأساسية
    categories = [
        {
            'name': _('الهيكل الخارجي'),
            'description': _('فحص الهيكل الخارجي للسيارة بما في ذلك الطلاء والألواح والزجاج'),
            'display_order': 1,
            'items': [
                {'name': _('المصد الأمامي'), 'display_order': 1, 'is_required': True},
                {'name': _('المصد الخلفي'), 'display_order': 2, 'is_required': True},
                {'name': _('الجناح الأمامي الأيمن'), 'display_order': 3, 'is_required': True},
                {'name': _('الجناح الأمامي الأيسر'), 'display_order': 4, 'is_required': True},
                {'name': _('الباب الأمامي الأيمن'), 'display_order': 5, 'is_required': True},
                {'name': _('الباب الأمامي الأيسر'), 'display_order': 6, 'is_required': True},
                {'name': _('الباب الخلفي الأيمن'), 'display_order': 7, 'is_required': True},
                {'name': _('الباب الخلفي الأيسر'), 'display_order': 8, 'is_required': True},
                {'name': _('السقف'), 'display_order': 9, 'is_required': True},
                {'name': _('غطاء المحرك'), 'display_order': 10, 'is_required': True},
                {'name': _('صندوق الأمتعة'), 'display_order': 11, 'is_required': True},
                {'name': _('الزجاج الأمامي'), 'display_order': 12, 'is_required': True},
                {'name': _('الزجاج الخلفي'), 'display_order': 13, 'is_required': True},
                {'name': _('زجاج النوافذ'), 'display_order': 14, 'is_required': True},
                {'name': _('المرايا الخارجية'), 'display_order': 15, 'is_required': True},
                {'name': _('المصابيح الأمامية'), 'display_order': 16, 'is_required': True},
                {'name': _('المصابيح الخلفية'), 'display_order': 17, 'is_required': True},
            ]
        },
        {
            'name': _('الإطارات والعجلات'),
            'description': _('فحص الإطارات وجنوط العجلات والفرامل'),
            'display_order': 2,
            'items': [
                {'name': _('الإطار الأمامي الأيمن'), 'display_order': 1, 'is_required': True},
                {'name': _('الإطار الأمامي الأيسر'), 'display_order': 2, 'is_required': True},
                {'name': _('الإطار الخلفي الأيمن'), 'display_order': 3, 'is_required': True},
                {'name': _('الإطار الخلفي الأيسر'), 'display_order': 4, 'is_required': True},
                {'name': _('الإطار الاحتياطي'), 'display_order': 5, 'is_required': True},
                {'name': _('جنط العجلة الأمامي الأيمن'), 'display_order': 6, 'is_required': True},
                {'name': _('جنط العجلة الأمامي الأيسر'), 'display_order': 7, 'is_required': True},
                {'name': _('جنط العجلة الخلفي الأيمن'), 'display_order': 8, 'is_required': True},
                {'name': _('جنط العجلة الخلفي الأيسر'), 'display_order': 9, 'is_required': True},
                {'name': _('أغطية العجلات'), 'display_order': 10, 'is_required': False},
                {'name': _('قفل الإطارات'), 'display_order': 11, 'is_required': False},
            ]
        },
        {
            'name': _('المقصورة الداخلية'),
            'description': _('فحص المقصورة الداخلية للسيارة بما في ذلك المقاعد ولوحة القيادة والأدوات'),
            'display_order': 3,
            'items': [
                {'name': _('المقاعد الأمامية'), 'display_order': 1, 'is_required': True},
                {'name': _('المقاعد الخلفية'), 'display_order': 2, 'is_required': True},
                {'name': _('أحزمة الأمان'), 'display_order': 3, 'is_required': True},
                {'name': _('لوحة القيادة'), 'display_order': 4, 'is_required': True},
                {'name': _('عجلة القيادة'), 'display_order': 5, 'is_required': True},
                {'name': _('عصا ناقل الحركة'), 'display_order': 6, 'is_required': True},
                {'name': _('مكيف الهواء / التدفئة'), 'display_order': 7, 'is_required': True},
                {'name': _('نظام الصوت'), 'display_order': 8, 'is_required': True},
                {'name': _('السجاد الأرضي'), 'display_order': 9, 'is_required': True},
                {'name': _('تجهيزات السقف'), 'display_order': 10, 'is_required': True},
                {'name': _('مقبض صندوق الأمتعة / غطاء المحرك'), 'display_order': 11, 'is_required': True},
                {'name': _('أدوات التحكم في النوافذ'), 'display_order': 12, 'is_required': True},
                {'name': _('أدوات التحكم في المرايا'), 'display_order': 13, 'is_required': True},
                {'name': _('فتحة السقف'), 'display_order': 14, 'is_required': False},
                {'name': _('مساحات الزجاج الأمامي'), 'display_order': 15, 'is_required': True},
                {'name': _('ماسحة الزجاج الخلفي'), 'display_order': 16, 'is_required': False},
            ]
        },
        {
            'name': _('المحرك ومكونات أسفل غطاء المحرك'),
            'description': _('فحص المحرك وصندوق المحرك والمكونات المرتبطة به'),
            'display_order': 4,
            'items': [
                {'name': _('المحرك (التشغيل)'), 'display_order': 1, 'is_required': True},
                {'name': _('زيت المحرك (المستوى)'), 'display_order': 2, 'is_required': True},
                {'name': _('سائل التبريد (المستوى)'), 'display_order': 3, 'is_required': True},
                {'name': _('سائل الفرامل (المستوى)'), 'display_order': 4, 'is_required': True},
                {'name': _('سائل التوجيه المعزز (المستوى)'), 'display_order': 5, 'is_required': True},
                {'name': _('سائل غسيل الزجاج (المستوى)'), 'display_order': 6, 'is_required': True},
                {'name': _('البطارية (الحالة والأطراف)'), 'display_order': 7, 'is_required': True},
                {'name': _('حزام المحرك'), 'display_order': 8, 'is_required': True},
                {'name': _('خراطيم المحرك'), 'display_order': 9, 'is_required': True},
                {'name': _('نظام العادم'), 'display_order': 10, 'is_required': True},
                {'name': _('تسريبات الزيت أو السوائل'), 'display_order': 11, 'is_required': True},
                {'name': _('مرشح الهواء'), 'display_order': 12, 'is_required': False},
            ]
        },
        {
            'name': _('المعدات والوثائق'),
            'description': _('فحص المعدات والوثائق المرفقة مع السيارة'),
            'display_order': 5,
            'items': [
                {'name': _('دليل المالك'), 'display_order': 1, 'is_required': True},
                {'name': _('كتيب الصيانة'), 'display_order': 2, 'is_required': True},
                {'name': _('عدة الإطار الاحتياطي'), 'display_order': 3, 'is_required': True},
                {'name': _('رافعة السيارة'), 'display_order': 4, 'is_required': True},
                {'name': _('مفتاح العجلات'), 'display_order': 5, 'is_required': True},
                {'name': _('مثلث التحذير'), 'display_order': 6, 'is_required': True},
                {'name': _('صندوق الإسعافات الأولية'), 'display_order': 7, 'is_required': False},
                {'name': _('طفاية الحريق'), 'display_order': 8, 'is_required': False},
                {'name': _('عاكسات الضوء'), 'display_order': 9, 'is_required': False},
                {'name': _('كابلات بدء التشغيل'), 'display_order': 10, 'is_required': False},
            ]
        },
        {
            'name': _('أنظمة السلامة والتشغيل'),
            'description': _('فحص أنظمة السلامة وتشغيل المركبة'),
            'display_order': 6,
            'items': [
                {'name': _('الفرامل (الأداء)'), 'display_order': 1, 'is_required': True},
                {'name': _('فرامل الركن (الأداء)'), 'display_order': 2, 'is_required': True},
                {'name': _('التوجيه (الأداء)'), 'display_order': 3, 'is_required': True},
                {'name': _('نظام التعليق'), 'display_order': 4, 'is_required': True},
                {'name': _('ناقل الحركة (تبديل السرعات)'), 'display_order': 5, 'is_required': True},
                {'name': _('نظام منع انغلاق المكابح (ABS)'), 'display_order': 6, 'is_required': True},
                {'name': _('مؤشرات لوحة القيادة'), 'display_order': 7, 'is_required': True},
                {'name': _('أضواء التحذير'), 'display_order': 8, 'is_required': True},
                {'name': _('نظام GPS / الملاحة'), 'display_order': 9, 'is_required': False},
                {'name': _('نظام مراقبة ضغط الإطارات'), 'display_order': 10, 'is_required': False},
                {'name': _('كاميرا الرجوع للخلف'), 'display_order': 11, 'is_required': False},
                {'name': _('أنظمة المساعدة على الركن'), 'display_order': 12, 'is_required': False},
                {'name': _('محسّات الركن الأمامية/الخلفية'), 'display_order': 13, 'is_required': False},
            ]
        },
    ]
    
    # إنشاء فئات وعناصر الفحص
    for category_data in categories:
        items = category_data.pop('items')
        category = CarInspectionCategory.objects.create(**category_data)
        print(f"تم إنشاء فئة: {category.name}")
        
        for item_data in items:
            item = CarInspectionItem.objects.create(category=category, **item_data)
            print(f"  - تم إنشاء عنصر فحص: {item.name}")
    
    print("تم إنشاء جميع فئات وعناصر الفحص الافتراضية بنجاح!")
else:
    print("فئات وعناصر الفحص موجودة بالفعل. لم يتم إنشاء بيانات جديدة.")