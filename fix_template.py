#!/usr/bin/env python3
import re

def update_car_detail_template():
    with open('templates/car_detail_django.html', 'r', encoding='utf-8') as file:
        content = file.read()
    
    # Fix badges
    content = content.replace('<i class="fas fa-car ms-2"></i>', '<i class="fas fa-car {% if is_english %}me-2{% else %}ms-2{% endif %}"></i>')
    content = content.replace('<i class="fas fa-cog ms-2"></i>', '<i class="fas fa-cog {% if is_english %}me-2{% else %}ms-2{% endif %}"></i>')
    content = content.replace('<i class="fas fa-gas-pump ms-2"></i>', '<i class="fas fa-gas-pump {% if is_english %}me-2{% else %}ms-2{% endif %}"></i>')
    
    # Fix availability badge
    content = content.replace('<i class="fas fa-check-circle ms-2"></i> متاحة', 
                             '<i class="fas fa-check-circle {% if is_english %}me-2{% else %}ms-2{% endif %}"></i> {% if is_english %}Available{% else %}متاحة{% endif %}')
    content = content.replace('<i class="fas fa-times-circle ms-2"></i> غير متاحة', 
                             '<i class="fas fa-times-circle {% if is_english %}me-2{% else %}ms-2{% endif %}"></i> {% if is_english %}Not Available{% else %}غير متاحة{% endif %}')
    
    # Fix panel headers
    content = content.replace('<h3><i class="fas fa-info-circle ms-2"></i> مواصفات السيارة</h3>', 
                             '<h3><i class="fas fa-info-circle {% if is_english %}me-2{% else %}ms-2{% endif %}"></i> {% if is_english %}Car Specifications{% else %}مواصفات السيارة{% endif %}</h3>')
    content = content.replace('<h3><i class="fas fa-list ms-2"></i> المميزات</h3>', 
                             '<h3><i class="fas fa-list {% if is_english %}me-2{% else %}ms-2{% endif %}"></i> {% if is_english %}Features{% else %}المميزات{% endif %}</h3>')
    content = content.replace('<h3><i class="fas fa-calendar-times ms-2"></i> التواريخ المحجوزة</h3>', 
                             '<h3><i class="fas fa-calendar-times {% if is_english %}me-2{% else %}ms-2{% endif %}"></i> {% if is_english %}Reserved Dates{% else %}التواريخ المحجوزة{% endif %}</h3>')
    
    # Fix specifications labels
    content = content.replace('<div class="spec-label">اللون</div>', '<div class="spec-label">{% if is_english %}Color{% else %}اللون{% endif %}</div>')
    content = content.replace('<div class="spec-label">عدد المقاعد</div>', '<div class="spec-label">{% if is_english %}Seats{% else %}عدد المقاعد{% endif %}</div>')
    content = content.replace('<div class="spec-label">سنة الصنع</div>', '<div class="spec-label">{% if is_english %}Year{% else %}سنة الصنع{% endif %}</div>')
    content = content.replace('<div class="spec-label">ناقل الحركة</div>', '<div class="spec-label">{% if is_english %}Transmission{% else %}ناقل الحركة{% endif %}</div>')
    content = content.replace('<div class="spec-label">نوع الوقود</div>', '<div class="spec-label">{% if is_english %}Fuel Type{% else %}نوع الوقود{% endif %}</div>')
    content = content.replace('<div class="spec-label">الفئة</div>', '<div class="spec-label">{% if is_english %}Category{% else %}الفئة{% endif %}</div>')
    
    # Fix loading text
    content = content.replace('<span class="visually-hidden">جاري التحميل...</span>', 
                             '<span class="visually-hidden">{% if is_english %}Loading...{% else %}جاري التحميل...{% endif %}</span>')
    content = content.replace('<p class="mt-2 text-muted">جاري تحميل التواريخ المحجوزة...</p>', 
                             '<p class="mt-2 text-muted">{% if is_english %}Loading reserved dates...{% else %}جاري تحميل التواريخ المحجوزة...{% endif %}</p>')
    
    # Fix reservation card
    content = content.replace('<h3>حجز هذه السيارة</h3>', '<h3>{% if is_english %}Book this Car{% else %}حجز هذه السيارة{% endif %}</h3>')
    content = content.replace('<div class="price-period ms-2">دينار/يوم</div>', 
                             '<div class="price-period {% if is_english %}ms-2{% else %}ms-2{% endif %}">{% if is_english %}JOD/day{% else %}دينار/يوم{% endif %}</div>')
    
    # Fix form labels
    content = content.replace('<label for="start_date" class="form-label">تاريخ الاستلام</label>', 
                             '<label for="start_date" class="form-label">{% if is_english %}Pick-up Date{% else %}تاريخ الاستلام{% endif %}</label>')
    content = content.replace('<label for="end_date" class="form-label">تاريخ التسليم</label>', 
                             '<label for="end_date" class="form-label">{% if is_english %}Return Date{% else %}تاريخ التسليم{% endif %}</label>')
    
    # Fix submit button
    content = content.replace('<i class="fas fa-calendar-check ms-2"></i> طلب الحجز', 
                             '<i class="fas fa-calendar-check {% if is_english %}me-2{% else %}ms-2{% endif %}"></i> {% if is_english %}Request Booking{% else %}طلب الحجز{% endif %}')
    
    with open('templates/car_detail_django.html', 'w', encoding='utf-8') as file:
        file.write(content)

update_car_detail_template()
print("Car detail template has been updated with language conditionals.")
