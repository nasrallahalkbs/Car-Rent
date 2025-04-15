"""
إنشاء حجز نشط (غير ملغي) لاختبار العرض في صفحة الحجوزات
"""
import os
import django
import datetime
from django.utils import timezone

# إعداد البيئة لجانغو
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'car_rental_project.settings')
django.setup()

from rental.models import User, Car, Reservation

def create_active_reservation():
    """إنشاء حجز نشط لاختبار العرض في صفحة الحجوزات"""
    
    # التحقق من وجود مستخدم اختباري
    try:
        user = User.objects.filter(username='user').first()
        if not user:
            print("لا يوجد مستخدم 'user'. الرجاء التحقق من الأسماء.")
            return
            
        # التحقق من وجود سيارة
        car = Car.objects.first()
        if not car:
            print("لا توجد سيارات في النظام. الرجاء إضافة سيارة أولاً.")
            return
            
        # تواريخ الحجز
        start_date = timezone.now() + datetime.timedelta(days=7)
        end_date = start_date + datetime.timedelta(days=3)
        
        # إنشاء حجز جديد مؤكد مع تاريخ انتهاء صلاحية المستقبل
        # إنشاء الحجز بحالة confirmed وليس cancelled
        expiry_date = timezone.now() + datetime.timedelta(hours=24)
        
        # حذف أي حجوزات محذوفة سابقاً للسيارة نفسها بنفس التواريخ
        Reservation.objects.filter(
            user=user,
            car=car,
            status='cancelled',
            start_date=start_date,
            end_date=end_date
        ).delete()
        
        # إنشاء حجز جديد بحالة confirmed
        reservation = Reservation.objects.create(
            user=user,
            car=car,
            start_date=start_date,
            end_date=end_date,
            status='confirmed',  # استخدام حالة غير cancelled
            payment_status='pending',
            confirmation_expiry=expiry_date,
            total_price=car.daily_rate * 3
        )
        
        print(f"تم إنشاء حجز نشط جديد برقم: {reservation.id}")
        print(f"حالة الحجز: {reservation.status}")
        print(f"حالة الدفع: {reservation.payment_status}")
        print(f"تاريخ انتهاء صلاحية الحجز: {reservation.confirmation_expiry}")
        
    except Exception as e:
        print(f"حدث خطأ: {e}")

if __name__ == "__main__":
    create_active_reservation()