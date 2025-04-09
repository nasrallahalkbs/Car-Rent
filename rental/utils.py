from .models import Reservation
from datetime import timedelta

def get_car_availability(car_id, start_date, end_date, exclude_reservation=None):
    """
    التحقق من توفر السيارة بين تاريخين محددين
    
    Args:
        car_id: معرف السيارة
        start_date: تاريخ البداية
        end_date: تاريخ النهاية
        exclude_reservation: معرف الحجز المراد استبعاده من التحقق (مفيد عند تعديل حجز موجود)
        
    Returns:
        bool: True إذا كانت السيارة متاحة، False خلاف ذلك
    """
    # البحث عن أي حجوزات تتداخل مع الفترة المطلوبة
    query = Reservation.objects.filter(
        car_id=car_id,
        status__in=['pending', 'confirmed'],  # البحث فقط عن الحجوزات النشطة
    ).exclude(
        # استبعاد الحجوزات التي تنتهي قبل تاريخ البداية المطلوب
        end_date__lt=start_date
    ).exclude(
        # استبعاد الحجوزات التي تبدأ بعد تاريخ النهاية المطلوب
        start_date__gt=end_date
    )
    
    # إذا تم تحديد حجز للاستبعاد، قم باستبعاده من نتائج البحث
    if exclude_reservation:
        query = query.exclude(id=exclude_reservation)
    
    # إذا وجدت أي حجوزات متداخلة، فالسيارة غير متاحة
    return not query.exists()

def calculate_total_price(car, start_date, end_date):
    """
    حساب السعر الإجمالي لحجز سيارة
    
    Args:
        car: كائن السيارة
        start_date: تاريخ البداية
        end_date: تاريخ النهاية
        
    Returns:
        Decimal: السعر الإجمالي للحجز
    """
    # حساب عدد الأيام
    days = (end_date - start_date).days + 1
    
    # حساب السعر الإجمالي
    total_price = car.daily_rate * days
    
    return total_price

def get_unavailable_dates(car_id):
    """
    الحصول على قائمة التواريخ غير المتاحة لسيارة محددة
    
    Args:
        car_id: معرف السيارة
        
    Returns:
        list: قائمة التواريخ غير المتاحة
    """
    # الحصول على جميع الحجوزات النشطة للسيارة
    reservations = Reservation.objects.filter(
        car_id=car_id, 
        status__in=['pending', 'confirmed']
    )
    
    unavailable_dates = []
    
    # إنشاء قائمة بجميع التواريخ المحجوزة
    for reservation in reservations:
        current_date = reservation.start_date
        while current_date <= reservation.end_date:
            unavailable_dates.append(current_date)
            current_date += timedelta(days=1)
            
    return unavailable_dates