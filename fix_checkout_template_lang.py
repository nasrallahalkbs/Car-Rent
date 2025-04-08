"""
إصلاح قالب الدفع (checkout.html) ليدعم اللغتين العربية والإنجليزية
هذا السكربت يعيد إنشاء ملف checkout.html مع دعم اللغتين العربية والإنجليزية
"""
import os

def create_new_checkout_template():
    """
    إنشاء ملف checkout.html جديد مع دعم اللغتين العربية والإنجليزية
    """
    template_path = 'templates/checkout.html'
    
    # محتوى القالب الجديد
    new_content = """{% extends 'layout_django.html' %}
{% load static %}

{% block title %}{% if is_english %}Checkout - CarRental{% else %}الدفع - كاررنتال{% endif %}{% endblock %}

{% block content %}
<div class="container py-5">
    <div class="row">
        <div class="col-lg-8 mx-auto">
            <div class="card shadow-sm border-0">
                <div class="card-header bg-primary text-white">
                    <h3 class="mb-0">{% if is_english %}Checkout{% else %}إتمام عملية الدفع{% endif %}</h3>
                </div>
                <div class="card-body p-4">
                    <!-- Order Summary -->
                    <div class="order-summary mb-4">
                        <h4 class="section-title">{% if is_english %}Order Summary{% else %}ملخص الطلب{% endif %}</h4>
                        
                        {% if reservation %}
                        <!-- Single Reservation Checkout -->
                        <div class="card mb-3">
                            <div class="card-body">
                                <div class="d-flex">
                                    <div class="flex-shrink-0">
                                        {% if reservation.car.image_url %}
                                        <img src="{{ reservation.car.image_url }}" alt="{{ reservation.car.make }} {{ reservation.car.model }}" class="img-thumbnail" style="width: 100px;">
                                        {% else %}
                                        <img src="{% static 'images/car-placeholder.png' %}" alt="{{ reservation.car.make }} {{ reservation.car.model }}" class="img-thumbnail" style="width: 100px;">
                                        {% endif %}
                                    </div>
                                    <div class="flex-grow-1 ms-3">
                                        <h5>{{ reservation.car.make }} {{ reservation.car.model }}</h5>
                                        <div class="small text-muted">
                                            {% if is_english %}
                                            From {{ reservation.start_date|date:"m/d/Y" }} to {{ reservation.end_date|date:"m/d/Y" }}
                                            ({{ reservation.days }} {% if reservation.days == 1 %}day{% else %}days{% endif %})
                                            {% else %}
                                            من {{ reservation.start_date|date:"Y/m/d" }} إلى {{ reservation.end_date|date:"Y/m/d" }}
                                            ({{ reservation.days }} {% if reservation.days == 1 %}يوم{% else %}أيام{% endif %})
                                            {% endif %}
                                        </div>
                                        <div class="mt-2">
                                            <span class="fw-bold">{% if is_english %}Reservation ID:{% else %}رقم الحجز:{% endif %}</span> {{ reservation.reservation_number }}
                                        </div>
                                    </div>
                                    <div class="flex-shrink-0 text-end">
                                        <div class="fw-bold">{{ reservation.car.daily_rate }} {% if is_english %}JOD/day{% else %}دينار/يوم{% endif %}</div>
                                        <div class="text-muted small">x {{ reservation.days }}</div>
                                    </div>
                                </div>
                            </div>
                        </div>
                        {% else %}
                        <!-- Cart Checkout -->
                        {% for item in cart_items %}
                        <div class="card mb-3">
                            <div class="card-body">
                                <div class="d-flex">
                                    <div class="flex-shrink-0">
                                        {% if item.car.image_url %}
                                        <img src="{{ item.car.image_url }}" alt="{{ item.car.make }} {{ item.car.model }}" class="img-thumbnail" style="width: 100px;">
                                        {% else %}
                                        <img src="{% static 'images/car-placeholder.png' %}" alt="{{ item.car.make }} {{ item.car.model }}" class="img-thumbnail" style="width: 100px;">
                                        {% endif %}
                                    </div>
                                    <div class="flex-grow-1 ms-3">
                                        <h5>{{ item.car.make }} {{ item.car.model }}</h5>
                                        <div class="small text-muted">
                                            {% if is_english %}
                                            From {{ item.start_date|date:"m/d/Y" }} to {{ item.end_date|date:"m/d/Y" }}
                                            ({{ item.days }} {% if item.days == 1 %}day{% else %}days{% endif %})
                                            {% else %}
                                            من {{ item.start_date|date:"Y/m/d" }} إلى {{ item.end_date|date:"Y/m/d" }}
                                            ({{ item.days }} {% if item.days == 1 %}يوم{% else %}أيام{% endif %})
                                            {% endif %}
                                        </div>
                                    </div>
                                    <div class="flex-shrink-0 text-end">
                                        <div class="fw-bold">{{ item.car.daily_rate }} {% if is_english %}JOD/day{% else %}دينار/يوم{% endif %}</div>
                                        <div class="text-muted small">x {{ item.days }}</div>
                                    </div>
                                </div>
                            </div>
                        </div>
                        {% endfor %}
                        {% endif %}
                        
                        <!-- Total -->
                        <div class="d-flex justify-content-between p-3 bg-light rounded">
                            <div class="fw-bold">{% if is_english %}Total Amount:{% else %}المبلغ الإجمالي:{% endif %}</div>
                            <div class="fw-bold fs-5">{{ total_amount }} {% if is_english %}JOD{% else %}دينار{% endif %}</div>
                        </div>
                    </div>
                    
                    <!-- Payment Form -->
                    <div class="payment-form">
                        <h4 class="section-title">{% if is_english %}Payment Details{% else %}تفاصيل الدفع{% endif %}</h4>
                        
                        <form method="post" action="{% url 'process_payment' %}" class="mb-4">
                            {% csrf_token %}
                            
                            {% if reservation %}
                            <input type="hidden" name="reservation_id" value="{{ reservation.id }}">
                            {% else %}
                            <input type="hidden" name="from_cart" value="1">
                            {% endif %}
                            
                            <!-- Payment Method -->
                            <div class="mb-4">
                                <label class="form-label">{% if is_english %}Payment Method{% else %}طريقة الدفع{% endif %}</label>
                                <div class="payment-methods">
                                    <div class="form-check mb-2">
                                        <input class="form-check-input" type="radio" name="payment_method" id="creditCard" value="credit_card" checked>
                                        <label class="form-check-label" for="creditCard">
                                            {% if is_english %}Credit/Debit Card{% else %}بطاقة ائتمان/خصم{% endif %}
                                        </label>
                                    </div>
                                    <div class="form-check mb-2">
                                        <input class="form-check-input" type="radio" name="payment_method" id="paypal" value="paypal">
                                        <label class="form-check-label" for="paypal">
                                            {% if is_english %}PayPal{% else %}باي بال{% endif %}
                                        </label>
                                    </div>
                                    <div class="form-check">
                                        <input class="form-check-input" type="radio" name="payment_method" id="cashOnDelivery" value="cash">
                                        <label class="form-check-label" for="cashOnDelivery">
                                            {% if is_english %}Pay at Pickup{% else %}الدفع عند الاستلام{% endif %}
                                        </label>
                                    </div>
                                </div>
                            </div>
                            
                            <!-- Credit Card Details (will be shown/hidden with JS) -->
                            <div id="creditCardDetails">
                                <div class="row mb-3">
                                    <div class="col-12">
                                        <label for="cardName" class="form-label">{% if is_english %}Cardholder Name{% else %}اسم حامل البطاقة{% endif %}</label>
                                        <input type="text" class="form-control" id="cardName" name="card_name">
                                    </div>
                                </div>
                                <div class="row mb-3">
                                    <div class="col-12">
                                        <label for="cardNumber" class="form-label">{% if is_english %}Card Number{% else %}رقم البطاقة{% endif %}</label>
                                        <input type="text" class="form-control" id="cardNumber" name="card_number" placeholder="XXXX XXXX XXXX XXXX">
                                    </div>
                                </div>
                                <div class="row mb-3">
                                    <div class="col-md-6 mb-3 mb-md-0">
                                        <label for="expiryDate" class="form-label">{% if is_english %}Expiry Date{% else %}تاريخ الانتهاء{% endif %}</label>
                                        <input type="text" class="form-control" id="expiryDate" name="expiry_date" placeholder="MM/YY">
                                    </div>
                                    <div class="col-md-6">
                                        <label for="cvv" class="form-label">{% if is_english %}CVV{% else %}رمز التحقق{% endif %}</label>
                                        <input type="text" class="form-control" id="cvv" name="cvv" placeholder="XXX">
                                    </div>
                                </div>
                            </div>
                            
                            <!-- Billing Address -->
                            <div class="mb-4">
                                <h5 class="mb-3">{% if is_english %}Billing Address{% else %}عنوان الفواتير{% endif %}</h5>
                                <div class="row mb-3">
                                    <div class="col-md-6 mb-3 mb-md-0">
                                        <label for="address" class="form-label">{% if is_english %}Address{% else %}العنوان{% endif %}</label>
                                        <input type="text" class="form-control" id="address" name="address">
                                    </div>
                                    <div class="col-md-6">
                                        <label for="city" class="form-label">{% if is_english %}City{% else %}المدينة{% endif %}</label>
                                        <input type="text" class="form-control" id="city" name="city">
                                    </div>
                                </div>
                                <div class="row">
                                    <div class="col-md-6 mb-3 mb-md-0">
                                        <label for="country" class="form-label">{% if is_english %}Country{% else %}البلد{% endif %}</label>
                                        <select class="form-select" id="country" name="country">
                                            <option value="">{% if is_english %}Select Country{% else %}اختر البلد{% endif %}</option>
                                            <option value="JO">{% if is_english %}Jordan{% else %}الأردن{% endif %}</option>
                                            <option value="SA">{% if is_english %}Saudi Arabia{% else %}المملكة العربية السعودية{% endif %}</option>
                                            <option value="AE">{% if is_english %}United Arab Emirates{% else %}الإمارات العربية المتحدة{% endif %}</option>
                                            <option value="KW">{% if is_english %}Kuwait{% else %}الكويت{% endif %}</option>
                                            <option value="QA">{% if is_english %}Qatar{% else %}قطر{% endif %}</option>
                                            <option value="OM">{% if is_english %}Oman{% else %}عمان{% endif %}</option>
                                            <option value="BH">{% if is_english %}Bahrain{% else %}البحرين{% endif %}</option>
                                        </select>
                                    </div>
                                    <div class="col-md-6">
                                        <label for="postalCode" class="form-label">{% if is_english %}Postal Code{% else %}الرمز البريدي{% endif %}</label>
                                        <input type="text" class="form-control" id="postalCode" name="postal_code">
                                    </div>
                                </div>
                            </div>
                            
                            <!-- Terms and Conditions -->
                            <div class="form-check mb-4">
                                <input class="form-check-input" type="checkbox" id="terms" name="terms" required>
                                <label class="form-check-label" for="terms">
                                    {% if is_english %}
                                    I agree to the <a href="#" data-bs-toggle="modal" data-bs-target="#termsModal">Terms and Conditions</a> and <a href="#" data-bs-toggle="modal" data-bs-target="#privacyModal">Privacy Policy</a>
                                    {% else %}
                                    أوافق على <a href="#" data-bs-toggle="modal" data-bs-target="#termsModal">الشروط والأحكام</a> و <a href="#" data-bs-toggle="modal" data-bs-target="#privacyModal">سياسة الخصوصية</a>
                                    {% endif %}
                                </label>
                            </div>
                            
                            <!-- Submit Button -->
                            <button type="submit" class="btn btn-primary btn-lg w-100">
                                {% if is_english %}
                                Complete Payment
                                {% else %}
                                إكمال الدفع
                                {% endif %}
                            </button>
                        </form>
                    </div>
                </div>
            </div>
            
            <div class="text-center mt-4">
                <a href="{% url 'index' %}" class="btn btn-outline-secondary">
                    <i class="fas fa-arrow-{% if is_english %}left{% else %}right{% endif %} {% if is_english %}me-2{% else %}ms-2{% endif %}"></i>
                    {% if is_english %}Back to Home{% else %}العودة إلى الصفحة الرئيسية{% endif %}
                </a>
            </div>
        </div>
    </div>
</div>

<!-- Terms and Conditions Modal -->
<div class="modal fade" id="termsModal" tabindex="-1" aria-labelledby="termsModalLabel" aria-hidden="true">
    <div class="modal-dialog modal-lg">
        <div class="modal-content">
            <div class="modal-header">
                <h5 class="modal-title" id="termsModalLabel">{% if is_english %}Terms and Conditions{% else %}الشروط والأحكام{% endif %}</h5>
                <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
            </div>
            <div class="modal-body">
                {% if is_english %}
                <h6>1. Rental Agreement</h6>
                <p>This agreement constitutes a contract between the renter and CarRental. The renter agrees to the terms and conditions outlined herein.</p>
                
                <h6>2. Payment</h6>
                <p>Full payment is required to complete the reservation. We accept credit/debit cards, PayPal, and cash payments at pickup.</p>
                
                <h6>3. Cancellation Policy</h6>
                <p>Cancellations made 48 hours or more before the pickup time will receive a full refund. Cancellations made less than 48 hours before pickup will be charged 50% of the total rental fee.</p>
                
                <h6>4. Insurance and Liability</h6>
                <p>Basic insurance is included in the rental price. The renter is responsible for any damage not covered by the insurance policy.</p>
                {% else %}
                <h6>1. اتفاقية الإيجار</h6>
                <p>تشكل هذه الاتفاقية عقدًا بين المستأجر وكاررنتال. يوافق المستأجر على الشروط والأحكام الموضحة هنا.</p>
                
                <h6>2. الدفع</h6>
                <p>يلزم الدفع الكامل لإتمام الحجز. نقبل بطاقات الائتمان/الخصم، وباي بال، والدفع النقدي عند الاستلام.</p>
                
                <h6>3. سياسة الإلغاء</h6>
                <p>عمليات الإلغاء التي تتم قبل 48 ساعة أو أكثر من وقت الاستلام ستحصل على استرداد كامل. سيتم فرض رسوم بنسبة 50٪ من إجمالي رسوم الإيجار على عمليات الإلغاء التي تتم قبل أقل من 48 ساعة من الاستلام.</p>
                
                <h6>4. التأمين والمسؤولية</h6>
                <p>التأمين الأساسي مشمول في سعر الإيجار. المستأجر مسؤول عن أي ضرر لا تغطيه بوليصة التأمين.</p>
                {% endif %}
            </div>
            <div class="modal-footer">
                <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">{% if is_english %}Close{% else %}إغلاق{% endif %}</button>
            </div>
        </div>
    </div>
</div>

<!-- Privacy Policy Modal -->
<div class="modal fade" id="privacyModal" tabindex="-1" aria-labelledby="privacyModalLabel" aria-hidden="true">
    <div class="modal-dialog modal-lg">
        <div class="modal-content">
            <div class="modal-header">
                <h5 class="modal-title" id="privacyModalLabel">{% if is_english %}Privacy Policy{% else %}سياسة الخصوصية{% endif %}</h5>
                <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
            </div>
            <div class="modal-body">
                {% if is_english %}
                <p>We respect your privacy and are committed to protecting your personal data. This privacy policy will inform you how we look after your personal data when you visit our website and rent our vehicles.</p>
                
                <h6>1. Data Collection</h6>
                <p>We collect personal identification information such as name, email address, phone number, and payment details to process your reservation and provide our services.</p>
                
                <h6>2. Data Storage</h6>
                <p>Your data is securely stored and processed according to industry-standard practices. We implement appropriate security measures to prevent unauthorized access.</p>
                
                <h6>3. Data Usage</h6>
                <p>We use your data solely for processing your reservation, providing customer support, and improving our services. We do not sell or share your data with third parties except as required to fulfill our services.</p>
                {% else %}
                <p>نحن نحترم خصوصيتك ونلتزم بحماية بياناتك الشخصية. ستعلمك سياسة الخصوصية هذه بكيفية الاعتناء ببياناتك الشخصية عند زيارة موقعنا واستئجار سياراتنا.</p>
                
                <h6>1. جمع البيانات</h6>
                <p>نقوم بجمع معلومات التعريف الشخصية مثل الاسم وعنوان البريد الإلكتروني ورقم الهاتف وتفاصيل الدفع لمعالجة حجزك وتقديم خدماتنا.</p>
                
                <h6>2. تخزين البيانات</h6>
                <p>يتم تخزين بياناتك ومعالجتها بشكل آمن وفقًا لممارسات معايير الصناعة. نقوم بتنفيذ إجراءات أمنية مناسبة لمنع الوصول غير المصرح به.</p>
                
                <h6>3. استخدام البيانات</h6>
                <p>نستخدم بياناتك فقط لمعالجة حجزك وتقديم الدعم للعملاء وتحسين خدماتنا. نحن لا نبيع أو نشارك بياناتك مع أطراف ثالثة إلا عند الضرورة لتقديم خدماتنا.</p>
                {% endif %}
            </div>
            <div class="modal-footer">
                <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">{% if is_english %}Close{% else %}إغلاق{% endif %}</button>
            </div>
        </div>
    </div>
</div>
{% endblock %}

{% block scripts %}
<script>
    document.addEventListener('DOMContentLoaded', function() {
        // Toggle payment method details
        const paymentMethods = document.querySelectorAll('input[name="payment_method"]');
        const creditCardDetails = document.getElementById('creditCardDetails');
        
        paymentMethods.forEach(method => {
            method.addEventListener('change', function() {
                if (this.value === 'credit_card') {
                    creditCardDetails.style.display = 'block';
                } else {
                    creditCardDetails.style.display = 'none';
                }
            });
        });
    });
</script>
{% endblock %}
"""
    
    # كتابة المحتوى إلى الملف
    with open(template_path, 'w', encoding='utf-8') as file:
        file.write(new_content)
    
    print(f"تم إنشاء ملف قالب الدفع الجديد: {template_path}")

if __name__ == "__main__":
    create_new_checkout_template()