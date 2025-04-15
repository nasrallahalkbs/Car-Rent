"""
إنشاء حجز عادي جديد لاختبار العرض في صفحة الحجوزات
"""
import os
import django
import datetime
from django.utils import timezone

# إعداد البيئة لجانغو
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'car_rental_project.settings')
django.setup()

from rental.models import User, Car, Reservation

def create_normal_reservation():
    """إنشاء حجز عادي جديد"""
    
    # التحقق من وجود مستخدم اختباري
    try:
        user = User.objects.filter(is_superuser=False).first()
        if not user:
            print("لا يوجد مستخدم غير مدير متاح. الرجاء إنشاء مستخدم أولاً.")
            return
            
        # التحقق من وجود سيارة
        car = Car.objects.first()
        if not car:
            print("لا توجد سيارات في النظام. الرجاء إضافة سيارة أولاً.")
            return
            
        # تواريخ الحجز
        start_date = timezone.now() + datetime.timedelta(days=10)
        end_date = start_date + datetime.timedelta(days=3)
        
        # تاريخ انتهاء بعد 24 ساعة
        expiry_date = timezone.now() + datetime.timedelta(hours=24)
        
        # إنشاء حجز جديد
        reservation = Reservation.objects.create(
            user=user,
            car=car,
            start_date=start_date,
            end_date=end_date,
            status='confirmed',
            payment_status='pending',
            confirmation_expiry=expiry_date,
            total_price=car.daily_rate * 3
        )
        
        print(f"تم إنشاء حجز عادي جديد برقم: {reservation.id}")
        print(f"تاريخ انتهاء صلاحية الحجز: {reservation.confirmation_expiry}")
        print(f"حالة الدفع: {reservation.payment_status}")
        
    except Exception as e:
        print(f"حدث خطأ: {e}")

if __name__ == "__main__":
    create_normal_reservation()