"""
تحديث قالب تفاصيل الدفع واستخدام القالب الاحترافي الجديد
"""

import os
import django
import time

# إعداد بيئة Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'car_rental_project.settings')
django.setup()

from django.shortcuts import render, redirect, get_object_or_404
from rental.models import Reservation, Car, User
from django.utils import timezone

def update_payment_view():
    """تحديث ملف admin_views.py لاستخدام القالب الجديد"""
    admin_views_path = 'rental/admin_views.py'
    
    with open(admin_views_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # البحث عن دالة payment_details وتحديث القالب المستخدم
    import re
    
    pattern = r"(\s+)template_name = ['|\"]admin/payment_detail_direct.html['|\"]"
    replacement = r"\1template_name = 'payment_receipt_premium.html'"
    
    if re.search(pattern, content):
        content = re.sub(pattern, replacement, content)
        print("تم تحديث القالب المستخدم في دالة payment_details")
    else:
        print("لم يتم العثور على سطر القالب في دالة payment_details")
    
    with open(admin_views_path, 'w', encoding='utf-8') as f:
        f.write(content)

def create_test_payment():
    """إنشاء حجز تجريبي مع معلومات دفع"""
    # التحقق من وجود مستخدمين وسيارات في النظام
    if User.objects.filter(is_admin=False).count() == 0:
        print("لا يوجد مستخدمين في النظام. جاري إنشاء مستخدم اختباري...")
        user = User.objects.create_user(
            username="test_user",
            email="test@example.com",
            password="Test@1234",
            first_name="مستخدم",
            last_name="اختباري"
        )
    else:
        # استخدام مستخدم موجود
        user = User.objects.filter(is_admin=False).first()
    
    if Car.objects.count() == 0:
        print("لا يوجد سيارات في النظام. جاري إنشاء سيارة اختبارية...")
        car = Car.objects.create(
            make="تويوتا",
            model="كامري",
            year=2022,
            color="أبيض",
            license_plate="ABC-1234",
            daily_rate=65.0,
            category="سيدان",
            seats=5,
            transmission="أوتوماتيك",
            fuel_type="بنزين",
            features="مكيف هواء، نظام ملاحة، بلوتوث",
            is_available=True
        )
    else:
        # استخدام سيارة موجودة
        car = Car.objects.first()
    
    # إنشاء حجز جديد مع معلومات دفع
    now = timezone.now()
    start_date = now.date()
    end_date = (now + timezone.timedelta(days=3)).date()
    
    # إنشاء حجز مدفوع
    import random
    payment_methods = ['visa', 'mastercard', 'amex', 'cash', 'bank_transfer']
    selected_method = random.choice(payment_methods)
    
    reservation = Reservation.objects.create(
        user=user,
        car=car,
        start_date=start_date,
        end_date=end_date,
        total_price=car.daily_rate * 3,
        status='confirmed',
        payment_status='paid',
        notes=f"""
تم الدفع بنجاح
طريقة الدفع: {selected_method}
رقم المرجع: REF-{random.randint(10000, 99999)}
        """
    )
    
    print(f"تم إنشاء حجز جديد برقم #{reservation.id}")
    print(f"يمكنك الآن الوصول إلى صفحة تفاصيل الدفع من خلال: /admin/payment/{reservation.id}")
    
    return reservation.id

def main():
    """تنفيذ كل الإجراءات المطلوبة"""
    print("جاري تحديث قالب تفاصيل الدفع...")
    update_payment_view()
    
    print("\nجاري إنشاء حجز تجريبي...")
    payment_id = create_test_payment()
    
    print("\nتم الانتهاء من التحديثات بنجاح!")
    print(f"يمكنك الآن زيارة هذا الرابط لمشاهدة القالب الجديد: /dashboard/payments/{payment_id}/")

if __name__ == "__main__":
    main()