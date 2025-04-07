#!/usr/bin/env python3

"""
تحسين قالب عرض تفاصيل السيارات
هذا السكربت يقوم بتعديل وتحسين قالب car_detail_django.html
"""

import os
import re

template_path = 'templates/car_detail_django.html'

try:
    with open(template_path, 'r', encoding='utf-8') as file:
        content = file.read()

    # إصلاح مشكلة تكرار وسم الهامش للأيقونات 
    # تصحيح أنماط مثل 'ms-2" ms-1"' أو '"ms-1"' الخ
    content = re.sub(r'ms-\d+" ms-\d+"', r'ms-2"', content)
    content = re.sub(r'ms-\d+"></i>', r'ms-2"></i>', content)
    content = re.sub(r'"ms-\d+"', r'ms-2"', content)

    # تحسين عرض الأيقونات
    icon_fixes = [
        # تصحيح أيقونات الفئات في القسم العلوي
        ('<i class="fas fa-car" ms-2"></i>', '<i class="fas fa-car ms-2"></i>'),
        ('<i class="fas fa-cog" ms-2"></i>', '<i class="fas fa-cog ms-2"></i>'),
        ('<i class="fas fa-gas-pump" ms-2"></i>', '<i class="fas fa-gas-pump ms-2"></i>'),
        ('<i class="fas fa-check-circle" ms-2"></i>', '<i class="fas fa-check-circle ms-2"></i>'),
        ('<i class="fas fa-times-circle" ms-2"></i>', '<i class="fas fa-times-circle ms-2"></i>'),
        
        # تصحيح أيقونات رؤوس الأقسام
        ('<i class="fas fa-info-circle" ms-2"></i>', '<i class="fas fa-info-circle ms-2"></i>'),
        ('<i class="fas fa-list" ms-2"></i>', '<i class="fas fa-list ms-2"></i>'),
        ('<i class="fas fa-calendar-times" ms-2"></i>', '<i class="fas fa-calendar-times ms-2"></i>'),
        
        # تصحيح أيقونات المواصفات
        ('<i class="fas fa-palette" ms-2"></i>', '<i class="fas fa-palette"></i>'),
        ('<i class="fas fa-users" ms-2"></i>', '<i class="fas fa-users"></i>'),
        ('<i class="fas fa-calendar-alt" ms-2"></i>', '<i class="fas fa-calendar-alt"></i>'),
        ('<i class="fas fa-cog" ms-2"></i>', '<i class="fas fa-cog"></i>'),
        ('<i class="fas fa-gas-pump" ms-2"></i>', '<i class="fas fa-gas-pump"></i>'),
        ('<i class="fas fa-tag" ms-2"></i>', '<i class="fas fa-tag"></i>'),
        
        # تصحيح أيقونات المميزات
        ('<i class="fas fa-check-circle" ms-2"></i>', '<i class="fas fa-check-circle"></i>'),
        
        # تصحيح أيقونات أزرار الحجز
        ('<i class="fas fa-calendar-check ms-2" ms-2"></i>', '<i class="fas fa-calendar-check ms-2"></i>'),
        ('<i class="fas fa-exclamation-triangle ms-2" ms-2"></i>', '<i class="fas fa-exclamation-triangle ms-2"></i>'),
        ('<i class="fas fa-bolt ms-2" ms-2"></i>', '<i class="fas fa-bolt ms-2"></i>'),
        ('<i class="fas fa-receipt ms-2" ms-2"></i>', '<i class="fas fa-receipt ms-2"></i>'),
        ('<i class="fas fa-shopping-cart ms-2" ms-2"></i>', '<i class="fas fa-shopping-cart ms-2"></i>'),
        
        # تصحيح أيقونات رسائل الخطأ
        ('<i class="fas fa-check-circle ms-2" ms-2"></i>', '<i class="fas fa-check-circle ms-2"></i>'),
        ('<i class="fas fa-calendar-times date-range-icon" ms-2"></i>', '<i class="fas fa-calendar-times date-range-icon"></i>'),
        ('<i class="fas fa-exclamation-circle ms-2" ms-2"></i>', '<i class="fas fa-exclamation-circle ms-2"></i>'),
    ]
    
    for old, new in icon_fixes:
        content = content.replace(old, new)
    
    # تحسين ترتيب الأيقونات والنصوص
    # إزالة المسافات الزائدة بعد الأيقونات
    content = re.sub(r'"></i>\s+</div>', r'"></i></div>', content)
    
    # إضافة الرسوم المتحركة لعناصر واجهة العرض
    # تحسين النص البديل للصور
    content = content.replace('class="car-hero-image"', 'class="car-hero-image animate-fade-in-up"')
    
    # تحسين التنسيق العام للقالب وإزالة الأنماط المتكررة
    content = content.replace('id="direct-booking-days">-- أيام', 'id="direct-booking-days">-- يوم')
    
    # تحسين كلاس أزرار الحجز
    content = content.replace('class="btn btn-success w-100 mt-3"', 'class="action-button d-block text-center text-decoration-none mt-3"')
    
    # تحسين ظهور التواريخ المحجوزة
    unavailable_dates_html = '''<div class="detail-panel-body">
                    <div id="unavailableDates" class="py-4 text-center">
                        <div class="spinner-border text-primary" role="status">
                            <span class="visually-hidden">جاري التحميل...</span>
                        </div>
                        <p class="mt-2 text-muted">جاري تحميل التواريخ المحجوزة...</p>
                    </div>
                </div>'''
    
    improved_unavailable_dates_html = '''<div class="detail-panel-body">
                    <div id="unavailableDates" class="py-3">
                        <div class="text-center">
                            <div class="spinner-border text-primary" role="status">
                                <span class="visually-hidden">جاري التحميل...</span>
                            </div>
                            <p class="mt-2 text-muted">جاري تحميل التواريخ المحجوزة...</p>
                        </div>
                    </div>
                </div>'''
    
    content = content.replace(unavailable_dates_html, improved_unavailable_dates_html)
    
    with open(template_path, 'w', encoding='utf-8') as file:
        file.write(content)
        
    print(f"تم تحسين قالب عرض تفاصيل السيارات بنجاح!")
except Exception as e:
    print(f"حدث خطأ أثناء تحسين قالب عرض تفاصيل السيارات: {e}")