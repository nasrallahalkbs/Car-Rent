"""
تحسين صفحة تفاصيل الدفع بتصميم احترافي مشابه للمتاجر الإلكترونية
"""

import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'car_rental_project.settings')
django.setup()

def create_css_file():
    """إنشاء ملف CSS احترافي جديد لصفحة تفاصيل الدفع"""
    css_content = """/* تصميم صفحة تفاصيل الدفع بأسلوب احترافي */

:root {
    /* ألوان أساسية */
    --primary-color: #1e40af;
    --primary-hover: #1e3a8a;
    --primary-light: #93c5fd;
    --primary-lighter: #dbeafe;
    --primary-border: #bfdbfe;
    
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
    
    /* الظلال */
    --shadow-sm: 0 1px 2px 0 rgba(0, 0, 0, 0.05);
    --shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.1), 0 1px 2px 0 rgba(0, 0, 0, 0.06);
    --shadow-md: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
    --shadow-lg: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05);
}

/* إعدادات عامة */
.payment-page {
    font-family: var(--font-sans);
    background-color: var(--gray-50);
    color: var(--gray-900);
    line-height: 1.5;
}

/* صفحة الفاتورة */
.invoice-container {
    max-width: 1000px;
    margin: 0 auto;
    padding: var(--space-8);
}

.invoice-header {
    background-color: white;
    border-radius: var(--radius-lg);
    box-shadow: var(--shadow-md);
    padding: var(--space-8);
    margin-bottom: var(--space-6);
    border: 1px solid var(--gray-200);
    position: relative;
    overflow: hidden;
}

.invoice-header::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: 8px;
    background: linear-gradient(to right, var(--primary-color), var(--primary-hover));
}

.invoice-title {
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    margin-bottom: var(--space-6);
    padding-bottom: var(--space-4);
    border-bottom: 1px solid var(--gray-200);
}

.invoice-logo {
    display: flex;
    align-items: center;
}

.invoice-logo i {
    font-size: 2rem;
    color: var(--primary-color);
    margin-left: var(--space-2);
}

.invoice-logo-text {
    font-size: 1.5rem;
    font-weight: 700;
    color: var(--gray-800);
}

.invoice-id {
    background-color: var(--primary-lighter);
    color: var(--primary-color);
    padding: var(--space-2) var(--space-4);
    border-radius: var(--radius);
    font-weight: 700;
    font-size: 1rem;
}

.invoice-details {
    display: flex;
    justify-content: space-between;
}

.invoice-info {
    max-width: 50%;
}

.invoice-label {
    font-size: 0.875rem;
    color: var(--gray-500);
    margin-bottom: var(--space-1);
}

.invoice-value {
    font-weight: 600;
    margin-bottom: var(--space-4);
}

.invoice-status {
    padding: var(--space-3) var(--space-6);
    border-radius: var(--radius-full);
    font-weight: 600;
    display: inline-flex;
    align-items: center;
}

.invoice-status i {
    margin-left: var(--space-2);
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

/* قسم تفاصيل السيارة */
.car-details {
    background-color: white;
    border-radius: var(--radius-lg);
    box-shadow: var(--shadow-md);
    padding: var(--space-8);
    margin-bottom: var(--space-6);
    border: 1px solid var(--gray-200);
}

.car-details-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: var(--space-6);
    padding-bottom: var(--space-4);
    border-bottom: 1px solid var(--gray-200);
}

.car-details-title {
    font-size: 1.25rem;
    font-weight: 600;
    color: var(--gray-800);
    display: flex;
    align-items: center;
}

.car-details-title i {
    color: var(--primary-color);
    margin-left: var(--space-2);
}

.car-info {
    display: flex;
    margin-bottom: var(--space-6);
}

.car-image {
    width: 100px;
    height: 80px;
    background-color: var(--gray-100);
    display: flex;
    align-items: center;
    justify-content: center;
    border-radius: var(--radius);
    margin-left: var(--space-6);
    border: 1px solid var(--gray-200);
}

.car-image i {
    font-size: 2.5rem;
    color: var(--gray-400);
}

.car-meta {
    flex: 1;
}

.car-name {
    font-size: 1.25rem;
    font-weight: 600;
    margin-bottom: var(--space-1);
    color: var(--gray-800);
}

.car-description {
    color: var(--gray-600);
    margin-bottom: var(--space-2);
}

.car-rental-period {
    font-size: 0.875rem;
    color: var(--gray-700);
    margin-top: var(--space-2);
}

.rental-details {
    display: flex;
    flex-wrap: wrap;
    margin-bottom: var(--space-4);
}

.rental-detail {
    margin-left: var(--space-6);
    margin-bottom: var(--space-4);
}

.rental-detail-label {
    font-size: 0.75rem;
    color: var(--gray-500);
    margin-bottom: var(--space-1);
}

.rental-detail-value {
    font-weight: 600;
    color: var(--gray-800);
}

/* قسم تفاصيل الدفع */
.payment-details {
    background-color: white;
    border-radius: var(--radius-lg);
    box-shadow: var(--shadow-md);
    padding: var(--space-8);
    margin-bottom: var(--space-6);
    border: 1px solid var(--gray-200);
}

.payment-details-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: var(--space-6);
    padding-bottom: var(--space-4);
    border-bottom: 1px solid var(--gray-200);
}

.payment-details-title {
    font-size: 1.25rem;
    font-weight: 600;
    color: var(--gray-800);
    display: flex;
    align-items: center;
}

.payment-details-title i {
    color: var(--primary-color);
    margin-left: var(--space-2);
}

.payment-method {
    display: flex;
    align-items: center;
    padding: var(--space-4);
    border: 1px solid var(--gray-200);
    border-radius: var(--radius);
    margin-bottom: var(--space-4);
}

.payment-method-icon {
    font-size: 2rem;
    margin-left: var(--space-4);
}

.payment-method-info {
    flex: 1;
}

.payment-method-name {
    font-weight: 600;
    font-size: 1rem;
    margin-bottom: var(--space-1);
}

.payment-method-details {
    font-size: 0.875rem;
    color: var(--gray-600);
}

.payment-grid {
    display: grid;
    grid-template-columns: repeat(2, 1fr);
    gap: var(--space-4);
}

.payment-field {
    margin-bottom: var(--space-4);
}

.payment-field-label {
    font-size: 0.875rem;
    color: var(--gray-500);
    margin-bottom: var(--space-1);
}

.payment-field-value {
    font-weight: 600;
    color: var(--gray-800);
}

/* جدول المبالغ */
.payment-summary {
    background-color: var(--gray-50);
    border-radius: var(--radius);
    margin-top: var(--space-6);
    border: 1px solid var(--gray-200);
    overflow: hidden;
}

.payment-summary-title {
    padding: var(--space-4);
    background-color: var(--gray-100);
    font-weight: 600;
    border-bottom: 1px solid var(--gray-200);
}

.payment-summary-content {
    padding: var(--space-4);
}

.payment-summary-row {
    display: flex;
    justify-content: space-between;
    padding: var(--space-2) 0;
    font-size: 0.875rem;
}

.payment-summary-row:not(:last-child) {
    border-bottom: 1px dashed var(--gray-200);
    margin-bottom: var(--space-2);
    padding-bottom: var(--space-2);
}

.payment-summary-total {
    display: flex;
    justify-content: space-between;
    margin-top: var(--space-4);
    padding-top: var(--space-4);
    border-top: 2px solid var(--gray-300);
    font-weight: 700;
}

/* جدول العميل */
.customer-section {
    background-color: white;
    border-radius: var(--radius-lg);
    box-shadow: var(--shadow-md);
    padding: var(--space-8);
    margin-bottom: var(--space-6);
    border: 1px solid var(--gray-200);
}

.customer-section-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: var(--space-6);
    padding-bottom: var(--space-4);
    border-bottom: 1px solid var(--gray-200);
}

.customer-section-title {
    font-size: 1.25rem;
    font-weight: 600;
    color: var(--gray-800);
    display: flex;
    align-items: center;
}

.customer-section-title i {
    color: var(--primary-color);
    margin-left: var(--space-2);
}

.customer-info {
    display: grid;
    grid-template-columns: repeat(2, 1fr);
    gap: var(--space-6);
}

.customer-info-box {
    background-color: var(--gray-50);
    border: 1px solid var(--gray-200);
    border-radius: var(--radius);
    padding: var(--space-4);
}

.customer-info-box-title {
    font-weight: 600;
    margin-bottom: var(--space-3);
    padding-bottom: var(--space-2);
    border-bottom: 1px solid var(--gray-200);
    color: var(--gray-700);
}

.customer-field {
    margin-bottom: var(--space-2);
}

.customer-field-label {
    font-size: 0.75rem;
    color: var(--gray-500);
}

.customer-field-value {
    font-weight: 500;
}

/* أزرار الإجراءات */
.actions-section {
    background-color: white;
    border-radius: var(--radius-lg);
    box-shadow: var(--shadow-md);
    padding: var(--space-8);
    margin-bottom: var(--space-6);
    border: 1px solid var(--gray-200);
    text-align: center;
}

.actions-title {
    font-size: 1rem;
    font-weight: 600;
    margin-bottom: var(--space-4);
    color: var(--gray-700);
}

.action-buttons {
    display: flex;
    flex-wrap: wrap;
    justify-content: center;
    gap: var(--space-4);
}

.action-button {
    padding: var(--space-3) var(--space-6);
    border-radius: var(--radius);
    font-weight: 500;
    text-decoration: none;
    display: inline-flex;
    align-items: center;
    transition: all 0.2s;
}

.action-button i {
    margin-left: var(--space-2);
}

.action-button-primary {
    background-color: var(--primary-color);
    color: white;
    border: 1px solid var(--primary-hover);
}

.action-button-primary:hover {
    background-color: var(--primary-hover);
}

.action-button-secondary {
    background-color: white;
    color: var(--gray-700);
    border: 1px solid var(--gray-300);
}

.action-button-secondary:hover {
    background-color: var(--gray-100);
}

.action-button-success {
    background-color: var(--success);
    color: white;
    border: 1px solid var(--success);
}

.action-button-success:hover {
    background-color: #0ca678;
}

.action-button-danger {
    background-color: var(--danger);
    color: white;
    border: 1px solid var(--danger);
}

.action-button-danger:hover {
    background-color: #e03131;
}

.action-button-warning {
    background-color: var(--warning);
    color: white;
    border: 1px solid var(--warning);
}

.action-button-warning:hover {
    background-color: #e67700;
}

/* التذييل */
.invoice-footer {
    text-align: center;
    margin-top: var(--space-12);
    color: var(--gray-500);
    font-size: 0.875rem;
}

/* تحسينات للجوال */
@media (max-width: 768px) {
    .invoice-details {
        flex-direction: column;
    }
    
    .invoice-info {
        max-width: 100%;
        margin-bottom: var(--space-4);
    }
    
    .car-info {
        flex-direction: column;
    }
    
    .car-image {
        margin-bottom: var(--space-4);
        margin-left: 0;
    }
    
    .rental-details {
        flex-direction: column;
    }
    
    .rental-detail {
        margin-left: 0;
    }
    
    .payment-grid {
        grid-template-columns: 1fr;
    }
    
    .customer-info {
        grid-template-columns: 1fr;
    }
    
    .action-buttons {
        flex-direction: column;
    }
}
"""
    
    # حفظ ملف CSS
    css_path = 'static/css/payment_invoice.css'
    with open(css_path, 'w', encoding='utf-8') as f:
        f.write(css_content)
        
    print(f"تم إنشاء ملف CSS في: {css_path}")
    return css_path

def create_html_template():
    """إنشاء قالب HTML جديد لصفحة تفاصيل الدفع"""
    template_content = """{% extends 'admin_layout.html' %}
{% load i18n %}
{% load static %}

{% block title %}تفاصيل الدفع #{{ payment.id }} - لوحة التحكم{% endblock %}

{% block styles %}
<link rel="stylesheet" href="{% static 'css/payment_invoice.css' %}?v={{ cache_buster }}">
{% endblock %}

{% block content %}
<div class="payment-page">
    <div class="invoice-container">
        <!-- ترويسة الفاتورة -->
        <div class="invoice-header">
            <div class="invoice-title">
                <div class="invoice-logo">
                    <i class="fas fa-file-invoice-dollar"></i>
                    <div class="invoice-logo-text">إيصال مدفوعات تأجير السيارات</div>
                </div>
                <div class="invoice-id">#{{ payment.id }}</div>
            </div>
            
            <div class="invoice-details">
                <div class="invoice-info">
                    <div class="invoice-label">تاريخ الإصدار</div>
                    <div class="invoice-value">{% if is_english %}{{ payment.date|date:"F d, Y" }}{% else %}{{ payment.date|date:"Y/m/d" }}{% endif %}</div>
                    
                    <div class="invoice-label">وقت المعاملة</div>
                    <div class="invoice-value">{{ payment.date|time:"h:i A" }}</div>
                    
                    <div class="invoice-label">مرجع الدفع</div>
                    <div class="invoice-value">{{ payment.reference_number|default:"—" }}</div>
                </div>
                
                <div class="invoice-info">
                    <div class="invoice-label">حالة الدفع</div>
                    <div class="invoice-value">
                        {% if payment.status == 'paid' %}
                        <div class="invoice-status status-paid">
                            <i class="fas fa-check-circle"></i> مدفوع بالكامل
                        </div>
                        {% elif payment.status == 'pending' %}
                        <div class="invoice-status status-pending">
                            <i class="fas fa-clock"></i> في انتظار الدفع
                        </div>
                        {% elif payment.status == 'refunded' %}
                        <div class="invoice-status status-refunded">
                            <i class="fas fa-undo-alt"></i> تم استرداد المبلغ
                        </div>
                        {% else %}
                        <div class="invoice-status status-cancelled">
                            <i class="fas fa-ban"></i> ملغي
                        </div>
                        {% endif %}
                    </div>
                    
                    <div class="invoice-label">المبلغ الإجمالي</div>
                    <div class="invoice-value" style="font-size: 1.5rem; font-weight: 700; color: var(--primary-color);">{{ payment.amount }} د.ك</div>
                </div>
            </div>
        </div>
        
        <!-- قسم تفاصيل السيارة -->
        <div class="car-details">
            <div class="car-details-header">
                <div class="car-details-title">
                    <i class="fas fa-car"></i> تفاصيل السيارة
                </div>
            </div>
            
            <div class="car-info">
                <div class="car-image">
                    <i class="fas fa-car-side"></i>
                </div>
                <div class="car-meta">
                    <div class="car-name">{{ payment.car.make }} {{ payment.car.model }}</div>
                    <div class="car-description">{{ payment.car.year }} | {{ payment.car.category }}</div>
                    <div class="car-rental-period">
                        <strong>فترة الإيجار:</strong> {% if is_english %}{{ payment.start_date|date:"m/d/Y" }}{% else %}{{ payment.start_date|date:"Y/m/d" }}{% endif %} إلى {% if is_english %}{{ payment.end_date|date:"m/d/Y" }}{% else %}{{ payment.end_date|date:"Y/m/d" }}{% endif %}
                    </div>
                </div>
            </div>
            
            <div class="rental-details">
                <div class="rental-detail">
                    <div class="rental-detail-label">رقم الحجز</div>
                    <div class="rental-detail-value">#{{ payment.id }}</div>
                </div>
                
                <div class="rental-detail">
                    <div class="rental-detail-label">حالة الحجز</div>
                    <div class="rental-detail-value">
                        {% if payment.status == 'paid' %}
                        <span style="color: var(--success)"><i class="fas fa-check-circle"></i> مكتمل</span>
                        {% elif payment.status == 'pending' %}
                        <span style="color: var(--warning)"><i class="fas fa-clock"></i> معلق</span>
                        {% elif payment.status == 'confirmed' %}
                        <span style="color: var(--success)"><i class="fas fa-check"></i> مؤكد</span>
                        {% else %}
                        <span style="color: var(--danger)"><i class="fas fa-ban"></i> ملغي</span>
                        {% endif %}
                    </div>
                </div>
                
                <div class="rental-detail">
                    <div class="rental-detail-label">نوع السيارة</div>
                    <div class="rental-detail-value">{{ payment.car.category }}</div>
                </div>
                
                <div class="rental-detail">
                    <div class="rental-detail-label">رقم اللوحة</div>
                    <div class="rental-detail-value">{{ payment.car.license_plate }}</div>
                </div>
            </div>
            
            <div class="payment-summary">
                <div class="payment-summary-title">ملخص التكاليف</div>
                <div class="payment-summary-content">
                    <div class="payment-summary-row">
                        <div>سعر الإيجار اليومي</div>
                        <div>{{ payment.car.daily_rate }} د.ك</div>
                    </div>
                    
                    <div class="payment-summary-row">
                        <div>عدد الأيام</div>
                        <div>{{ days }} يوم</div>
                    </div>
                    
                    <div class="payment-summary-row">
                        <div>المجموع الفرعي</div>
                        <div>{{ payment.car.daily_rate }} × {{ days }}</div>
                    </div>
                    
                    <div class="payment-summary-total">
                        <div>المجموع</div>
                        <div>{{ payment.amount }} د.ك</div>
                    </div>
                </div>
            </div>
        </div>
        
        <!-- قسم تفاصيل الدفع -->
        <div class="payment-details">
            <div class="payment-details-header">
                <div class="payment-details-title">
                    <i class="fas fa-credit-card"></i> تفاصيل الدفع
                </div>
            </div>
            
            <div class="payment-method">
                {% if payment.payment_method == 'visa' %}
                <i class="fab fa-cc-visa payment-method-icon" style="color: #1a1f71;"></i>
                <div class="payment-method-info">
                    <div class="payment-method-name">فيزا</div>
                    <div class="payment-method-details">{{ payment.masked_card_number|default:"**** **** **** ****" }}</div>
                </div>
                {% elif payment.payment_method == 'mastercard' %}
                <i class="fab fa-cc-mastercard payment-method-icon" style="color: #eb001b;"></i>
                <div class="payment-method-info">
                    <div class="payment-method-name">ماستركارد</div>
                    <div class="payment-method-details">{{ payment.masked_card_number|default:"**** **** **** ****" }}</div>
                </div>
                {% elif payment.payment_method == 'amex' %}
                <i class="fab fa-cc-amex payment-method-icon" style="color: #2e77bc;"></i>
                <div class="payment-method-info">
                    <div class="payment-method-name">أمريكان إكسبرس</div>
                    <div class="payment-method-details">{{ payment.masked_card_number|default:"**** **** **** ****" }}</div>
                </div>
                {% elif payment.payment_method == 'cash' %}
                <i class="fas fa-money-bill-wave payment-method-icon" style="color: var(--success);"></i>
                <div class="payment-method-info">
                    <div class="payment-method-name">دفع نقدي</div>
                    <div class="payment-method-details">تم الدفع نقداً</div>
                </div>
                {% elif payment.payment_method == 'bank_transfer' %}
                <i class="fas fa-university payment-method-icon" style="color: var(--primary-color);"></i>
                <div class="payment-method-info">
                    <div class="payment-method-name">تحويل بنكي</div>
                    <div class="payment-method-details">{{ payment.reference_number|default:"لا يوجد رقم مرجعي" }}</div>
                </div>
                {% else %}
                <i class="fas fa-credit-card payment-method-icon"></i>
                <div class="payment-method-info">
                    <div class="payment-method-name">{{ payment.payment_method }}</div>
                </div>
                {% endif %}
            </div>
            
            <div class="payment-grid">
                <div class="payment-field">
                    <div class="payment-field-label">تاريخ الدفع</div>
                    <div class="payment-field-value">{% if is_english %}{{ payment.date|date:"F d, Y" }}{% else %}{{ payment.date|date:"Y/m/d" }}{% endif %}</div>
                </div>
                
                <div class="payment-field">
                    <div class="payment-field-label">وقت الدفع</div>
                    <div class="payment-field-value">{{ payment.date|time:"h:i A" }}</div>
                </div>
                
                <div class="payment-field">
                    <div class="payment-field-label">رقم المرجع</div>
                    <div class="payment-field-value">{{ payment.reference_number|default:"—" }}</div>
                </div>
                
                <div class="payment-field">
                    <div class="payment-field-label">حالة الدفع</div>
                    <div class="payment-field-value">
                        {% if payment.status == 'paid' %}
                        <span style="color: var(--success)"><i class="fas fa-check-circle"></i> مدفوع بالكامل</span>
                        {% elif payment.status == 'pending' %}
                        <span style="color: var(--warning)"><i class="fas fa-clock"></i> في انتظار الدفع</span>
                        {% elif payment.status == 'refunded' %}
                        <span style="color: var(--info)"><i class="fas fa-undo-alt"></i> تم استرداد المبلغ</span>
                        {% else %}
                        <span style="color: var(--danger)"><i class="fas fa-ban"></i> ملغي</span>
                        {% endif %}
                    </div>
                </div>
            </div>
            
            {% if payment.notes %}
            <div style="margin-top: var(--space-6); padding: var(--space-4); background-color: var(--gray-50); border-radius: var(--radius); border: 1px solid var(--gray-200);">
                <div style="font-weight: 600; margin-bottom: var(--space-2);">ملاحظات الدفع:</div>
                <div style="white-space: pre-line; color: var(--gray-700);">{{ payment.notes }}</div>
            </div>
            {% endif %}
        </div>
        
        <!-- قسم معلومات العميل -->
        <div class="customer-section">
            <div class="customer-section-header">
                <div class="customer-section-title">
                    <i class="fas fa-user"></i> معلومات العميل
                </div>
            </div>
            
            <div class="customer-info">
                <div class="customer-info-box">
                    <div class="customer-info-box-title">معلومات الاتصال</div>
                    
                    <div class="customer-field">
                        <div class="customer-field-label">الاسم</div>
                        <div class="customer-field-value">{{ payment.user.first_name }} {{ payment.user.last_name }}</div>
                    </div>
                    
                    <div class="customer-field">
                        <div class="customer-field-label">البريد الإلكتروني</div>
                        <div class="customer-field-value">{{ payment.user.email }}</div>
                    </div>
                    
                    <div class="customer-field">
                        <div class="customer-field-label">رقم الهاتف</div>
                        <div class="customer-field-value">{{ payment.user.phone_number|default:"غير متوفر" }}</div>
                    </div>
                </div>
                
                <div class="customer-info-box">
                    <div class="customer-info-box-title">معلومات الحساب</div>
                    
                    <div class="customer-field">
                        <div class="customer-field-label">اسم المستخدم</div>
                        <div class="customer-field-value">{{ payment.user.username }}</div>
                    </div>
                    
                    <div class="customer-field">
                        <div class="customer-field-label">تاريخ التسجيل</div>
                        <div class="customer-field-value">{% if is_english %}{{ payment.user.date_joined|date:"M d, Y" }}{% else %}{{ payment.user.date_joined|date:"Y/m/d" }}{% endif %}</div>
                    </div>
                    
                    <div class="customer-field">
                        <div class="customer-field-label">عدد الحجوزات</div>
                        <div class="customer-field-value">{{ payment.user.reservation_set.count }}</div>
                    </div>
                </div>
            </div>
        </div>
        
        <!-- قسم أزرار الإجراءات -->
        <div class="actions-section">
            <div class="actions-title">الإجراءات المتاحة</div>
            
            <div class="action-buttons">
                <a href="{% url 'admin_payments' %}" class="action-button action-button-secondary">
                    <i class="fas fa-arrow-right"></i> العودة للسجل
                </a>
                
                <a href="{% url 'print_receipt' payment_id=payment.id %}" class="action-button action-button-primary">
                    <i class="fas fa-print"></i> طباعة الإيصال
                </a>
                
                <a href="{% url 'download_receipt' payment_id=payment.id %}" class="action-button action-button-secondary">
                    <i class="fas fa-file-pdf"></i> تحميل PDF
                </a>
                
                {% if payment.status == 'pending' %}
                <a href="{% url 'mark_as_paid' payment_id=payment.id %}" class="action-button action-button-success">
                    <i class="fas fa-check-circle"></i> تأكيد الدفع
                </a>
                
                <a href="{% url 'cancel_payment' payment_id=payment.id %}" 
                   class="action-button action-button-danger"
                   onclick="return confirm('هل أنت متأكد من حذف هذه الدفعة؟\\n\\nسيتم حذف الدفعة نهائياً من قاعدة البيانات ولن تتمكن من استعادتها لاحقاً.\\n\\nاضغط موافق للتأكيد.');">
                    <i class="fas fa-trash-alt"></i> حذف نهائي
                </a>
                {% endif %}
                
                {% if payment.status == 'paid' %}
                <a href="{% url 'process_refund' payment_id=payment.id %}" class="action-button action-button-warning">
                    <i class="fas fa-undo"></i> رد المبلغ
                </a>
                {% endif %}
            </div>
        </div>
        
        <div class="invoice-footer">
            &copy; {{ "now"|date:"Y" }} نظام تأجير السيارات العالمية | جميع الحقوق محفوظة
        </div>
    </div>
</div>
{% endblock %}"""
    
    # حفظ قالب HTML
    template_path = 'templates/admin/payment_detail_invoice.html'
    with open(template_path, 'w', encoding='utf-8') as f:
        f.write(template_content)
        
    print(f"تم إنشاء قالب HTML في: {template_path}")
    return template_path

def update_admin_views():
    """تحديث admin_views.py لاستخدام القالب الجديد"""
    from rental.admin_views import payment_details
    import inspect
    
    # الحصول على كود دالة تفاصيل الدفع
    source_code = inspect.getsource(payment_details)
    
    # تعديل اسم القالب
    modified_code = source_code.replace(
        "template_name = 'admin/payment_detail_ecommerce.html'",
        "template_name = 'admin/payment_detail_invoice.html'"
    )
    
    # تغيير قيمة cache_buster
    import time
    timestamp = int(time.time())
    modified_code = modified_code.replace(
        "context['cache_buster'] = '1744904985'",
        f"context['cache_buster'] = '{timestamp}'"
    )
    
    # حفظ التغييرات في ملف منفصل للتحقق منها
    code_path = 'update_payment_detail_view.py'
    with open(code_path, 'w', encoding='utf-8') as f:
        f.write(f"""\"\"\"
تحديث دالة تفاصيل الدفع في ملف admin_views.py
\"\"\"

# قم بتعديل ملف admin_views.py بحيث يستبدل دالة payment_details بالدالة التالية:

{modified_code}
""")
    
    # طباعة تعليمات للمستخدم حول كيفية تطبيق التعديلات
    print(f"تم إنشاء ملف التحديث في: {code_path}")
    print("\nيرجى تنفيذ الأمر التالي لتحديث ملف admin_views.py:")
    print(f"\n1. افتح ملف admin_views.py وابحث عن دالة payment_details")
    print(f"2. قم بتغيير اسم القالب إلى: 'admin/payment_detail_invoice.html'")
    print(f"3. قم بتحديث قيمة cache_buster إلى: '{timestamp}'")
    
    return code_path
    
def main():
    """تنفيذ التعديلات"""
    print("جاري تحسين صفحة تفاصيل الدفع بتصميم احترافي...\n")
    
    # إنشاء ملف CSS
    css_path = create_css_file()
    
    # إنشاء قالب HTML
    template_path = create_html_template()
    
    # تحديث admin_views.py
    code_path = update_admin_views()
    
    print("\nتم الانتهاء من إنشاء الملفات المطلوبة بنجاح!")
    print("\nلتطبيق التغييرات، قم باتباع الخطوات التالية:")
    print(f"1. تأكد من وجود الملفات التالية:")
    print(f"   - {css_path}")
    print(f"   - {template_path}")
    print(f"2. قم بتحديث ملف admin_views.py كما هو موضح في: {code_path}")
    print(f"3. أعد تشغيل التطبيق")

if __name__ == "__main__":
    main()