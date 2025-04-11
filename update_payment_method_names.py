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
    
    # البحث عن قاموس أسماء طرق الدفع باللغة الإنجليزية وإضافة التحويل البنكي
    english_dict_pattern = r'PAYMENT_METHOD_NAMES_EN\s*=\s*{([^}]+)}'
    english_dict_match = re.search(english_dict_pattern, content, re.DOTALL)
    
    if english_dict_match:
        english_dict_content = english_dict_match.group(1)
        if "'bank_transfer':" not in english_dict_content:
            new_english_dict_content = english_dict_content + "\n    'bank_transfer': 'Bank Transfer',"
            new_content = content.replace(english_dict_content, new_english_dict_content)
            content = new_content
    
    # البحث عن قاموس أسماء طرق الدفع باللغة العربية وإضافة التحويل البنكي
    arabic_dict_pattern = r'PAYMENT_METHOD_NAMES_AR\s*=\s*{([^}]+)}'
    arabic_dict_match = re.search(arabic_dict_pattern, content, re.DOTALL)
    
    if arabic_dict_match:
        arabic_dict_content = arabic_dict_match.group(1)
        if "'bank_transfer':" not in arabic_dict_content:
            new_arabic_dict_content = arabic_dict_content + "\n    'bank_transfer': 'تحويل بنكي',"
            new_content = content.replace(arabic_dict_content, new_arabic_dict_content)
            content = new_content
    
    # حفظ التغييرات
    with open(file_path, 'w', encoding='utf-8') as file:
        file.write(content)
    
    print("تم إضافة التحويل البنكي إلى قواميس أسماء طرق الدفع بنجاح")
    return True

def main():
    """تنفيذ الدالة الرئيسية للسكريبت"""
    print("بدء تحديث طرق الدفع المتاحة...")
    update_payment_method_names()
    print("تم تحديث طرق الدفع المتاحة بنجاح!")

if __name__ == "__main__":
    main()