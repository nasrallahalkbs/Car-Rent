"""
إصلاح قالب التأكيد (confirmation_django.html) ليدعم اللغتين العربية والإنجليزية
"""

import os

def fix_confirmation_template():
    """
    تحديث ملف confirmation_django.html لدعم اللغتين العربية والإنجليزية
    باستخدام شرط {% if is_english %} كما في القوالب الأخرى
    """
    template_path = 'templates/confirmation_django.html'
    
    # التأكد من وجود الملف
    if not os.path.exists(template_path):
        print(f"لم يتم العثور على الملف: {template_path}")
        return
    
    # قراءة محتوى الملف
    with open(template_path, 'r', encoding='utf-8') as file:
        content = file.read()
    
    # تحديث عنوان الصفحة
    content = content.replace(
        '{% block title %}تأكيد الحجز{% endblock %}',
        '{% block title %}{% if is_english %}Reservation Confirmation{% else %}تأكيد الحجز{% endif %}{% endblock %}'
    )
    
    # تحديث نص الحجز قيد الانتظار
    content = content.replace(
        '<h2 class="mb-4">تم استلام طلب الحجز!</h2>',
        '<h2 class="mb-4">{% if is_english %}Reservation Request Received!{% else %}تم استلام طلب الحجز!{% endif %}</h2>'
    )
    
    content = content.replace(
        '<p class="lead mb-4">\n                        شكراً لك، تم استلام طلب حجزك وهو قيد المراجعة الآن. سيتم إشعارك عند الموافقة على طلبك.\n                    </p>',
        '<p class="lead mb-4">\n                        {% if is_english %}Thank you, your reservation request has been received and is under review. You will be notified when your request is approved.{% else %}شكراً لك، تم استلام طلب حجزك وهو قيد المراجعة الآن. سيتم إشعارك عند الموافقة على طلبك.{% endif %}\n                    </p>'
    )
    
    # تحديث عنوان تفاصيل الحجز
    content = content.replace(
        '<h5 class="border-bottom pb-2 mb-3">تفاصيل الحجز</h5>',
        '<h5 class="border-bottom pb-2 mb-3">{% if is_english %}Reservation Details{% else %}تفاصيل الحجز{% endif %}</h5>'
    )
    
    # تحديث حقول تفاصيل الحجز
    content = content.replace(
        '<div class="col-sm-4 fw-bold">رقم الحجز:</div>',
        '<div class="col-sm-4 fw-bold">{% if is_english %}Reservation Number:{% else %}رقم الحجز:{% endif %}</div>'
    )
    
    content = content.replace(
        '<div class="col-sm-4 fw-bold">السيارة:</div>',
        '<div class="col-sm-4 fw-bold">{% if is_english %}Car:{% else %}السيارة:{% endif %}</div>'
    )
    
    content = content.replace(
        '<div class="col-sm-4 fw-bold">تاريخ الاستلام:</div>',
        '<div class="col-sm-4 fw-bold">{% if is_english %}Pick-up Date:{% else %}تاريخ الاستلام:{% endif %}</div>'
    )
    
    content = content.replace(
        '<div class="col-sm-8">{{ reservation.start_date|date:"Y/m/d" }}</div>',
        '<div class="col-sm-8">{{ reservation.start_date|date:"m/d/Y" if is_english else reservation.start_date|date:"Y/m/d" }}</div>'
    )
    
    content = content.replace(
        '<div class="col-sm-4 fw-bold">تاريخ التسليم:</div>',
        '<div class="col-sm-4 fw-bold">{% if is_english %}Return Date:{% else %}تاريخ التسليم:{% endif %}</div>'
    )
    
    content = content.replace(
        '<div class="col-sm-8">{{ reservation.end_date|date:"Y/m/d" }}</div>',
        '<div class="col-sm-8">{{ reservation.end_date|date:"m/d/Y" if is_english else reservation.end_date|date:"Y/m/d" }}</div>'
    )
    
    content = content.replace(
        '<div class="col-sm-4 fw-bold">المدة:</div>',
        '<div class="col-sm-4 fw-bold">{% if is_english %}Duration:{% else %}المدة:{% endif %}</div>'
    )
    
    content = content.replace(
        '<div class="col-sm-8">{{ reservation.days }} يوم</div>',
        '<div class="col-sm-8">{{ reservation.days }} {% if is_english %}day{% if reservation.days > 1 %}s{% endif %}{% else %}يوم{% endif %}</div>'
    )
    
    content = content.replace(
        '<div class="col-sm-4 fw-bold">السعر اليومي:</div>',
        '<div class="col-sm-4 fw-bold">{% if is_english %}Daily Rate:{% else %}السعر اليومي:{% endif %}</div>'
    )
    
    content = content.replace(
        '<div class="col-sm-8">{{ reservation.car.daily_rate }} دينار</div>',
        '<div class="col-sm-8">{{ reservation.car.daily_rate }} {% if is_english %}JOD{% else %}دينار{% endif %}</div>'
    )
    
    content = content.replace(
        '<div class="col-sm-4 fw-bold">المبلغ الإجمالي:</div>',
        '<div class="col-sm-4 fw-bold">{% if is_english %}Total Amount:{% else %}المبلغ الإجمالي:{% endif %}</div>'
    )
    
    content = content.replace(
        '<div class="col-sm-8">{{ total_amount }} دينار</div>',
        '<div class="col-sm-8">{{ total_amount }} {% if is_english %}JOD{% else %}دينار{% endif %}</div>'
    )
    
    content = content.replace(
        '<div class="col-sm-4 fw-bold">حالة الحجز:</div>',
        '<div class="col-sm-4 fw-bold">{% if is_english %}Reservation Status:{% else %}حالة الحجز:{% endif %}</div>'
    )
    
    # تحديث حالات الحجز
    content = content.replace(
        '<span class="badge bg-warning">قيد الانتظار</span>',
        '<span class="badge bg-warning">{% if is_english %}Pending{% else %}قيد الانتظار{% endif %}</span>'
    )
    
    content = content.replace(
        '<span class="badge bg-success">مؤكد</span>',
        '<span class="badge bg-success">{% if is_english %}Confirmed{% else %}مؤكد{% endif %}</span>'
    )
    
    content = content.replace(
        '<span class="badge bg-danger">ملغي</span>',
        '<span class="badge bg-danger">{% if is_english %}Cancelled{% else %}ملغي{% endif %}</span>'
    )
    
    # تحديث أزرار الإجراءات
    content = content.replace(
        '<a href="{% url \'payment\' reservation.id %}" class="btn btn-primary btn-lg">\n                        <i class="fas fa-credit-card ms-2"></i>الانتقال إلى الدفع\n                    </a>',
        '<a href="{% url \'payment\' reservation.id %}" class="btn btn-primary btn-lg">\n                        <i class="fas fa-credit-card {% if is_english %}me-2{% else %}ms-2{% endif %}"></i>{% if is_english %}Proceed to Payment{% else %}الانتقال إلى الدفع{% endif %}\n                    </a>'
    )
    
    content = content.replace(
        '<a href="{% url \'profile\' %}" class="btn btn-secondary btn-lg ms-2">\n                        <i class="fas fa-user ms-2"></i>الذهاب إلى الملف الشخصي\n                    </a>',
        '<a href="{% url \'profile\' %}" class="btn btn-secondary btn-lg {% if is_english %}ms-2{% else %}me-2{% endif %}">\n                        <i class="fas fa-user {% if is_english %}me-2{% else %}ms-2{% endif %}"></i>{% if is_english %}Go to Profile{% else %}الذهاب إلى الملف الشخصي{% endif %}\n                    </a>'
    )
    
    # تحديث حالة الحجز المؤكد
    content = content.replace(
        '<div class="icon-circle icon-circle-success mb-4">\n                        <i class="fas fa-check fa-4x text-success"></i>\n                    </div>\n                    <h2 class="mb-4">تم تأكيد الحجز!</h2>\n                    <p class="lead mb-4">\n                        تهانينا! تم تأكيد حجزك وإصدار إيصال الدفع. يمكنك طباعة الإيصال من لوحة المستخدم الخاصة بك.\n                    </p>',
        '<div class="icon-circle icon-circle-success mb-4">\n                        <i class="fas fa-check fa-4x text-success"></i>\n                    </div>\n                    <h2 class="mb-4">{% if is_english %}Reservation Confirmed!{% else %}تم تأكيد الحجز!{% endif %}</h2>\n                    <p class="lead mb-4">\n                        {% if is_english %}Congratulations! Your reservation has been confirmed and a payment receipt has been issued. You can print the receipt from your user dashboard.{% else %}تهانينا! تم تأكيد حجزك وإصدار إيصال الدفع. يمكنك طباعة الإيصال من لوحة المستخدم الخاصة بك.{% endif %}\n                    </p>'
    )
    
    # تحديث حالة الحجز الملغي
    content = content.replace(
        '<div class="icon-circle icon-circle-danger mb-4">\n                        <i class="fas fa-times fa-4x text-danger"></i>\n                    </div>\n                    <h2 class="mb-4">تم إلغاء الحجز</h2>\n                    <p class="lead mb-4">\n                        نأسف لإبلاغك أنه تم إلغاء هذا الحجز. إذا كنت قد دفعت بالفعل، سيتم رد المبلغ خلال 3-5 أيام عمل.\n                    </p>',
        '<div class="icon-circle icon-circle-danger mb-4">\n                        <i class="fas fa-times fa-4x text-danger"></i>\n                    </div>\n                    <h2 class="mb-4">{% if is_english %}Reservation Cancelled{% else %}تم إلغاء الحجز{% endif %}</h2>\n                    <p class="lead mb-4">\n                        {% if is_english %}We regret to inform you that this reservation has been cancelled. If you have already paid, the amount will be refunded within 3-5 business days.{% else %}نأسف لإبلاغك أنه تم إلغاء هذا الحجز. إذا كنت قد دفعت بالفعل، سيتم رد المبلغ خلال 3-5 أيام عمل.{% endif %}\n                    </p>'
    )
    
    # تحديث أزرار العودة
    content = content.replace(
        '<a href="{% url \'index\' %}" class="btn btn-outline-secondary">العودة إلى الصفحة الرئيسية</a>',
        '<a href="{% url \'index\' %}" class="btn btn-outline-secondary">{% if is_english %}Return to Home Page{% else %}العودة إلى الصفحة الرئيسية{% endif %}</a>'
    )
    
    # كتابة المحتوى المعدل إلى الملف
    with open(template_path, 'w', encoding='utf-8') as file:
        file.write(content)
    
    print(f"تم تحديث الملف: {template_path}")

if __name__ == "__main__":
    fix_confirmation_template()