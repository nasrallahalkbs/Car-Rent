"""
تطبيق التصميم الاحترافي فائق الجودة لصفحة تفاصيل الدفع وإضافة روابط لها
"""

import os
import django
import time
import shutil
import re

# إعداد بيئة Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'car_rental_project.settings')
django.setup()

def ensure_styles_applied():
    """التأكد من وجود ملف CSS التصميم الاحترافي"""
    # التحقق من وجود ملف CSS
    css_file_path = 'static/css/payment_ultra_pro.css'
    if not os.path.exists(css_file_path):
        print(f"[!] ملف CSS غير موجود: {css_file_path}")
        print("    يرجى التأكد من إنشاء ملف CSS")
        return False
    
    print(f"[✓] ملف CSS موجود: {css_file_path}")
    return True

def ensure_template_applied():
    """التأكد من وجود قالب التصميم الاحترافي"""
    # التحقق من وجود ملف القالب
    template_file_path = 'templates/admin/payment_detail_ultra.html'
    if not os.path.exists(template_file_path):
        print(f"[!] ملف القالب غير موجود: {template_file_path}")
        print("    يرجى التأكد من إنشاء ملف القالب")
        return False
    
    print(f"[✓] ملف القالب موجود: {template_file_path}")
    return True

def update_admin_view():
    """تحديث ملف admin_views.py لاستخدام القالب الجديد"""
    admin_views_path = 'rental/admin_views.py'
    
    with open(admin_views_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # البحث عن دالة payment_details وتحديث القالب المستخدم
    import re
    
    # نمط للبحث عن سطر تحديد القالب
    template_pattern = r"(\s+)template_name = ['|\"]admin/payment_detail_[^'\"]+['|\"]"
    
    # استبدال السطر بالقالب الجديد
    replacement = r"\1template_name = 'admin/payment_detail_ultra.html'"
    
    if re.search(template_pattern, content):
        content = re.sub(template_pattern, replacement, content)
        print("[✓] تم تحديث القالب المستخدم في دالة payment_details")
    else:
        # البحث باستخدام نمط بديل
        alt_pattern = r"(\s+)# استخدام القالب.+\n\s+template_name = ['|\"]admin/payment_detail_[^'\"]+['|\"]"
        alt_replacement = r"\1# استخدام القالب الاحترافي فائق الجودة مع CSS منفصل\n\1template_name = 'admin/payment_detail_ultra.html'"
        
        if re.search(alt_pattern, content):
            content = re.sub(alt_pattern, alt_replacement, content)
            print("[✓] تم تحديث القالب المستخدم في دالة payment_details (نمط بديل)")
        else:
            print("[!] لم يتم العثور على سطر تعريف القالب في دالة payment_details")
            return False
    
    with open(admin_views_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    return True

def add_payment_menu_link():
    """إضافة رابط في قائمة الإدارة للوصول إلى صفحة المدفوعات"""
    admin_layout_path = 'templates/admin/admin_layout.html'
    
    # التحقق من وجود الملف
    if not os.path.exists(admin_layout_path):
        print(f"[!] ملف تخطيط الإدارة غير موجود: {admin_layout_path}")
        return False
    
    with open(admin_layout_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # البحث عن قائمة الروابط
    payment_link_pattern = r'<a href="{% url \'admin_payments\' %}"'
    
    # التحقق مما إذا كان الرابط موجودًا بالفعل
    if re.search(payment_link_pattern, content):
        print("[✓] رابط صفحة المدفوعات موجود بالفعل في قائمة الإدارة")
        return True
    
    # البحث عن نهاية قائمة الروابط
    menu_pattern = r'(<!-- القائمة الرئيسية -->\s+<ul[^>]*>)(.+?)(<\/ul>)'
    
    # التأكد من العثور على القائمة
    menu_match = re.search(menu_pattern, content, re.DOTALL)
    if not menu_match:
        print("[!] لم يتم العثور على قائمة الروابط في ملف تخطيط الإدارة")
        return False
    
    # إنشاء عنصر قائمة جديد للمدفوعات
    payment_menu_item = '''
                <li class="nav-item">
                    <a href="{% url 'admin_payments' %}" class="nav-link {% if request.path == '/dashboard/payments/' %}active{% endif %}">
                        <i class="fas fa-money-bill-wave"></i>
                        <span>{% if is_english %}Payments{% else %}المدفوعات{% endif %}</span>
                    </a>
                </li>'''
    
    # استبدال القائمة بإضافة عنصر المدفوعات
    new_menu = menu_match.group(1) + menu_match.group(2) + payment_menu_item + menu_match.group(3)
    updated_content = content.replace(menu_match.group(0), new_menu)
    
    with open(admin_layout_path, 'w', encoding='utf-8') as f:
        f.write(updated_content)
    
    print("[✓] تمت إضافة رابط صفحة المدفوعات إلى قائمة الإدارة")
    return True

def ensure_payment_route():
    """التأكد من وجود مسار للوصول إلى صفحة المدفوعات في ملف urls.py"""
    urls_path = 'rental/urls.py'
    
    with open(urls_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # البحث عن مسار الدفع
    payment_route_pattern = r"path\('dashboard/payments/',.+?'admin_payments'\)"
    
    # التحقق مما إذا كان المسار موجودًا بالفعل
    if re.search(payment_route_pattern, content, re.DOTALL):
        print("[✓] مسار صفحة المدفوعات موجود بالفعل في ملف urls.py")
        return True
    
    # البحث عن نمط بديل
    alt_pattern = r"path\('dashboard/payments/?',.+?\),"
    if re.search(alt_pattern, content):
        print("[✓] مسار صفحة المدفوعات موجود بالفعل (نمط بديل)")
        return True
    
    # البحث عن مسارات لوحة التحكم
    dashboard_pattern = r"(# مسارات لوحة التحكم.+?)(path\('dashboard/\w+)"
    match = re.search(dashboard_pattern, content, re.DOTALL)
    
    if not match:
        print("[!] لم يتم العثور على قسم مسارات لوحة التحكم في ملف urls.py")
        return False
    
    # إضافة مسار جديد للمدفوعات
    new_path = match.group(1) + "path('dashboard/payments/', admin_views.admin_payments, name='admin_payments'),\n    " + match.group(2)
    updated_content = content.replace(match.group(0), new_path)
    
    with open(urls_path, 'w', encoding='utf-8') as f:
        f.write(updated_content)
    
    print("[✓] تمت إضافة مسار صفحة المدفوعات إلى ملف urls.py")
    return True

def create_payment_link():
    """إنشاء سكريبت سريع لإضافة روابط للمدفوعات في الواجهة"""
    script_path = 'add_payment_links.py'
    
    script_content = '''"""
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
    if '<a href="{% url \'payment_details\'' in content:
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
    if '<a href="{% url \'payment_details\'' in content:
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
    
    print("\n[✓] تم الانتهاء من إضافة روابط تفاصيل الدفع بنجاح!")

if __name__ == "__main__":
    main()
'''
    
    with open(script_path, 'w', encoding='utf-8') as f:
        f.write(script_content)
    
    print(f"[✓] تم إنشاء سكريبت لإضافة روابط المدفوعات: {script_path}")
    return True

def create_test_payment():
    """إنشاء حجز تجريبي مع معلومات دفع لاختبار التصميم"""
    
    # استيراد النماذج المطلوبة
    from rental.models import Car, User, Reservation
    from django.utils import timezone
    import random
    
    print("\n[*] إنشاء بيانات اختبار للتصميم الجديد...")
    
    # التحقق من وجود مستخدمين في النظام
    if User.objects.filter(is_admin=False).count() == 0:
        print("[!] لا يوجد مستخدمين في النظام. جاري إنشاء مستخدم اختباري...")
        user = User.objects.create_user(
            username="test_user",
            email="test@example.com",
            password="Test@1234",
            first_name="مستخدم",
            last_name="اختباري"
        )
    else:
        user = User.objects.filter(is_admin=False).first()
        print(f"[✓] تم العثور على مستخدم: {user.username}")
    
    # التحقق من وجود سيارات في النظام
    if Car.objects.count() == 0:
        print("[!] لا توجد سيارات في النظام. جاري إنشاء سيارة اختبارية...")
        car = Car.objects.create(
            make="تويوتا",
            model="كامري",
            year=2024,
            color="أبيض",
            license_plate="KWT-1234",
            daily_rate=65.0,
            category="سيدان",
            seats=5,
            transmission="أوتوماتيك",
            fuel_type="بنزين",
            features="مكيف هواء، نظام ملاحة، بلوتوث",
            is_available=True
        )
    else:
        car = Car.objects.first()
        print(f"[✓] تم العثور على سيارة: {car.make} {car.model}")
    
    # إنشاء حجز جديد مع معلومات دفع
    now = timezone.now()
    
    # تعيين تواريخ الحجز
    start_date = now.date()
    end_date = (now + timezone.timedelta(days=5)).date()
    
    # إنشاء حجز مدفوع
    payment_methods = ['visa', 'mastercard', 'amex', 'cash', 'bank_transfer']
    selected_method = random.choice(payment_methods)
    
    # حساب سعر الحجز
    total_price = car.daily_rate * 5
    
    # التحقق من وجود حجز تجريبي سابق
    existing_reservation = Reservation.objects.filter(id=54).first()
    if existing_reservation:
        print(f"[!] تم العثور على حجز سابق بالرقم 54. جاري تحديث بياناته...")
        existing_reservation.user = user
        existing_reservation.car = car
        existing_reservation.start_date = start_date
        existing_reservation.end_date = end_date
        existing_reservation.total_price = total_price
        existing_reservation.status = 'confirmed'
        existing_reservation.payment_status = 'paid'
        existing_reservation.notes = f"""
تم الدفع بنجاح
طريقة الدفع: {selected_method}
رقم المرجع: REF-{random.randint(10000, 99999)}
        """
        existing_reservation.save()
        reservation = existing_reservation
    else:
        print("[*] إنشاء حجز جديد للاختبار...")
        reservation = Reservation.objects.create(
            user=user,
            car=car,
            start_date=start_date,
            end_date=end_date,
            total_price=total_price,
            status='confirmed',
            payment_status='paid',
            notes=f"""
تم الدفع بنجاح
طريقة الدفع: {selected_method}
رقم المرجع: REF-{random.randint(10000, 99999)}
            """
        )
    
    print(f"[✓] تم إنشاء/تحديث حجز تجريبي برقم #{reservation.id}")
    print(f"[*] يمكنك الآن الوصول إلى صفحة تفاصيل الدفع من خلال: /dashboard/payments/{reservation.id}/")
    
    return reservation.id

def main():
    """دالة رئيسية لتنفيذ جميع الخطوات"""
    print("\n=== تطبيق التصميم الاحترافي فائق الجودة لصفحة تفاصيل الدفع ===\n")
    
    all_success = True
    
    # التحقق من وجود ملفات التصميم
    if not ensure_styles_applied():
        all_success = False
    
    if not ensure_template_applied():
        all_success = False
    
    # تحديث الكود لاستخدام التصميم الجديد
    if not update_admin_view():
        all_success = False
    
    # تأكيد وجود مسار للمدفوعات
    if not ensure_payment_route():
        all_success = False
    
    # إضافة رابط في قائمة الإدارة
    add_payment_menu_link()
    
    # إنشاء سكريبت لإضافة روابط المدفوعات
    create_payment_link()
    
    # إنشاء بيانات اختبار
    payment_id = create_test_payment()
    
    print("\n=== ملخص التنفيذ ===")
    if all_success:
        print("\n[✓] تم تطبيق التصميم الاحترافي بنجاح!")
    else:
        print("\n[!] تم تطبيق التصميم مع بعض التحذيرات. يرجى مراجعة الرسائل أعلاه.")
    
    print(f"\n[*] للوصول إلى صفحة تفاصيل الدفع التجريبية: /dashboard/payments/{payment_id}/")
    print(f"[*] لتنفيذ سكريبت إضافة روابط المدفوعات: python add_payment_links.py")

if __name__ == "__main__":
    main()