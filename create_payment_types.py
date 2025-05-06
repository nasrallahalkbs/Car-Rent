"""
إنشاء مجموعة متنوعة من الحجوزات مع حالات دفع مختلفة
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

def create_payment_samples():
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
        cars = [
            Car.objects.create(
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
            ),
            Car.objects.create(
                make="تويوتا",
                model="كامري",
                year=2024,
                color="أبيض",
                license_plate="DEF-5678",
                daily_rate=30.0,
                category="سيدان",
                seats=5,
                transmission="أوتوماتيك",
                fuel_type="بنزين",
                features="مكيف هواء، نظام ملاحة، كاميرا خلفية",
                is_available=True
            ),
            Car.objects.create(
                make="نيسان",
                model="ألتيما",
                year=2023,
                color="فضي",
                license_plate="GHI-9012",
                daily_rate=22.0,
                category="سيدان",
                seats=5,
                transmission="أوتوماتيك",
                fuel_type="بنزين",
                features="مكيف هواء، بلوتوث",
                is_available=True
            )
        ]
    else:
        # استخدام سيارات موجودة
        cars = list(Car.objects.all()[:3])
        if len(cars) < 3:
            # تكرار السيارة الأولى في حالة عدم وجود عدد كافي
            cars = cars + [cars[0]] * (3 - len(cars))
    
    now = timezone.now()
    
    # 1. إنشاء حجز مدفوع بالفيزا
    start_date = now.date()
    end_date = (now + timedelta(days=3)).date()
    
    visa_reservation = Reservation.objects.create(
        user=user,
        car=cars[0],
        start_date=start_date,
        end_date=end_date,
        total_price=cars[0].daily_rate * 3,
        status='confirmed',
        payment_status='paid',
        payment_method='credit_card',
        payment_date=now,
        notes="""
تم الدفع بنجاح
طريقة الدفع: visa
رقم المرجع: REF-{0}
        """.format(random.randint(10000, 99999))
    )
    
    # 2. إنشاء حجز معلق الدفع (بانتظار التحويل البنكي)
    start_date = (now + timedelta(days=7)).date()
    end_date = (now + timedelta(days=10)).date()
    
    pending_bank_reservation = Reservation.objects.create(
        user=user,
        car=cars[1],
        start_date=start_date,
        end_date=end_date,
        total_price=cars[1].daily_rate * 3,
        status='confirmed',
        payment_status='pending',
        payment_method='bank_transfer',
        confirmation_expiry=now + timedelta(hours=24),
        notes="""
في انتظار تأكيد التحويل البنكي
طريقة الدفع: bank_transfer
رقم المرجع: بانتظار التأكيد
        """
    )
    
    # 3. إنشاء حجز مسترد المبلغ
    start_date = (now - timedelta(days=14)).date()
    end_date = (now - timedelta(days=10)).date()
    
    refunded_reservation = Reservation.objects.create(
        user=user,
        car=cars[2],
        start_date=start_date,
        end_date=end_date,
        total_price=cars[2].daily_rate * 4,
        status='cancelled',
        payment_status='refunded',
        payment_method='credit_card',
        payment_date=now - timedelta(days=14),
        notes="""
تم استرداد المبلغ كاملاً
طريقة الدفع: amex
رقم المرجع: REF-{0}
سبب الاسترداد: إلغاء بواسطة العميل
        """.format(random.randint(10000, 99999))
    )
    
    print(f"تم إنشاء الحجوزات التالية:")
    print(f"1. حجز مدفوع (فيزا): #{visa_reservation.id}")
    print(f"2. حجز معلق (تحويل بنكي): #{pending_bank_reservation.id}")
    print(f"3. حجز مسترد: #{refunded_reservation.id}")
    
    print("\nيمكنك الآن الوصول إلى صفحة المدفوعات من خلال: /admin/payments/")

if __name__ == "__main__":
    create_payment_samples()