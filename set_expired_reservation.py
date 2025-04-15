"""
تعديل تاريخ انتهاء الحجز ليكون منتهي الصلاحية
"""
import os
import django

# إعداد Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'main.settings')
django.setup()

from django.utils import timezone
from rental.models import Reservation
import datetime

def set_reservation_expired(reservation_id):
    """تعديل تاريخ انتهاء الحجز ليكون منتهي الصلاحية"""
    try:
        reservation = Reservation.objects.get(id=reservation_id)
        # تعيين تاريخ انتهاء قبل ساعة من الوقت الحالي
        reservation.confirmation_expiry = timezone.now() - datetime.timedelta(hours=1)
        reservation.save()
        print(f'تم تعديل تاريخ انتهاء الحجز رقم {reservation.id} إلى {reservation.confirmation_expiry}')
    except Reservation.DoesNotExist:
        print(f"لم يتم العثور على حجز برقم {reservation_id}")

if __name__ == "__main__":
    # استخدام الحجز الذي تم إنشاؤه مسبقاً
    set_reservation_expired(43)