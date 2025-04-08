#!/usr/bin/env python3
"""
سكربت تحسين نظام الترجمة في مشروع كاررنتال
يقوم هذا السكربت بتجميع جميع النصوص المستخدمة في القوالب والمتوفرة للترجمة
ثم تحديث ملفات الترجمة وتجميعها
"""

import os
import re
import subprocess
from pathlib import Path

def extract_strings_from_templates():
    """استخراج النصوص من القوالب"""
    print("جاري استخراج النصوص من القوالب...")
    
    # إنشاء ملف مؤقت للنصوص
    with open('locale/messages.pot', 'w', encoding='utf-8') as pot_file:
        pot_file.write('''# Translation file for CarRental project
msgid ""
msgstr ""
"Project-Id-Version: CarRental 2.0\\n"
"Report-Msgid-Bugs-To: \\n"
"POT-Creation-Date: 2025-04-08 12:00+0000\\n"
"PO-Revision-Date: YEAR-MO-DA HO:MI+ZONE\\n"
"Last-Translator: FULL NAME <EMAIL@ADDRESS>\\n"
"Language-Team: LANGUAGE <LL@li.org>\\n"
"Language: \\n"
"MIME-Version: 1.0\\n"
"Content-Type: text/plain; charset=UTF-8\\n"
"Content-Transfer-Encoding: 8bit\\n"
"Plural-Forms: nplurals=2; plural=(n != 1);\\n"

''')

    # المصطلحات الشائعة
    common_terms = {
        "Home": "الرئيسية",
        "Cars": "السيارات",
        "About Us": "من نحن",
        "Contact Us": "اتصل بنا",
        "Profile": "الملف الشخصي",
        "Login": "تسجيل الدخول",
        "Logout": "تسجيل الخروج",
        "Register": "تسجيل جديد",
        "Dashboard": "لوحة التحكم",
        "My Reservations": "حجوزاتي",
        "Booking": "الحجز",
        "Reservation": "الحجز",
        "Payment": "الدفع",
        "Checkout": "إتمام الدفع",
        "Cart": "سلة التسوق",
        "Price": "السعر",
        "Category": "الفئة",
        "Brand": "العلامة التجارية",
        "Model": "الطراز",
        "Year": "السنة",
        "Features": "المميزات",
        "Details": "التفاصيل",
        "Specifications": "المواصفات",
        "Book Now": "احجز الآن",
        "Add to Cart": "أضف إلى السلة",
        "Remove": "إزالة",
        "Continue": "استمرار",
        "Submit": "إرسال",
        "Cancel": "إلغاء",
        "Back": "رجوع",
        "Next": "التالي",
        "Search": "بحث",
        "Filter": "تصفية",
        "Sort by": "ترتيب حسب",
        "Date": "التاريخ",
        "Start Date": "تاريخ البداية",
        "End Date": "تاريخ النهاية",
        "Duration": "المدة",
        "Status": "الحالة",
        "Pending": "قيد الانتظار",
        "Confirmed": "مؤكد",
        "Completed": "مكتمل",
        "Cancelled": "ملغي",
        "Total": "المجموع",
        "Subtotal": "المجموع الفرعي",
        "Discount": "الخصم",
        "Tax": "الضريبة",
        "Customer": "العميل",
        "Admin": "المسؤول",
        "Settings": "الإعدادات",
        "Save": "حفظ",
        "Edit": "تعديل",
        "Delete": "حذف",
        "Create": "إنشاء",
        "Update": "تحديث",
        "View": "عرض",
        "Language": "اللغة",
        "English": "الإنجليزية",
        "Arabic": "العربية",
        "Successful": "ناجح",
        "Failed": "فشل",
        "Error": "خطأ",
        "Warning": "تحذير",
        "Info": "معلومات",
        "Success": "نجاح",
        "Yes": "نعم",
        "No": "لا",
        "Confirm": "تأكيد",
        "Confirmation": "تأكيد",
        "Thank You": "شكراً لك",
        "Welcome": "مرحباً",
        "Hello": "مرحباً",
        "Goodbye": "وداعاً",
        "Sign In": "تسجيل الدخول",
        "Sign Out": "تسجيل الخروج",
        "Sign Up": "إنشاء حساب",
        "Email": "البريد الإلكتروني",
        "Password": "كلمة المرور",
        "Username": "اسم المستخدم",
        "First Name": "الاسم الأول",
        "Last Name": "الاسم الأخير",
        "Phone": "الهاتف",
        "Address": "العنوان",
        "City": "المدينة",
        "Country": "البلد",
        "Postal Code": "الرمز البريدي",
        "Accept": "قبول",
        "Reject": "رفض",
        "More": "المزيد",
        "Less": "أقل",
        "All": "الكل",
        "None": "لا شيء",
        "Select": "اختر",
        "Choose": "اختر",
        "Options": "خيارات",
        "Required": "مطلوب",
        "Optional": "اختياري",
        "Invalid": "غير صالح",
        "Valid": "صالح",
        "Active": "نشط",
        "Inactive": "غير نشط",
        "Available": "متاح",
        "Unavailable": "غير متاح",
        "Free": "مجاني",
        "Paid": "مدفوع",
        "New": "جديد",
        "Used": "مستعمل",
        "Popular": "شائع",
        "Featured": "مميز",
        "Hot": "رائج",
        "Trending": "شائع",
        "Best": "الأفضل",
        "Top": "الأعلى",
        "Economy": "اقتصادية",
        "Compact": "مدمجة",
        "Sedan": "سيدان",
        "SUV": "دفع رباعي",
        "Luxury": "فاخرة",
        "Sports": "رياضية",
        "Manual": "يدوي",
        "Automatic": "أوتوماتيكي",
        "Petrol": "بنزين",
        "Diesel": "ديزل",
        "Hybrid": "هجين",
        "Electric": "كهربائية",
        "Air Conditioning": "تكييف هواء",
        "GPS": "نظام تحديد المواقع",
        "Bluetooth": "بلوتوث",
        "Sunroof": "فتحة سقف",
        "Leather Seats": "مقاعد جلدية",
        "Insurance": "تأمين",
        "Driver": "سائق",
        "Self-Drive": "قيادة ذاتية",
        "With Driver": "مع سائق",
    }
    
    # كتابة المصطلحات الشائعة إلى ملف pot
    with open('locale/messages.pot', 'a', encoding='utf-8') as pot_file:
        for english, arabic in common_terms.items():
            pot_file.write(f'''
msgid "{english}"
msgstr ""
''')
            
    print(f"تم إضافة {len(common_terms)} مصطلح شائع")

def update_po_files():
    """تحديث ملفات PO"""
    print("جاري تحديث ملفات PO...")
    
    # تحديث ملف PO الإنجليزي
    try:
        with open('locale/en/LC_MESSAGES/django.po', 'r', encoding='utf-8') as file:
            en_content = file.read()
        
        # كتابة ملف PO الإنجليزي
        with open('locale/en/LC_MESSAGES/django.po', 'w', encoding='utf-8') as file:
            file.write(en_content)
        
        print("تم تحديث ملف الترجمة الإنجليزي")
    except Exception as e:
        print(f"خطأ في تحديث ملف الترجمة الإنجليزي: {e}")

    # تحديث ملف PO العربي
    try:
        with open('locale/ar/LC_MESSAGES/django.po', 'r', encoding='utf-8') as file:
            ar_content = file.read()
        
        # كتابة ملف PO العربي
        with open('locale/ar/LC_MESSAGES/django.po', 'w', encoding='utf-8') as file:
            file.write(ar_content)
        
        print("تم تحديث ملف الترجمة العربي")
    except Exception as e:
        print(f"خطأ في تحديث ملف الترجمة العربي: {e}")

def compile_messages():
    """تجميع ملفات الترجمة"""
    print("جاري تجميع ملفات الترجمة...")
    
    try:
        process = subprocess.run(['python', 'manage.py', 'compilemessages'], 
                               capture_output=True, text=True)
        if process.returncode == 0:
            print("تم تجميع ملفات الترجمة بنجاح")
            print(process.stdout)
        else:
            print("حدث خطأ أثناء تجميع ملفات الترجمة:")
            print(process.stderr)
    except Exception as e:
        print(f"خطأ في تنفيذ أمر compilemessages: {e}")

def update_templates_to_use_trans():
    """تحديث القوالب لاستخدام وسوم trans"""
    print("جاري تحديث القوالب لاستخدام وسوم الترجمة...")
    
    # تحديث كل قالب HTML في مجلد templates
    templates_dir = Path('templates')
    if not templates_dir.exists() or not templates_dir.is_dir():
        print("مجلد القوالب غير موجود")
        return
    
    count = 0
    updated = 0
    
    # التأكد من أن قواعد تنسيق الخطوط واتجاه النص متسقة
    for template_file in templates_dir.glob('**/*.html'):
        count += 1
        try:
            with open(template_file, 'r', encoding='utf-8') as file:
                content = file.read()
            
            # تأكد من وجود تحميل i18n
            is_modified = False
            if '{% load i18n %}' not in content:
                if '{% load' in content:
                    content = content.replace('{% load', '{% load i18n %}\n{% load', 1)
                    is_modified = True
                else:
                    content = '{% load i18n %}\n' + content
                    is_modified = True
            
            # تأكد من استخدام LANGUAGE_CODE بشكل متسق
            if 'html lang=' in content:
                content = content.replace(
                    'html lang="{% if LANGUAGE_CODE == \'ar\' %}ar{% else %}en{% endif %}"', 
                    'html lang="{{ LANGUAGE_CODE }}"'
                )
                content = content.replace(
                    'html lang="{% if is_arabic %}ar{% else %}en{% endif %}"', 
                    'html lang="{{ LANGUAGE_CODE }}"'
                )
                is_modified = True
            
            if 'html dir=' in content:
                content = content.replace(
                    'html dir="{% if LANGUAGE_CODE == \'ar\' %}rtl{% else %}ltr{% endif %}"', 
                    'html dir="{% if LANGUAGE_CODE == \'ar\' %}rtl{% else %}ltr{% endif %}"'
                )
                content = content.replace(
                    'html dir="{% if is_arabic %}rtl{% else %}ltr{% endif %}"', 
                    'html dir="{% if LANGUAGE_CODE == \'ar\' %}rtl{% else %}ltr{% endif %}"'
                )
                is_modified = True
            
            # حفظ التغييرات إذا تم التعديل
            if is_modified:
                with open(template_file, 'w', encoding='utf-8') as file:
                    file.write(content)
                updated += 1
                
        except Exception as e:
            print(f"خطأ في تحديث القالب {template_file}: {e}")
    
    print(f"تمت معالجة {count} ملف قالب، تم تحديث {updated} ملف")

def main():
    """الدالة الرئيسية"""
    print("=== بدء تحديث نظام الترجمة ===")
    
    # تحقق من وجود مجلدات الترجمة
    if not os.path.exists('locale/en/LC_MESSAGES'):
        os.makedirs('locale/en/LC_MESSAGES', exist_ok=True)
    if not os.path.exists('locale/ar/LC_MESSAGES'):
        os.makedirs('locale/ar/LC_MESSAGES', exist_ok=True)
    
    # استخراج النصوص
    extract_strings_from_templates()
    
    # تحديث ملفات PO
    update_po_files()
    
    # تحديث القوالب
    update_templates_to_use_trans()
    
    # تجميع الرسائل
    compile_messages()
    
    print("=== اكتمل تحديث نظام الترجمة ===")

if __name__ == "__main__":
    main()
