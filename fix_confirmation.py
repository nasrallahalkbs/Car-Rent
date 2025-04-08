#!/usr/bin/env python3

import re

def fix_confirmation_template():
    with open('templates/confirmation.html', 'r', encoding='utf-8') as file:
        content = file.read()
    
    # Fix title
    content = re.sub(
        r'{% block title %}تأكيد الحجز{% endblock %}',
        r'{% block title %}{% if is_english %}Reservation Confirmation{% else %}تأكيد الحجز{% endif %}{% endblock %}',
        content
    )
    
    # Fix broken icon style attributes (ms-1 outside the tag)
    content = re.sub(
        r'<i class="fas fa-([a-z-]+) fa-4x text-([a-z]+)" ms-1></i>',
        r'<i class="fas fa-\1 fa-4x text-\2 {% if is_english %}me-1{% else %}ms-1{% endif %}"></i>',
        content
    )
    
    content = re.sub(
        r'<i class="fas fa-([a-z-]+) ms-2" ms-1></i>',
        r'<i class="fas fa-\1 {% if is_english %}me-2{% else %}ms-2{% endif %}"></i>',
        content
    )
    
    # Fix pending reservation text
    content = re.sub(
        r'<h2 class="mb-4">تم استلام طلب الحجز!</h2>',
        r'<h2 class="mb-4">{% if is_english %}Reservation Request Received!{% else %}تم استلام طلب الحجز!{% endif %}</h2>',
        content
    )
    
    content = re.sub(
        r'<p class="lead mb-4">\s*شكراً لك، تم استلام طلب حجزك وهو قيد المراجعة الآن. سيتم إشعارك عند الموافقة على طلبك.\s*</p>',
        r'<p class="lead mb-4">{% if is_english %}Thank you, your reservation request has been received and is under review. You will be notified when your request is approved.{% else %}شكراً لك، تم استلام طلب حجزك وهو قيد المراجعة الآن. سيتم إشعارك عند الموافقة على طلبك.{% endif %}</p>',
        content,
        flags=re.DOTALL
    )
    
    # Fix reservation details heading
    content = re.sub(
        r'<h5 class="border-bottom pb-2 mb-3">تفاصيل الحجز</h5>',
        r'<h5 class="border-bottom pb-2 mb-3">{% if is_english %}Reservation Details{% else %}تفاصيل الحجز{% endif %}</h5>',
        content
    )
    
    # Fix reservation details field labels
    field_labels = {
        "رقم الحجز:": "Reservation ID:",
        "السيارة:": "Vehicle:",
        "تاريخ الاستلام:": "Pickup Date:",
        "تاريخ التسليم:": "Return Date:",
        "المجموع:": "Total:",
        "حالة الحجز:": "Reservation Status:",
        "حالة الدفع:": "Payment Status:"
    }
    
    for arabic, english in field_labels.items():
        content = re.sub(
            rf'<div class="col-sm-4 fw-bold">{arabic}</div>',
            f'<div class="col-sm-4 fw-bold">{{% if is_english %}}{english}{{% else %}}{arabic}{{% endif %}}</div>',
            content
        )
    
    # Fix status badges text
    status_badges = {
        '<span class="badge bg-warning">قيد المراجعة</span>': '<span class="badge bg-warning">{% if is_english %}Under Review{% else %}قيد المراجعة{% endif %}</span>',
        '<span class="badge bg-secondary">في انتظار الموافقة</span>': '<span class="badge bg-secondary">{% if is_english %}Awaiting Approval{% else %}في انتظار الموافقة{% endif %}</span>',
        '<span class="badge bg-success">تمت الموافقة</span>': '<span class="badge bg-success">{% if is_english %}Approved{% else %}تمت الموافقة{% endif %}</span>',
        '<span class="badge bg-warning">في انتظار الدفع</span>': '<span class="badge bg-warning">{% if is_english %}Awaiting Payment{% else %}في انتظار الدفع{% endif %}</span>',
        '<span class="badge bg-success">مكتمل</span>': '<span class="badge bg-success">{% if is_english %}Completed{% else %}مكتمل{% endif %}</span>',
        '<span class="badge bg-success">مدفوع</span>': '<span class="badge bg-success">{% if is_english %}Paid{% else %}مدفوع{% endif %}</span>'
    }
    
    for arabic, bilingual in status_badges.items():
        content = content.replace(arabic, bilingual)
    
    # Fix alert messages
    content = re.sub(
        r'<div class="alert alert-info">\s*<i class="fas fa-info-circle[^>]*></i> سيتم إشعارك عبر البريد الإلكتروني عند الموافقة على طلب الحجز. يمكنك أيضاً متابعة حالة الحجز من خلال صفحة "حجوزاتي".\s*</div>',
        r'<div class="alert alert-info"><i class="fas fa-info-circle {% if is_english %}me-2{% else %}ms-2{% endif %}"></i> {% if is_english %}You will be notified by email when your reservation request is approved. You can also track the status of your reservation through the "My Reservations" page.{% else %}سيتم إشعارك عبر البريد الإلكتروني عند الموافقة على طلب الحجز. يمكنك أيضاً متابعة حالة الحجز من خلال صفحة "حجوزاتي".{% endif %}</div>',
        content,
        flags=re.DOTALL
    )
    
    content = re.sub(
        r'<div class="alert alert-success">\s*<i class="fas fa-info-circle[^>]*></i> تم إرسال تفاصيل الحجز والفاتورة إلى بريدك الإلكتروني.\s*</div>',
        r'<div class="alert alert-success"><i class="fas fa-info-circle {% if is_english %}me-2{% else %}ms-2{% endif %}"></i> {% if is_english %}Reservation details and invoice have been sent to your email.{% else %}تم إرسال تفاصيل الحجز والفاتورة إلى بريدك الإلكتروني.{% endif %}</div>',
        content,
        flags=re.DOTALL
    )
    
    # Fix button texts
    button_texts = {
        '<i class="fas fa-list ms-2" ms-1></i> عرض حجوزاتي': '<i class="fas fa-list {% if is_english %}me-2{% else %}ms-2{% endif %}"></i> {% if is_english %}View My Reservations{% else %}عرض حجوزاتي{% endif %}',
        '<i class="fas fa-car ms-2" ms-1></i> متابعة التصفح': '<i class="fas fa-car {% if is_english %}me-2{% else %}ms-2{% endif %}"></i> {% if is_english %}Continue Browsing{% else %}متابعة التصفح{% endif %}',
        '<i class="fas fa-credit-card ms-2" ms-1></i> إكمال الدفع': '<i class="fas fa-credit-card {% if is_english %}me-2{% else %}ms-2{% endif %}"></i> {% if is_english %}Complete Payment{% else %}إكمال الدفع{% endif %}'
    }
    
    for arabic, bilingual in button_texts.items():
        content = content.replace(arabic, bilingual)
    
    # Fix confirmed reservation text
    content = re.sub(
        r'<h2 class="mb-4">تمت الموافقة على الحجز!</h2>',
        r'<h2 class="mb-4">{% if is_english %}Reservation Approved!{% else %}تمت الموافقة على الحجز!{% endif %}</h2>',
        content
    )
    
    content = re.sub(
        r'<p class="lead mb-4">\s*تمت الموافقة على حجزك بنجاح! يمكنك الآن إكمال عملية الدفع لتأكيد الحجز.\s*</p>',
        r'<p class="lead mb-4">{% if is_english %}Your reservation has been successfully approved! You can now complete the payment process to confirm your reservation.{% else %}تمت الموافقة على حجزك بنجاح! يمكنك الآن إكمال عملية الدفع لتأكيد الحجز.{% endif %}</p>',
        content,
        flags=re.DOTALL
    )
    
    # Fix completed reservation text
    content = re.sub(
        r'<h2 class="mb-4">تم الحجز بنجاح!</h2>',
        r'<h2 class="mb-4">{% if is_english %}Reservation Successful!{% else %}تم الحجز بنجاح!{% endif %}</h2>',
        content
    )
    
    content = re.sub(
        r'<p class="lead mb-4">\s*شكراً لك! تم تأكيد حجزك ودفع القيمة بنجاح. سيارتك جاهزة للاستلام في التاريخ المحدد.\s*</p>',
        r'<p class="lead mb-4">{% if is_english %}Thank you! Your reservation has been confirmed and payment has been processed successfully. Your car is ready for pickup on the specified date.{% else %}شكراً لك! تم تأكيد حجزك ودفع القيمة بنجاح. سيارتك جاهزة للاستلام في التاريخ المحدد.{% endif %}</p>',
        content,
        flags=re.DOTALL
    )
    
    # Fix default state text
    content = re.sub(
        r'<h2 class="mb-4">معالجة الحجز</h2>',
        r'<h2 class="mb-4">{% if is_english %}Processing Reservation{% else %}معالجة الحجز{% endif %}</h2>',
        content
    )
    
    content = re.sub(
        r'<p class="lead mb-4">\s*تم استلام طلب حجزك. يمكنك متابعة حالة الحجز من خلال صفحة "حجوزاتي".\s*</p>',
        r'<p class="lead mb-4">{% if is_english %}Your reservation request has been received. You can track the status of your reservation through the "My Reservations" page.{% else %}تم استلام طلب حجزك. يمكنك متابعة حالة الحجز من خلال صفحة "حجوزاتي".{% endif %}</p>',
        content,
        flags=re.DOTALL
    )
    
    # Fix price display
    content = re.sub(
        r'<div class="col-sm-8">{{ reservation.total_price }} دينار</div>',
        r'<div class="col-sm-8">{% if is_english %}${{ reservation.total_price }}{% else %}{{ reservation.total_price }} دينار{% endif %}</div>',
        content
    )
    
    # Fix date format
    content = re.sub(
        r'{{ reservation.start_date\|date:"d F Y" }}',
        r'{% if is_english %}{{ reservation.start_date|date:"F d, Y" }}{% else %}{{ reservation.start_date|date:"d F Y" }}{% endif %}',
        content
    )
    
    content = re.sub(
        r'{{ reservation.end_date\|date:"d F Y" }}',
        r'{% if is_english %}{{ reservation.end_date|date:"F d, Y" }}{% else %}{{ reservation.end_date|date:"d F Y" }}{% endif %}',
        content
    )
    
    # Write the changes back
    with open('templates/confirmation.html', 'w', encoding='utf-8') as file:
        file.write(content)
    
    print("Confirmation template updated with bilingual support.")

fix_confirmation_template()
