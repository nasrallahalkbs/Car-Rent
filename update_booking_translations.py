#!/usr/bin/env python3
"""
إضافة ترجمات للحقول الجديدة في نموذج الحجز
هذا السكريبت يقوم بإضافة ترجمات للمصطلحات الجديدة المستخدمة في نموذج الحجز المحدث
"""

def update_translations():
    """تحديث ملفات الترجمة لإضافة المصطلحات الجديدة"""
    # قاموس المصطلحات الجديدة (الإنجليزية والعربية)
    new_terms = {
        # معلومات العميل
        "Full Name (as in ID)*": "الاسم الكامل (كما في البطاقة)*",
        "National ID Number*": "رقم البطاقة الوطنية*",
        "National ID Card Image*": "صورة البطاقة الوطنية*",
        "Upload a clear image of your national ID card": "قم بتحميل صورة واضحة للبطاقة الوطنية",
        "Full Name:": "الاسم الكامل:",
        "National ID:": "رقم البطاقة الوطنية:",
        "ID Card Image:": "صورة البطاقة الوطنية:",
        "Provided": "تم التقديم",
        
        # تفاصيل الإيجار
        "Rental Details": "تفاصيل الإيجار",
        "Rental Type*": "نوع الإيجار*",
        "-- Select Rental Type --": "-- اختر نوع الإيجار --",
        "Daily Rental": "إيجار يومي",
        "Weekly Rental": "إيجار أسبوعي",
        "Monthly Rental": "إيجار شهري",
        "Corporate Rental": "إيجار للشركات",
        "Special Event": "مناسبة خاصة",
        "Rental Type:": "نوع الإيجار:",

        # طرق الدفع
        "Payment Method*": "طريقة الدفع*",
        "-- Select Payment Method --": "-- اختر طريقة الدفع --",
        "Cash Payment": "دفع نقدي",
        "Electronic Payment": "دفع إلكتروني",
        "Credit/Debit Card": "بطاقة ائتمان/خصم",
        "Bank Transfer": "تحويل بنكي",
        "Payment Method:": "طريقة الدفع:",
        
        # الضمانات
        "Guarantee Type*": "نوع الضمان*",
        "-- Select Guarantee Type --": "-- اختر نوع الضمان --",
        "National ID Card": "البطاقة الوطنية",
        "Passport": "جواز السفر",
        "Driving License": "رخصة القيادة",
        "Security Deposit": "وديعة تأمين",
        "Credit Card Hold": "حجز على بطاقة الائتمان",
        "Guarantee Type:": "نوع الضمان:",
        "Deposit Amount (if applicable)": "مبلغ الوديعة (إن وجد)",
        "Deposit Amount:": "مبلغ الوديعة:",
        "Guarantee Details": "تفاصيل الضمان",
        "Guarantee Details:": "تفاصيل الضمان:",
        "Additional details about the guarantee provided": "تفاصيل إضافية عن الضمان المقدم",
        "Information about the guarantee: For ID Card/Passport - mention issuing authority; for Credit Card Hold - mention card type.": "معلومات عن الضمان: للبطاقة الشخصية/جواز السفر - اذكر جهة الإصدار؛ لبطاقة الائتمان - اذكر نوع البطاقة.",
        
        # الحالة
        "Status": "الحالة",
        "Under Review": "قيد المراجعة",
        "Pending Approval": "في انتظار الموافقة",
        "Approved": "تمت الموافقة",
        "Awaiting Payment": "في انتظار الدفع",
        "Completed": "مكتمل",
        "Paid": "مدفوع",
        
        # عناصر واجهة أخرى
        "Customer Information": "معلومات العميل",
        "Additional Notes": "ملاحظات إضافية",
        "Any special requests or additional notes?": "أي طلبات خاصة أو ملاحظات إضافية؟",
        "Total Amount:": "المبلغ الإجمالي:",
    }
    
    # تحديث ملف الترجمة العربي
    with open('locale/ar/LC_MESSAGES/django.po', 'r', encoding='utf-8') as file:
        ar_content = file.read()
    
    # ابحث عن نهاية الملف للإضافة
    last_translation_index = ar_content.rfind('msgstr')
    if last_translation_index != -1:
        position_to_append = ar_content.find('\n', last_translation_index) + 1
        header = ar_content[:position_to_append]
        
        # أضف ترجمات جديدة
        new_translations = ""
        for english, arabic in new_terms.items():
            # تحقق مما إذا كان المصطلح موجودًا بالفعل
            if f'msgid "{english}"' not in ar_content:
                new_translations += f'''
msgid "{english}"
msgstr "{arabic}"
'''
        
        # احفظ الملف المحدث
        with open('locale/ar/LC_MESSAGES/django.po', 'w', encoding='utf-8') as file:
            file.write(header + new_translations)
    
    print("تم تحديث ملفات الترجمة بنجاح.")

if __name__ == "__main__":
    update_translations()