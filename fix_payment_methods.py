"""
إضافة دعم التحويل البنكي إلى قائمة طرق الدفع المتاحة
هذا السكريبت يقوم بتحديث ملف payment_views.py لإضافة دعم التحويل البنكي
"""

import re
import os

def add_bank_transfer_method():
    """
    إضافة طريقة الدفع عبر التحويل البنكي إلى ملف views.py
    """
    file_path = 'rental/payment_views.py'
    
    if not os.path.exists(file_path):
        print(f"الملف {file_path} غير موجود")
        return False
    
    # قراءة محتوى الملف
    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()
    
    # إضافة التحويل البنكي إلى قاموس أسماء الطرق باللغة الإنجليزية
    pattern_en = r"method_names = \{'credit_card': 'Credit Card', 'paypal': 'PayPal', 'apple_pay': 'Apple Pay', 'google_pay': 'Google Pay'\}"
    replacement_en = """method_names = {
                    'credit_card': 'Credit Card', 
                    'bank_transfer': 'Bank Transfer',
                    'paypal': 'PayPal', 
                    'apple_pay': 'Apple Pay', 
                    'google_pay': 'Google Pay'
                }"""
    
    # إضافة التحويل البنكي إلى قاموس أسماء الطرق باللغة العربية
    pattern_ar = r"method_names = \{'credit_card': 'بطاقة ائتمان', 'paypal': 'باي بال', 'apple_pay': 'آبل باي', 'google_pay': 'جوجل باي'\}"
    replacement_ar = """method_names = {
                    'credit_card': 'بطاقة ائتمان', 
                    'bank_transfer': 'تحويل بنكي',
                    'paypal': 'باي بال', 
                    'apple_pay': 'آبل باي', 
                    'google_pay': 'جوجل باي'
                }"""
    
    # استبدال النصوص
    modified_content = re.sub(pattern_en, replacement_en, content)
    modified_content = re.sub(pattern_ar, replacement_ar, modified_content)
    
    # كتابة المحتوى المعدل إلى الملف
    with open(file_path, 'w', encoding='utf-8') as file:
        file.write(modified_content)
    
    print("تم إضافة دعم التحويل البنكي بنجاح")
    return True

def add_bank_transfer_template():
    """
    إضافة قالب صفحة التحويل البنكي
    """
    file_path = 'templates/payment_bank_transfer.html'
    
    bank_transfer_template = """{% extends 'base.html' %}
{% load static %}

{% block title %}
{% if is_english %}Bank Transfer Payment{% else %}الدفع عبر التحويل البنكي{% endif %}
{% endblock %}

{% block styles %}
<link rel="stylesheet" href="{% static 'css/payment.css' %}">
<style>
    .bank-info {
        background-color: var(--light-bg);
        border-radius: 8px;
        padding: 20px;
        margin-bottom: 20px;
    }
    .bank-info p {
        margin-bottom: 10px;
    }
    .bank-note {
        background-color: var(--bs-warning-bg-subtle);
        border-left: 4px solid var(--bs-warning);
        padding: 15px;
        margin-top: 20px;
        border-radius: 4px;
    }
    .verification-form {
        background-color: var(--light-bg);
        border-radius: 8px;
        padding: 20px;
        margin-top: 30px;
    }
</style>
{% endblock %}

{% block content %}
<div class="container my-5">
    <div class="row justify-content-center">
        <div class="col-lg-10">
            <div class="card shadow-sm">
                <div class="card-body p-lg-5">
                    <div class="text-center mb-4">
                        <h2 class="card-title">
                            {% if is_english %}Bank Transfer Payment{% else %}الدفع عبر التحويل البنكي{% endif %}
                        </h2>
                        <p class="text-muted">
                            {% if is_english %}
                            Please transfer the amount of <strong>${{ total_amount }}</strong> to our bank account.
                            {% else %}
                            يرجى تحويل مبلغ <strong>${{ total_amount }}</strong> إلى حسابنا البنكي.
                            {% endif %}
                        </p>
                    </div>
                    
                    <div class="bank-info">
                        <h4 class="mb-3">
                            {% if is_english %}Bank Account Details{% else %}تفاصيل الحساب البنكي{% endif %}
                        </h4>
                        <p><strong>{% if is_english %}Bank Name{% else %}اسم البنك{% endif %}:</strong> International Bank of Car Rentals</p>
                        <p><strong>{% if is_english %}Account Name{% else %}اسم الحساب{% endif %}:</strong> CarRental LLC</p>
                        <p><strong>{% if is_english %}Account Number{% else %}رقم الحساب{% endif %}:</strong> 1234567890</p>
                        <p><strong>{% if is_english %}IBAN{% else %}رقم الآيبان{% endif %}:</strong> SA12 3456 7890 1234 5678 9012</p>
                        <p><strong>{% if is_english %}SWIFT/BIC Code{% else %}رمز السويفت{% endif %}:</strong> CRLBNK123</p>
                        <p><strong>{% if is_english %}Branch{% else %}الفرع{% endif %}:</strong> Main Branch</p>
                    </div>
                    
                    <div class="bank-note">
                        <h5 class="mb-2">
                            {% if is_english %}Important{% else %}هام{% endif %}
                        </h5>
                        <p>
                            {% if is_english %}
                            Please include your reservation ID <strong>#{{ reservation.id }}</strong> in the payment reference field when making the transfer.
                            {% else %}
                            يرجى تضمين رقم الحجز <strong>#{{ reservation.id }}</strong> في حقل المرجع عند إجراء التحويل.
                            {% endif %}
                        </p>
                        <p class="mb-0">
                            {% if is_english %}
                            After completing the transfer, please fill out the form below to confirm your payment.
                            {% else %}
                            بعد إتمام التحويل، يرجى ملء النموذج أدناه لتأكيد الدفع الخاص بك.
                            {% endif %}
                        </p>
                    </div>
                    
                    <div class="verification-form">
                        <form method="post" action="{% url 'payment_gateway' %}?reservation_id={{ reservation.id }}">
                            {% csrf_token %}
                            <input type="hidden" name="payment_method" value="bank_transfer">
                            
                            <div class="mb-3">
                                <label for="transfer_date" class="form-label">
                                    {% if is_english %}Transfer Date{% else %}تاريخ التحويل{% endif %}
                                </label>
                                <input type="date" class="form-control" id="transfer_date" name="transfer_date" required>
                            </div>
                            
                            <div class="mb-3">
                                <label for="transfer_reference" class="form-label">
                                    {% if is_english %}Transfer Reference Number{% else %}رقم مرجع التحويل{% endif %}
                                </label>
                                <input type="text" class="form-control" id="transfer_reference" name="transfer_reference" required>
                            </div>
                            
                            <div class="mb-3">
                                <label for="bank_name" class="form-label">
                                    {% if is_english %}Your Bank Name{% else %}اسم البنك الخاص بك{% endif %}
                                </label>
                                <input type="text" class="form-control" id="bank_name" name="bank_name" required>
                            </div>
                            
                            <div class="mb-3">
                                <label for="transfer_amount" class="form-label">
                                    {% if is_english %}Transfer Amount{% else %}مبلغ التحويل{% endif %}
                                </label>
                                <div class="input-group">
                                    <span class="input-group-text">$</span>
                                    <input type="number" step="0.01" class="form-control" id="transfer_amount" name="transfer_amount" 
                                        value="{{ total_amount }}" required>
                                </div>
                            </div>
                            
                            <div class="mb-3">
                                <label for="notes" class="form-label">
                                    {% if is_english %}Additional Notes{% else %}ملاحظات إضافية{% endif %}
                                </label>
                                <textarea class="form-control" id="notes" name="notes" rows="3"></textarea>
                            </div>
                            
                            <div class="d-grid gap-2">
                                <button type="submit" class="btn btn-primary py-3">
                                    {% if is_english %}
                                    Confirm Bank Transfer
                                    {% else %}
                                    تأكيد التحويل البنكي
                                    {% endif %}
                                </button>
                            </div>
                        </form>
                    </div>
                </div>
            </div>
        </div>
    </div>
</div>
{% endblock %}
"""
    
    # إنشاء القالب
    with open(file_path, 'w', encoding='utf-8') as file:
        file.write(bank_transfer_template)
    
    print("تم إنشاء قالب التحويل البنكي بنجاح")
    return True

def add_bank_transfer_route():
    """
    إضافة مسار جديد لصفحة التحويل البنكي
    """
    file_path = 'rental/urls.py'
    
    if not os.path.exists(file_path):
        print(f"الملف {file_path} غير موجود")
        return False
    
    # قراءة محتوى الملف
    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()
    
    # البحث عن نمط مسارات الدفع للإضافة بعدها
    payment_routes_pattern = r"(path\('payment/paypal/', payment_views\.paypal_payment, name='paypal_payment'\),)"
    bank_transfer_route = r"\1\n    path('payment/bank-transfer/', payment_views.bank_transfer_payment, name='bank_transfer_payment'),"
    
    # إضافة المسار الجديد
    modified_content = re.sub(payment_routes_pattern, bank_transfer_route, content)
    
    # حفظ التغييرات
    with open(file_path, 'w', encoding='utf-8') as file:
        file.write(modified_content)
    
    print("تم إضافة مسار التحويل البنكي بنجاح")
    return True

def add_bank_transfer_view():
    """
    إضافة الدالة المسؤولة عن عرض صفحة التحويل البنكي في ملف payment_views.py
    """
    file_path = 'rental/payment_views.py'
    
    if not os.path.exists(file_path):
        print(f"الملف {file_path} غير موجود")
        return False
    
    # قراءة محتوى الملف
    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()
    
    # دالة عرض صفحة التحويل البنكي
    bank_transfer_view = """
@login_required
def bank_transfer_payment(request):
    """
    Bank transfer payment interface
    Allows users to view bank account details and enter transfer details
    """
    # التحقق مما إذا كان المستخدم يأتي من حجز محدد
    reservation_id = request.GET.get('reservation_id')
    
    # تحديد لغة المستخدم
    current_language = get_language()
    is_english = current_language == 'en'
    is_rtl = current_language == 'ar'
    
    if not reservation_id:
        # إذا لم يتم تحديد معرف الحجز، إعادة توجيه المستخدم إلى صفحة الحجوزات
        messages.error(
            request, 
            "Reservation ID is required for bank transfer payment." if is_english else 
            "رقم الحجز مطلوب للدفع عبر التحويل البنكي."
        )
        return redirect('my_reservations')
    
    # الحصول على تفاصيل الحجز
    reservation = get_object_or_404(
        Reservation, 
        id=reservation_id, 
        user=request.user, 
        status='confirmed', 
        payment_status='pending'
    )
    
    context = {
        'reservation': reservation,
        'total_amount': reservation.total_price,
        'is_english': is_english,
        'is_rtl': is_rtl
    }
    
    return render(request, 'payment_bank_transfer.html', context)
"""
    
    # إضافة الدالة الجديدة في نهاية الملف
    modified_content = content + bank_transfer_view
    
    # حفظ التغييرات
    with open(file_path, 'w', encoding='utf-8') as file:
        file.write(modified_content)
    
    print("تم إضافة دالة عرض صفحة التحويل البنكي بنجاح")
    return True

def update_payment_gateway_view():
    """
    تحديث دالة payment_gateway في ملف payment_views.py لإضافة معالجة التحويل البنكي
    """
    file_path = 'rental/payment_views.py'
    
    if not os.path.exists(file_path):
        print(f"الملف {file_path} غير موجود")
        return False
    
    # قراءة محتوى الملف
    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()
    
    # إضافة معالجة التحويل البنكي بعد التحقق من بيانات البطاقة الائتمانية
    bank_transfer_processing_pattern = r"(# التحقق من بيانات البطاقة إذا كانت وسيلة الدفع هي البطاقة الائتمانية\s+if payment_method == 'credit_card':.*?)(# في الحالة الحقيقية، هنا سيتم الاتصال بخدمة معالجة الدفع)"
    bank_transfer_processing = r"\1# معالجة التحويل البنكي\n            elif payment_method == 'bank_transfer':\n                transfer_date = request.POST.get('transfer_date')\n                transfer_reference = request.POST.get('transfer_reference')\n                bank_name = request.POST.get('bank_name')\n                transfer_amount = request.POST.get('transfer_amount')\n                \n                # التحقق من إدخال البيانات المطلوبة\n                if not all([transfer_date, transfer_reference, bank_name, transfer_amount]):\n                    if is_english:\n                        error_message = 'Please fill in all bank transfer details.'\n                    else:\n                        error_message = 'يرجى ملء جميع تفاصيل التحويل البنكي.'\n                    \n                    messages.error(request, error_message)\n                    return redirect(f'/payment/bank-transfer/?reservation_id={reservation_id}')\n                \n                # إضافة بيانات التحويل البنكي إلى السجل (في التطبيق الحقيقي)\n                # هنا يمكن تخزين بيانات التحويل في نموذج منفصل أو في حقول إضافية في نموذج الحجز\n                \n                # في هذا المثال، نفترض أن التحويل تم بنجاح ونقوم بإنشاء رقم مرجعي للدفع\n                payment_reference = f\"BT-{uuid.uuid4().hex[:8].upper()}\"\n            \n            \2"
    
    # استبدال النص
    modified_content = re.sub(bank_transfer_processing_pattern, bank_transfer_processing, content, flags=re.DOTALL)
    
    # حفظ التغييرات
    with open(file_path, 'w', encoding='utf-8') as file:
        file.write(modified_content)
    
    print("تم تحديث دالة payment_gateway لدعم التحويل البنكي بنجاح")
    return True

def main():
    """تنفيذ الدالة الرئيسية للسكريبت"""
    print("بدء إضافة دعم التحويل البنكي...")
    
    # إضافة التحويل البنكي إلى قائمة طرق الدفع
    add_bank_transfer_method()
    
    # إضافة قالب صفحة التحويل البنكي
    add_bank_transfer_template()
    
    # إضافة مسار صفحة التحويل البنكي
    add_bank_transfer_route()
    
    # إضافة دالة عرض صفحة التحويل البنكي
    add_bank_transfer_view()
    
    # تحديث دالة payment_gateway لمعالجة التحويل البنكي
    update_payment_gateway_view()
    
    print("تم إضافة دعم التحويل البنكي بنجاح!")

if __name__ == "__main__":
    main()