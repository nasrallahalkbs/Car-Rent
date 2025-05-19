"""
تغيير عملة التطبيق من الدينار إلى الريال اليمني

هذا السكريبت يقوم بتحديث العملة في جميع الملفات المناسبة في المشروع
من الدينار إلى الريال اليمني
"""

import os
import re
from pathlib import Path

def update_currency_in_templates():
    """
    تغيير عملة التطبيق في ملفات القوالب من الدينار إلى الريال اليمني
    """
    templates_dir = Path('templates')
    
    # قائمة بملفات القوالب التي يحتمل أن تحتوي على العملة
    template_files = [
        templates_dir / 'admin' / 'payment_detail_django.html',
        templates_dir / 'admin' / 'payment_receipt_django.html',
        templates_dir / 'admin' / 'payment_table_django.html',
        templates_dir / 'car_detail_django.html',
        templates_dir / 'checkout_django.html',
        templates_dir / 'payment_receipt_premium.html',
    ]
    
    # أنماط استبدال للعملة في ملفات HTML
    replacements = [
        (r'(\d+)\s*دينار', r'\1 ريال يمني'),  # مثل: 50 دينار -> 50 ريال يمني
        (r'(\d+\.\d+)\s*دينار', r'\1 ريال يمني'),  # مثل: 50.5 دينار -> 50.5 ريال يمني
        (r'دينار', r'ريال يمني'),  # استبدال كلمة دينار وحدها
    ]
    
    # نقوم بالتعديل على ملفات القوالب الموجودة فقط
    for template_file in template_files:
        if template_file.exists():
            print(f"جاري تحديث العملة في: {template_file}")
            try:
                with open(template_file, 'r', encoding='utf-8') as file:
                    content = file.read()
                
                # تطبيق الاستبدالات على المحتوى
                for pattern, replacement in replacements:
                    content = re.sub(pattern, replacement, content)
                
                # تحديث محتوى الملف
                with open(template_file, 'w', encoding='utf-8') as file:
                    file.write(content)
                
                print(f"✅ تم تحديث العملة في: {template_file}")
            
            except Exception as e:
                print(f"❌ حدث خطأ أثناء تحديث {template_file}: {e}")

def update_currency_in_python_files():
    """
    تغيير العملة في ملفات بايثون التي تحتوي على تصدير أو عرض العملة
    """
    python_files = [
        'rental/admin_views.py',
        'rental/payment_views.py',
        'rental/views.py',
    ]
    
    # أنماط استبدال للعملة في ملفات Python
    replacements = [
        (r'(["\'])دينار(["\'])', r'\1ريال يمني\2'),  # استبدال النصوص مثل "دينار" أو 'دينار'
        (r'f"(.+?)دينار(.+?)"', r'f"\1ريال يمني\2"'),  # استبدال في سلاسل f-string
        (r"f'(.+?)دينار(.+?)'", r"f'\1ريال يمني\2'"),  # استبدال في سلاسل f-string
    ]
    
    for py_file in python_files:
        if os.path.exists(py_file):
            print(f"جاري تحديث العملة في: {py_file}")
            try:
                with open(py_file, 'r', encoding='utf-8') as file:
                    content = file.read()
                
                # تطبيق الاستبدالات على المحتوى
                for pattern, replacement in replacements:
                    content = re.sub(pattern, replacement, content)
                
                # تحديث محتوى الملف
                with open(py_file, 'w', encoding='utf-8') as file:
                    file.write(content)
                
                print(f"✅ تم تحديث العملة في: {py_file}")
            
            except Exception as e:
                print(f"❌ حدث خطأ أثناء تحديث {py_file}: {e}")

def update_currency_symbols():
    """
    تحديث رموز العملة مثل JD (دينار أردني) إلى YER أو ر.ي (ريال يمني)
    """
    files_with_symbols = [
        'templates/admin/payment_detail_django.html',
        'templates/admin/payment_receipt_django.html',
        'templates/checkout_django.html',
        'templates/car_detail_django.html',
    ]
    
    # أنماط استبدال رموز العملة
    replacements = [
        (r'JD', r'YER'),  # استبدال رمز العملة الإنجليزي
        (r'د\.أ', r'ر.ي'),  # استبدال رمز العملة العربي
    ]
    
    for file_path in files_with_symbols:
        if os.path.exists(file_path):
            print(f"جاري تحديث رمز العملة في: {file_path}")
            try:
                with open(file_path, 'r', encoding='utf-8') as file:
                    content = file.read()
                
                # تطبيق الاستبدالات على المحتوى
                for pattern, replacement in replacements:
                    content = re.sub(pattern, replacement, content)
                
                # تحديث محتوى الملف
                with open(file_path, 'w', encoding='utf-8') as file:
                    file.write(content)
                
                print(f"✅ تم تحديث رمز العملة في: {file_path}")
            
            except Exception as e:
                print(f"❌ حدث خطأ أثناء تحديث {file_path}: {e}")

def update_context_processor():
    """
    تحديث سياق العملة في context_processors إذا كان موجوداً
    """
    context_processor_file = 'rental/context_processors.py'
    
    if os.path.exists(context_processor_file):
        print(f"جاري تحديث معلومات العملة في: {context_processor_file}")
        try:
            with open(context_processor_file, 'r', encoding='utf-8') as file:
                content = file.read()
            
            # البحث عن متغير العملة وتحديث قيمته
            currency_pattern = r"'currency':\s*['\"](.*?)['\"]"
            if re.search(currency_pattern, content):
                content = re.sub(currency_pattern, "'currency': 'ريال يمني'", content)
                
                # تحديث رمز العملة أيضاً إذا كان موجوداً
                symbol_pattern = r"'currency_symbol':\s*['\"](.*?)['\"]"
                if re.search(symbol_pattern, content):
                    content = re.sub(symbol_pattern, "'currency_symbol': 'ر.ي'", content)
                
                # حفظ التعديلات
                with open(context_processor_file, 'w', encoding='utf-8') as file:
                    file.write(content)
                
                print(f"✅ تم تحديث معلومات العملة في: {context_processor_file}")
            else:
                print(f"⚠️ لم يتم العثور على متغير العملة في {context_processor_file}")
            
        except Exception as e:
            print(f"❌ حدث خطأ أثناء تحديث {context_processor_file}: {e}")

def update_javascript_files():
    """
    تحديث معلومات العملة في ملفات JavaScript
    """
    js_files = [
        'static/js/payment.js',
        'static/js/checkout.js',
    ]
    
    # أنماط استبدال للعملة في ملفات JavaScript
    replacements = [
        (r'["\'](.*?)دينار(.*?)["\']', r'"\1ريال يمني\2"'),  # استبدال النصوص مثل "xx دينار xx"
        (r'JD', r'YER'),  # استبدال رمز العملة
        (r'د\.أ', r'ر.ي'),  # استبدال رمز العملة العربي
    ]
    
    for js_file in js_files:
        if os.path.exists(js_file):
            print(f"جاري تحديث العملة في: {js_file}")
            try:
                with open(js_file, 'r', encoding='utf-8') as file:
                    content = file.read()
                
                # تطبيق الاستبدالات على المحتوى
                for pattern, replacement in replacements:
                    content = re.sub(pattern, replacement, content)
                
                # تحديث محتوى الملف
                with open(js_file, 'w', encoding='utf-8') as file:
                    file.write(content)
                
                print(f"✅ تم تحديث العملة في: {js_file}")
            
            except Exception as e:
                print(f"❌ حدث خطأ أثناء تحديث {js_file}: {e}")

def main():
    """
    الدالة الرئيسية لتنفيذ تحديث العملة في جميع أنحاء التطبيق
    """
    print("بدء عملية تحديث العملة من الدينار إلى الريال اليمني...")
    
    # تحديث العملة في ملفات القوالب
    update_currency_in_templates()
    
    # تحديث العملة في ملفات بايثون
    update_currency_in_python_files()
    
    # تحديث رموز العملة
    update_currency_symbols()
    
    # تحديث معالج السياق إذا كان موجوداً
    update_context_processor()
    
    # تحديث ملفات JavaScript
    update_javascript_files()
    
    print("✅ تم الانتهاء من تحديث العملة بنجاح!")

if __name__ == "__main__":
    main()