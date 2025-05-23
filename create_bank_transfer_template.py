"""
هذا السكريبت يقوم بإنشاء قالب صفحة التحويل البنكي
"""

import os

def create_bank_transfer_template():
    """إنشاء قالب صفحة التحويل البنكي"""
    file_path = 'templates/payment_bank_transfer.html'
    
    bank_transfer_template = """{% extends 'base.html' %}
{% load static %}

{% block title %}
{% if is_english %}Bank Transfer Payment{% else %}الدفع عبر التحويل البنكي{% endif %}
{% endblock %}

{% block styles %}
<link rel="stylesheet" href="{% static 'css/payment.css' %}">
<style>
    .bank-info {
        background-color: var(--light-bg);
        border-radius: 8px;
        padding: 20px;
        margin-bottom: 20px;
    }
    .bank-info p {
        margin-bottom: 10px;
    }
    .bank-note {
        background-color: var(--bs-warning-bg-subtle);
        border-left: 4px solid var(--bs-warning);
        padding: 15px;
        margin-top: 20px;
        border-radius: 4px;
    }
    .verification-form {
        background-color: var(--light-bg);
        border-radius: 8px;
        padding: 20px;
        margin-top: 30px;
    }
</style>
{% endblock %}

{% block content %}
<div class="container my-5">
    <div class="row justify-content-center">
        <div class="col-lg-10">
            <div class="card shadow-sm">
                <div class="card-body p-lg-5">
                    <div class="text-center mb-4">
                        <h2 class="card-title">
                            {% if is_english %}Bank Transfer Payment{% else %}الدفع عبر التحويل البنكي{% endif %}
                        </h2>
                        <p class="text-muted">
                            {% if is_english %}
                            Please transfer the amount of <strong>${{ total_amount }}</strong> to our bank account.
                            {% else %}
                            يرجى تحويل مبلغ <strong>${{ total_amount }}</strong> إلى حسابنا البنكي.
                            {% endif %}
                        </p>
                    </div>
                    
                    <div class="bank-info">
                        <h4 class="mb-3">
                            {% if is_english %}Bank Account Details{% else %}تفاصيل الحساب البنكي{% endif %}
                        </h4>
                        <p><strong>{% if is_english %}Bank Name{% else %}اسم البنك{% endif %}:</strong> International Bank of Car Rentals</p>
                        <p><strong>{% if is_english %}Account Name{% else %}اسم الحساب{% endif %}:</strong> CarRental LLC</p>
                        <p><strong>{% if is_english %}Account Number{% else %}رقم الحساب{% endif %}:</strong> 1234567890</p>
                        <p><strong>{% if is_english %}IBAN{% else %}رقم الآيبان{% endif %}:</strong> SA12 3456 7890 1234 5678 9012</p>
                        <p><strong>{% if is_english %}SWIFT/BIC Code{% else %}رمز السويفت{% endif %}:</strong> CRLBNK123</p>
                        <p><strong>{% if is_english %}Branch{% else %}الفرع{% endif %}:</strong> Main Branch</p>
                    </div>
                    
                    <div class="bank-note">
                        <h5 class="mb-2">
                            {% if is_english %}Important{% else %}هام{% endif %}
                        </h5>
                        <p>
                            {% if is_english %}
                            Please include your reservation ID <strong>#{{ reservation.id }}</strong> in the payment reference field when making the transfer.
                            {% else %}
                            يرجى تضمين رقم الحجز <strong>#{{ reservation.id }}</strong> في حقل المرجع عند إجراء التحويل.
                            {% endif %}
                        </p>
                        <p class="mb-0">
                            {% if is_english %}
                            After completing the transfer, please fill out the form below to confirm your payment.
                            {% else %}
                            بعد إتمام التحويل، يرجى ملء النموذج أدناه لتأكيد الدفع الخاص بك.
                            {% endif %}
                        </p>
                    </div>
                    
                    <div class="verification-form">
                        <form method="post" action="{% url 'payment_gateway' %}?reservation_id={{ reservation.id }}">
                            {% csrf_token %}
                            <input type="hidden" name="payment_method" value="bank_transfer">
                            
                            <div class="mb-3">
                                <label for="transfer_date" class="form-label">
                                    {% if is_english %}Transfer Date{% else %}تاريخ التحويل{% endif %}
                                </label>
                                <input type="date" class="form-control" id="transfer_date" name="transfer_date" required>
                            </div>
                            
                            <div class="mb-3">
                                <label for="transfer_reference" class="form-label">
                                    {% if is_english %}Transfer Reference Number{% else %}رقم مرجع التحويل{% endif %}
                                </label>
                                <input type="text" class="form-control" id="transfer_reference" name="transfer_reference" required>
                            </div>
                            
                            <div class="mb-3">
                                <label for="bank_name" class="form-label">
                                    {% if is_english %}Your Bank Name{% else %}اسم البنك الخاص بك{% endif %}
                                </label>
                                <input type="text" class="form-control" id="bank_name" name="bank_name" required>
                            </div>
                            
                            <div class="mb-3">
                                <label for="transfer_amount" class="form-label">
                                    {% if is_english %}Transfer Amount{% else %}مبلغ التحويل{% endif %}
                                </label>
                                <div class="input-group">
                                    <span class="input-group-text">$</span>
                                    <input type="number" step="0.01" class="form-control" id="transfer_amount" name="transfer_amount" 
                                        value="{{ total_amount }}" required>
                                </div>
                            </div>
                            
                            <div class="mb-3">
                                <label for="notes" class="form-label">
                                    {% if is_english %}Additional Notes{% else %}ملاحظات إضافية{% endif %}
                                </label>
                                <textarea class="form-control" id="notes" name="notes" rows="3"></textarea>
                            </div>
                            
                            <div class="d-grid gap-2">
                                <button type="submit" class="btn btn-primary py-3">
                                    {% if is_english %}
                                    Confirm Bank Transfer
                                    {% else %}
                                    تأكيد التحويل البنكي
                                    {% endif %}
                                </button>
                            </div>
                        </form>
                    </div>
                </div>
            </div>
        </div>
    </div>
</div>
{% endblock %}
"""
    
    # إنشاء دليل templates إذا لم يكن موجوداً
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    
    # إنشاء القالب
    with open(file_path, 'w', encoding='utf-8') as file:
        file.write(bank_transfer_template)
    
    print("تم إنشاء قالب التحويل البنكي بنجاح")

if __name__ == "__main__":
    create_bank_transfer_template()