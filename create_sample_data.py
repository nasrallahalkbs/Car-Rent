"""
إنشاء بيانات تجريبية لقاعدة البيانات للاختبار
"""
import os
import django
import datetime
from decimal import Decimal

# إعداد البيئة
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'car_rental_project.settings')
django.setup()

# استيراد النماذج بعد إعداد البيئة
from django.contrib.auth.models import User
from rental.models import Car, Reservation, Review

def create_sample_data():
    """إنشاء بيانات تجريبية"""
    
    # إنشاء مستخدم تجريبي إذا لم يكن موجودًا
    try:
        test_user = User.objects.get(username='test_user')
        print("المستخدم التجريبي موجود بالفعل")
    except User.DoesNotExist:
        test_user = User.objects.create_user(
            username='test_user',
            email='test@example.com',
            password='password123',
            first_name='محمد',
            last_name='أحمد'
        )
        print("تم إنشاء المستخدم التجريبي")
    
    # إنشاء سيارة تجريبية
    car, created = Car.objects.get_or_create(
        make='تويوتا',
        model='كامري',
        year=2023,
        defaults={
            'category': 'Luxury',  # استخدم الفئات من CATEGORY_CHOICES
            'transmission': 'Automatic',
            'fuel_type': 'Gas',
            'seats': 5,
            'color': 'أبيض',
            'license_plate': 'ABC-123',
            'daily_rate': Decimal('50.00'),
            'is_available': True,
            'image_url': '/static/images/car-placeholder.svg',
            'features': 'تكييف,بلوتوث,كاميرا خلفية,نظام ملاحة'
        }
    )
    if created:
        print("تم إنشاء السيارة التجريبية")
    else:
        print("السيارة التجريبية موجودة بالفعل")
    
    # إنشاء حجز تجريبي مع ضمان بطاقة ائتمان
    today = datetime.date.today()
    start_date = today + datetime.timedelta(days=5)
    end_date = today + datetime.timedelta(days=10)
    
    # احسب المدة والسعر
    duration = (end_date - start_date).days
    total_price = car.daily_rate * duration
    
    # إنشاء حجز تجريبي
    reservation, created = Reservation.objects.get_or_create(
        user=test_user,
        car=car,
        start_date=start_date,
        end_date=end_date,
        defaults={
            'status': 'confirmed',
            'payment_status': 'pending',
            'total_price': total_price,
            'deposit_amount': Decimal('200.00'),
            'full_name': 'محمد أحمد محمود',
            'national_id': '1234567890',
            'guarantee_type': 'credit_card',
            'guarantee_details': '4111111111111111',
            'payment_method': 'credit_card',
            'notes': 'هذا حجز تجريبي مع ضمان بطاقة ائتمان',
        }
    )
    
    if created:
        print("تم إنشاء الحجز التجريبي رقم:", reservation.id)
    else:
        print("الحجز التجريبي موجود بالفعل رقم:", reservation.id)
    
    return reservation

if __name__ == "__main__":
    print("جاري إنشاء البيانات التجريبية...")
    reservation = create_sample_data()
    print(f"اكتمل إنشاء البيانات التجريبية. يمكنك عرض الحجز من خلال: /ar/reservation/{reservation.id}/")