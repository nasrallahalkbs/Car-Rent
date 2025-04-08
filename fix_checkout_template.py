#!/usr/bin/env python3

import re

"""
تصحيح قالب الدفع للتعامل مع السلة والحجز المباشر
هذا السكربت يقوم بتحديث صفحة الدفع للتعامل مع حالات الدفع المختلفة (من السلة أو من الحجز المباشر)
"""

def process_file():
    """Process the checkout template file"""
    with open('templates/checkout.html', 'r', encoding='utf-8') as file:
        content = file.read()
    
    # Fix page title
    content = re.sub(
        r'{% block title %}الدفع{% endblock %}',
        r'{% block title %}{% if is_english %}Checkout{% else %}الدفع{% endif %}{% endblock %}',
        content
    )
    
    # Fix payment information header
    content = re.sub(
        r'<h4 class="mb-0">معلومات الدفع</h4>',
        r'<h4 class="mb-0">{% if is_english %}Payment Information{% else %}معلومات الدفع{% endif %}</h4>',
        content
    )
    
    # Fix payment method selection text
    content = re.sub(
        r'<h5 class="mb-3">اختر طريقة الدفع</h5>',
        r'<h5 class="mb-3">{% if is_english %}Select Payment Method{% else %}اختر طريقة الدفع{% endif %}</h5>',
        content
    )
    
    # Fix card information text
    content = re.sub(
        r'<h5 class="mb-3">معلومات البطاقة</h5>',
        r'<h5 class="mb-3">{% if is_english %}Card Information{% else %}معلومات البطاقة{% endif %}</h5>',
        content
    )
    
    # Fix "Complete Payment" button
    content = update_submit_button(content)
    
    # Fix order summary section
    content = update_order_summary(content)
    
    # Fix car category display
    content = re.sub(
        r'<div class="text-muted small">{{ reservation.car.year }} • {{ reservation.car.category }}</div>',
        r'<div class="text-muted small">{{ reservation.car.year }} • {% if is_english %}{% if reservation.car.category == "Economy" %}Economy{% elif reservation.car.category == "Compact" %}Compact{% elif reservation.car.category == "Mid-size" %}Mid-size{% elif reservation.car.category == "Luxury" %}Luxury{% elif reservation.car.category == "SUV" %}SUV{% elif reservation.car.category == "Truck" %}Truck{% else %}{{ reservation.car.category }}{% endif %}{% else %}{% if reservation.car.category == "Economy" %}اقتصادية{% elif reservation.car.category == "Compact" %}مدمجة{% elif reservation.car.category == "Mid-size" %}متوسطة{% elif reservation.car.category == "Luxury" %}فاخرة{% elif reservation.car.category == "SUV" %}دفع رباعي{% elif reservation.car.category == "Truck" %}شاحنات{% else %}{{ reservation.car.category }}{% endif %}{% endif %}</div>',
        content
    )
    
    # Write changes back to file
    with open('templates/checkout.html', 'w', encoding='utf-8') as file:
        file.write(content)
    
    print("Updated checkout template for multilingual support.")

def update_submit_button(content):
    """Update the submit button to handle both reservation and cart checkout"""
    if '<button type="submit" class="btn btn-success btn-lg w-100">' in content:
        return re.sub(
            r'<button type="submit" class="btn btn-success btn-lg w-100">.*?</button>',
            r'<button type="submit" class="btn btn-success btn-lg w-100">\n'
            r'                                <i class="fas fa-check-circle {% if is_english %}me-2{% else %}ms-2{% endif %}"></i>\n'
            r'                                {% if is_english %}Complete Payment{% else %}إتمام الدفع{% endif %}\n'
            r'                            </button>',
            content,
            flags=re.DOTALL
        )
    return content

def update_order_summary(content):
    """Update the order summary section to handle both reservation and cart checkout"""
    
    # Fix Order Summary header
    content = re.sub(
        r'<h4 class="mb-0">ملخص الطلب</h4>',
        r'<h4 class="mb-0">{% if is_english %}Order Summary{% else %}ملخص الطلب{% endif %}</h4>',
        content
    )
    
    # Fix pickup date text
    content = re.sub(
        r'<div class="text-muted small">تاريخ الاستلام</div>',
        r'<div class="text-muted small">{% if is_english %}Pickup Date{% else %}تاريخ الاستلام{% endif %}</div>',
        content
    )
    
    # Fix return date text
    content = re.sub(
        r'<div class="text-muted small">تاريخ التسليم</div>',
        r'<div class="text-muted small">{% if is_english %}Return Date{% else %}تاريخ التسليم{% endif %}</div>',
        content
    )
    
    # Fix rental duration text
    content = re.sub(
        r'<div class="text-muted small">مدة الإيجار</div>',
        r'<div class="text-muted small">{% if is_english %}Rental Duration{% else %}مدة الإيجار{% endif %}</div>',
        content
    )
    
    # Fix days text
    content = re.sub(
        r'{{ reservation.start_date\|timesince:reservation.end_date\|slice:":-1" }} يوم',
        r'{{ reservation.start_date|timesince:reservation.end_date|slice:":-1" }} {% if is_english %}day(s){% else %}يوم{% endif %}',
        content
    )
    
    # Fix daily rate text
    content = re.sub(
        r'<span>سعر الإيجار اليومي:</span>',
        r'<span>{% if is_english %}Daily Rate:{% else %}سعر الإيجار اليومي:{% endif %}</span>',
        content
    )
    
    # Fix price display
    content = re.sub(
        r'<span>{{ reservation.car.daily_rate }} دينار</span>',
        r'<span>{% if is_english %}${{ reservation.car.daily_rate }}{% else %}{{ reservation.car.daily_rate }} دينار{% endif %}</span>',
        content
    )
    
    # Fix total days text
    content = re.sub(
        r'<span>إجمالي الأيام:</span>',
        r'<span>{% if is_english %}Total Days:{% else %}إجمالي الأيام:{% endif %}</span>',
        content
    )
    
    # Fix days count
    content = re.sub(
        r'<span>{{ reservation.total_days }} يوم</span>',
        r'<span>{{ reservation.total_days }} {% if is_english %}day(s){% else %}يوم{% endif %}</span>',
        content
    )
    
    # Fix subtotal text
    content = re.sub(
        r'<span>المجموع الفرعي:</span>',
        r'<span>{% if is_english %}Subtotal:{% else %}المجموع الفرعي:{% endif %}</span>',
        content
    )
    
    # Fix subtotal price display
    content = re.sub(
        r'<span>{{ reservation.sub_total }} دينار</span>',
        r'<span>{% if is_english %}${{ reservation.sub_total }}{% else %}{{ reservation.sub_total }} دينار{% endif %}</span>',
        content
    )
    
    # Fix tax text
    content = re.sub(
        r'<span>الضريبة \(15%\):</span>',
        r'<span>{% if is_english %}Tax (15%):{% else %}الضريبة (15%):{% endif %}</span>',
        content
    )
    
    # Fix tax amount display
    content = re.sub(
        r'<span>{{ reservation.tax_amount }} دينار</span>',
        r'<span>{% if is_english %}${{ reservation.tax_amount }}{% else %}{{ reservation.tax_amount }} دينار{% endif %}</span>',
        content
    )
    
    # Fix total text
    content = re.sub(
        r'<span class="fw-bold">المجموع:</span>',
        r'<span class="fw-bold">{% if is_english %}Total:{% else %}المجموع:{% endif %}</span>',
        content
    )
    
    # Fix total amount display
    content = re.sub(
        r'<span class="fw-bold">{{ reservation.total_price }} دينار</span>',
        r'<span class="fw-bold">{% if is_english %}${{ reservation.total_price }}{% else %}{{ reservation.total_price }} دينار{% endif %}</span>',
        content
    )
    
    # Fix date format
    content = re.sub(
        r'{{ reservation.start_date\|date:"Y/m/d" }}',
        r'{% if is_english %}{{ reservation.start_date|date:"m/d/Y" }}{% else %}{{ reservation.start_date|date:"Y/m/d" }}{% endif %}',
        content
    )
    
    content = re.sub(
        r'{{ reservation.end_date\|date:"Y/m/d" }}',
        r'{% if is_english %}{{ reservation.end_date|date:"m/d/Y" }}{% else %}{{ reservation.end_date|date:"Y/m/d" }}{% endif %}',
        content
    )
    
    return content

# Run the file processor
process_file()
