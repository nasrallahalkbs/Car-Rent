#!/usr/bin/env python
"""
إنشاء تقرير حالة سيارة اختباري للتأكد من عمل الفورم بشكل صحيح
"""

import os
import django
from django.utils import timezone
from datetime import timedelta

# إعداد Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'car_rental_project.settings')
django.setup()

# استيراد النماذج بعد إعداد Django
from django.contrib.auth import get_user_model
from rental.models import Car, Reservation, CarConditionReport

User = get_user_model()

def create_test_car_condition_report():
    """إنشاء تقرير حالة سيارة اختباري"""
    print("بدء إنشاء تقرير حالة سيارة اختباري...")

    # البحث عن مستخدم موجود أو إنشاء مستخدم جديد
    try:
        user = User.objects.filter(is_staff=True).first()
        if not user:
            user = User.objects.create_user(
                username="admin_test",
                password="Admin123!",
                email="admin_test@example.com",
                is_staff=True
            )
            print(f"تم إنشاء مستخدم جديد: {user.username}")
        else:
            print(f"تم العثور على مستخدم موجود: {user.username}")
    except Exception as e:
        print(f"خطأ في العثور على/إنشاء مستخدم: {str(e)}")
        return

    # البحث عن مستخدم عادي أو إنشاء مستخدم جديد
    try:
        customer = User.objects.filter(is_staff=False).first()
        if not customer:
            customer = User.objects.create_user(
                username="customer_test",
                password="Customer123!",
                email="customer_test@example.com",
                is_staff=False
            )
            print(f"تم إنشاء عميل جديد: {customer.username}")
        else:
            print(f"تم العثور على عميل موجود: {customer.username}")
    except Exception as e:
        print(f"خطأ في العثور على/إنشاء عميل: {str(e)}")
        return

    # البحث عن سيارة موجودة أو إنشاء سيارة جديدة
    try:
        car = Car.objects.first()
        if not car:
            car = Car.objects.create(
                make="تويوتا",
                model="كورولا",
                year=2023,
                color="أبيض",
                plate_number="أ ب ج 1234",
                daily_rate=200.0,
                is_available=True
            )
            print(f"تم إنشاء سيارة جديدة: {car}")
        else:
            print(f"تم العثور على سيارة موجودة: {car}")
    except Exception as e:
        print(f"خطأ في العثور على/إنشاء سيارة: {str(e)}")
        return

    # البحث عن حجز موجود أو إنشاء حجز جديد
    try:
        # البحث عن حجز موجود للسيارة
        reservation = Reservation.objects.filter(car=car).first()
        
        if not reservation:
            # إنشاء حجز جديد
            start_date = timezone.now() - timedelta(days=7)
            end_date = timezone.now() - timedelta(days=1)
            
            reservation = Reservation.objects.create(
                user=customer,
                car=car,
                start_date=start_date,
                end_date=end_date,
                pickup_location="مكتب الشركة الرئيسي",
                return_location="مكتب الشركة الرئيسي",
                status="completed",  # مكتمل
                total_price=car.daily_rate * 6,  # 6 أيام
                payment_status="paid"  # مدفوع
            )
            print(f"تم إنشاء حجز جديد: {reservation.id}")
        else:
            print(f"تم العثور على حجز موجود: {reservation.id}")
            
    except Exception as e:
        print(f"خطأ في العثور على/إنشاء حجز: {str(e)}")
        return

    # إنشاء تقرير حالة السيارة
    try:
        print(f"[{timezone.now()}] بدء عملية حفظ تقرير حالة السيارة...")
        
        # طباعة معلومات الحجز المرتبط
        print(f"الحجز المرتبط: {reservation.id}")
        print(f"حالة الحجز: {reservation.status}")
        
        report = CarConditionReport.objects.create(
            car=car,
            reservation=reservation,  # ربط التقرير بالحجز
            report_type='return',  # استلام أو تسليم
            inspection_type='visual',  # بصري أو إلكتروني
            mileage=15000,
            date=timezone.now(),
            car_condition='excellent',  # ممتاز، جيد، متوسط، سيء
            fuel_level='full',  # ممتلئ، 3/4، 1/2، 1/4، فارغ
            notes="تم فحص السيارة وهي بحالة ممتازة",
            created_by=user
        )
        print(f"✅ تم إنشاء تقرير حالة السيارة بنجاح: {report.id}")
        
        # طباعة تفاصيل التقرير
        print(f"معرف التقرير: {report.id}")
        print(f"السيارة: {report.car}")
        print(f"الحجز: {report.reservation}")
        print(f"نوع التقرير: {report.get_report_type_display()}")
        print(f"نوع الفحص: {report.get_inspection_type_display()}")
        print(f"المسافة المقطوعة: {report.mileage}")
        print(f"التاريخ: {report.date}")
        print(f"حالة السيارة: {report.get_car_condition_display()}")
        print(f"مستوى الوقود: {report.get_fuel_level_display()}")
        print(f"الملاحظات: {report.notes}")
        print(f"تم الإنشاء بواسطة: {report.created_by}")
        print(f"تاريخ الإنشاء: {report.created_at}")
        
        return report
    except Exception as e:
        print(f"❌ خطأ في إنشاء تقرير حالة السيارة: {str(e)}")
        return None

if __name__ == "__main__":
    report = create_test_car_condition_report()
    if report:
        print("✅✅ تم إنشاء التقرير بنجاح!")
    else:
        print("❌❌ فشل إنشاء التقرير!")