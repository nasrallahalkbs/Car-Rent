"""
تطبيق التصميم الاحترافي لصفحة تفاصيل الدفع مباشرة

هذا السكريبت يقوم بتنفيذ التغييرات مباشرة بدلاً من إنشاء ملفات جديدة
"""

import os
import time

def apply_ultra_pro_design():
    """تطبيق التصميم الاحترافي فوراً"""
    
    # 1. تحديث ملف CSS
    css_content = """/* تصميم صفحة تفاصيل الدفع بأسلوب احترافي */

:root {
    /* ألوان أساسية */
    --primary-color: #1e40af;
    --primary-hover: #1e3a8a;
    --primary-light: #93c5fd;
    --primary-lighter: #dbeafe;
    --primary-border: #bfdbfe;
    --primary-gradient: linear-gradient(135deg, #1e40af, #3b82f6);
    --primary-dark: #1e3a8a;
    
    /* ألوان رمادية */
    --gray-50: #f9fafb;
    --gray-100: #f3f4f6;
    --gray-200: #e5e7eb;
    --gray-300: #d1d5db;
    --gray-400: #9ca3af;
    --gray-500: #6b7280;
    --gray-600: #4b5563;
    --gray-700: #374151;
    --gray-800: #1f2937;
    --gray-900: #111827;
    
    /* ألوان حالة */
    --success: #10b981;
    --success-light: #d1fae5;
    --success-border: #a7f3d0;
    
    --warning: #f59e0b;
    --warning-light: #fef3c7;
    --warning-border: #fde68a;
    
    --danger: #ef4444;
    --danger-light: #fee2e2;
    --danger-border: #fecaca;
    
    --info: #3b82f6;
    --info-light: #dbeafe;
    --info-border: #bfdbfe;
    
    /* الخطوط */
    --font-sans: 'Tajawal', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
    
    /* المساحات */
    --space-1: 0.25rem;
    --space-2: 0.5rem;
    --space-3: 0.75rem;
    --space-4: 1rem;
    --space-5: 1.25rem;
    --space-6: 1.5rem;
    --space-8: 2rem;
    --space-10: 2.5rem;
    --space-12: 3rem;
    
    /* نصف القطر */
    --radius-sm: 0.25rem;
    --radius: 0.375rem;
    --radius-md: 0.5rem;
    --radius-lg: 0.75rem;
    --radius-xl: 1rem;
    --radius-full: 9999px;
    
    /* الظلال */
    --shadow-sm: 0 1px 2px 0 rgba(0, 0, 0, 0.05);
    --shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.1), 0 1px 2px 0 rgba(0, 0, 0, 0.06);
    --shadow-md: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
    --shadow-lg: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05);
    --shadow-xl: 0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04);
    --shadow-blue: 0 0 15px rgba(59, 130, 246, 0.15);
    
    /* الانتقالات */
    --transition-base: 0.2s ease-in-out;
    
    /* الحدود */
    --border-color: var(--gray-200);
    --light-bg: var(--gray-50);
}

/* التصميم العام */
.payment-page {
    font-family: var(--font-sans);
    background-color: var(--gray-50);
    color: var(--gray-900);
    line-height: 1.5;
    padding: 2rem 0;
}

.payment-container {
    max-width: 950px;
    margin: 0 auto;
    padding: 0 1rem;
}

/* بطاقة تفاصيل الدفع */
.payment-card {
    background-color: white;
    border-radius: var(--radius-lg);
    box-shadow: var(--shadow-lg);
    margin-bottom: 1.5rem;
    border: 1px solid var(--border-color);
    overflow: hidden;
    position: relative;
    transition: all var(--transition-base);
}

.payment-card:hover {
    box-shadow: var(--shadow-xl);
    transform: translateY(-3px);
}

.payment-card-header {
    padding: 1.5rem;
    border-bottom: 1px solid var(--border-color);
    background: linear-gradient(to right, var(--primary-lighter), white);
    position: relative;
}

.payment-card-header::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    height: 5px;
    background: var(--primary-gradient);
}

.payment-card-title {
    display: flex;
    align-items: center;
    font-weight: 700;
    font-size: 1.25rem;
    color: var(--primary-dark);
    margin-bottom: 0.5rem;
}

.payment-card-title i {
    margin-left: 0.75rem;
    color: var(--primary-color);
}

.payment-card-body {
    padding: 1.5rem;
}

/* معلومات الدفع الرئيسية */
.payment-main-info {
    display: flex;
    flex-wrap: wrap;
    margin-bottom: 1.5rem;
    padding-bottom: 1.5rem;
    border-bottom: 1px solid var(--border-color);
}

.payment-badge {
    background-color: var(--primary-lighter);
    color: var(--primary-color);
    font-weight: 600;
    padding: 0.5rem 1rem;
    border-radius: var(--radius-full);
    display: inline-flex;
    align-items: center;
    border: 1px solid var(--primary-border);
    box-shadow: var(--shadow-sm);
    margin-bottom: 1rem;
}

.payment-badge i {
    margin-left: 0.5rem;
}

.payment-id {
    font-size: 1.5rem;
    font-weight: 700;
    color: var(--primary-color);
    margin-bottom: 0.5rem;
}

.payment-reservation {
    font-size: 0.875rem;
    color: var(--gray-500);
}

.payment-amount {
    font-size: 2rem;
    font-weight: 800;
    color: var(--primary-color);
    margin: 1rem 0;
}

.payment-currency {
    font-size: 1rem;
    color: var(--gray-600);
    margin-right: 0.25rem;
}

/* حالات الدفع */
.payment-status {
    display: inline-flex;
    align-items: center;
    padding: 0.5rem 1rem;
    border-radius: var(--radius-full);
    font-weight: 600;
    font-size: 0.875rem;
}

.payment-status i {
    margin-left: 0.5rem;
}

.status-paid {
    background-color: var(--success-light);
    color: var(--success);
    border: 1px solid var(--success-border);
}

.status-pending {
    background-color: var(--warning-light);
    color: var(--warning);
    border: 1px solid var(--warning-border);
}

.status-refunded {
    background-color: var(--info-light);
    color: var(--info);
    border: 1px solid var(--info-border);
}

.status-cancelled {
    background-color: var(--danger-light);
    color: var(--danger);
    border: 1px solid var(--danger-border);
}

/* تفاصيل العميل والحجز والمدفوعات */
.details-grid {
    display: grid;
    grid-template-columns: repeat(2, 1fr);
    gap: 1.5rem;
}

@media (max-width: 768px) {
    .details-grid {
        grid-template-columns: 1fr;
    }
}

.detail-group {
    margin-bottom: 1.5rem;
}

.detail-label {
    font-size: 0.875rem;
    color: var(--gray-500);
    margin-bottom: 0.25rem;
}

.detail-value {
    font-weight: 600;
    color: var(--gray-800);
}

/* أيقونات طرق الدفع */
.payment-method-icon {
    font-size: 1.75rem;
    margin-left: 0.5rem;
    vertical-align: middle;
    filter: drop-shadow(0 3px 5px rgba(0, 0, 0, 0.1));
    transition: all var(--transition-base);
}

.payment-method-icon.visa {
    color: #1a1f71;
    filter: drop-shadow(0 3px 5px rgba(26, 31, 113, 0.15));
}

.detail-value:hover .payment-method-icon.visa {
    filter: drop-shadow(0 4px 8px rgba(26, 31, 113, 0.25));
}

.payment-method-icon.mastercard {
    color: #eb001b;
    filter: drop-shadow(0 3px 5px rgba(235, 0, 27, 0.15));
}

.detail-value:hover .payment-method-icon.mastercard {
    filter: drop-shadow(0 4px 8px rgba(235, 0, 27, 0.25));
}

.payment-method-icon.amex {
    color: #2e77bc;
    filter: drop-shadow(0 3px 5px rgba(46, 119, 188, 0.15));
}

.detail-value:hover .payment-method-icon.amex {
    filter: drop-shadow(0 4px 8px rgba(46, 119, 188, 0.25));
}

.payment-method-icon.cash {
    color: #10b981;
    filter: drop-shadow(0 3px 5px rgba(16, 185, 129, 0.15));
}

.detail-value:hover .payment-method-icon.cash {
    filter: drop-shadow(0 4px 8px rgba(16, 185, 129, 0.25));
}

.payment-method-icon.bank {
    color: #0ea5e9;
    filter: drop-shadow(0 3px 5px rgba(14, 165, 233, 0.15));
}

.detail-value:hover .payment-method-icon.bank {
    filter: drop-shadow(0 4px 8px rgba(14, 165, 233, 0.25));
}

/* ملخص المدفوعات والتكاليف - تصميم فائق الاحترافية */
.payment-summary {
    margin-top: 2rem;
    border-radius: var(--radius-xl);
    overflow: hidden;
    box-shadow: var(--shadow-lg);
    border: 1px solid var(--border-color);
    transition: all var(--transition-base);
    transform-style: preserve-3d;
    background: white;
    position: relative;
}

.payment-summary:hover {
    box-shadow: var(--shadow-xl), var(--shadow-blue);
    transform: translateY(-7px);
}

.payment-summary::before {
    content: "";
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    height: 7px;
    background: var(--primary-gradient);
    z-index: 2;
}

.payment-summary-header {
    background: linear-gradient(to right, var(--light-bg), white);
    padding: 1.5rem;
    border-bottom: 1px solid var(--border-color);
    font-weight: 700;
    color: var(--primary-dark);
    font-size: 1.125rem;
}

.payment-summary-body {
    padding: 1.5rem;
}

.payment-summary-row {
    display: flex;
    justify-content: space-between;
    margin-bottom: 1rem;
    padding-bottom: 1rem;
    border-bottom: 1px dashed var(--border-color);
}

.payment-summary-label {
    color: var(--gray-600);
}

.payment-summary-value {
    font-weight: 600;
    color: var(--gray-800);
}

.payment-summary-total {
    display: flex;
    justify-content: space-between;
    padding-top: 1rem;
    border-top: 2px solid var(--primary-lighter);
}

.payment-summary-total-label {
    font-weight: 700;
    font-size: 1.125rem;
    color: var(--primary-dark);
}

.payment-summary-total-value {
    font-weight: 800;
    font-size: 1.5rem;
    color: var(--primary-color);
}

/* تفاصيل السيارة */
.car-info {
    margin-top: 1.5rem;
    display: flex;
    flex-direction: column;
}

.car-image {
    width: 100%;
    height: 200px;
    background-color: var(--gray-100);
    border-radius: var(--radius);
    overflow: hidden;
    margin-bottom: 1rem;
    border: 1px solid var(--border-color);
    box-shadow: var(--shadow);
    display: flex;
    align-items: center;
    justify-content: center;
}

.car-image img {
    width: 100%;
    height: 100%;
    object-fit: cover;
}

.car-details-grid {
    display: grid;
    grid-template-columns: repeat(2, 1fr);
    gap: 1rem;
    margin-top: 1rem;
}

.car-detail-item {
    background-color: var(--gray-50);
    padding: 1rem;
    border-radius: var(--radius);
    border: 1px solid var(--border-color);
}

.car-detail-label {
    font-size: 0.75rem;
    color: var(--gray-500);
    margin-bottom: 0.25rem;
}

.car-detail-value {
    font-weight: 600;
    color: var(--gray-800);
}

/* أزرار الإجراءات */
.payment-actions {
    display: flex;
    flex-wrap: wrap;
    gap: 0.75rem;
    justify-content: flex-end;
    margin-top: 2rem;
}

.payment-action-btn {
    padding: 0.75rem 1.5rem;
    border-radius: var(--radius);
    font-weight: 600;
    display: inline-flex;
    align-items: center;
    text-decoration: none;
    transition: all var(--transition-base);
    cursor: pointer;
}

.payment-action-btn i {
    margin-left: 0.5rem;
}

.btn-primary {
    background-color: var(--primary-color);
    color: white;
    border: 1px solid var(--primary-hover);
}

.btn-primary:hover {
    background-color: var(--primary-hover);
    box-shadow: 0 4px 8px rgba(30, 64, 175, 0.2);
    transform: translateY(-2px);
}

.btn-light {
    background-color: white;
    color: var(--gray-700);
    border: 1px solid var(--border-color);
}

.btn-light:hover {
    background-color: var(--gray-50);
    box-shadow: 0 4px 8px rgba(0, 0, 0, 0.05);
    transform: translateY(-2px);
}

/* بطاقة الإيصال */
.receipt-card {
    background-color: white;
    border-radius: var(--radius-lg);
    box-shadow: var(--shadow);
    padding: 2rem;
    max-width: 600px;
    margin: 0 auto;
}

.receipt-company {
    text-align: center;
    margin-bottom: 2rem;
}

.receipt-logo {
    font-size: 3rem;
    color: var(--primary-color);
    margin-bottom: 0.5rem;
}

.receipt-company-name {
    font-size: 1.5rem;
    font-weight: 700;
    color: var(--gray-800);
}

.receipt-company-info {
    color: var(--gray-600);
    margin-top: 0.5rem;
}

.receipt-heading {
    text-align: center;
    margin-bottom: 2rem;
}

.receipt-title {
    font-size: 1.25rem;
    font-weight: 700;
    color: var(--gray-800);
    margin-bottom: 0.5rem;
}

.receipt-number {
    color: var(--gray-600);
}

.receipt-date {
    color: var(--gray-500);
    font-size: 0.875rem;
    text-align: left;
    margin-bottom: 2rem;
}

.receipt-border {
    height: 5px;
    background: var(--primary-gradient);
    margin: 2rem 0;
    border-radius: var(--radius-full);
}

/* تحسينات إضافية للعرض المتجاوب */
@media (max-width: 576px) {
    .payment-card-header, .payment-card-body {
        padding: 1rem;
    }
    
    .payment-amount {
        font-size: 1.5rem;
    }
    
    .details-grid {
        grid-template-columns: 1fr;
        gap: 1rem;
    }
    
    .car-details-grid {
        grid-template-columns: 1fr;
    }
    
    .payment-summary-header, .payment-summary-body {
        padding: 1rem;
    }
    
    .payment-actions {
        flex-direction: column;
    }
    
    .payment-action-btn {
        width: 100%;
        justify-content: center;
    }
}

/* تأثيرات حركية */
.payment-card, .payment-summary {
    animation: fadeIn 0.6s ease-in-out;
}

@keyframes fadeIn {
    from {
        opacity: 0;
        transform: translateY(20px);
    }
    to {
        opacity: 1;
        transform: translateY(0);
    }
}

.car-image {
    overflow: hidden;
}

.car-image img {
    transition: transform 0.5s ease;
}

.car-image:hover img {
    transform: scale(1.05);
}

/* الطباعة */
@media print {
    .payment-page {
        background-color: white;
        padding: 0;
    }
    
    .payment-card, .payment-summary {
        box-shadow: none;
        border: 1px solid #ddd;
        break-inside: avoid;
    }
    
    .payment-actions {
        display: none;
    }
}"""
    
    # حفظ ملف CSS
    css_path = 'staticfiles/css/payment_ultra_pro.css'
    with open(css_path, 'w', encoding='utf-8') as f:
        f.write(css_content)
    
    print(f"تم إنشاء/تحديث ملف CSS: {css_path}")
    
    # 2. إنشاء قالب HTML
    html_content = """{% extends 'admin_layout.html' %}
{% load i18n %}
{% load static %}

{% block title %}{% if is_english %}Payment Details{% else %}تفاصيل الدفع{% endif %} #{{ payment.id }}{% endblock %}

{% block styles %}
<link rel="stylesheet" href="{% static 'css/payment_ultra_pro.css' %}?v={{ cache_buster }}">
{% endblock %}

{% block content %}
<div class="payment-page">
    <div class="payment-container">
        <!-- بطاقة معلومات الدفع الرئيسية -->
        <div class="payment-card">
            <div class="payment-card-header">
                <div class="payment-card-title">
                    <i class="fas fa-file-invoice-dollar"></i>
                    {% if is_english %}Payment Details{% else %}تفاصيل الدفع{% endif %}
                </div>
                <div>
                    {% if payment.car %}
                    <span class="payment-badge">
                        <i class="fas fa-car"></i>
                        {% if is_english %}Car Rental{% else %}تأجير سيارة{% endif %}
                    </span>
                    {% endif %}
                </div>
            </div>
            <div class="payment-card-body">
                <!-- معلومات الدفع الرئيسية -->
                <div class="payment-main-info">
                    <div class="col-md-6 mb-4">
                        <div class="payment-id">
                            {% if is_english %}Payment{% else %}الدفعة{% endif %} #{{ payment.id }}
                        </div>
                        {% if payment.reservation %}
                        <div class="payment-reservation">
                            {% if is_english %}for Reservation{% else %}للحجز{% endif %} #{{ payment.reservation.id }}
                        </div>
                        {% endif %}
                        
                        <div class="payment-amount">
                            {{ payment.amount }} <span class="payment-currency">{% if is_english %}KWD{% else %}د.ك{% endif %}</span>
                        </div>
                        
                        <div>
                            {% if payment.status == 'paid' %}
                            <div class="payment-status status-paid">
                                <i class="fas fa-check-circle"></i> 
                                {% if is_english %}Paid{% else %}مدفوع{% endif %}
                            </div>
                            {% elif payment.status == 'pending' %}
                            <div class="payment-status status-pending">
                                <i class="fas fa-clock"></i> 
                                {% if is_english %}Pending{% else %}قيد الانتظار{% endif %}
                            </div>
                            {% elif payment.status == 'refunded' %}
                            <div class="payment-status status-refunded">
                                <i class="fas fa-undo-alt"></i> 
                                {% if is_english %}Refunded{% else %}مسترجع{% endif %}
                            </div>
                            {% else %}
                            <div class="payment-status status-cancelled">
                                <i class="fas fa-ban"></i>
                                {% if is_english %}Cancelled{% else %}ملغي{% endif %}
                            </div>
                            {% endif %}
                        </div>
                    </div>
                </div>
                
                <!-- تفاصيل الدفع والحجز -->
                <div class="details-grid">
                    <div>
                        <h5 class="detail-label">{% if is_english %}Payment Information{% else %}معلومات الدفع{% endif %}</h5>
                        <div class="detail-group">
                            <div class="detail-label">{% if is_english %}Date{% else %}التاريخ{% endif %}</div>
                            <div class="detail-value">{% if is_english %}{{ payment.date|date:"F d, Y" }}{% else %}{{ payment.date|date:"Y/m/d" }}{% endif %}</div>
                        </div>
                        
                        <div class="detail-group">
                            <div class="detail-label">{% if is_english %}Time{% else %}الوقت{% endif %}</div>
                            <div class="detail-value">{% if is_english %}{{ payment.date|date:"h:i A" }}{% else %}{{ payment.date|date:"H:i" }}{% endif %}</div>
                        </div>
                        
                        <div class="detail-group">
                            <div class="detail-label">{% if is_english %}Reference Number{% else %}رقم المرجع{% endif %}</div>
                            <div class="detail-value">{{ payment.reference_number|default:"—" }}</div>
                        </div>
                        
                        <div class="detail-group">
                            <div class="detail-label">{% if is_english %}Payment Method{% else %}طريقة الدفع{% endif %}</div>
                            <div class="detail-value">
                                {% if payment.payment_method == 'visa' %}
                                <i class="fab fa-cc-visa payment-method-icon visa"></i> 
                                {% if is_english %}Visa Card{% else %}بطاقة فيزا{% endif %}
                                {% elif payment.payment_method == 'mastercard' %}
                                <i class="fab fa-cc-mastercard payment-method-icon mastercard"></i> 
                                {% if is_english %}MasterCard{% else %}ماستركارد{% endif %}
                                {% elif payment.payment_method == 'amex' %}
                                <i class="fab fa-cc-amex payment-method-icon amex"></i> 
                                {% if is_english %}American Express{% else %}أمريكان إكسبرس{% endif %}
                                {% elif payment.payment_method == 'cash' %}
                                <i class="fas fa-money-bill-wave payment-method-icon cash"></i> 
                                {% if is_english %}Cash{% else %}نقداً{% endif %}
                                {% elif payment.payment_method == 'bank_transfer' %}
                                <i class="fas fa-university payment-method-icon bank"></i> 
                                {% if is_english %}Bank Transfer{% else %}تحويل بنكي{% endif %}
                                {% else %}
                                <i class="fas fa-credit-card payment-method-icon"></i> 
                                {{ payment.payment_method }}
                                {% endif %}
                            </div>
                        </div>
                    </div>
                    
                    <div>
                        {% if payment.user %}
                        <h5 class="detail-label">{% if is_english %}Customer Information{% else %}معلومات العميل{% endif %}</h5>
                        <div class="detail-group">
                            <div class="detail-label">{% if is_english %}Name{% else %}الاسم{% endif %}</div>
                            <div class="detail-value">{{ payment.user.get_full_name|default:payment.user.username }}</div>
                        </div>
                        
                        <div class="detail-group">
                            <div class="detail-label">{% if is_english %}Email{% else %}البريد الإلكتروني{% endif %}</div>
                            <div class="detail-value">{{ payment.user.email }}</div>
                        </div>
                        
                        <div class="detail-group">
                            <div class="detail-label">{% if is_english %}User ID{% else %}معرّف المستخدم{% endif %}</div>
                            <div class="detail-value">{{ payment.user.id }}</div>
                        </div>
                        
                        <div class="detail-group">
                            <div class="detail-label">{% if is_english %}Registration Date{% else %}تاريخ التسجيل{% endif %}</div>
                            <div class="detail-value">{% if is_english %}{{ payment.user.date_joined|date:"F d, Y" }}{% else %}{{ payment.user.date_joined|date:"Y/m/d" }}{% endif %}</div>
                        </div>
                        {% endif %}
                    </div>
                </div>
                
                {% if payment.car %}
                <!-- معلومات السيارة -->
                <h5 class="detail-label mt-4">{% if is_english %}Car Information{% else %}معلومات السيارة{% endif %}</h5>
                <div class="car-info">
                    <div class="car-image">
                        {% if payment.car.image %}
                        <img src="{{ payment.car.image.url }}" alt="{{ payment.car.make }} {{ payment.car.model }}">
                        {% else %}
                        <i class="fas fa-car"></i>
                        {% endif %}
                    </div>
                    
                    <h5 class="mb-2">{{ payment.car.make }} {{ payment.car.model }} {{ payment.car.year }}</h5>
                    
                    <div class="car-details-grid">
                        <div class="car-detail-item">
                            <div class="car-detail-label">{% if is_english %}Rental Period{% else %}فترة التأجير{% endif %}</div>
                            <div class="car-detail-value">{{ days }} {% if is_english %}day{{ days|pluralize }}{% else %}يوم{% if days > 2 %}اً{% elif days > 10 %}{% endif %}{% endif %}</div>
                        </div>
                        
                        <div class="car-detail-item">
                            <div class="car-detail-label">{% if is_english %}Daily Rate{% else %}السعر اليومي{% endif %}</div>
                            <div class="car-detail-value">{{ payment.car.daily_rate }} {% if is_english %}KWD{% else %}د.ك{% endif %}</div>
                        </div>
                        
                        <div class="car-detail-item">
                            <div class="car-detail-label">{% if is_english %}Start Date{% else %}تاريخ البداية{% endif %}</div>
                            <div class="car-detail-value">{% if is_english %}{{ payment.start_date|date:"M d, Y" }}{% else %}{{ payment.start_date|date:"Y/m/d" }}{% endif %}</div>
                        </div>
                        
                        <div class="car-detail-item">
                            <div class="car-detail-label">{% if is_english %}End Date{% else %}تاريخ النهاية{% endif %}</div>
                            <div class="car-detail-value">{% if is_english %}{{ payment.end_date|date:"M d, Y" }}{% else %}{{ payment.end_date|date:"Y/m/d" }}{% endif %}</div>
                        </div>
                    </div>
                </div>
                {% endif %}
                
                <!-- ملخص الدفع -->
                <div class="payment-summary">
                    <div class="payment-summary-header">
                        {% if is_english %}Cost Summary{% else %}ملخص التكاليف{% endif %}
                    </div>
                    <div class="payment-summary-body">
                        {% if payment.car %}
                        <div class="payment-summary-row">
                            <div class="payment-summary-label">{% if is_english %}Daily Rate{% else %}السعر اليومي{% endif %}</div>
                            <div class="payment-summary-value">{{ payment.car.daily_rate }} {% if is_english %}KWD{% else %}د.ك{% endif %}</div>
                        </div>
                        
                        <div class="payment-summary-row">
                            <div class="payment-summary-label">{% if is_english %}Rental Period{% else %}فترة التأجير{% endif %}</div>
                            <div class="payment-summary-value">{{ days }} {% if is_english %}day{{ days|pluralize }}{% else %}يوم{% if days > 2 %}اً{% elif days > 10 %}{% endif %}{% endif %}</div>
                        </div>
                        
                        <div class="payment-summary-row">
                            <div class="payment-summary-label">{% if is_english %}Subtotal{% else %}المجموع الفرعي{% endif %}</div>
                            <div class="payment-summary-value">{{ payment.amount }} {% if is_english %}KWD{% else %}د.ك{% endif %}</div>
                        </div>
                        {% endif %}
                        
                        <div class="payment-summary-total">
                            <div class="payment-summary-total-label">{% if is_english %}Total{% else %}المجموع الكلي{% endif %}</div>
                            <div class="payment-summary-total-value">{{ payment.amount }} {% if is_english %}KWD{% else %}د.ك{% endif %}</div>
                        </div>
                    </div>
                </div>
                
                <!-- أزرار الإجراءات -->
                <div class="payment-actions">
                    {% if payment.status == 'paid' %}
                    <a href="{% url 'process_refund' payment_id=payment.id %}" class="payment-action-btn btn-light" onclick="return confirm('{% if is_english %}Are you sure you want to refund this payment?{% else %}هل أنت متأكد من استرداد هذه الدفعة؟{% endif %}')">
                        <i class="fas fa-undo-alt"></i> {% if is_english %}Refund Payment{% else %}استرداد المبلغ{% endif %}
                    </a>
                    {% endif %}
                    
                    <a href="{% url 'admin_payments' %}" class="payment-action-btn btn-light">
                        <i class="fas fa-arrow-left"></i> {% if is_english %}Back to Payments{% else %}العودة للمدفوعات{% endif %}
                    </a>
                    
                    <a href="{% url 'download_receipt' payment_id=payment.id %}" class="payment-action-btn btn-primary">
                        <i class="fas fa-file-download"></i> {% if is_english %}Download Receipt{% else %}تنزيل الإيصال{% endif %}
                    </a>
                </div>
            </div>
        </div>
    </div>
</div>
{% endblock %}"""
    
    # حفظ قالب HTML
    template_path = 'templates/admin/payment_detail_direct.html'
    with open(template_path, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print(f"تم إنشاء/تحديث قالب HTML: {template_path}")
    
    # 3. تحديث ملف admin_views.py
    admin_views_path = 'rental/admin_views.py'
    with open(admin_views_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # تحديث دالة payment_details لاستخدام القالب الجديد والتنسيق المحسن
    import re
    
    pattern = r"def payment_details\(request, payment_id\):.*?return render\(request, ['\"].*?['\"], context\)"
    replacement = """def payment_details(request, payment_id):
    \"\"\"Admin view to show payment details\"\"\"
    payment = get_object_or_404(Reservation, id=payment_id)
    
    # Calculate the number of days between start_date and end_date
    delta = (payment.end_date - payment.start_date).days + 1
    
    # Add additional payment fields needed by template
    payment.date = payment.created_at  # Use created_at for payment date
    payment.reference_number = ''  # Default empty reference number
    payment.status = payment.payment_status  # Map payment_status to status
    payment.amount = payment.total_price  # Map total_price to amount
    
    # Extract payment method and reference number from notes if available
    if payment.notes:
        notes_lines = payment.notes.split('\\n')
        for line in notes_lines:
            if 'طريقة الدفع:' in line:
                payment.payment_method = line.split('طريقة الدفع:')[1].strip()
            elif 'رقم المرجع:' in line:
                payment.reference_number = line.split('رقم المرجع:')[1].strip()
    
    # Default values if not found in notes
    if not hasattr(payment, 'payment_method'):
        payment.payment_method = 'visa'  # Default payment method
    
    # تحديد لغة المستخدم
    from django.utils.translation import get_language
    current_language = get_language()
    is_english = current_language == 'en'
    is_rtl = current_language == 'ar'
    
    context = {
        'payment': payment,
        'days': delta,
        'amount': payment.total_price,
        'current_user': request.user,
        'is_english': is_english,
        'is_rtl': is_rtl,
    }
    
    # استخدام القالب المباشر مع التصميم الاحترافي
    template_name = 'admin/payment_detail_direct.html'
    
    # إضافة مكون زمني لإجبار المتصفح على تحديث الصفحة وعدم استخدام النسخة المخزنة
    import time
    context['cache_buster'] = str(int(time.time()))
    
    return render(request, template_name, context)"""
    
    updated_content = re.sub(pattern, replacement, content, flags=re.DOTALL)
    
    with open(admin_views_path, 'w', encoding='utf-8') as f:
        f.write(updated_content)
    
    print(f"تم تحديث ملف admin_views.py لاستخدام التصميم الجديد")
    
    # 4. نسخ ملفات CSS إلى مجلد staticfiles
    staticfiles_path = 'staticfiles/css/'
    
    # التأكد من وجود المجلد
    os.makedirs(staticfiles_path, exist_ok=True)
    
    # نسخ ملف CSS من المجلد static إلى staticfiles
    static_css_path = 'static/css/payment_ultra_pro.css'
    with open(static_css_path, 'w', encoding='utf-8') as f:
        f.write(css_content)
    
    print(f"تم نسخ ملف CSS إلى المجلد static: {static_css_path}")
    
    return "تم تطبيق التصميم الاحترافي الجديد بنجاح"

if __name__ == "__main__":
    print(apply_ultra_pro_design())