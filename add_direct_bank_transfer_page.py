"""
إنشاء صفحة وصول مباشر للتحويل البنكي متاحة من الصفحة الرئيسية
"""

import os
import re

def create_bank_transfer_page():
    """إنشاء صفحة مباشرة للتحويل البنكي"""
    file_path = 'templates/bank_transfer_info.html'
    
    bank_transfer_template = """{% extends 'layout_django.html' %}
{% load static %}

{% block title %}
{% if is_english %}Bank Transfer Information{% else %}معلومات التحويل البنكي{% endif %}
{% endblock %}

{% block content %}
<div class="container my-5">
    <div class="row justify-content-center">
        <div class="col-lg-10">
            <div class="card shadow">
                <div class="card-header bg-primary text-white py-3">
                    <h3 class="card-title mb-0">
                        {% if is_english %}Bank Transfer Payment{% else %}الدفع عبر التحويل البنكي{% endif %}
                    </h3>
                </div>
                <div class="card-body p-4">
                    <div class="row mb-4">
                        <div class="col-md-6">
                            <div class="p-4 bg-light rounded">
                                <h4 class="mb-3">
                                    {% if is_english %}Bank Account Details{% else %}تفاصيل الحساب البنكي{% endif %}
                                </h4>
                                <div class="mb-3">
                                    <p class="mb-1"><strong>{% if is_english %}Bank Name{% else %}اسم البنك{% endif %}:</strong> International Bank of Car Rentals</p>
                                    <p class="mb-1"><strong>{% if is_english %}Account Name{% else %}اسم الحساب{% endif %}:</strong> CarRental LLC</p>
                                    <p class="mb-1"><strong>{% if is_english %}Account Number{% else %}رقم الحساب{% endif %}:</strong> 1234567890</p>
                                    <p class="mb-1"><strong>{% if is_english %}IBAN{% else %}رقم الآيبان{% endif %}:</strong> SA12 3456 7890 1234 5678 9012</p>
                                    <p class="mb-1"><strong>{% if is_english %}SWIFT/BIC Code{% else %}رمز السويفت{% endif %}:</strong> CRLBNK123</p>
                                    <p class="mb-0"><strong>{% if is_english %}Branch{% else %}الفرع{% endif %}:</strong> Main Branch</p>
                                </div>
                            </div>
                        </div>
                        <div class="col-md-6">
                            <div class="p-4 bg-warning-subtle rounded">
                                <h4 class="mb-3">{% if is_english %}Important Information{% else %}معلومات هامة{% endif %}</h4>
                                <ul class="mb-0">
                                    <li class="mb-2">{% if is_english %}Include your name and phone number as reference{% else %}قم بتضمين اسمك ورقم هاتفك كمرجع{% endif %}</li>
                                    <li class="mb-2">{% if is_english %}Processing time: 1-2 business days{% else %}وقت المعالجة: 1-2 يوم عمل{% endif %}</li>
                                    <li class="mb-2">{% if is_english %}After transferring, submit your payment details through the form{% else %}بعد التحويل، قم بتقديم تفاصيل الدفع من خلال النموذج{% endif %}</li>
                                    <li>{% if is_english %}You will receive a confirmation email after verification{% else %}ستتلقى بريدًا إلكترونيًا للتأكيد بعد التحقق{% endif %}</li>
                                </ul>
                            </div>
                        </div>
                    </div>
                    
                    <div class="row">
                        <div class="col-12">
                            <div class="alert alert-info" role="alert">
                                <h5 class="alert-heading">{% if is_english %}How it works{% else %}كيف يعمل{% endif %}</h5>
                                <p>
                                    {% if is_english %}
                                    After completing your transfer, please fill out the form below to notify us and provide your transfer details. Our team will verify the payment and update your booking status accordingly.
                                    {% else %}
                                    بعد إتمام التحويل، يرجى ملء النموذج أدناه لإخطارنا وتقديم تفاصيل التحويل الخاص بك. سيقوم فريقنا بالتحقق من الدفع وتحديث حالة الحجز الخاص بك وفقًا لذلك.
                                    {% endif %}
                                </p>
                            </div>
                        </div>
                    </div>
                    
                    <div class="mt-4">
                        <div class="text-center">
                            <h4 class="mb-4">{% if is_english %}Submit Payment Details{% else %}تقديم تفاصيل الدفع{% endif %}</h4>
                        </div>
                        <div class="row justify-content-center">
                            <div class="col-md-8">
                                <form method="post" action="{% url 'payment_gateway' %}" class="mb-0">
                                    {% csrf_token %}
                                    <input type="hidden" name="payment_method" value="bank_transfer">
                                    
                                    <div class="mb-3">
                                        <label for="full_name" class="form-label">{% if is_english %}Full Name{% else %}الاسم الكامل{% endif %}</label>
                                        <input type="text" class="form-control" id="full_name" name="full_name" required>
                                    </div>
                                    
                                    <div class="mb-3">
                                        <label for="email" class="form-label">{% if is_english %}Email{% else %}البريد الإلكتروني{% endif %}</label>
                                        <input type="email" class="form-control" id="email" name="email" required>
                                    </div>
                                    
                                    <div class="mb-3">
                                        <label for="phone" class="form-label">{% if is_english %}Phone Number{% else %}رقم الهاتف{% endif %}</label>
                                        <input type="tel" class="form-control" id="phone" name="phone" required>
                                    </div>
                                    
                                    <div class="row mb-3">
                                        <div class="col-md-6">
                                            <label for="transfer_date" class="form-label">{% if is_english %}Transfer Date{% else %}تاريخ التحويل{% endif %}</label>
                                            <input type="date" class="form-control" id="transfer_date" name="transfer_date" required>
                                        </div>
                                        <div class="col-md-6">
                                            <label for="transfer_amount" class="form-label">{% if is_english %}Amount Transferred{% else %}المبلغ المحول{% endif %}</label>
                                            <div class="input-group">
                                                <span class="input-group-text">$</span>
                                                <input type="number" step="0.01" min="0" class="form-control" id="transfer_amount" name="transfer_amount" required>
                                            </div>
                                        </div>
                                    </div>
                                    
                                    <div class="mb-3">
                                        <label for="transfer_reference" class="form-label">{% if is_english %}Transfer Reference/ID{% else %}مرجع/معرف التحويل{% endif %}</label>
                                        <input type="text" class="form-control" id="transfer_reference" name="transfer_reference" required>
                                    </div>
                                    
                                    <div class="mb-4">
                                        <label for="notes" class="form-label">{% if is_english %}Additional Notes{% else %}ملاحظات إضافية{% endif %}</label>
                                        <textarea class="form-control" id="notes" name="notes" rows="3"></textarea>
                                    </div>
                                    
                                    <div class="d-grid gap-2">
                                        <button type="submit" class="btn btn-primary py-3">
                                            {% if is_english %}Submit Payment Information{% else %}إرسال معلومات الدفع{% endif %}
                                        </button>
                                        <a href="{% url 'index' %}" class="btn btn-outline-secondary">
                                            {% if is_english %}Back to Home{% else %}العودة إلى الصفحة الرئيسية{% endif %}
                                        </a>
                                    </div>
                                </form>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
            
            <div class="card mt-4 shadow">
                <div class="card-header bg-light py-3">
                    <h4 class="card-title mb-0">{% if is_english %}Frequently Asked Questions{% else %}الأسئلة الشائعة{% endif %}</h4>
                </div>
                <div class="card-body p-4">
                    <div class="accordion" id="accordionFAQ">
                        <div class="accordion-item">
                            <h2 class="accordion-header">
                                <button class="accordion-button" type="button" data-bs-toggle="collapse" data-bs-target="#collapseOne" aria-expanded="true" aria-controls="collapseOne">
                                    {% if is_english %}How long does it take to process a bank transfer?{% else %}كم من الوقت يستغرق معالجة التحويل البنكي؟{% endif %}
                                </button>
                            </h2>
                            <div id="collapseOne" class="accordion-collapse collapse show" data-bs-parent="#accordionFAQ">
                                <div class="accordion-body">
                                    {% if is_english %}
                                    Bank transfers typically take 1-2 business days to process. Once we receive and verify your payment, we'll update your reservation status and send you a confirmation email.
                                    {% else %}
                                    عادة ما تستغرق التحويلات البنكية من 1 إلى 2 يوم عمل للمعالجة. بمجرد استلام الدفعة والتحقق منها، سنقوم بتحديث حالة الحجز الخاص بك وإرسال بريد إلكتروني للتأكيد.
                                    {% endif %}
                                </div>
                            </div>
                        </div>
                        <div class="accordion-item">
                            <h2 class="accordion-header">
                                <button class="accordion-button collapsed" type="button" data-bs-toggle="collapse" data-bs-target="#collapseTwo" aria-expanded="false" aria-controls="collapseTwo">
                                    {% if is_english %}What should I do if I made a mistake in my transfer details?{% else %}ماذا أفعل إذا ارتكبت خطأ في تفاصيل التحويل الخاصة بي؟{% endif %}
                                </button>
                            </h2>
                            <div id="collapseTwo" class="accordion-collapse collapse" data-bs-parent="#accordionFAQ">
                                <div class="accordion-body">
                                    {% if is_english %}
                                    If you made a mistake, please contact our customer service immediately at support@carrental.com or call our hotline at +1-234-567-8900. We'll help resolve any issues related to your payment.
                                    {% else %}
                                    إذا ارتكبت خطأ، يرجى الاتصال بخدمة العملاء على الفور على support@carrental.com أو الاتصال بالخط الساخن على +1-234-567-8900. سنساعد في حل أي مشكلات متعلقة بالدفع الخاص بك.
                                    {% endif %}
                                </div>
                            </div>
                        </div>
                        <div class="accordion-item">
                            <h2 class="accordion-header">
                                <button class="accordion-button collapsed" type="button" data-bs-toggle="collapse" data-bs-target="#collapseThree" aria-expanded="false" aria-controls="collapseThree">
                                    {% if is_english %}Is bank transfer secure?{% else %}هل التحويل البنكي آمن؟{% endif %}
                                </button>
                            </h2>
                            <div id="collapseThree" class="accordion-collapse collapse" data-bs-parent="#accordionFAQ">
                                <div class="accordion-body">
                                    {% if is_english %}
                                    Yes, bank transfers are one of the most secure payment methods. They're processed through established banking systems with multiple security protocols. Additionally, you will receive a confirmation and transaction record for your payment.
                                    {% else %}
                                    نعم، التحويلات البنكية هي من أكثر طرق الدفع أمانًا. تتم معالجتها من خلال أنظمة مصرفية راسخة مع بروتوكولات أمان متعددة. بالإضافة إلى ذلك، ستتلقى تأكيداً وسجلاً للمعاملة الخاصة بالدفع.
                                    {% endif %}
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>
</div>
{% endblock %}"""
    
    # إنشاء القالب
    with open(file_path, 'w', encoding='utf-8') as file:
        file.write(bank_transfer_template)
    
    print("تم إنشاء صفحة معلومات التحويل البنكي بنجاح")
    return True

def add_route_to_urls():
    """إضافة مسار لصفحة معلومات التحويل البنكي"""
    file_path = 'rental/urls.py'
    
    if not os.path.exists(file_path):
        print(f"الملف {file_path} غير موجود")
        return False
    
    # قراءة محتوى الملف
    with open(file_path, 'r', encoding='utf-8') as file:
        lines = file.readlines()
    
    # إضافة مسار جديد بعد مسار about-us
    new_lines = []
    for line in lines:
        new_lines.append(line)
        if "path('about-us/'" in line:
            new_lines.append("    path('bank-transfer-info/', views.bank_transfer_info, name='bank_transfer_info'),\n")
    
    # كتابة المحتوى المعدل
    with open(file_path, 'w', encoding='utf-8') as file:
        file.writelines(new_lines)
    
    print("تم إضافة مسار صفحة معلومات التحويل البنكي بنجاح")
    return True

def add_view_to_views():
    """إضافة دالة عرض لصفحة معلومات التحويل البنكي"""
    file_path = 'rental/views.py'
    
    if not os.path.exists(file_path):
        print(f"الملف {file_path} غير موجود")
        return False
    
    # قراءة محتوى الملف
    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()
    
    # دالة عرض صفحة معلومات التحويل البنكي
    view_function = """
def bank_transfer_info(request):
    # Get user language
    from django.utils.translation import get_language
    current_language = get_language()
    is_english = current_language == 'en'
    is_rtl = current_language == 'ar'
    
    context = {
        'is_english': is_english,
        'is_rtl': is_rtl
    }
    
    return render(request, 'bank_transfer_info.html', context)
"""
    
    # إضافة الدالة في نهاية الملف
    with open(file_path, 'a', encoding='utf-8') as file:
        file.write(view_function)
    
    print("تم إضافة دالة عرض صفحة معلومات التحويل البنكي بنجاح")
    return True

def add_link_to_navbar():
    """إضافة رابط صفحة معلومات التحويل البنكي في القائمة الرئيسية"""
    file_path = 'templates/layout_django.html'
    
    if not os.path.exists(file_path):
        print(f"الملف {file_path} غير موجود")
        return False
    
    # قراءة محتوى الملف
    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()
    
    # البحث عن موضع القائمة الرئيسية
    nav_link_pattern = r'(<a class="nav-link" href="{% url \'about_us\' %}">[^<]*</a>\s*</li>)'
    bank_transfer_link = """
                <li class="nav-item">
                    <a class="nav-link" href="{% url 'bank_transfer_info' %}">
                        <i class="fas fa-university me-1"></i>
                        {% if is_english %}Bank Transfer Info{% else %}معلومات التحويل البنكي{% endif %}
                    </a>
                </li>
    """
    
    # إضافة الرابط بعد رابط About Us
    if re.search(nav_link_pattern, content):
        new_content = re.sub(nav_link_pattern, r'\1' + bank_transfer_link, content)
        
        # حفظ التغييرات
        with open(file_path, 'w', encoding='utf-8') as file:
            file.write(new_content)
        
        print("تم إضافة رابط صفحة معلومات التحويل البنكي إلى القائمة الرئيسية بنجاح")
        return True
    else:
        print("لم يتم العثور على رابط About Us في القائمة الرئيسية")
        return False

def main():
    """تنفيذ الدالة الرئيسية للسكريبت"""
    print("بدء إنشاء صفحة معلومات التحويل البنكي...")
    
    create_bank_transfer_page()
    add_route_to_urls()
    add_view_to_views()
    add_link_to_navbar()
    
    print("تم إنشاء صفحة معلومات التحويل البنكي بنجاح!")

if __name__ == "__main__":
    main()