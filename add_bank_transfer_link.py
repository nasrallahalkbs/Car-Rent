"""
إضافة رابط مباشر لصفحة التحويل البنكي في صفحة التأكيد وصفحة السلة
"""

import os
import re

def add_link_to_confirmation():
    """إضافة رابط التحويل البنكي إلى صفحة التأكيد"""
    file_path = 'templates/confirmation_django.html'
    
    if not os.path.exists(file_path):
        print(f"الملف {file_path} غير موجود")
        return False
    
    # قراءة محتوى الملف
    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()
    
    # العثور على موضع إضافة الرابط (قبل إغلاق الكارد)
    payment_link_section = """
        <div class="mt-4 text-center">
            <p class="mb-2">{% if is_english %}Payment options:{% else %}خيارات الدفع:{% endif %}</p>
            <a href="{% url 'payment_gateway' %}{% if reservation_id %}?reservation_id={{ reservation_id }}{% endif %}" class="btn btn-primary mb-2">
                {% if is_english %}Pay Now{% else %}ادفع الآن{% endif %}
            </a>
            <a href="{% url 'bank_transfer_payment' %}{% if reservation_id %}?reservation_id={{ reservation_id }}{% endif %}" class="btn btn-outline-primary mb-2">
                {% if is_english %}Pay via Bank Transfer{% else %}الدفع عبر التحويل البنكي{% endif %}
            </a>
        </div>
    """
    
    # البحث عن نمط لإضافة الرابط بعده
    card_body_pattern = r'<div class="card-body">(.*?)<div class="text-center mt-4">'
    
    if re.search(card_body_pattern, content, re.DOTALL):
        # إذا وجد النمط، إضافة الرابط قبل قسم text-center
        new_content = re.sub(card_body_pattern, r'<div class="card-body">\1' + payment_link_section + r'<div class="text-center mt-4">', content, flags=re.DOTALL)
    else:
        # إذا لم يوجد النمط، إضافة الرابط في نهاية الكارد
        card_body_end_pattern = r'(</div>\s*</div>\s*</div>\s*</div>)'
        new_content = re.sub(card_body_end_pattern, payment_link_section + r'\1', content, flags=re.DOTALL)
    
    # حفظ التغييرات
    with open(file_path, 'w', encoding='utf-8') as file:
        file.write(new_content)
    
    print("تم إضافة رابط التحويل البنكي إلى صفحة التأكيد بنجاح")
    return True

def add_link_to_cart():
    """إضافة رابط التحويل البنكي إلى صفحة السلة"""
    file_path = 'templates/cart_django.html'
    
    if not os.path.exists(file_path):
        print(f"الملف {file_path} غير موجود")
        return False
    
    # قراءة محتوى الملف
    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()
    
    # العثور على موضع إضافة الرابط (قبل زر الدفع الحالي)
    payment_button_pattern = r'<a href="{% url \'checkout\' %}" class="(btn btn-primary[^"]*)"[^>]*>'
    payment_buttons = """
            <div class="d-grid gap-2">
                <a href="{% url 'checkout' %}" class="btn btn-primary">
                    {% if is_english %}Proceed to Checkout{% else %}المتابعة إلى الدفع{% endif %}
                </a>
                <a href="{% url 'bank_transfer_payment' %}" class="btn btn-outline-primary">
                    {% if is_english %}Pay via Bank Transfer{% else %}الدفع عبر التحويل البنكي{% endif %}
                </a>
            </div>
    """
    
    # استبدال زر الدفع الحالي بقسم الأزرار الجديد
    if re.search(payment_button_pattern, content):
        new_content = re.sub(
            payment_button_pattern + r'[^<]*</a>', 
            payment_buttons, 
            content
        )
    else:
        print("لم يتم العثور على زر الدفع في صفحة السلة")
        return False
    
    # حفظ التغييرات
    with open(file_path, 'w', encoding='utf-8') as file:
        file.write(new_content)
    
    print("تم إضافة رابط التحويل البنكي إلى صفحة السلة بنجاح")
    return True

def add_direct_link_to_navbar():
    """إضافة رابط مباشر للتحويل البنكي في شريط التنقل"""
    file_path = 'templates/layout_django.html'
    
    if not os.path.exists(file_path):
        print(f"الملف {file_path} غير موجود")
        return False
    
    # قراءة محتوى الملف
    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()
    
    # رابط التحويل البنكي ليضاف قبل زر تسجيل الخروج
    bank_transfer_link = """
                <li class="nav-item">
                    <a class="nav-link" href="{% url 'bank_transfer_payment' %}">
                        <i class="fas fa-university me-1"></i>
                        {% if is_english %}Bank Transfer{% else %}التحويل البنكي{% endif %}
                    </a>
                </li>
    """
    
    # البحث عن نمط قائمة المستخدم (بعد رابط الحجوزات)
    user_menu_pattern = r'(<a class="nav-link" href="{% url \'my_reservations\' %}">[^<]*</a>\s*</li>)'
    
    # إضافة الرابط بعد رابط الحجوزات
    if re.search(user_menu_pattern, content):
        new_content = re.sub(user_menu_pattern, r'\1' + bank_transfer_link, content)
    else:
        print("لم يتم العثور على قائمة المستخدم في الشريط العلوي")
        return False
    
    # حفظ التغييرات
    with open(file_path, 'w', encoding='utf-8') as file:
        file.write(new_content)
    
    print("تم إضافة رابط التحويل البنكي إلى شريط التنقل بنجاح")
    return True

def add_links_to_reservations():
    """إضافة رابط التحويل البنكي إلى صفحة الحجوزات"""
    file_path = 'templates/reservations_django.html'
    
    if not os.path.exists(file_path):
        print(f"الملف {file_path} غير موجود")
        return False
    
    # قراءة محتوى الملف
    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()
    
    # العثور على موضع إضافة الرابط (أزرار تفاصيل الحجز)
    payment_button_pattern = r'<a href="{% url \'payment_gateway\' %}[^"]*" class="(btn btn-sm btn-primary[^"]*)"[^>]*>'
    new_payment_buttons = """
                                        <div class="btn-group">
                                            <a href="{% url 'payment_gateway' %}?reservation_id={{ reservation.id }}" class="btn btn-sm btn-primary">
                                                <i class="fas fa-credit-card"></i>
                                                {% if is_english %}Pay Now{% else %}ادفع الآن{% endif %}
                                            </a>
                                            <a href="{% url 'bank_transfer_payment' %}?reservation_id={{ reservation.id }}" class="btn btn-sm btn-outline-primary">
                                                <i class="fas fa-university"></i>
                                                {% if is_english %}Bank Transfer{% else %}تحويل بنكي{% endif %}
                                            </a>
                                        </div>
    """
    
    # استبدال زر الدفع الحالي بقسم الأزرار الجديد
    if re.search(payment_button_pattern, content):
        new_content = re.sub(
            payment_button_pattern + r'[^<]*</a>', 
            new_payment_buttons, 
            content
        )
    else:
        print("لم يتم العثور على زر الدفع في صفحة الحجوزات")
        return False
    
    # حفظ التغييرات
    with open(file_path, 'w', encoding='utf-8') as file:
        file.write(new_content)
    
    print("تم إضافة رابط التحويل البنكي إلى صفحة الحجوزات بنجاح")
    return True

def add_bank_transfer_card_to_index():
    """إضافة بطاقة معلومات التحويل البنكي للصفحة الرئيسية"""
    file_path = 'templates/index_django.html'
    
    if not os.path.exists(file_path):
        print(f"الملف {file_path} غير موجود")
        return False
    
    # قراءة محتوى الملف
    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()
    
    # بطاقة معلومات التحويل البنكي
    bank_transfer_card = """
    <!-- بطاقة معلومات التحويل البنكي -->
    <div class="container my-5">
        <div class="card border-0 shadow-sm overflow-hidden">
            <div class="row g-0">
                <div class="col-md-4 d-none d-md-block">
                    <div class="bg-primary h-100 d-flex align-items-center justify-content-center p-5 text-white">
                        <div class="text-center">
                            <i class="fas fa-university fa-5x mb-3"></i>
                            <h3>{% if is_english %}Now Available!{% else %}متوفر الآن!{% endif %}</h3>
                            <p class="mb-0">{% if is_english %}Pay securely via bank transfer{% else %}ادفع بأمان عبر التحويل البنكي{% endif %}</p>
                        </div>
                    </div>
                </div>
                <div class="col-md-8">
                    <div class="card-body p-4 p-lg-5">
                        <h3 class="card-title">{% if is_english %}Pay via Bank Transfer{% else %}الدفع عبر التحويل البنكي{% endif %}</h3>
                        <p class="card-text">
                            {% if is_english %}
                            We've added a new payment option! Now you can securely pay for your car rentals via bank transfer.
                            {% else %}
                            لقد أضفنا خيار دفع جديد! يمكنك الآن الدفع بأمان مقابل تأجير السيارات عبر التحويل البنكي.
                            {% endif %}
                        </p>
                        <div class="mb-4">
                            <div class="d-flex align-items-center mb-2">
                                <i class="fas fa-check-circle text-success me-2"></i>
                                <span>{% if is_english %}Secure payments{% else %}مدفوعات آمنة{% endif %}</span>
                            </div>
                            <div class="d-flex align-items-center mb-2">
                                <i class="fas fa-check-circle text-success me-2"></i>
                                <span>{% if is_english %}Full transaction details{% else %}تفاصيل المعاملة كاملة{% endif %}</span>
                            </div>
                            <div class="d-flex align-items-center mb-2">
                                <i class="fas fa-check-circle text-success me-2"></i>
                                <span>{% if is_english %}Convenient processing{% else %}معالجة مريحة{% endif %}</span>
                            </div>
                        </div>
                        <a href="{% url 'bank_transfer_payment' %}" class="btn btn-primary">
                            {% if is_english %}Try Bank Transfer Now{% else %}جرب التحويل البنكي الآن{% endif %}
                        </a>
                    </div>
                </div>
            </div>
        </div>
    </div>
    """
    
    # إضافة البطاقة قبل نهاية المحتوى
    content_end_pattern = r'({% endblock %}\s*$)'
    
    new_content = re.sub(content_end_pattern, bank_transfer_card + r'\1', content)
    
    # حفظ التغييرات
    with open(file_path, 'w', encoding='utf-8') as file:
        file.write(new_content)
    
    print("تم إضافة بطاقة معلومات التحويل البنكي إلى الصفحة الرئيسية بنجاح")
    return True

def main():
    """تنفيذ الدالة الرئيسية للسكريبت"""
    print("بدء إضافة روابط التحويل البنكي إلى مختلف صفحات الموقع...")
    
    # إضافة الروابط
    add_link_to_confirmation()
    add_link_to_cart()
    add_direct_link_to_navbar()
    add_links_to_reservations()
    add_bank_transfer_card_to_index()
    
    print("تم إضافة جميع الروابط بنجاح!")

if __name__ == "__main__":
    main()