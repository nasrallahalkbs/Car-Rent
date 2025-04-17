"""
إنشاء حجز تجريبي مع معلومات دفع لعرض صفحة تفاصيل الدفع
"""

import os
import django
import random
from datetime import timedelta

# إعداد بيئة Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'car_rental_project.settings')
django.setup()

from django.utils import timezone
from rental.models import User, Car, Reservation

def create_payment_sample():
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
            make="هوندا",
            model="أكورد",
            year=2025,
            color="أسود",
            license_plate="ABC-1234",
            daily_rate=25.0,
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
    end_date = (now + timedelta(days=3)).date()
    
    # إنشاء حجز مدفوع
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

if __name__ == "__main__":
    create_payment_sample()