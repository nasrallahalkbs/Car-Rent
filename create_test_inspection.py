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

from rental.models import Car, CarConditionReport, CarInspectionCategory, CarInspectionItem, Reservation, User

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
        
    # التأكد من وجود مستخدم على الأقل
    if User.objects.count() == 0:
        print("إنشاء مستخدم تجريبي أولاً...")
        # ملاحظة: هنا نستخدم create_user بدلاً من create للمستخدمين
        user = User.objects.create_user(
            username="test_user",
            email="test@example.com",
            password="test12345",
            first_name="مستخدم",
            last_name="تجريبي"
        )
    else:
        user = User.objects.first()
    
    # التأكد من وجود حجز على الأقل
    try:
        # محاولة الحصول على حجز موجود
        reservation = Reservation.objects.first()
        if not reservation:
            raise Reservation.DoesNotExist
    except:
        print("إنشاء حجز تجريبي أولاً...")
        today = timezone.now().date()
        pickup_date = today
        return_date = today + datetime.timedelta(days=7)
        
        # إنشاء حجز جديد
        reservation = Reservation.objects.create(
            user=user,
            car=car,
            start_date=pickup_date,
            end_date=return_date,
            pickup_date=pickup_date,
            return_date=return_date,
            total_price=1000,
            reservation_number="TEST123",
            status="confirmed",
            payment_status="paid"
        )
    
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
        print(f"يمكنك الآن الوصول إلى صفحة التقرير عبر: /ar/admin/car-condition/{report.id}/details/")
        
        # إضافة صور تجريبية للتقرير (الهيكل الخارجي)
        from django.core.files.base import ContentFile
        from rental.models import CarInspectionImage
        
        print("إضافة صور تجريبية للهيكل الخارجي...")
        
        descriptions = [
            "صورة أمامية",
            "صورة خلفية",
            "صورة جانبية",
            "صورة داخلية"
        ]
        
        for desc in descriptions:
            # إنشاء ملف محتوى فارغ - ملاحظة: في بيئة الإنتاج، سيتم تحميل صور حقيقية
            # هنا ننشئ ملف فارغ فقط للتجربة
            content = ContentFile(b'TEST IMAGE CONTENT')
            
            # إنشاء صورة جديدة للتقرير - نضيف صور عامة (لا تنتمي لعنصر فحص محدد)
            image = CarInspectionImage(
                report=report,
                description=desc,
                # لا نضيف حقل inspection_detail لأنها صورة عامة
            )
            
            # حفظ الملف بإسم مناسب
            image_name = f"test_image_{desc.split(' ')[1]}.jpg"
            image.image.save(image_name, content, save=False)
            image.save()
            
            print(f"✓ تمت إضافة {desc}")
        
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