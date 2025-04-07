#!/usr/bin/env python

"""
تصحيح قالب الدفع للتعامل مع السلة والحجز المباشر
هذا السكربت يقوم بتحديث صفحة الدفع للتعامل مع حالات الدفع المختلفة (من السلة أو من الحجز المباشر)
"""

import re
import os

def process_file():
    """Process the checkout template file"""
    template_path = "templates/checkout.html"
    
    # Make sure the file exists
    if not os.path.exists(template_path):
        print(f"Error: {template_path} does not exist")
        return False
    
    # Read the file
    with open(template_path, "r", encoding="utf-8") as file:
        content = file.read()
    
    # Make the necessary changes
    updated_content = update_submit_button(content)
    updated_content = update_order_summary(updated_content)
    
    # Write the changes back to the file
    with open(template_path, "w", encoding="utf-8") as file:
        file.write(updated_content)
    
    print(f"Successfully updated {template_path}")
    return True

def update_submit_button(content):
    """Update the submit button to handle both reservation and cart checkout"""
    submit_button_pattern = r'<!-- Submit Button -->\s*<button type="submit" class="btn btn-primary btn-lg w-100">\s*<i class="fas fa-lock ms-2"></i>إتمام الدفع - {{ reservation.total_price }} دينار\s*</button>'
    
    replacement = '''<!-- Submit Button -->
                        <button type="submit" class="btn btn-primary btn-lg w-100">
                            <i class="fas fa-lock ms-2"></i>إتمام الدفع {% if reservation %}- {{ reservation.total_price }} دينار{% else %}- {{ cart_total }} دينار{% endif %}
                        </button>'''
    
    return re.sub(submit_button_pattern, replacement, content)

def update_order_summary(content):
    """Update the order summary section to handle both reservation and cart checkout"""
    # Find the beginning of the order summary card
    order_summary_pattern = r'<!-- Order Summary -->\s*<div class="card shadow-sm border-0 mb-4">.*?<div class="card-body">'
    
    # Split content at this point to insert conditional logic
    match = re.search(order_summary_pattern, content, re.DOTALL)
    if not match:
        print("Warning: Could not find order summary section")
        return content
        
    # Split at the match end position
    pre_content = content[:match.end()]
    post_content = content[match.end():]
    
    # Add conditional rendering for reservation or cart items
    conditional_block = '''
                    {% if reservation %}
                    <!-- Single Reservation Summary -->
                    <div class="reservation-car d-flex align-items-center mb-3 pb-3 border-bottom">
                        {% if reservation.car.image_url %}
                        <img src="{{ reservation.car.image_url }}" alt="{{ reservation.car.make }}" class="rounded ms-3" width="60">
                        {% else %}
                        <img src="{% static 'images/car-placeholder.svg' %}" alt="{{ reservation.car.make }}" class="rounded ms-3" width="60">
                        {% endif %}
                        <div>
                            <div class="fw-semibold">{{ reservation.car.make }} {{ reservation.car.model }}</div>
                            <div class="text-muted small">{{ reservation.car.year }} • {{ reservation.car.category }}</div>
                        </div>
                    </div>
                    
                    <div class="reservation-details mb-3 pb-3 border-bottom">
                        <div class="mb-2">
                            <div class="text-muted small">تاريخ الاستلام</div>
                            <div>{{ reservation.start_date|date:"Y/m/d" }}</div>
                        </div>
                        <div class="mb-2">
                            <div class="text-muted small">تاريخ التسليم</div>
                            <div>{{ reservation.end_date|date:"Y/m/d" }}</div>
                        </div>
                        <div>
                            <div class="text-muted small">مدة الإيجار</div>
                            <div>{{ reservation.start_date|timesince:reservation.end_date|slice:":-1" }} يوم</div>
                        </div>
                    </div>
                    
                    <div class="price-summary">
                        <div class="d-flex justify-content-between mb-2">
                            <span>سعر الإيجار اليومي:</span>
                            <span>{{ reservation.car.daily_rate }} دينار</span>
                        </div>
                        <div class="d-flex justify-content-between mb-2">
                            <span>عدد الأيام:</span>
                            <span>{{ reservation.start_date|timesince:reservation.end_date|slice:":-1" }} يوم</span>
                        </div>
                        <hr>
                        <div class="d-flex justify-content-between fw-bold">
                            <span>المجموع:</span>
                            <span>{{ reservation.total_price }} دينار</span>
                        </div>
                    </div>
                    {% else %}
                    <!-- Cart Items Summary -->
                    {% for item in cart_items %}
                    <div class="cart-car d-flex align-items-center mb-3 pb-3 border-bottom">
                        {% if item.car.image_url %}
                        <img src="{{ item.car.image_url }}" alt="{{ item.car.make }}" class="rounded ms-3" width="60">
                        {% else %}
                        <img src="{% static 'images/car-placeholder.svg' %}" alt="{{ item.car.make }}" class="rounded ms-3" width="60">
                        {% endif %}
                        <div>
                            <div class="fw-semibold">{{ item.car.make }} {{ item.car.model }}</div>
                            <div class="text-muted small">{{ item.car.year }} • {{ item.car.category }}</div>
                            <div class="text-muted small">{{ item.start_date|date:"Y/m/d" }} - {{ item.end_date|date:"Y/m/d" }}</div>
                            <div class="text-primary">{{ item.total }} دينار</div>
                        </div>
                    </div>
                    {% endfor %}
                    
                    <div class="price-summary">
                        <div class="d-flex justify-content-between mb-2">
                            <span>عدد السيارات:</span>
                            <span>{{ cart_items|length }}</span>
                        </div>
                        <div class="d-flex justify-content-between mb-2">
                            <span>مجموع الأيام:</span>
                            <span>{{ total_days }} يوم</span>
                        </div>
                        <hr>
                        <div class="d-flex justify-content-between fw-bold">
                            <span>المجموع:</span>
                            <span>{{ cart_total }} دينار</span>
                        </div>
                    </div>
                    {% endif %}
'''
    
    # Replace the existing content with conditional logic
    old_content_pattern = r'<div class="reservation-car d-flex align-items-center mb-3 pb-3 border-bottom">.*?<div class="d-flex justify-content-between fw-bold">.*?<span>{{ reservation.total_price }} دينار</span>.*?</div>.*?</div>'
    
    # Check if we can find the pattern to replace
    if re.search(old_content_pattern, post_content, re.DOTALL):
        updated_post_content = re.sub(old_content_pattern, conditional_block, post_content, flags=re.DOTALL)
        return pre_content + updated_post_content
    else:
        # If pattern not found, insert at the beginning of post_content
        return pre_content + conditional_block + post_content

if __name__ == "__main__":
    process_file()
