"""
إنشاء حجز اختباري مع تاريخ انتهاء صلاحية لاختبار العد التنازلي
"""
import os
import django
import datetime
from django.utils import timezone

# إعداد البيئة لجانغو
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'car_rental_project.settings')
django.setup()

from rental.models import User, Car, Reservation

def create_test_reservation():
    """إنشاء حجز اختباري مع تاريخ انتهاء صلاحية"""
    
    # التحقق من وجود مستخدم اختباري
    try:
        user = User.objects.filter(is_superuser=False).first()
        if not user:
            # إنشاء مستخدم اختباري إذا لم يكن موجودًا
            user = User.objects.create_user(
                username='testuser',
                email='test@example.com',
                password='testpassword123'
            )
            print(f"تم إنشاء مستخدم اختباري: {user.username}")
        else:
            print(f"تم استخدام المستخدم الموجود: {user.username}")
            
        # التحقق من وجود سيارة
        car = Car.objects.first()
        if not car:
            print("لا توجد سيارات في النظام. الرجاء إضافة سيارة أولاً.")
            return
            
        # تواريخ الحجز
        start_date = timezone.now() + datetime.timedelta(days=1)
        end_date = start_date + datetime.timedelta(days=3)
        
        # إنشاء حجز جديد مؤكد مع تاريخ انتهاء صلاحية بعد 12 ساعة
        reservation = Reservation.objects.create(
            user=user,
            car=car,
            start_date=start_date,
            end_date=end_date,
            status='confirmed',
            payment_status='pending',
            confirmation_expiry=timezone.now() + datetime.timedelta(hours=12),
            total_price=car.daily_rate * 3
        )
        
        print(f"تم إنشاء حجز اختباري برقم: {reservation.id}")
        print(f"تاريخ انتهاء صلاحية الحجز: {reservation.confirmation_expiry}")
        print(f"يجب الدفع قبل: {reservation.confirmation_expiry}")
        
    except Exception as e:
        print(f"حدث خطأ: {e}")

if __name__ == "__main__":
    create_test_reservation()