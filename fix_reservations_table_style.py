"""
تعديل تنسيق جدول الحجوزات ليطابق التصميم المطلوب
"""

import os
import re
import time
from datetime import datetime

def update_template():
    """تحديث قالب صفحة الحجوزات"""
    template_path = "templates/admin/reservations_django.html"
    
    # التحقق من وجود القالب
    if not os.path.exists(template_path):
        print("❌ ملف القالب غير موجود!")
        return False
    
    with open(template_path, "r", encoding="utf-8") as file:
        content = file.read()
    
    # إضافة timestamp جديد للتأكد من تحديث الكاش في المتصفح
    timestamp = int(time.time())
    if "CACHE_BUSTER" in content:
        content = re.sub(r"CACHE_BUSTER \d+", f"CACHE_BUSTER {timestamp}", content, 1)
    else:
        content = f"<!-- CACHE_BUSTER {timestamp} -->\n" + content
    
    # كتابة المحتوى المحدث
    with open(template_path, "w", encoding="utf-8") as file:
        file.write(content)
    
    print(f"✅ تم تحديث قالب الحجوزات مع معرّف كاش جديد: {timestamp}")
    return True

def update_css():
    """تحديث ملف CSS الخاص بجدول الحجوزات"""
    css_path = "static/css/old-table.css"
    
    # التحقق من وجود ملف CSS
    if not os.path.exists(css_path):
        print("❌ ملف CSS غير موجود!")
        return False
    
    with open(css_path, "r", encoding="utf-8") as file:
        content = file.read()
    
    # إضافة timestamp جديد للتأكد من تحديث الكاش في المتصفح
    timestamp = int(time.time())
    if "CACHE_BUSTER" in content:
        content = re.sub(r"CACHE_BUSTER \d+", f"CACHE_BUSTER {timestamp}", content, 1)
    else:
        content = f"/* CACHE_BUSTER {timestamp} */\n" + content
    
    # كتابة المحتوى المحدث
    with open(css_path, "w", encoding="utf-8") as file:
        file.write(content)
    
    print(f"✅ تم تحديث ملف CSS مع معرّف كاش جديد: {timestamp}")
    return True

def override_css():
    """تطبيق التنسيق الصحيح مباشرة"""
    css_path = "static/css/old-table.css"
    timestamp = int(time.time())
    
    css_content = f"""/* CACHE_BUSTER {timestamp} */
/* أنماط التصميم القديم للجدول */

/* تنسيق الأزرار الملونة كما في الصورة المرفقة */
.action-icons {
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 8px;
}
.action-icon {
    width: 24px;
    height: 24px;
    border-radius: 4px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 12px;
    color: white !important;
    cursor: pointer;
    transition: all 0.2s ease;
    text-decoration: none;
}
.action-icon:hover {
    transform: scale(1.1);
    color: white !important;
    text-decoration: none;
}
.action-icon.red {
    background-color: #f44336;
}
.action-icon.blue {
    background-color: #3361ff;
}
.action-icon.yellow {
    background-color: #ffc107;
}
.action-icon.green {
    background-color: #4caf50;
}
.action-icon.purple {
    background-color: #9c27b0;
}

/* تنسيق شارات الحالة كما في الصورة المرفقة */
.status-badge {
    padding: 6px 12px;
    border-radius: 20px;
    font-size: 0.8rem;
    font-weight: 600;
    display: inline-block;
    text-align: center;
}
.status-pending {
    background-color: #fff8e1;
    color: #ff9800;
}
.status-confirmed {
    background-color: #e8f5e9;
    color: #4caf50;
}
.status-completed {
    background-color: #e3f2fd;
    color: #2196f3;
}
.status-cancelled {
    background-color: #ffebee;
    color: #f44336;
}

/* تنسيق الجدول كما في الصورة المرفقة */
.reservation-table {
    width: 100%;
    border-collapse: collapse;
    background-color: white;
    border-radius: 8px;
    overflow: hidden;
    margin-bottom: 20px;
}

.reservation-table thead {
    background-color: #f0f5ff;
    border-bottom: 1px solid #e2e8f0;
}

.reservation-table th {
    padding: 12px 15px;
    text-align: center;
    font-weight: 600;
    color: #3361ff;
    border: none;
}

.reservation-table tr {
    border-bottom: 1px solid #eee;
}

.reservation-table td {
    padding: 12px 8px;
    text-align: center;
    vertical-align: middle;
}

/* تنسيق صف الأزرار */
.filter-top {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 15px;
}

.filter-btn {
    background-color: #3361ff;
    color: white;
    border: none;
    border-radius: 5px;
    padding: 8px 15px;
    cursor: pointer;
    text-decoration: none;
}

.filter-btn:hover {
    background-color: #2851e3;
    color: white;
    text-decoration: none;
}

.search-box {
    position: relative;
}

.search-input {
    padding: 8px 15px 8px 40px;
    border: 1px solid #ddd;
    border-radius: 5px;
    min-width: 250px;
}

.search-icon {
    position: absolute;
    left: 12px;
    top: 50%;
    transform: translateY(-50%);
    color: #aaa;
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
  width: 50px;
  height: 35px;
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
  
  .action-icons {
    justify-content: flex-start;
  }
  
  [dir="rtl"] .action-icons {
    justify-content: flex-end;
  }
}
""" % int(time.time())
    
    with open(css_path, "w", encoding="utf-8") as file:
        file.write(css_content)
    
    print(f"✅ تم إعادة كتابة ملف CSS بالكامل")
    return True

def update_template_content():
    """تحديث محتوى قالب صفحة الحجوزات"""
    template_path = "templates/admin/reservations_django.html"
    
    html_content = """<!-- CACHE_BUSTER %d -->{% extends 'admin/enhanced/admin_layout.html' %}
{% load static %}
{% load i18n %}

{% block extra_head %}
<link rel="stylesheet" href="{% static 'css/old-table.css' %}">
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
    
    <!-- جدول الحجوزات بالتصميم المطلوب -->
    <div class="filter-top mb-3">
        <div class="d-flex align-items-center">
            <a href="#" class="filter-btn ms-2">
                <i class="fas fa-filter ms-1"></i> {% trans "Filter" %}
            </a>
            <div class="search-box">
                <i class="fas fa-search search-icon"></i>
                <input type="text" class="search-input" placeholder="{% trans 'Search...' %}">
            </div>
        </div>
        <div>
            <a href="#" class="filter-btn">
                <i class="fas fa-upload ms-1"></i> {% trans "Excel Import" %}
            </a>
        </div>
    </div>
    
    <div class="table-container">
        {% if reservations %}
            <table class="reservation-table">
                <thead>
                    <tr>
                        <th>#</th>
                        <th>{% trans "Customer" %}</th>
                        <th>{% trans "Car" %}</th>
                        <th>{% trans "Price" %}</th>
                        <th>{% trans "Dates" %}</th>
                        <th>{% trans "Status" %}</th>
                        <th>{% trans "Payment Status" %}</th>
                        <th>{% trans "Date Created" %}</th>
                        <th>{% trans "Actions" %}</th>
                    </tr>
                </thead>
                <tbody>
                    {% for reservation in reservations %}
                    <tr>
                        <td>
                            <a href="{% url 'admin_reservation_detail' reservation.id %}" class="reservation-id">
                                #{{ reservation.id }}
                            </a>
                        </td>
                        <td>
                            <div class="d-flex align-items-center justify-content-center">
                                <div class="user-avatar">
                                    <i class="fas fa-user-circle fa-2x text-primary"></i>
                                </div>
                                <div class="ms-2 text-start">
                                    <div>{{ reservation.user.first_name }} {{ reservation.user.last_name }}</div>
                                    <small class="text-muted">{{ reservation.user.email }}</small>
                                </div>
                            </div>
                        </td>
                        <td>
                            <div>{{ reservation.car.make }} {{ reservation.car.model }}</div>
                            <small class="text-muted">{{ reservation.car.year }}</small>
                        </td>
                        <td>
                            <div>{{ reservation.total_price }} {% trans "SAR" %}</div>
                        </td>
                        <td>
                            <div>
                                {% if is_english %}
                                {{ reservation.pickup_date|date:"m/d/Y" }} - {{ reservation.return_date|date:"m/d/Y" }}
                                {% else %}
                                {{ reservation.pickup_date|date:"d/m/Y" }} - {{ reservation.return_date|date:"d/m/Y" }}
                                {% endif %}
                            </div>
                            <small class="text-muted">{{ reservation.days }} {% trans "days" %}</small>
                        </td>
                        <td>
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
                        <td>
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
                        <td>
                            <div>
                                {% if is_english %}
                                {{ reservation.created_at|date:"m/d/Y" }}
                                {% else %}
                                {{ reservation.created_at|date:"d/m/Y" }}
                                {% endif %}
                            </div>
                        </td>
                        <td>
                            <div class="action-icons">
                                <!-- أزرار العمليات على شكل أيقونات كما في التصميم المرفق -->
                                <a href="{% url 'admin_reservation_detail' reservation.id %}" class="action-icon blue" title="{% trans 'View Details' %}">
                                    <i class="fas fa-eye"></i>
                                </a>
                                
                                {% if reservation.status == 'pending' %}
                                <a href="{% url 'update_reservation_status' reservation.id 'confirmed' %}" class="action-icon green" title="{% trans 'Confirm Reservation' %}">
                                    <i class="fas fa-check"></i>
                                </a>
                                {% endif %}
                                
                                {% if reservation.status == 'pending' or reservation.status == 'confirmed' %}
                                <a href="{% url 'update_reservation_status' reservation.id 'cancelled' %}" class="action-icon red" title="{% trans 'Cancel Reservation' %}">
                                    <i class="fas fa-times"></i>
                                </a>
                                {% endif %}
                                
                                {% if reservation.status == 'confirmed' %}
                                <a href="{% url 'update_reservation_status' reservation.id 'completed' %}" class="action-icon purple" title="{% trans 'Mark as Completed' %}">
                                    <i class="fas fa-flag-checkered"></i>
                                </a>
                                {% endif %}
                            </div>
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
        
        // إضافة محتوى الجدول
        printWindow.document.write(printContents);
        
        printWindow.document.write('</body></html>');
        printWindow.document.close();
        printWindow.focus();
        
        // طباعة بعد تحميل الموارد
        setTimeout(function() {
            printWindow.print();
            printWindow.close();
        }, 1000);
    }
</script>
{% endblock %}""" % int(time.time())
    
    with open(template_path, "w", encoding="utf-8") as file:
        file.write(html_content)
    
    print(f"✅ تم إعادة كتابة محتوى قالب الحجوزات بالكامل")
    return True

def touch_main_file():
    """لمس الملف الرئيسي لإعادة تحميل التطبيق"""
    with open("main.py", "a") as file:
        file.write("\n# " + str(datetime.now()))
    
    print("✅ تم تنشيط إعادة تحميل التطبيق")
    return True

def main():
    """الدالة الرئيسية"""
    print("🔄 بدء عملية تحديث تنسيق جدول الحجوزات...")
    
    override_css()
    update_template_content()
    touch_main_file()
    
    print("✅ تم الانتهاء من تحديث تنسيق جدول الحجوزات")
    print("ℹ️ قم بتحديث الصفحة بالضغط على Ctrl+F5 لمسح ذاكرة التخزين المؤقت")

if __name__ == "__main__":
    main()