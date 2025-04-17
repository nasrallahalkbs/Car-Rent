"""
إضافة روابط إلى الواجهة للوصول إلى صفحة المدفوعات والإيصالات
"""

import os
import django
import re

# إعداد بيئة Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'car_rental_project.settings')
django.setup()

def add_payment_links_to_reservation_detail():
    """إضافة رابط للوصول إلى تفاصيل الدفع من صفحة تفاصيل الحجز"""
    template_path = 'templates/reservation_detail_django.html'
    
    if not os.path.exists(template_path):
        print(f"[!] ملف قالب تفاصيل الحجز غير موجود: {template_path}")
        return False
    
    with open(template_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # البحث عن قسم معلومات الدفع
    payment_section_pattern = r'(<!-- معلومات الدفع -->[\s\S]+?)<div class="card-footer'
    match = re.search(payment_section_pattern, content)
    
    if not match:
        print("[!] لم يتم العثور على قسم معلومات الدفع في قالب تفاصيل الحجز")
        return False
    
    # التحقق مما إذا كان الرابط موجودًا بالفعل
    if '<a href="{% url 'payment_details'' in content:
        print("[✓] رابط تفاصيل الدفع موجود بالفعل في قالب تفاصيل الحجز")
        return True
    
    # إضافة رابط تفاصيل الدفع
    payment_link = f"""
            <!-- رابط تفاصيل الدفع -->
            <div class="mt-3">
                <a href="{{% url 'payment_details' payment_id=reservation.id %}}" class="btn btn-primary w-100">
                    <i class="fas fa-file-invoice-dollar me-2"></i>
                    {{% if is_english %}}View Payment Details{{% else %}}عرض تفاصيل الدفع{{% endif %}}
                </a>
            </div>
            
            <div class="card-footer"""
    
    updated_content = content.replace(match.group(0), match.group(1) + payment_link)
    
    with open(template_path, 'w', encoding='utf-8') as f:
        f.write(updated_content)
    
    print("[✓] تمت إضافة رابط تفاصيل الدفع إلى قالب تفاصيل الحجز")
    return True

def add_payment_links_to_reservation_table():
    """إضافة رابط للوصول إلى تفاصيل الدفع من جدول الحجوزات"""
    template_path = 'templates/reservation_table_django.html'
    
    if not os.path.exists(template_path):
        print(f"[!] ملف قالب جدول الحجوزات غير موجود: {template_path}")
        return False
    
    with open(template_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # البحث عن أزرار الإجراءات
    actions_pattern = r'(<div class="d-flex.+?reservation.id %}">[\s\S]+?</a>)([\s\S]+?</div>)'
    match = re.search(actions_pattern, content)
    
    if not match:
        print("[!] لم يتم العثور على قسم أزرار الإجراءات في قالب جدول الحجوزات")
        return False
    
    # التحقق مما إذا كان الرابط موجودًا بالفعل
    if '<a href="{% url 'payment_details'' in content:
        print("[✓] رابط تفاصيل الدفع موجود بالفعل في قالب جدول الحجوزات")
        return True
    
    # إضافة رابط تفاصيل الدفع
    payment_link = f"""
                <!-- رابط تفاصيل الدفع -->
                <a href="{{% url 'payment_details' payment_id=reservation.id %}}" class="btn btn-info btn-sm ms-1" 
                    title="{{% if is_english %}}Payment Details{{% else %}}تفاصيل الدفع{{% endif %}}">
                    <i class="fas fa-file-invoice-dollar"></i>
                </a>"""
    
    updated_content = content.replace(match.group(0), match.group(1) + payment_link + match.group(2))
    
    with open(template_path, 'w', encoding='utf-8') as f:
        f.write(updated_content)
    
    print("[✓] تمت إضافة رابط تفاصيل الدفع إلى قالب جدول الحجوزات")
    return True

def main():
    """تنفيذ الوظائف الرئيسية"""
    add_payment_links_to_reservation_detail()
    add_payment_links_to_reservation_table()
    
    print("
[✓] تم الانتهاء من إضافة روابط تفاصيل الدفع بنجاح!")

if __name__ == "__main__":
    main()
