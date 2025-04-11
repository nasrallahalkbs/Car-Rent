"""
تحديث صفحة بوابة الدفع لإظهار خيار التحويل البنكي بشكل أوضح
"""

import os
import re

def update_payment_gateway_html():
    """تحديث قالب بوابة الدفع لإبراز خيار التحويل البنكي"""
    file_path = 'templates/payment_gateway.html'
    
    if not os.path.exists(file_path):
        print(f"الملف {file_path} غير موجود")
        return False
    
    # قراءة محتوى الملف
    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()
    
    # البحث عن قسم خيارات الدفع وإضافة فئة خاصة للتحويل البنكي
    payment_options_pattern = r'(<div class="upg-payment-options[^"]*">)'
    
    # إضافة أسلوب CSS لتمييز طريقة الدفع عبر التحويل البنكي
    css_highlight = """
<style>
.upg-payment-option-highlight {
    position: relative;
    border: 2px solid var(--pg-primary);
    border-radius: 15px;
    padding: 10px;
    margin-bottom: 20px;
    background: linear-gradient(to bottom, rgba(219, 234, 254, 0.2), rgba(255, 255, 255, 1));
}

.upg-payment-option-highlight::before {
    content: "{% if is_english %}Recommended{% else %}موصى به{% endif %}";
    position: absolute;
    top: -12px;
    left: 50%;
    transform: translateX(-50%);
    background-color: var(--pg-primary);
    color: white;
    padding: 2px 15px;
    border-radius: 15px;
    font-size: 0.8rem;
    font-weight: bold;
    z-index: 1;
    white-space: nowrap;
}

.upg-bank-transfer-info-section {
    background-color: #f8f9fa;
    border: 1px solid #dee2e6;
    border-radius: 10px;
    padding: 20px;
    margin-top: 20px;
    margin-bottom: 30px;
}

.upg-bank-transfer-info-section h4 {
    margin-bottom: 15px;
    color: var(--pg-primary);
}
</style>
"""
    
    # تحديث القسم العلوي لإضافة الأسلوب
    if '</style>' in content:
        new_content = content.replace('</style>', '</style>' + css_highlight)
    else:
        new_content = content.replace('{% block extra_css %}', '{% block extra_css %}' + css_highlight)
    
    # إضافة قسم معلومات التحويل البنكي المختصرة والمميزة
    bank_transfer_highlight = """
<!-- قسم معلومات التحويل البنكي المميز -->
<div class="upg-bank-transfer-info-section">
    <div class="row align-items-center">
        <div class="col-md-8">
            <h4><i class="fas fa-university me-2"></i> {% if is_english %}Bank Transfer Payment{% else %}الدفع عبر التحويل البنكي{% endif %}</h4>
            <p>{% if is_english %}You can now pay securely via bank transfer - view complete account details and transfer instructions.{% else %}يمكنك الآن الدفع بأمان عبر التحويل البنكي - اعرض تفاصيل الحساب الكاملة وتعليمات التحويل.{% endif %}</p>
            <ul class="list-unstyled mb-0">
                <li><i class="fas fa-check-circle text-success me-2"></i> {% if is_english %}Secure and reliable payment method{% else %}طريقة دفع آمنة وموثوقة{% endif %}</li>
                <li><i class="fas fa-check-circle text-success me-2"></i> {% if is_english %}Clear tracking of your payment{% else %}تتبع واضح لعملية الدفع الخاصة بك{% endif %}</li>
                <li><i class="fas fa-check-circle text-success me-2"></i> {% if is_english %}Full support from our customer service{% else %}دعم كامل من خدمة العملاء لدينا{% endif %}</li>
            </ul>
        </div>
        <div class="col-md-4 text-md-end">
            <a href="{% url 'bank_transfer_payment' %}{% if reservation_id %}?reservation_id={{ reservation_id }}{% endif %}" class="btn btn-primary btn-lg">
                {% if is_english %}Go to Bank Transfer{% else %}انتقل إلى التحويل البنكي{% endif %}
            </a>
        </div>
    </div>
</div>
"""
    
    # إضافة القسم المميز قبل الفورم
    form_pattern = r'(<form[^>]*id="payment-form"[^>]*>)'
    if re.search(form_pattern, new_content):
        new_content = re.sub(form_pattern, bank_transfer_highlight + r'\1', new_content)
    
    # تحديث خيار التحويل البنكي ليكون مميزًا عن باقي الخيارات
    bank_transfer_option_pattern = r'(<div class="upg-payment-option">\s*<input[^>]*value="bank_transfer"[^>]*>[\s\S]*?</div>\s*</div>)'
    
    if re.search(bank_transfer_option_pattern, new_content):
        new_content = re.sub(bank_transfer_option_pattern, r'<div class="upg-payment-option-highlight">\1</div>', new_content)
    
    # حفظ التغييرات
    with open(file_path, 'w', encoding='utf-8') as file:
        file.write(new_content)
    
    print("تم تحديث قالب بوابة الدفع لإبراز خيار التحويل البنكي بنجاح")
    return True

def main():
    """تنفيذ الدالة الرئيسية للسكريبت"""
    update_payment_gateway_html()

if __name__ == "__main__":
    main()