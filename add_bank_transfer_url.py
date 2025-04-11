"""
إضافة مسار التحويل البنكي إلى ملف urls.py
"""

import os

def add_bank_transfer_url():
    """إضافة مسار التحويل البنكي"""
    file_path = 'rental/urls.py'
    
    if not os.path.exists(file_path):
        print(f"الملف {file_path} غير موجود")
        return False
    
    # قراءة محتوى الملف
    with open(file_path, 'r', encoding='utf-8') as file:
        lines = file.readlines()
    
    # العثور على موضع إضافة المسار الجديد
    new_lines = []
    for line in lines:
        new_lines.append(line)
        # بعد مسار PayPal مباشرة
        if "path('payment/paypal/'" in line:
            # إضافة مسار التحويل البنكي
            new_lines.append("    path('payment/bank-transfer/', payment_views.bank_transfer_payment, name='bank_transfer_payment'),\n")
    
    # كتابة المحتوى المعدل
    with open(file_path, 'w', encoding='utf-8') as file:
        file.writelines(new_lines)
    
    print("تم إضافة مسار التحويل البنكي بنجاح")
    return True

if __name__ == "__main__":
    add_bank_transfer_url()