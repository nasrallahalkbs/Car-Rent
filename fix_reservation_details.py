"""
إصلاح صفحة تفاصيل الحجز في لوحة التحكم
هذا السكريبت يقوم بإنشاء وإصلاح ملفات القوالب والروابط المتعلقة بعرض تفاصيل الحجز
"""

import os
import shutil
from pathlib import Path

def ensure_template_directory():
    """التأكد من وجود مجلد للقوالب"""
    Path('templates/admin').mkdir(parents=True, exist_ok=True)

def create_simple_template():
    """إنشاء قالب بسيط لعرض تفاصيل الحجز"""
    template_path = 'templates/admin/reservation_detail_simple.html'
    
    template_content = """{% extends "admin_layout.html" %}
{% load i18n %}
{% load static %}

{% block title %}تفاصيل الحجز{% endblock %}

{% block content %}
<div class="container-fluid py-4">
    <div class="row">
        <div class="col-12 mb-4">
            <div class="card shadow-sm border-0">
                <div class="card-body">
                    <h2 class="card-title mb-4">تفاصيل الحجز #{{ reservation.id }}</h2>
                    
                    <a href="{% url 'admin_reservations' %}" class="btn btn-outline-secondary mb-4">
                        <i class="fas fa-arrow-right ms-2"></i> العودة للحجوزات
                    </a>
                    
                    <div class="row">
                        <div class="col-md-6">
                            <h5 class="mb-3">معلومات الحجز</h5>
                            <p><strong>رقم الحجز:</strong> {{ reservation.reservation_number|default:"--" }}</p>
                            <p><strong>تاريخ الاستلام:</strong> {{ reservation.start_date|date:"Y/m/d" }}</p>
                            <p><strong>تاريخ التسليم:</strong> {{ reservation.end_date|date:"Y/m/d" }}</p>
                            <p><strong>عدد الأيام:</strong> {{ days }} يوم</p>
                            <p><strong>المبلغ الإجمالي:</strong> {{ reservation.total_price }} د.ك</p>
                            
                            <h5 class="mt-4 mb-3">حالة الحجز</h5>
                            <p>
                                {% if reservation.status == 'pending' %}
                                <span class="badge bg-warning">قيد المراجعة</span>
                                {% elif reservation.status == 'confirmed' %}
                                <span class="badge bg-success">تمت الموافقة</span>
                                {% elif reservation.status == 'completed' %}
                                <span class="badge bg-info">مكتمل</span>
                                {% elif reservation.status == 'cancelled' %}
                                <span class="badge bg-danger">ملغي</span>
                                {% endif %}
                                
                                {% if reservation.payment_status == 'pending' %}
                                <span class="badge bg-secondary">في انتظار الدفع</span>
                                {% elif reservation.payment_status == 'paid' %}
                                <span class="badge bg-success">مدفوع</span>
                                {% elif reservation.payment_status == 'refunded' %}
                                <span class="badge bg-danger">مسترجع</span>
                                {% elif reservation.payment_status == 'expired' %}
                                <span class="badge bg-danger">منتهي الصلاحية</span>
                                {% endif %}
                            </p>
                        </div>
                        
                        <div class="col-md-6">
                            <h5 class="mb-3">معلومات العميل</h5>
                            <p><strong>الاسم:</strong> {{ reservation.user.get_full_name }}</p>
                            <p><strong>البريد الإلكتروني:</strong> {{ reservation.user.email }}</p>
                            <p><strong>اسم المستخدم:</strong> {{ reservation.user.username }}</p>

                            <h5 class="mt-4 mb-3">معلومات السيارة</h5>
                            <p><strong>السيارة:</strong> {{ reservation.car.make }} {{ reservation.car.model }} ({{ reservation.car.year }})</p>
                            <p><strong>فئة السيارة:</strong> {{ reservation.car.category }}</p>
                            <p><strong>اللون:</strong> {{ reservation.car.color }}</p>
                            <p><strong>لوحة الترخيص:</strong> {{ reservation.car.license_plate }}</p>
                        </div>
                    </div>
                    
                    <div class="mt-4">
                        <div class="mb-3">
                            {% if reservation.status == 'pending' %}
                            <a href="{% url 'confirm_reservation' reservation.id %}" class="btn btn-success me-2">
                                <i class="fas fa-check ms-1"></i> تأكيد الحجز
                            </a>
                            {% endif %}

                            {% if reservation.status != 'cancelled' %}
                            <a href="{% url 'cancel_reservation_admin' reservation.id %}" class="btn btn-warning me-2">
                                <i class="fas fa-times ms-1"></i> إلغاء الحجز
                            </a>
                            {% endif %}

                            {% if reservation.status == 'confirmed' and reservation.payment_status == 'pending' %}
                            <a href="{% url 'mark_as_paid' reservation.id %}" class="btn btn-primary me-2">
                                <i class="fas fa-money-bill ms-1"></i> تعيين كمدفوع
                            </a>
                            {% endif %}

                            {% if reservation.status == 'confirmed' and reservation.payment_status == 'paid' %}
                            <a href="{% url 'complete_reservation' reservation.id %}" class="btn btn-info me-2">
                                <i class="fas fa-flag-checkered ms-1"></i> تعيين كمكتمل
                            </a>
                            {% endif %}
                            
                            <a href="javascript:void(0);" onclick="confirmDelete({{ reservation.id }})" class="btn btn-danger">
                                <i class="fas fa-trash-alt ms-1"></i> حذف نهائي
                            </a>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>
</div>

<script>
function confirmDelete(reservationId) {
    if (confirm('هل أنت متأكد من حذف هذا الحجز نهائياً؟')) {
        window.location.href = "{% url 'delete_reservation' 0 %}".replace('0', reservationId);
    }
}
</script>
{% endblock %}"""
    
    with open(template_path, 'w', encoding='utf-8') as file:
        file.write(template_content)
    
    print(f"تم إنشاء القالب المبسط: {template_path}")
    return template_path

def fix_admin_view_function():
    """تحديث دالة عرض تفاصيل الحجز في admin_views.py"""
    views_path = 'rental/admin_views.py'
    
    # قراءة محتوى الملف
    if not os.path.exists(views_path):
        print(f"خطأ: الملف {views_path} غير موجود")
        return False
    
    with open(views_path, 'r', encoding='utf-8') as file:
        content = file.read()
    
    # البحث عن دالة admin_reservation_detail والتأكد من وجودها
    if "def admin_reservation_detail" not in content:
        print("خطأ: دالة admin_reservation_detail غير موجودة في الملف")
        return False
    
    # إنشاء دالة بديلة بسيطة
    new_function = '''@login_required
@admin_required
def admin_reservation_detail(request, reservation_id):
    """Admin view to show reservation details"""
    try:
        # إضافة سجل بسيط
        print(f"Accessing reservation details for ID: {reservation_id}")
        
        # الحصول على تفاصيل الحجز
        reservation = get_object_or_404(Reservation, id=reservation_id)
        
        # حساب عدد الأيام
        delta = (reservation.end_date - reservation.start_date).days + 1
        
        # تحديد اللغة
        from django.utils.translation import get_language
        current_language = get_language()
        is_english = current_language == 'en'
        is_rtl = current_language == 'ar'
        
        # إعداد سياق القالب
        context = {
            'reservation': reservation,
            'days': delta,
            'is_english': is_english,
            'is_rtl': is_rtl,
            'current_user': request.user,
        }
        
        # استخدام القالب البسيط
        return render(request, 'admin/reservation_detail_simple.html', context)
    
    except Exception as e:
        # تسجيل الخطأ
        print(f"Error showing reservation details: {str(e)}")
        messages.error(request, f"حدث خطأ أثناء عرض تفاصيل الحجز: {str(e)}")
        return redirect('admin_reservations')'''
    
    # استبدال الدالة القديمة بالجديدة
    import re
    pattern = r'@login_required\s+@admin_required\s+def admin_reservation_detail\([^{]*?\):[^}]*?(?=@login_required|@admin_required|def |$)'
    new_content = re.sub(pattern, new_function, content, flags=re.DOTALL)
    
    if new_content == content:
        print("تحذير: لم يتم استبدال الدالة، قد تكون هناك مشكلة في النمط")
        # طريقة بديلة للحفظ كملف جديد
        with open('rental/admin_views_modified.py', 'w', encoding='utf-8') as file:
            file.write(content.replace('@login_required\n@admin_required\ndef admin_reservation_detail', new_function))
        print("تم إنشاء ملف بديل: rental/admin_views_modified.py")
        
        return False
    
    with open(views_path, 'w', encoding='utf-8') as file:
        file.write(new_content)
    
    print(f"تم تحديث دالة admin_reservation_detail في {views_path}")
    return True

def fix_template_links():
    """تصحيح روابط URL في قالب الحجوزات"""
    template_path = 'templates/admin/reservations_django.html'
    
    if not os.path.exists(template_path):
        print(f"خطأ: الملف {template_path} غير موجود")
        return False
    
    with open(template_path, 'r', encoding='utf-8') as file:
        content = file.read()
    
    # تصحيح أنماط الروابط
    content = content.replace("{% url 'admin_reservation_detail' reservation_id=reservation.id %}", 
                             "{% url 'admin_reservation_detail' reservation.id %}")
    
    content = content.replace("{% url 'delete_reservation' reservation_id=reservation.id %}", 
                             "{% url 'delete_reservation' reservation.id %}")
    
    content = content.replace("{% url 'mark_as_paid' payment_id=reservation.id %}", 
                             "{% url 'mark_as_paid' reservation.id %}")
    
    with open(template_path, 'w', encoding='utf-8') as file:
        file.write(content)
    
    print(f"تم تصحيح روابط URL في {template_path}")
    return True

def main():
    """الدالة الرئيسية لتنفيذ الإصلاحات"""
    print("بدء إصلاح مشكلة عرض تفاصيل الحجز...")
    
    # التأكد من وجود مجلد القوالب
    ensure_template_directory()
    
    # إنشاء قالب بسيط
    template_path = create_simple_template()
    
    # إصلاح روابط القالب
    fix_template_links()
    
    # تحديث دالة العرض
    fix_admin_view_function()
    
    print("تم الانتهاء من إصلاح مشكلة عرض تفاصيل الحجز بنجاح")

if __name__ == "__main__":
    main()