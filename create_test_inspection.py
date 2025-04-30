"""
إنشاء تقرير فحص سيارة تجريبي للاختبار
"""
import os
import django
import datetime
from django.utils import timezone

# إعداد Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "car_rental_project.settings")
django.setup()

from rental.models import Car, CarConditionReport, CarInspectionCategory, CarInspectionItem, Reservation, Customer

def create_test_inspection_report():
    """إنشاء تقرير فحص سيارة تجريبي"""
    
    # التأكد من وجود سيارة على الأقل
    if Car.objects.count() == 0:
        print("إنشاء سيارة تجريبية أولاً...")
        car = Car.objects.create(
            make="تويوتا",
            model="كامري",
            year=2023,
            license_plate="ABC123",
            color="أبيض",
            category="economy",
            transmission="automatic",
            fuel_type="petrol",
            is_active=True
        )
    else:
        car = Car.objects.first()
        
    # التأكد من وجود عميل على الأقل
    if Customer.objects.count() == 0:
        print("إنشاء عميل تجريبي أولاً...")
        customer = Customer.objects.create(
            name="عميل تجريبي",
            email="test@example.com",
            phone="123456789",
            id_number="123456789012",
            id_type="national_id"
        )
    else:
        customer = Customer.objects.first()
    
    # التأكد من وجود حجز على الأقل
    if Reservation.objects.count() == 0:
        print("إنشاء حجز تجريبي أولاً...")
        reservation = Reservation.objects.create(
            car=car,
            customer=customer,
            pickup_date=timezone.now(),
            return_date=timezone.now() + datetime.timedelta(days=7),
            status="confirmed",
            total_price=1000,
            payment_status="unpaid"
        )
    else:
        reservation = Reservation.objects.first()
    
    # إنشاء تقرير فحص جديد
    try:
        report = CarConditionReport.objects.create(
            car=car,
            reservation=reservation,
            date=timezone.now(),
            mileage=15000,
            report_type="inspection",
            fuel_level="half",
            car_condition="good",
            notes="تقرير فحص تجريبي لاختبار التغييرات على نموذج الفحص"
        )
        
        print(f"تم إنشاء تقرير فحص تجريبي (رقم {report.id}) للسيارة {car.make} {car.model}")
        print(f"يمكنك الآن الوصول إلى صفحة التقرير عبر الرابط: /ar/admin/car-condition/{report.id}/details/")
        
        return report
    except Exception as e:
        print(f"حدث خطأ أثناء إنشاء التقرير: {str(e)}")
        
        # عرض الحقول المطلوبة لنموذج CarConditionReport
        print("\nالحقول المطلوبة لنموذج CarConditionReport:")
        for field in CarConditionReport._meta.fields:
            if not field.blank and not field.null and not field.has_default():
                print(f"- {field.name}: مطلوب")
            else:
                print(f"- {field.name}: اختياري")
        
        return None

if __name__ == "__main__":
    create_test_inspection_report()