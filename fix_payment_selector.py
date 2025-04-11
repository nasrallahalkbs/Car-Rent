"""
إصلاح مباشر لقسم اختيار طريقة الدفع في صفحة بوابة الدفع
"""

def fix_payment_options():
    """إصلاح اختيار طريقة الدفع وتوفير التحويل البنكي كخيار رئيسي"""
    file_path = 'templates/payment_gateway.html'
    
    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()
    
    # البحث عن قسم اختيار طريقة الدفع بواسطة النص المميز
    payment_options_section_start = content.find('{% if is_english %}Select Payment Method{% else %}اختر وسيلة الدفع{% endif %}')
    if payment_options_section_start == -1:
        print("لم يتم العثور على قسم طرق الدفع")
        return False
    
    # أسلوب البطاقة الجديدة
    new_styling = """
<style>
/* Payment Method Selector Styles */
.payment-method-selector {
    margin-bottom: 2rem;
}

.payment-method-card {
    border: 1px solid #e0e0e0;
    border-radius: 12px;
    padding: 15px;
    margin-bottom: 15px;
    cursor: pointer;
    transition: all 0.3s ease;
    position: relative;
    overflow: hidden;
}

.payment-method-card:hover {
    transform: translateY(-3px);
    box-shadow: 0 5px 15px rgba(0,0,0,0.1);
}

.payment-method-card.selected {
    border-color: #2563eb;
    background-color: rgba(219, 234, 254, 0.2);
    box-shadow: 0 5px 15px rgba(37, 99, 235, 0.1);
}

.payment-method-card.selected::after {
    content: '';
    position: absolute;
    top: -2px;
    right: -2px;
    width: 30px;
    height: 30px;
    background-color: #2563eb;
    transform: rotate(45deg) translate(20px, -20px);
}

.payment-method-card.selected::before {
    content: '✓';
    position: absolute;
    top: 3px;
    right: 5px;
    color: white;
    font-size: 12px;
    z-index: 1;
}

.payment-method-card .payment-icon {
    font-size: 24px;
    margin-right: 15px;
    width: 40px;
    text-align: center;
}

.payment-method-header {
    display: flex;
    align-items: center;
    margin-bottom: 10px;
}

.payment-method-title {
    font-size: 16px;
    font-weight: 600;
    margin: 0;
}

.payment-method-description {
    font-size: 14px;
    color: #6b7280;
    margin: 0;
}

.payment-bank-method {
    border: 2px solid #2563eb;
    border-radius: 12px;
    position: relative;
}

.payment-bank-method::before {
    content: '{% if is_english %}Recommended{% else %}موصى به{% endif %}';
    position: absolute;
    top: -12px;
    left: 50%;
    transform: translateX(-50%);
    background-color: #2563eb;
    color: white;
    padding: 2px 15px;
    border-radius: 15px;
    font-size: 12px;
    font-weight: bold;
    z-index: 1;
}

.rtl .payment-method-header .payment-icon {
    margin-right: 0;
    margin-left: 15px;
}

.payment-method-info {
    display: flex;
    justify-content: space-between;
    align-items: center;
}

.payment-method-badge {
    background-color: rgba(37, 99, 235, 0.1);
    color: #2563eb;
    font-size: 12px;
    padding: 2px 8px;
    border-radius: 10px;
}

.payment-bank-badge {
    background-color: rgba(16, 185, 129, 0.1);
    color: #10b981;
}

.payment-direct-button {
    display: block;
    width: 100%;
    margin-top: 10px;
    padding: 8px 0;
    text-align: center;
    background-color: #2563eb;
    color: white;
    border-radius: 8px;
    font-weight: 500;
    transition: all 0.3s ease;
}

.payment-direct-button:hover {
    background-color: #1d4ed8;
    text-decoration: none;
    color: white;
}
</style>
"""
    
    # إضافة الأسلوب الجديد قبل نهاية قسم الأساليب
    style_position = content.find('</style>')
    if style_position != -1:
        content = content[:style_position] + new_styling + content[style_position:]
    else:
        css_block_end = content.find('{% endblock extra_css %}')
        if css_block_end != -1:
            content = content[:css_block_end] + new_styling + content[css_block_end:]
    
    # محتوى قسم اختيار طريقة الدفع الجديد
    new_payment_selector = """
<div class="section mb-4" id="payment-methods-section">
    <h3 class="section-title mb-3">{% if is_english %}Select Payment Method{% else %}اختر طريقة الدفع{% endif %}</h3>
    
    <div class="payment-method-selector">
        <!-- طريقة الدفع: التحويل البنكي -->
        <div class="payment-method-card payment-bank-method mb-4">
            <div class="payment-method-header">
                <div class="payment-icon text-primary">
                    <i class="fas fa-university"></i>
                </div>
                <div>
                    <h4 class="payment-method-title">{% if is_english %}Bank Transfer{% else %}تحويل بنكي{% endif %}</h4>
                    <p class="payment-method-description">{% if is_english %}Secure bank transfer with account details{% else %}تحويل بنكي آمن مع تفاصيل الحساب{% endif %}</p>
                </div>
            </div>
            <div class="payment-method-info">
                <span class="payment-method-badge payment-bank-badge">{% if is_english %}1-2 business days{% else %}1-2 يوم عمل{% endif %}</span>
            </div>
            <a href="{% url 'bank_transfer_payment' %}{% if reservation_id %}?reservation_id={{ reservation_id }}{% endif %}" class="payment-direct-button mt-3">
                {% if is_english %}Pay via Bank Transfer{% else %}الدفع عبر التحويل البنكي{% endif %}
            </a>
        </div>
        
        <!-- طريقة الدفع: بطاقة ائتمان -->
        <div class="payment-method-card selected" onclick="selectPaymentMethod('credit_card')">
            <input type="radio" id="payment_method_credit_card" name="payment_method" value="credit_card" class="d-none" checked>
            <div class="payment-method-header">
                <div class="payment-icon text-primary">
                    <i class="fas fa-credit-card"></i>
                </div>
                <div>
                    <h4 class="payment-method-title">{% if is_english %}Credit Card{% else %}بطاقة ائتمان{% endif %}</h4>
                    <p class="payment-method-description">{% if is_english %}Pay securely with your credit card{% else %}ادفع بأمان باستخدام بطاقتك الائتمانية{% endif %}</p>
                </div>
            </div>
            <div class="payment-method-info">
                <span class="payment-method-badge">{% if is_english %}Instant{% else %}فوري{% endif %}</span>
            </div>
        </div>
        
        <!-- طريقة الدفع: باي بال -->
        <div class="payment-method-card" onclick="selectPaymentMethod('paypal')">
            <input type="radio" id="payment_method_paypal" name="payment_method" value="paypal" class="d-none">
            <div class="payment-method-header">
                <div class="payment-icon" style="color: #0070ba;">
                    <i class="fab fa-paypal"></i>
                </div>
                <div>
                    <h4 class="payment-method-title">PayPal</h4>
                    <p class="payment-method-description">{% if is_english %}Pay securely with PayPal{% else %}ادفع بأمان باستخدام باي بال{% endif %}</p>
                </div>
            </div>
            <div class="payment-method-info">
                <span class="payment-method-badge">{% if is_english %}Instant{% else %}فوري{% endif %}</span>
            </div>
        </div>
        
        <!-- طريقة الدفع: ابل باي -->
        <div class="payment-method-card" onclick="selectPaymentMethod('apple_pay')">
            <input type="radio" id="payment_method_apple_pay" name="payment_method" value="apple_pay" class="d-none">
            <div class="payment-method-header">
                <div class="payment-icon" style="color: #000;">
                    <i class="fab fa-apple-pay"></i>
                </div>
                <div>
                    <h4 class="payment-method-title">Apple Pay</h4>
                    <p class="payment-method-description">{% if is_english %}Quick payment with Apple Pay{% else %}دفع سريع باستخدام آبل باي{% endif %}</p>
                </div>
            </div>
            <div class="payment-method-info">
                <span class="payment-method-badge">{% if is_english %}Instant{% else %}فوري{% endif %}</span>
            </div>
        </div>
        
        <!-- طريقة الدفع: قوقل باي -->
        <div class="payment-method-card" onclick="selectPaymentMethod('google_pay')">
            <input type="radio" id="payment_method_google_pay" name="payment_method" value="google_pay" class="d-none">
            <div class="payment-method-header">
                <div class="payment-icon" style="color: #4285f4;">
                    <i class="fab fa-google-pay"></i>
                </div>
                <div>
                    <h4 class="payment-method-title">Google Pay</h4>
                    <p class="payment-method-description">{% if is_english %}Quick payment with Google Pay{% else %}دفع سريع باستخدام جوجل باي{% endif %}</p>
                </div>
            </div>
            <div class="payment-method-info">
                <span class="payment-method-badge">{% if is_english %}Instant{% else %}فوري{% endif %}</span>
            </div>
        </div>
    </div>
</div>

<script>
function selectPaymentMethod(method) {
    // إزالة الفئة 'selected' من جميع البطاقات
    document.querySelectorAll('.payment-method-card').forEach(card => {
        card.classList.remove('selected');
    });
    
    // إضافة الفئة 'selected' للبطاقة المختارة
    document.querySelector(`#payment_method_${method}`).closest('.payment-method-card').classList.add('selected');
    
    // تحديد قيمة زر الاختيار المناسب
    document.querySelector(`#payment_method_${method}`).checked = true;
    
    // عرض النموذج المناسب وإخفاء باقي النماذج
    document.querySelectorAll('.payment-form').forEach(form => {
        form.classList.add('d-none');
    });
    document.querySelector(`#${method}-payment-form-container`).classList.remove('d-none');
}
</script>
"""
    
    # العثور على موضع إدراج قسم اختيار طريقة الدفع
    search_pattern = '<div class="section mb-4" id="payment-methods-section">'
    section_start = content.find(search_pattern)
    
    if section_start != -1:
        # العثور على نهاية القسم
        section_end = content.find('<div class="section', section_start + len(search_pattern))
        if section_end == -1:
            section_end = content.find('<!-- Payment Forms', section_start)
        
        if section_end != -1:
            # استبدال قسم اختيار طريقة الدفع بالقسم الجديد
            content = content[:section_start] + new_payment_selector + content[section_end:]
        else:
            print("لم يتم العثور على نهاية قسم طرق الدفع")
            return False
    else:
        print("لم يتم العثور على قسم طرق الدفع")
        return False
    
    # حفظ التغييرات
    with open(file_path, 'w', encoding='utf-8') as file:
        file.write(content)
    
    print("تم تحديث قسم اختيار طريقة الدفع بنجاح")
    return True

if __name__ == "__main__":
    fix_payment_options()