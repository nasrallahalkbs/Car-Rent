"""
عرض قائمة الحجوزات للمستخدم المطلوب
"""
import os
import django
from django.utils import timezone

# إعداد البيئة لجانغو
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'car_rental_project.settings')
django.setup()

from rental.models import User, Reservation

def list_user_reservations(username):
    """عرض حجوزات المستخدم"""
    try:
        user = User.objects.get(username=username)
        print(f'حجوزات المستخدم {username} (ID: {user.id}):')
        
        reservations = Reservation.objects.filter(user=user)
        if not reservations:
            print("لا توجد حجوزات لهذا المستخدم.")
            return
            
        now = timezone.now()
        
        for res in reservations:
            expiry_info = ""
            if res.confirmation_expiry:
                if res.confirmation_expiry > now:
                    remaining = res.confirmation_expiry - now
                    hours = remaining.seconds // 3600
                    minutes = (remaining.seconds % 3600) // 60
                    expiry_info = f" - متبقي {hours} ساعة و {minutes} دقيقة حتى انتهاء المهلة"
                else:
                    expiry_info = " - انتهت مهلة الدفع"
                    
            print(f'- حجز رقم: {res.id}')
            print(f'  السيارة: {res.car.make} {res.car.model}')
            print(f'  الحالة: {res.status} / حالة الدفع: {res.payment_status}')
            print(f'  تاريخ انتهاء التأكيد: {res.confirmation_expiry}{expiry_info}')
            print()
            
    except User.DoesNotExist:
        print(f"المستخدم {username} غير موجود")
    except Exception as e:
        print(f"حدث خطأ: {e}")

if __name__ == "__main__":
    list_user_reservations("user")