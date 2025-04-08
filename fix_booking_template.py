"""
إصلاح قالب الحجز (booking.html) ليدعم اللغتين العربية والإنجليزية
"""

import os

def fix_booking_template():
    """
    تحديث ملف booking.html لدعم اللغتين العربية والإنجليزية
    باستخدام شرط {% if is_english %} كما في القوالب الأخرى
    """
    template_path = 'templates/booking.html'
    
    # التأكد من وجود الملف
    if not os.path.exists(template_path):
        print(f"لم يتم العثور على الملف: {template_path}")
        return
    
    # قراءة محتوى الملف
    with open(template_path, 'r', encoding='utf-8') as file:
        content = file.read()
    
    # تحديث عنوان الصفحة
    content = content.replace(
        '{% block title %}حجز - {{ car.make }} {{ car.model }}{% endblock %}',
        '{% block title %}{% if is_english %}Booking - {{ car.make }} {{ car.model }}{% else %}حجز - {{ car.make }} {{ car.model }}{% endif %}{% endblock %}'
    )
    
    # تحديث عنوان البطاقة
    content = content.replace(
        '<h3 class="mb-0">طلب حجز - {{ car.make }} {{ car.model }}</h3>',
        '<h3 class="mb-0">{% if is_english %}Booking Request - {{ car.make }} {{ car.model }}{% else %}طلب حجز - {{ car.make }} {{ car.model }}{% endif %}</h3>'
    )
    
    # تحديث أيقونات الهوامش
    content = content.replace(
        '<i class="fas fa-car ms-1"></i>', 
        '<i class="fas fa-car {% if is_english %}me-1{% else %}ms-1{% endif %}"></i>'
    )
    content = content.replace(
        '<i class="fas fa-cog ms-1"></i>', 
        '<i class="fas fa-cog {% if is_english %}me-1{% else %}ms-1{% endif %}"></i>'
    )
    content = content.replace(
        '<i class="fas fa-gas-pump ms-1"></i>', 
        '<i class="fas fa-gas-pump {% if is_english %}me-1{% else %}ms-1{% endif %}"></i>'
    )
    
    # تحديث نص السعر اليومي
    content = content.replace(
        '<strong>السعر اليومي:</strong> {{ car.daily_rate }} دينار / يوم',
        '<strong>{% if is_english %}Daily Rate:{% else %}السعر اليومي:{% endif %}</strong> {{ car.daily_rate }} {% if is_english %}JOD / day{% else %}دينار / يوم{% endif %}'
    )
    
    # تحديث نص السيارة في سلة التسوق
    content = content.replace(
        'هذه السيارة موجودة في سلة التسوق للفترة من {{ cart_item.start_date|date:"Y/m/d" }} إلى {{ cart_item.end_date|date:"Y/m/d" }}',
        '{% if is_english %}This car is already in your cart for the period from {{ cart_item.start_date|date:"m/d/Y" }} to {{ cart_item.end_date|date:"m/d/Y" }}{% else %}هذه السيارة موجودة في سلة التسوق للفترة من {{ cart_item.start_date|date:"Y/m/d" }} إلى {{ cart_item.end_date|date:"Y/m/d" }}{% endif %}'
    )
    
    # تحديث عنوان تفاصيل الحجز
    content = content.replace(
        '<i class="far fa-calendar-alt ms-2"></i>تفاصيل الحجز',
        '<i class="far fa-calendar-alt {% if is_english %}me-2{% else %}ms-2{% endif %}"></i>{% if is_english %}Booking Details{% else %}تفاصيل الحجز{% endif %}'
    )
    
    # تحديث حقول التاريخ
    content = content.replace(
        '<label for="start_date" class="form-label">تاريخ الاستلام*</label>',
        '<label for="start_date" class="form-label">{% if is_english %}Pick-up Date*{% else %}تاريخ الاستلام*{% endif %}</label>'
    )
    content = content.replace(
        '<label for="end_date" class="form-label">تاريخ التسليم*</label>',
        '<label for="end_date" class="form-label">{% if is_english %}Return Date*{% else %}تاريخ التسليم*{% endif %}</label>'
    )
    
    # تحديث عنوان معلومات العميل
    content = content.replace(
        '<i class="far fa-user ms-2"></i>معلومات العميل',
        '<i class="far fa-user {% if is_english %}me-2{% else %}ms-2{% endif %}"></i>{% if is_english %}Customer Information{% else %}معلومات العميل{% endif %}'
    )
    
    # تحديث حقول معلومات العميل
    content = content.replace(
        '<label for="first_name" class="form-label">الاسم الأول*</label>',
        '<label for="first_name" class="form-label">{% if is_english %}First Name*{% else %}الاسم الأول*{% endif %}</label>'
    )
    content = content.replace(
        '<label for="last_name" class="form-label">الاسم الأخير*</label>',
        '<label for="last_name" class="form-label">{% if is_english %}Last Name*{% else %}الاسم الأخير*{% endif %}</label>'
    )
    content = content.replace(
        '<label for="email" class="form-label">البريد الإلكتروني*</label>',
        '<label for="email" class="form-label">{% if is_english %}Email*{% else %}البريد الإلكتروني*{% endif %}</label>'
    )
    content = content.replace(
        '<label for="phone" class="form-label">رقم الهاتف*</label>',
        '<label for="phone" class="form-label">{% if is_english %}Phone Number*{% else %}رقم الهاتف*{% endif %}</label>'
    )
    
    # تحديث قسم الملاحظات الإضافية
    content = content.replace(
        '<label for="notes" class="form-label">ملاحظات إضافية</label>',
        '<label for="notes" class="form-label">{% if is_english %}Additional Notes{% else %}ملاحظات إضافية{% endif %}</label>'
    )
    content = content.replace(
        'placeholder="أي طلبات خاصة أو ملاحظات إضافية؟"',
        'placeholder="{% if is_english %}Any special requests or additional notes?{% else %}أي طلبات خاصة أو ملاحظات إضافية؟{% endif %}"'
    )
    
    # تحديث ملخص الحجز
    content = content.replace(
        '<h5 class="mb-0">ملخص الحجز</h5>',
        '<h5 class="mb-0">{% if is_english %}Booking Summary{% else %}ملخص الحجز{% endif %}</h5>'
    )
    content = content.replace(
        '<span>السعر اليومي:</span>',
        '<span>{% if is_english %}Daily Rate:{% else %}السعر اليومي:{% endif %}</span>'
    )
    content = content.replace(
        '<strong>{{ car.daily_rate }} دينار</strong>',
        '<strong>{{ car.daily_rate }} {% if is_english %}JOD{% else %}دينار{% endif %}</strong>'
    )
    content = content.replace(
        '<span>عدد الأيام:</span>',
        '<span>{% if is_english %}Number of Days:{% else %}عدد الأيام:{% endif %}</span>'
    )
    content = content.replace(
        '<span>الإجمالي:</span>',
        '<span>{% if is_english %}Total:{% else %}الإجمالي:{% endif %}</span>'
    )
    
    # تحديث قسم الشروط والأحكام
    content = content.replace(
        'أوافق على <a href="#" data-bs-toggle="modal" data-bs-target="#termsModal">الشروط والأحكام</a>',
        '{% if is_english %}I agree to the <a href="#" data-bs-toggle="modal" data-bs-target="#termsModal">Terms and Conditions</a>{% else %}أوافق على <a href="#" data-bs-toggle="modal" data-bs-target="#termsModal">الشروط والأحكام</a>{% endif %}'
    )
    
    # تحديث زر الإرسال
    content = content.replace(
        '<i class="fas fa-paper-plane ms-2"></i>إرسال طلب الحجز',
        '<i class="fas fa-paper-plane {% if is_english %}me-2{% else %}ms-2{% endif %}"></i>{% if is_english %}Submit Booking Request{% else %}إرسال طلب الحجز{% endif %}'
    )
    
    # تحديث تنبيه المعلومات
    content = content.replace(
        'سيتم مراجعة طلب الحجز والرد عليه في أقرب وقت ممكن. بعد الموافقة، سيمكنك إتمام عملية الدفع.',
        '{% if is_english %}Your booking request will be reviewed as soon as possible. After approval, you can complete the payment process.{% else %}سيتم مراجعة طلب الحجز والرد عليه في أقرب وقت ممكن. بعد الموافقة، سيمكنك إتمام عملية الدفع.{% endif %}'
    )
    
    # تحديث نافذة الشروط والأحكام
    content = content.replace(
        '<h5 class="modal-title" id="termsModalLabel">الشروط والأحكام</h5>',
        '<h5 class="modal-title" id="termsModalLabel">{% if is_english %}Terms and Conditions{% else %}الشروط والأحكام{% endif %}</h5>'
    )
    
    # كتابة المحتوى المعدل إلى الملف
    with open(template_path, 'w', encoding='utf-8') as file:
        file.write(content)
    
    print(f"تم تحديث الملف: {template_path}")

if __name__ == "__main__":
    fix_booking_template()