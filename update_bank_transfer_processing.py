"""
إضافة معالجة التحويل البنكي إلى دالة payment_gateway في ملف payment_views.py
"""

import os
import re

def update_payment_gateway():
    """إضافة معالجة التحويل البنكي إلى دالة payment_gateway"""
    file_path = 'rental/payment_views.py'
    
    if not os.path.exists(file_path):
        print(f"الملف {file_path} غير موجود")
        return False
    
    # قراءة محتوى الملف
    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()
    
    # العثور على موقع إضافة كود معالجة التحويل البنكي
    credit_card_processing_end = re.search(r'if payment_method == \'credit_card\':(.*?)(# في الحالة الحقيقية|# In a real)', content, re.DOTALL)
    
    if not credit_card_processing_end:
        print("لم يتم العثور على موقع إضافة كود معالجة التحويل البنكي")
        return False
    
    # كود معالجة التحويل البنكي
    bank_transfer_processing = """
            # معالجة التحويل البنكي
            elif payment_method == 'bank_transfer':
                transfer_date = request.POST.get('transfer_date')
                transfer_reference = request.POST.get('transfer_reference')
                bank_name = request.POST.get('bank_name')
                transfer_amount = request.POST.get('transfer_amount')
                
                # التحقق من إدخال البيانات المطلوبة
                if not all([transfer_date, transfer_reference, bank_name, transfer_amount]):
                    if is_english:
                        error_message = 'Please fill in all bank transfer details.'
                    else:
                        error_message = 'يرجى ملء جميع تفاصيل التحويل البنكي.'
                    
                    messages.error(request, error_message)
                    return redirect(f'/payment/bank-transfer/?reservation_id={reservation_id}')
                
                # إضافة بيانات التحويل البنكي إلى السجل (في التطبيق الحقيقي)
                # هنا يمكن تخزين بيانات التحويل في نموذج منفصل أو في حقول إضافية في نموذج الحجز
                
                # في هذا المثال، نفترض أن التحويل تم بنجاح ونقوم بإنشاء رقم مرجعي للدفع
                payment_reference = f"BT-{uuid.uuid4().hex[:8].upper()}"
            """
    
    # إضافة كود معالجة التحويل البنكي
    new_content = content[:credit_card_processing_end.end(1)] + bank_transfer_processing + content[credit_card_processing_end.end(1):]
    
    # حفظ التغييرات
    with open(file_path, 'w', encoding='utf-8') as file:
        file.write(new_content)
    
    print("تم إضافة معالجة التحويل البنكي بنجاح")
    return True

if __name__ == "__main__":
    update_payment_gateway()