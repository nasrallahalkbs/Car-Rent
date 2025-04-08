#!/usr/bin/env python3

import re

def fix_cart_template():
    with open('templates/cart.html', 'r', encoding='utf-8') as file:
        content = file.read()
    
    # Fix title
    content = re.sub(
        r'{% block title %}Your Cart - CarRental{% endblock %}',
        r'{% block title %}{% if is_english %}Your Cart - CarRental{% else %}سلة التسوق - كاررنتال{% endif %}{% endblock %}',
        content
    )
    
    # Fix heading
    content = re.sub(
        r'<h1 class="mb-4">Your Cart</h1>',
        r'<h1 class="mb-4">{% if is_english %}Your Cart{% else %}سلة التسوق{% endif %}</h1>',
        content
    )
    
    # Fix Card header - Reserved Cars
    content = re.sub(
        r'<h4 class="mb-0">Reserved Cars</h4>',
        r'<h4 class="mb-0">{% if is_english %}Reserved Cars{% else %}السيارات المحجوزة{% endif %}</h4>',
        content
    )
    
    # Fix table headers
    content = re.sub(
        r'<th>Vehicle</th>',
        r'<th>{% if is_english %}Vehicle{% else %}السيارة{% endif %}</th>',
        content
    )
    
    content = re.sub(
        r'<th>Dates</th>',
        r'<th>{% if is_english %}Dates{% else %}التواريخ{% endif %}</th>',
        content
    )
    
    content = re.sub(
        r'<th>Days</th>',
        r'<th>{% if is_english %}Days{% else %}الأيام{% endif %}</th>',
        content
    )
    
    content = re.sub(
        r'<th>Price</th>',
        r'<th>{% if is_english %}Price{% else %}السعر{% endif %}</th>',
        content
    )
    
    # Fix "to" text
    content = re.sub(
        r'<small class="text-muted">to</small>',
        r'<small class="text-muted">{% if is_english %}to{% else %}إلى{% endif %}</small>',
        content
    )
    
    # Fix button text - Continue Shopping
    content = re.sub(
        r'<i class="fas fa-arrow-left me-2"></i>Continue Shopping',
        r'<i class="fas fa-arrow-left {% if is_english %}me-2{% else %}ms-2{% endif %}"></i>{% if is_english %}Continue Shopping{% else %}مواصلة التسوق{% endif %}',
        content
    )
    
    # Fix Order Summary header
    content = re.sub(
        r'<h4 class="mb-0">Order Summary</h4>',
        r'<h4 class="mb-0">{% if is_english %}Order Summary{% else %}ملخص الطلب{% endif %}</h4>',
        content
    )
    
    # Fix Summary texts
    content = re.sub(
        r'<span>Subtotal:</span>',
        r'<span>{% if is_english %}Subtotal:{% else %}المجموع الفرعي:{% endif %}</span>',
        content
    )
    
    content = re.sub(
        r'<span>Tax \(Included\):</span>',
        r'<span>{% if is_english %}Tax (Included):{% else %}الضريبة (مشمولة):{% endif %}</span>',
        content
    )
    
    content = re.sub(
        r'<span class="fw-bold">Total:</span>',
        r'<span class="fw-bold">{% if is_english %}Total:{% else %}المجموع:{% endif %}</span>',
        content
    )
    
    # Fix checkout button
    content = re.sub(
        r'<i class="fas fa-credit-card me-2"></i>Proceed to Checkout',
        r'<i class="fas fa-credit-card {% if is_english %}me-2{% else %}ms-2{% endif %}"></i>{% if is_english %}Proceed to Checkout{% else %}المتابعة إلى الدفع{% endif %}',
        content
    )
    
    # Fix empty cart text
    content = re.sub(
        r'<h3>Your cart is empty</h3>',
        r'<h3>{% if is_english %}Your cart is empty{% else %}سلة التسوق فارغة{% endif %}</h3>',
        content
    )
    
    content = re.sub(
        r'<p class="text-muted mb-4">Looks like you haven\'t added any cars to your cart yet.</p>',
        r'<p class="text-muted mb-4">{% if is_english %}Looks like you haven\'t added any cars to your cart yet.{% else %}يبدو أنك لم تضف أي سيارات إلى سلة التسوق بعد.{% endif %}</p>',
        content
    )
    
    # Fix browse cars button
    content = re.sub(
        r'<i class="fas fa-car me-2"></i>Browse Cars',
        r'<i class="fas fa-car {% if is_english %}me-2{% else %}ms-2{% endif %}"></i>{% if is_english %}Browse Cars{% else %}تصفح السيارات{% endif %}',
        content
    )
    
    # Fix date format
    content = re.sub(
        r'{{ item.item.start_date\|date:"m/d/Y" }}',
        r'{% if is_english %}{{ item.item.start_date|date:"m/d/Y" }}{% else %}{{ item.item.start_date|date:"Y/m/d" }}{% endif %}',
        content
    )
    
    content = re.sub(
        r'{{ item.item.end_date\|date:"m/d/Y" }}',
        r'{% if is_english %}{{ item.item.end_date|date:"m/d/Y" }}{% else %}{{ item.item.end_date|date:"Y/m/d" }}{% endif %}',
        content
    )
    
    # Fix car image alignment
    content = re.sub(
        r'<img src="{{ item.car.image_url }}" alt="{{ item.car.make }} {{ item.car.model }}" class="me-3"',
        r'<img src="{{ item.car.image_url }}" alt="{{ item.car.make }} {{ item.car.model }}" class="{% if is_english %}me-3{% else %}ms-3{% endif %}"',
        content
    )
    
    # Fix price display for Arabic
    content = re.sub(
        r'<td>\${{ item.price\|floatformat:2 }}</td>',
        r'<td>{% if is_english %}${{ item.price|floatformat:2 }}{% else %}{{ item.price|floatformat:2 }} ${% endif %}</td>',
        content
    )
    
    content = re.sub(
        r'<span>\${{ total_price\|floatformat:2 }}</span>',
        r'<span>{% if is_english %}${{ total_price|floatformat:2 }}{% else %}{{ total_price|floatformat:2 }} ${% endif %}</span>',
        content
    )
    
    content = re.sub(
        r'<span>\$0.00</span>',
        r'<span>{% if is_english %}$0.00{% else %}0.00 ${% endif %}</span>',
        content
    )
    
    content = re.sub(
        r'<span class="fw-bold">\${{ total_price\|floatformat:2 }}</span>',
        r'<span class="fw-bold">{% if is_english %}${{ total_price|floatformat:2 }}{% else %}{{ total_price|floatformat:2 }} ${% endif %}</span>',
        content
    )
    
    # Fix category display
    content = re.sub(
        r'<small class="text-muted">{{ item.car.category }}</small>',
        r'<small class="text-muted">{% if is_english %}{% if item.car.category == "Economy" %}Economy{% elif item.car.category == "Compact" %}Compact{% elif item.car.category == "Mid-size" %}Mid-size{% elif item.car.category == "Luxury" %}Luxury{% elif item.car.category == "SUV" %}SUV{% elif item.car.category == "Truck" %}Truck{% else %}{{ item.car.category }}{% endif %}{% else %}{% if item.car.category == "Economy" %}اقتصادية{% elif item.car.category == "Compact" %}مدمجة{% elif item.car.category == "Mid-size" %}متوسطة{% elif item.car.category == "Luxury" %}فاخرة{% elif item.car.category == "SUV" %}دفع رباعي{% elif item.car.category == "Truck" %}شاحنات{% else %}{{ item.car.category }}{% endif %}{% endif %}</small>',
        content
    )
    
    # Write the changes back
    with open('templates/cart.html', 'w', encoding='utf-8') as file:
        file.write(content)
    
    print("Cart template updated with bilingual support.")

fix_cart_template()
