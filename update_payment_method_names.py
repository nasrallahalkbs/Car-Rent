"""
إضافة التحويل البنكي إلى قائمة طرق الدفع المتاحة
"""

import os
import re

def update_payment_method_names():
    """إضافة التحويل البنكي إلى قواميس أسماء طرق الدفع"""
    file_path = 'rental/payment_views.py'
    
    if not os.path.exists(file_path):
        print(f"الملف {file_path} غير موجود")
        return False
    
    # قراءة محتوى الملف
    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()
    
    # تحديث قاموس أسماء طرق الدفع باللغة الإنجليزية
    content = content.replace(
        "method_names = {'credit_card': 'Credit Card', 'paypal': 'PayPal', 'apple_pay': 'Apple Pay', 'google_pay': 'Google Pay'}",
        "method_names = {'credit_card': 'Credit Card', 'bank_transfer': 'Bank Transfer', 'paypal': 'PayPal', 'apple_pay': 'Apple Pay', 'google_pay': 'Google Pay'}"
    )
    
    # تحديث قاموس أسماء طرق الدفع باللغة العربية
    content = content.replace(
        "method_names = {'credit_card': 'بطاقة ائتمان', 'paypal': 'باي بال', 'apple_pay': 'آبل باي', 'google_pay': 'جوجل باي'}",
        "method_names = {'credit_card': 'بطاقة ائتمان', 'bank_transfer': 'تحويل بنكي', 'paypal': 'باي بال', 'apple_pay': 'آبل باي', 'google_pay': 'جوجل باي'}"
    )
    
    # كتابة المحتوى المعدل إلى الملف
    with open(file_path, 'w', encoding='utf-8') as file:
        file.write(content)
    
    print("تم تحديث قواميس أسماء طرق الدفع بنجاح")
    return True

if __name__ == "__main__":
    update_payment_method_names()