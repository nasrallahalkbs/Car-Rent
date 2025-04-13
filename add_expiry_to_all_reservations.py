"""
إضافة تاريخ انتهاء مهلة الدفع لجميع الحجوزات
"""
import os
import django
import datetime

# إعداد البيئة لجانغو
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'car_rental_project.settings')
django.setup()

from rental.models import Reservation

def add_expiry_to_all_reservations():
    """إضافة تاريخ انتهاء لكل الحجوزات المؤكدة التي ليس لديها تاريخ انتهاء"""
    # الحصول على الحجوزات المؤكدة بدون تاريخ انتهاء
    reservations = Reservation.objects.filter(status='confirmed', confirmation_expiry=None)
    
    # عدد الحجوزات التي تم تحديثها
    count = 0
    
    # لكل حجز، إضافة تاريخ انتهاء بعد 24 ساعة من الآن
    for reservation in reservations:
        now = datetime.datetime.now(datetime.timezone.utc)
        reservation.confirmation_expiry = now + datetime.timedelta(hours=24)
        reservation.save()
        count += 1
        print(f"تم تحديث الحجز رقم {reservation.id} بتاريخ انتهاء: {reservation.confirmation_expiry}")
    
    print(f"تم تحديث {count} حجز بنجاح.")

if __name__ == "__main__":
    add_expiry_to_all_reservations()