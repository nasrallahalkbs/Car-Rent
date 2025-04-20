"""
استعادة التصميم القديم للوحة إدارة الحجوزات

هذا السكريبت يقوم باستعادة التصميم القديم للوحة إدارة الحجوزات في لوحة التحكم
مع الحفاظ على قائمة لوحة التحكم كما هي دون تغيير.
"""

import os
import re
import datetime
from pathlib import Path

def ensure_old_css_files():
    """التأكد من وجود ملفات CSS القديمة المطلوبة"""
    
    # إنشاء ملف old-table.css إذا لم يكن موجودًا
    old_table_css_path = 'static/css/old-table.css'
    if not os.path.exists(old_table_css_path):
        css_content = """/* أنماط التصميم القديم للجدول */
.reservation-table {
  width: 100%;
  border-collapse: collapse;
  background-color: #f5f7fa;
  border-radius: 8px;
  overflow: hidden;
}

.reservation-table thead {
  background-color: white;
  border-bottom: 1px solid #e2e8f0;
}

.reservation-table th {
  padding: 15px;
  text-align: center;
  font-weight: 600;
  color: #64748b;
  font-size: 0.9rem;
}

.reservation-table tr {
  margin-bottom: 10px; 
  border-bottom: 15px solid white;
  background-color: #f8fafc;
}

.reservation-table td {
  padding: 15px 10px;
  text-align: center;
  vertical-align: middle;
}

/* إجراءات */
.action-btn {
  padding: 8px 15px;
  border-radius: 30px;
  display: inline-block;
  margin: 3px;
  font-weight: 500;
}

.btn-confirm {
  background-color: #0d9488;
  color: white;
  text-decoration: none;
}

.btn-pending {
  background-color: #6b7280;
  color: white;
  text-decoration: none;
}

/* السعر */
.price-display {
  color: #3b82f6;
  font-weight: bold;
  font-size: 1.15rem;
  direction: ltr;
}

/* المدة */
.duration-display {
  display: flex;
  align-items: center;
  justify-content: center;
}

.duration-day {
  background-color: #e6f2ff;
  color: #3b82f6;
  font-weight: 600;
  padding: 2px 10px;
  border-radius: 15px;
  font-size: 0.9rem;
  margin: 0 5px;
}

/* معلومات السيارة */
.car-info {
  display: flex;
  align-items: center;
  justify-content: center;
}

.car-info img {
  width: 70px;
  height: 45px;
  object-fit: cover;
  border-radius: 4px;
  margin-right: 10px;
}

[dir="rtl"] .car-info img {
  margin-right: 0;
  margin-left: 10px;
}

.car-details {
  text-align: left;
}

[dir="rtl"] .car-details {
  text-align: right;
}

.car-make-model {
  font-weight: 600;
  color: #334155;
  margin-bottom: 3px;
}

.car-year {
  font-size: 0.8rem;
  color: #64748b;
}

/* معرف الحجز */
.reservation-id {
  font-weight: 700;
  color: #3b82f6;
  text-decoration: none;
  font-size: 1.1rem;
}

/* بطاقات الإحصائيات */
.stats-cards {
  display: flex;
  flex-wrap: wrap;
  margin-bottom: 20px;
  gap: 15px;
}

.stat-card {
  padding: 20px;
  border-radius: 10px;
  flex: 1;
  min-width: 200px;
  background-color: white;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);
  display: flex;
  align-items: center;
  gap: 15px;
}

.stat-icon {
  width: 50px;
  height: 50px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.stat-icon i {
  font-size: 1.4rem;
  color: white;
}

.stat-label {
  color: #64748b;
  font-size: 0.9rem;
  margin-bottom: 5px;
}

.stat-value {
  font-size: 1.5rem;
  font-weight: 700;
  color: #334155;
}

.pending-icon {
  background-color: #eab308;
}

.confirmed-icon {
  background-color: #22c55e;
}

.cancelled-icon {
  background-color: #ef4444;
}

.completed-icon {
  background-color: #3b82f6;
}

/* قسم التصفية والبحث */
.filter-section {
  background-color: white;
  padding: 20px;
  border-radius: 10px;
  margin-bottom: 20px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);
}

.filter-form {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 15px;
}

.filter-group {
  margin-bottom: 15px;
}

.filter-label {
  display: block;
  margin-bottom: 5px;
  font-weight: 500;
  color: #475569;
}

.filter-select,
.filter-input {
  width: 100%;
  padding: 10px;
  border: 1px solid #e2e8f0;
  border-radius: 6px;
  background-color: #f8fafc;
}

.filter-actions {
  display: flex;
  gap: 10px;
  align-items: flex-end;
}

.filter-btn {
  padding: 10px 15px;
  border-radius: 6px;
  border: none;
  font-weight: 500;
  cursor: pointer;
}

.search-btn {
  background-color: #3b82f6;
  color: white;
}

.reset-btn {
  background-color: #e2e8f0;
  color: #475569;
}

/* أزرار إضافية للعمليات المجمعة */
.bulk-actions {
  display: flex;
  gap: 10px;
  margin-bottom: 20px;
}

.action-btn-bulk {
  padding: 10px 15px;
  border-radius: 6px;
  background-color: #f8fafc;
  border: 1px solid #e2e8f0;
  color: #475569;
  font-weight: 500;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 5px;
}

.action-btn-bulk i {
  font-size: 0.9rem;
}

.print-btn {
  background-color: #3b82f6;
  color: white;
  border: none;
}

/* تصميم متجاوب للشاشات الصغيرة */
@media (max-width: 767px) {
  .reservation-table thead {
    display: none;
  }
  
  .reservation-table, .reservation-table tbody, .reservation-table tr, .reservation-table td {
    display: block;
    width: 100%;
  }
  
  .reservation-table tr {
    margin-bottom: 20px;
    border-radius: 8px;
    overflow: hidden;
    box-shadow: 0 2px 10px rgba(0,0,0,0.05);
  }
  
  .reservation-table td {
    text-align: right;
    padding: 10px;
    position: relative;
    padding-left: 50%;
    border-bottom: 1px solid #e2e8f0;
  }
  
  .reservation-table td:before {
    position: absolute;
    left: 10px;
    width: 45%;
    padding-right: 10px;
    white-space: nowrap;
    font-weight: 600;
    content: attr(data-label);
    text-align: left;
  }
  
  [dir="rtl"] .reservation-table td {
    text-align: left;
    padding-left: 10px;
    padding-right: 50%;
  }
  
  [dir="rtl"] .reservation-table td:before {
    left: auto;
    right: 10px;
    text-align: right;
    padding-right: 0;
    padding-left: 10px;
  }
  
  .car-info {
    justify-content: flex-end;
  }
  
  [dir="rtl"] .car-info {
    justify-content: flex-start;
  }
  
  .filter-form {
    grid-template-columns: 1fr;
  }
}
"""
        os.makedirs(os.path.dirname(old_table_css_path), exist_ok=True)
        with open(old_table_css_path, 'w', encoding='utf-8') as f:
            f.write(css_content)
        print(f"تم إنشاء ملف CSS الجديد: {old_table_css_path}")

def restore_reservations_template():
    """استعادة التصميم القديم لصفحة إدارة الحجوزات"""
    
    template_path = 'templates/admin/reservations_django.html'
    
    # التحقق من وجود المجلد
    os.makedirs(os.path.dirname(template_path), exist_ok=True)
    
    # إنشاء قالب الحجوزات بالتصميم القديم
    template_content = """{% extends 'admin/admin_layout.html' %}
{% load static %}
{% load i18n %}

{% block extra_head %}
<link rel="stylesheet" href="{% static 'css/old-table.css' %}">
<style>
    /* تخصيص إضافي للصفحة */
    .dashboard-title {
        margin-bottom: 25px;
    }
    .timestamp {
        color: #64748b;
        font-size: 0.8rem;
        margin-top: 10px;
    }
    .table-container {
        background-color: white;
        border-radius: 10px;
        padding: 20px;
        overflow-x: auto;
        box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);
    }
    .status-badge {
        padding: 5px 10px;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: 600;
        display: inline-block;
    }
    .status-confirmed {
        background-color: #dcfce7;
        color: #16a34a;
    }
    .status-pending {
        background-color: #fef9c3;
        color: #ca8a04;
    }
    .status-cancelled {
        background-color: #fee2e2;
        color: #dc2626;
    }
    .status-completed {
        background-color: #dbeafe;
        color: #2563eb;
    }
    .pagination-container {
        margin-top: 20px;
        display: flex;
        justify-content: center;
    }
    .page-link {
        margin: 0 5px;
        padding: 8px 15px;
        border-radius: 6px;
        background-color: #f8fafc;
        color: #475569;
        text-decoration: none;
    }
    .page-link.active {
        background-color: #3b82f6;
        color: white;
    }
    .empty-state {
        text-align: center;
        padding: 50px 20px;
    }
    .empty-state i {
        font-size: 3rem;
        color: #cbd5e1;
        margin-bottom: 20px;
    }
    .empty-state-message {
        font-size: 1.2rem;
        color: #64748b;
        margin-bottom: 20px;
    }
</style>
{% endblock %}

{% block content %}
<div class="container-fluid py-4">
    <div class="d-flex justify-content-between align-items-center dashboard-title">
        <h2>{% trans "Reservations Management" %}</h2>
        <div class="timestamp">
            {% now "Y-m-d H:i" as current_time %}
            {% if is_english %}
                Last updated: {{ current_time }}
            {% else %}
                آخر تحديث: {{ current_time }}
            {% endif %}
        </div>
    </div>
    
    <!-- بطاقات الإحصائيات -->
    <div class="stats-cards">
        <div class="stat-card">
            <div class="stat-icon pending-icon">
                <i class="fas fa-hourglass-half"></i>
            </div>
            <div>
                <div class="stat-label">{% trans "Pending" %}</div>
                <div class="stat-value">{{ pending_count }}</div>
            </div>
        </div>
        <div class="stat-card">
            <div class="stat-icon confirmed-icon">
                <i class="fas fa-check-circle"></i>
            </div>
            <div>
                <div class="stat-label">{% trans "Confirmed" %}</div>
                <div class="stat-value">{{ confirmed_count }}</div>
            </div>
        </div>
        <div class="stat-card">
            <div class="stat-icon cancelled-icon">
                <i class="fas fa-times-circle"></i>
            </div>
            <div>
                <div class="stat-label">{% trans "Cancelled" %}</div>
                <div class="stat-value">{{ cancelled_count }}</div>
            </div>
        </div>
        <div class="stat-card">
            <div class="stat-icon completed-icon">
                <i class="fas fa-flag-checkered"></i>
            </div>
            <div>
                <div class="stat-label">{% trans "Completed" %}</div>
                <div class="stat-value">{{ completed_count }}</div>
            </div>
        </div>
    </div>
    
    <!-- قسم التصفية والبحث -->
    <div class="filter-section">
        <form method="get" class="filter-form">
            <div class="filter-group">
                <label class="filter-label">{% trans "Status" %}</label>
                <select name="status" class="filter-select">
                    <option value="">{% trans "All" %}</option>
                    <option value="pending" {% if status == 'pending' %}selected{% endif %}>{% trans "Pending" %}</option>
                    <option value="confirmed" {% if status == 'confirmed' %}selected{% endif %}>{% trans "Confirmed" %}</option>
                    <option value="cancelled" {% if status == 'cancelled' %}selected{% endif %}>{% trans "Cancelled" %}</option>
                    <option value="completed" {% if status == 'completed' %}selected{% endif %}>{% trans "Completed" %}</option>
                </select>
            </div>
            <div class="filter-group">
                <label class="filter-label">{% trans "Payment Status" %}</label>
                <select name="payment_status" class="filter-select">
                    <option value="">{% trans "All" %}</option>
                    <option value="pending" {% if payment_status == 'pending' %}selected{% endif %}>{% trans "Pending" %}</option>
                    <option value="paid" {% if payment_status == 'paid' %}selected{% endif %}>{% trans "Paid" %}</option>
                    <option value="refunded" {% if payment_status == 'refunded' %}selected{% endif %}>{% trans "Refunded" %}</option>
                </select>
            </div>
            <div class="filter-group">
                <label class="filter-label">{% trans "Start Date" %}</label>
                <input type="date" name="start_date" value="{{ start_date|date:'Y-m-d' }}" class="filter-input">
            </div>
            <div class="filter-group">
                <label class="filter-label">{% trans "End Date" %}</label>
                <input type="date" name="end_date" value="{{ end_date|date:'Y-m-d' }}" class="filter-input">
            </div>
            <div class="filter-group">
                <label class="filter-label">{% trans "Search" %}</label>
                <input type="text" name="search" value="{{ search }}" placeholder="{% trans 'Search ID, Customer...' %}" class="filter-input">
            </div>
            <div class="filter-actions">
                <button type="submit" class="filter-btn search-btn">
                    <i class="fas fa-search me-1"></i> {% trans "Search" %}
                </button>
                <a href="{% url 'admin_reservations' %}" class="filter-btn reset-btn">
                    <i class="fas fa-redo me-1"></i> {% trans "Reset" %}
                </a>
            </div>
        </form>
    </div>
    
    <!-- أزرار العمليات المجمعة -->
    <div class="bulk-actions">
        <button type="button" class="action-btn-bulk print-btn" onclick="printTable()">
            <i class="fas fa-print"></i> {% trans "Print" %}
        </button>
        <button type="button" class="action-btn-bulk">
            <i class="fas fa-file-export"></i> {% trans "Export" %}
        </button>
    </div>
    
    <!-- جدول الحجوزات -->
    <div class="table-container">
        {% if reservations %}
            <table class="reservation-table">
                <thead>
                    <tr>
                        <th>{% trans "Reservation ID" %}</th>
                        <th>{% trans "Customer" %}</th>
                        <th>{% trans "Car" %}</th>
                        <th>{% trans "Pickup - Return" %}</th>
                        <th>{% trans "Duration" %}</th>
                        <th>{% trans "Total" %}</th>
                        <th>{% trans "Status" %}</th>
                        <th>{% trans "Payment Status" %}</th>
                        <th>{% trans "Actions" %}</th>
                    </tr>
                </thead>
                <tbody>
                    {% for reservation in reservations %}
                    <tr>
                        <td data-label="{% trans 'Reservation ID' %}">
                            <a href="{% url 'admin_reservation_detail' reservation.id %}" class="reservation-id">
                                #{{ reservation.reservation_number }}
                            </a>
                        </td>
                        <td data-label="{% trans 'Customer' %}">
                            <div>{{ reservation.user.first_name }} {{ reservation.user.last_name }}</div>
                            <small>{{ reservation.user.email }}</small>
                        </td>
                        <td data-label="{% trans 'Car' %}">
                            <div class="car-info">
                                <img src="{{ reservation.car.image.url }}" alt="{{ reservation.car.make }} {{ reservation.car.model }}">
                                <div class="car-details">
                                    <div class="car-make-model">{{ reservation.car.make }} {{ reservation.car.model }}</div>
                                    <div class="car-year">{{ reservation.car.year }}</div>
                                </div>
                            </div>
                        </td>
                        <td data-label="{% trans 'Pickup - Return' %}">
                            <div>
                                {% if is_english %}
                                {{ reservation.pickup_date|date:"m/d/Y" }}
                                {% else %}
                                {{ reservation.pickup_date|date:"d/m/Y" }}
                                {% endif %}
                            </div>
                            <div class="mt-1">
                                {% if is_english %}
                                {{ reservation.return_date|date:"m/d/Y" }}
                                {% else %}
                                {{ reservation.return_date|date:"d/m/Y" }}
                                {% endif %}
                            </div>
                        </td>
                        <td data-label="{% trans 'Duration' %}">
                            <div class="duration-display">
                                <span class="duration-day">{{ reservation.days }} {% trans "days" %}</span>
                            </div>
                        </td>
                        <td data-label="{% trans 'Total' %}">
                            <div class="price-display">
                                {{ reservation.total_price }} {% trans "SAR" %}
                            </div>
                        </td>
                        <td data-label="{% trans 'Status' %}">
                            <span class="status-badge status-{{ reservation.status }}">
                                {% if reservation.status == 'pending' %}
                                    {% trans "Pending" %}
                                {% elif reservation.status == 'confirmed' %}
                                    {% trans "Confirmed" %}
                                {% elif reservation.status == 'cancelled' %}
                                    {% trans "Cancelled" %}
                                {% elif reservation.status == 'completed' %}
                                    {% trans "Completed" %}
                                {% endif %}
                            </span>
                        </td>
                        <td data-label="{% trans 'Payment Status' %}">
                            <span class="status-badge {% if reservation.payment_status == 'paid' %}status-confirmed{% elif reservation.payment_status == 'refunded' %}status-cancelled{% else %}status-pending{% endif %}">
                                {% if reservation.payment_status == 'pending' %}
                                    {% trans "Pending" %}
                                {% elif reservation.payment_status == 'paid' %}
                                    {% trans "Paid" %}
                                {% elif reservation.payment_status == 'refunded' %}
                                    {% trans "Refunded" %}
                                {% endif %}
                            </span>
                        </td>
                        <td data-label="{% trans 'Actions' %}">
                            <a href="{% url 'admin_reservation_detail' reservation.id %}" class="action-btn btn-pending">
                                <i class="fas fa-eye"></i> {% trans "View" %}
                            </a>
                            
                            {% if reservation.status == 'pending' %}
                            <a href="{% url 'update_reservation_status' reservation.id 'confirmed' %}" class="action-btn btn-confirm confirm-button">
                                <i class="fas fa-check"></i> {% trans "Confirm" %}
                            </a>
                            {% endif %}
                            
                            {% if reservation.status == 'pending' or reservation.status == 'confirmed' %}
                            <a href="{% url 'update_reservation_status' reservation.id 'cancelled' %}" class="action-btn btn-danger cancel-button">
                                <i class="fas fa-times"></i> {% trans "Cancel" %}
                            </a>
                            {% endif %}
                            
                            {% if reservation.status == 'confirmed' %}
                            <a href="{% url 'update_reservation_status' reservation.id 'completed' %}" class="action-btn btn-primary complete-button">
                                <i class="fas fa-flag-checkered"></i> {% trans "Complete" %}
                            </a>
                            {% endif %}
                        </td>
                    </tr>
                    {% endfor %}
                </tbody>
            </table>
        {% else %}
            <div class="empty-state">
                <i class="far fa-calendar-times"></i>
                <div class="empty-state-message">{% trans "No reservations found with the specified criteria." %}</div>
                <a href="{% url 'admin_reservations' %}" class="btn btn-primary">
                    <i class="fas fa-sync me-1"></i> {% trans "View All Reservations" %}
                </a>
            </div>
        {% endif %}
    </div>
    
    <!-- ترقيم الصفحات -->
    {% if reservations.has_other_pages %}
    <div class="pagination-container">
        {% if reservations.has_previous %}
            <a href="?page={{ reservations.previous_page_number }}{% for key, value in request.GET.items %}{% if key != 'page' %}&{{ key }}={{ value }}{% endif %}{% endfor %}" class="page-link">
                <i class="fas fa-chevron-left"></i>
            </a>
        {% endif %}
        
        {% for num in reservations.paginator.page_range %}
            {% if num == reservations.number %}
                <span class="page-link active">{{ num }}</span>
            {% elif num > reservations.number|add:'-3' and num < reservations.number|add:'3' %}
                <a href="?page={{ num }}{% for key, value in request.GET.items %}{% if key != 'page' %}&{{ key }}={{ value }}{% endif %}{% endfor %}" class="page-link">{{ num }}</a>
            {% endif %}
        {% endfor %}
        
        {% if reservations.has_next %}
            <a href="?page={{ reservations.next_page_number }}{% for key, value in request.GET.items %}{% if key != 'page' %}&{{ key }}={{ value }}{% endif %}{% endfor %}" class="page-link">
                <i class="fas fa-chevron-right"></i>
            </a>
        {% endif %}
    </div>
    {% endif %}
</div>
{% endblock %}

{% block scripts %}
<script>
    document.addEventListener('DOMContentLoaded', function() {
        // زر التأكيد
        const confirmButtons = document.querySelectorAll('a[href*="update_reservation_status"][href*="confirmed"]');
        confirmButtons.forEach(button => {
            button.addEventListener('click', function(e) {
                e.preventDefault();
                if (confirm('هل أنت متأكد من رغبتك في تأكيد هذا الحجز؟')) {
                    const reservation_id = this.href.split('/').slice(-3)[0];
                    window.location.href = `/ar/dashboard/reservations/${reservation_id}/confirmed/`;
                }
            });
        });
        
        // زر الإلغاء
        const cancelButtons = document.querySelectorAll('a[href*="update_reservation_status"][href*="cancelled"]');
        cancelButtons.forEach(button => {
            button.addEventListener('click', function(e) {
                e.preventDefault();
                if (confirm('هل أنت متأكد من رغبتك في إلغاء هذا الحجز؟')) {
                    const reservation_id = this.href.split('/').slice(-3)[0];
                    window.location.href = `/ar/dashboard/reservations/${reservation_id}/cancelled/`;
                }
            });
        });

        // زر الإكمال
        const completeButtons = document.querySelectorAll('a[href*="update_reservation_status"][href*="completed"]');
        completeButtons.forEach(button => {
            button.addEventListener('click', function(e) {
                e.preventDefault();
                const reservation_id = this.href.split('/').slice(-3)[0];
                window.location.href = `/ar/dashboard/reservations/${reservation_id}/completed/`;
            });
        });
    });

    // دالة لطباعة جدول الحجوزات
    function printTable() {
        var printContents = document.querySelector('.table-container').innerHTML;
        var originalContents = document.body.innerHTML;
        
        // تخصيص صفحة الطباعة
        var printWindow = window.open('', '', 'height=600,width=800');
        printWindow.document.write('<html><head><title>طباعة الحجوزات</title>');
        printWindow.document.write('<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css">');
        printWindow.document.write('<style>body { font-family: Arial; padding: 20px; direction: rtl; } .table { width: 100%; } .table th { background-color: #f8f9fa; } @media print { .print-header { display: block!important; text-align: center; margin-bottom: 20px; } }</style>');
        printWindow.document.write('</head><body>');
        
        // إضافة ترويسة الطباعة
        printWindow.document.write('<div class="print-header">');
        printWindow.document.write('<h2>إدارة الحجوزات</h2>');
        printWindow.document.write('<p>تاريخ الطباعة: ' + new Date().toLocaleDateString('ar-SA') + '</p>');
        printWindow.document.write('</div>');
        
        // محتوى الجدول
        printWindow.document.write(printContents);
        
        printWindow.document.write('</body></html>');
        printWindow.document.close();
        printWindow.focus();
        
        // طباعة المستند بعد تحميل الصفحة
        printWindow.onload = function() {
            printWindow.print();
            printWindow.close();
        };
    }
</script>
{% endblock %}
"""
    
    with open(template_path, 'w', encoding='utf-8') as f:
        f.write(template_content)
    print(f"تم إنشاء ملف القالب الجديد: {template_path}")

def update_admin_view():
    """تحديث ملف admin_views.py لعرض الإحصائيات في الصفحة"""
    
    admin_views_file = 'rental/admin_views.py'
    
    # التحقق من وجود الملف
    if not os.path.exists(admin_views_file):
        print(f"لم يتم العثور على ملف {admin_views_file}")
        return
    
    with open(admin_views_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # البحث عن دالة عرض الحجوزات
    admin_reservations_pattern = r'def admin_reservations\(request\):(.*?)def'
    match = re.search(admin_reservations_pattern, content, re.DOTALL)
    
    if not match:
        print("لم يتم العثور على دالة admin_reservations في الملف")
        return
    
    # تحديث دالة admin_reservations لإضافة الإحصائيات
    updated_view = """def admin_reservations(request):
    # التحقق من صلاحيات المستخدم
    if not is_admin(request):
        return redirect('home')
    
    # الحصول على معلمات التصفية
    status = request.GET.get('status', '')
    payment_status = request.GET.get('payment_status', '')
    start_date_str = request.GET.get('start_date', '')
    end_date_str = request.GET.get('end_date', '')
    search = request.GET.get('search', '')
    
    # تصفية الحجوزات
    reservations = Reservation.objects.all().order_by('-created_at')
    
    # تطبيق التصفية حسب الحالة
    if status:
        reservations = reservations.filter(status=status)
    
    # تطبيق التصفية حسب حالة الدفع
    if payment_status:
        reservations = reservations.filter(payment_status=payment_status)
    
    # تطبيق التصفية حسب التاريخ
    if start_date_str:
        try:
            start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
            reservations = reservations.filter(pickup_date__gte=start_date)
        except ValueError:
            pass
    
    if end_date_str:
        try:
            end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
            reservations = reservations.filter(return_date__lte=end_date)
        except ValueError:
            pass
    
    # تطبيق البحث
    if search:
        reservations = reservations.filter(
            Q(reservation_number__icontains=search) |
            Q(user__first_name__icontains=search) |
            Q(user__last_name__icontains=search) |
            Q(user__email__icontains=search) |
            Q(car__make__icontains=search) |
            Q(car__model__icontains=search)
        )
    
    # إحصائيات عدد الحجوزات حسب الحالة
    pending_count = Reservation.objects.filter(status='pending').count()
    confirmed_count = Reservation.objects.filter(status='confirmed').count()
    cancelled_count = Reservation.objects.filter(status='cancelled').count()
    completed_count = Reservation.objects.filter(status='completed').count()
    
    # ترقيم الصفحات
    paginator = Paginator(reservations, 10)  # 10 حجوزات في كل صفحة
    page_number = request.GET.get('page', 1)
    
    try:
        reservations = paginator.page(page_number)
    except (PageNotAnInteger, EmptyPage):
        reservations = paginator.page(1)
    
    # تحديد لغة المستخدم
    current_language = get_language()
    is_english = current_language == 'en'
    
    context = {
        'reservations': reservations,
        'pending_count': pending_count,
        'confirmed_count': confirmed_count,
        'cancelled_count': cancelled_count,
        'completed_count': completed_count,
        'status': status,
        'payment_status': payment_status,
        'start_date': start_date_str,
        'end_date': end_date_str,
        'search': search,
        'is_english': is_english,
        'is_rtl': current_language == 'ar'
    }
    
    return render(request, 'admin/reservations_django.html', context)

def"""
    
    # استبدال الدالة القديمة بالدالة الجديدة
    updated_content = content.replace(match.group(0), updated_view)
    
    # التأكد من تضمين الاستيرادات الضرورية
    import_statements = [
        "from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger",
        "from django.db.models import Q",
        "from datetime import datetime",
    ]
    
    for import_statement in import_statements:
        if import_statement not in content:
            # إضافة الاستيراد بعد الاستيرادات الموجودة
            import_section_end = content.find("\n\n", content.find("import"))
            updated_content = updated_content[:import_section_end] + "\n" + import_statement + updated_content[import_section_end:]
    
    # حفظ التغييرات
    with open(admin_views_file, 'w', encoding='utf-8') as f:
        f.write(updated_content)
    
    print(f"تم تحديث ملف {admin_views_file}")

def ensure_css_link():
    """التأكد من وجود ربط لملف CSS في قالب admin_layout.html"""
    
    admin_layout_file = 'templates/admin/admin_layout.html'
    
    # التحقق من وجود الملف
    if not os.path.exists(admin_layout_file):
        print(f"لم يتم العثور على ملف {admin_layout_file}")
        return
    
    with open(admin_layout_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # البحث عن قسم عناصر head إضافية
    extra_head_pattern = r'{%\s*block\s+extra_head\s*%}(.*?){%\s*endblock\s*%}'
    
    if not re.search(extra_head_pattern, content, re.DOTALL):
        # إضافة قسم extra_head إذا لم يكن موجودًا
        head_end = content.find('</head>')
        if head_end != -1:
            updated_content = content[:head_end] + '\n{% block extra_head %}{% endblock %}\n' + content[head_end:]
            
            with open(admin_layout_file, 'w', encoding='utf-8') as f:
                f.write(updated_content)
            
            print(f"تم إضافة قسم extra_head إلى ملف {admin_layout_file}")

def check_template_language():
    """التأكد من وجود دعم للغة في القوالب"""
    
    # التحقق من وجود ملف قاموس الترجمة
    locale_dir = 'locale/ar/LC_MESSAGES'
    django_po = os.path.join(locale_dir, 'django.po')
    
    if not os.path.exists(django_po):
        print(f"تنبيه: ملف الترجمة {django_po} غير موجود. قد تظهر بعض النصوص باللغة الإنجليزية فقط.")

def create_force_update_script():
    """إنشاء سكريبت سريع لتحديث الصفحة بشكل قسري بإضافة طابع زمني للملفات"""
    
    script_path = 'force_update_templates.py'
    script_content = """
import os
import time

def force_update_templates():
    '''
    Add timestamp comment to template files to force browser reload
    '''
    templates_dir = 'templates/admin'
    timestamp = int(time.time())
    
    for root, dirs, files in os.walk(templates_dir):
        for file in files:
            if file.endswith('.html'):
                file_path = os.path.join(root, file)
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Remove previous cache buster comments
                content = content.replace('<!-- CACHE_BUSTER -->', '')
                
                # Add new timestamp comment
                content = f'<!-- CACHE_BUSTER {timestamp} -->' + content
                
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                
                print(f"Updated {file_path}")
    
    # Update CSS files too
    css_dir = 'static/css'
    if os.path.exists(css_dir):
        for file in os.listdir(css_dir):
            if file.endswith('.css'):
                file_path = os.path.join(css_dir, file)
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Remove previous cache buster comments
                content = content.replace('/* CACHE_BUSTER */', '')
                
                # Add new timestamp comment
                content = f'/* CACHE_BUSTER {timestamp} */\\n' + content
                
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                
                print(f"Updated {file_path}")

if __name__ == "__main__":
    force_update_templates()
    print("All files updated successfully. Please restart the server and reload the page.")
"""
    
    with open(script_path, 'w', encoding='utf-8') as f:
        f.write(script_content)
    
    print(f"تم إنشاء سكريبت تحديث قسري: {script_path}")

def main():
    """تنفيذ الوظائف الرئيسية للسكريبت"""
    
    print("بدء استعادة التصميم القديم للوحة إدارة الحجوزات...")
    
    # التأكد من وجود ملفات CSS الضرورية
    ensure_old_css_files()
    
    # استعادة قالب الحجوزات
    restore_reservations_template()
    
    # تحديث ملف admin_views.py
    update_admin_view()
    
    # التأكد من وجود قسم extra_head في قالب admin_layout.html
    ensure_css_link()
    
    # التحقق من دعم اللغة
    check_template_language()
    
    # إنشاء سكريبت تحديث قسري
    create_force_update_script()
    
    print("\nتم استعادة التصميم القديم للوحة إدارة الحجوزات بنجاح!")
    print("\nملاحظات هامة:")
    print("1. تأكد من تسجيل الدخول كمستخدم مسؤول لمشاهدة لوحة إدارة الحجوزات")
    print("2. إذا لم تظهر التغييرات، قم بتنفيذ السكريبت 'python force_update_templates.py' وأعد تشغيل الخادم")
    print("3. قد تحتاج إلى حذف ذاكرة التخزين المؤقت في المتصفح باستخدام Ctrl+F5")

if __name__ == "__main__":
    main()