#!/usr/bin/env python
"""
إنشاء تقرير حالة سيارة اختباري كامل مع صور وعناصر فحص للتأكد من عمل النموذج بشكل صحيح
"""

import os
import django
import tempfile
from PIL import Image
from io import BytesIO
from django.utils import timezone
from django.core.files.uploadedfile import SimpleUploadedFile
from datetime import timedelta
import random

# إعداد Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'car_rental_project.settings')
django.setup()

# استيراد النماذج بعد إعداد Django
from django.contrib.auth import get_user_model
from rental.models import Car, Reservation, CarConditionReport, CarInspectionImage, CarInspectionItem, CarInspectionDetail, CarInspectionCategory

User = get_user_model()

def create_test_image(filename, color=(255, 0, 0)):
    """إنشاء صورة اختبارية لرفعها مع التقرير"""
    image = Image.new('RGB', (100, 100), color=color)
    temp_file = BytesIO()
    image.save(temp_file, format='JPEG')
    temp_file.seek(0)
    
    # إنشاء ملف مرفوع وهمي
    return SimpleUploadedFile(
        name=filename,
        content=temp_file.read(),
        content_type='image/jpeg'
    )

def create_test_car_condition_report():
    """إنشاء تقرير حالة سيارة اختباري كامل"""
    print("بدء إنشاء تقرير حالة سيارة اختباري كامل...")

    # البحث عن مستخدم موجود أو إنشاء مستخدم جديد
    try:
        user = User.objects.filter(is_staff=True).first()
        if not user:
            user = User.objects.create_user(
                username="admin_test",
                password="Admin123!",
                email="admin_test@example.com",
                is_staff=True
            )
            print(f"تم إنشاء مستخدم جديد: {user.username}")
        else:
            print(f"تم العثور على مستخدم موجود: {user.username}")
    except Exception as e:
        print(f"خطأ في العثور على/إنشاء مستخدم: {str(e)}")
        return

    # البحث عن مستخدم عادي أو إنشاء مستخدم جديد
    try:
        customer = User.objects.filter(is_staff=False).first()
        if not customer:
            customer = User.objects.create_user(
                username="customer_test",
                password="Customer123!",
                email="customer_test@example.com",
                is_staff=False
            )
            print(f"تم إنشاء عميل جديد: {customer.username}")
        else:
            print(f"تم العثور على عميل موجود: {customer.username}")
    except Exception as e:
        print(f"خطأ في العثور على/إنشاء عميل: {str(e)}")
        return

    # البحث عن سيارة موجودة أو إنشاء سيارة جديدة
    try:
        car = Car.objects.first()
        if not car:
            car = Car.objects.create(
                make="تويوتا",
                model="كورولا",
                year=2023,
                color="أبيض",
                plate_number="أ ب ج 1234",
                daily_rate=200.0,
                is_available=True
            )
            print(f"تم إنشاء سيارة جديدة: {car}")
        else:
            print(f"تم العثور على سيارة موجودة: {car}")
    except Exception as e:
        print(f"خطأ في العثور على/إنشاء سيارة: {str(e)}")
        return

    # البحث عن حجز موجود أو إنشاء حجز جديد
    try:
        # البحث عن حجز موجود للسيارة
        reservation = Reservation.objects.filter(car=car).first()
        
        if not reservation:
            # إنشاء حجز جديد
            start_date = timezone.now() - timedelta(days=7)
            end_date = timezone.now() - timedelta(days=1)
            
            reservation = Reservation.objects.create(
                user=customer,
                car=car,
                start_date=start_date,
                end_date=end_date,
                pickup_location="مكتب الشركة الرئيسي",
                return_location="مكتب الشركة الرئيسي",
                status="completed",  # مكتمل
                total_price=car.daily_rate * 6,  # 6 أيام
                payment_status="paid"  # مدفوع
            )
            print(f"تم إنشاء حجز جديد: {reservation.id}")
        else:
            print(f"تم العثور على حجز موجود: {reservation.id}")
            
    except Exception as e:
        print(f"خطأ في العثور على/إنشاء حجز: {str(e)}")
        return

    # التحقق من وجود فئات وعناصر الفحص
    try:
        # إنشاء فئات الفحص إذا لم تكن موجودة
        categories = []
        category_names = ["المحرك", "نظام التعليق", "الفرامل", "الإطارات", "الهيكل الخارجي", "المقصورة الداخلية"]
        
        for i, name in enumerate(category_names):
            category, created = CarInspectionCategory.objects.get_or_create(
                name=name,
                defaults={
                    'description': f'فحص {name}',
                    'display_order': i+1,
                    'is_active': True
                }
            )
            categories.append(category)
            if created:
                print(f"تم إنشاء فئة فحص جديدة: {category.name}")
            else:
                print(f"تم العثور على فئة فحص موجودة: {category.name}")
        
        # التأكد من وجود عناصر فحص لكل فئة
        inspection_items = []
        for category in categories:
            # إنشاء عناصر فحص لهذه الفئة إذا لم تكن موجودة
            items_count = CarInspectionItem.objects.filter(category=category).count()
            
            if items_count == 0:
                for i in range(3):  # إنشاء 3 عناصر لكل فئة
                    item = CarInspectionItem.objects.create(
                        category=category,
                        name=f"{category.name} - عنصر {i+1}",
                        description=f"وصف لعنصر {category.name} رقم {i+1}",
                        is_active=True,
                        display_order=i+1,
                        is_important=True if i == 0 else False
                    )
                    inspection_items.append(item)
                    print(f"تم إنشاء عنصر فحص جديد: {item.name}")
            else:
                items = CarInspectionItem.objects.filter(category=category)
                inspection_items.extend(items)
                print(f"تم العثور على {items.count()} عنصر فحص لفئة {category.name}")
    
    except Exception as e:
        print(f"خطأ في التحقق من/إنشاء فئات وعناصر الفحص: {str(e)}")
        return

    # إنشاء تقرير حالة السيارة
    try:
        print(f"[{timezone.now()}] بدء عملية حفظ تقرير حالة السيارة...")
        
        # طباعة معلومات الحجز المرتبط
        print(f"الحجز المرتبط: {reservation.id}")
        print(f"حالة الحجز: {reservation.status}")
        
        print("معلومات التقرير قبل الحفظ - السيارة ID: {}, الحجز ID: {}".format(car.id, reservation.id))
        
        # إنشاء تقرير جديد
        report = CarConditionReport.objects.create(
            car=car,
            reservation=reservation,  # ربط التقرير بالحجز
            report_type='return',  # استلام أو تسليم
            inspection_type='visual',  # بصري أو إلكتروني
            mileage=15000,
            date=timezone.now(),
            car_condition='excellent',  # ممتاز، جيد، متوسط، سيء
            fuel_level='full',  # ممتلئ، 3/4، 1/2، 1/4، فارغ
            notes="تم فحص السيارة وهي بحالة ممتازة",
            created_by=user
        )
        
        print("\n=== ملخص بيانات التقرير قبل الحفظ النهائي ===")
        print(f"🚗 السيارة: {car.make} {car.model} (ID: {car.id})")
        print(f"📋 نوع التقرير: {report.get_report_type_display()}")
        print(f"📅 التاريخ: {report.date}")
        print(f"🔍 نوع الفحص: {report.inspection_type}")
        print(f"🔢 عداد المسافات: {report.mileage} كم")
        print(f"⛽ مستوى الوقود: {report.fuel_level}%")
        print(f"📝 الملاحظات: {report.notes}")
        print("===========================================\n")
        
        # إنشاء صور للتقرير
        image_types = [
            ('front_image', 'صورة أمامية للسيارة', (255, 0, 0)),  # أحمر
            ('rear_image', 'صورة خلفية للسيارة', (0, 255, 0)),     # أخضر
            ('side_image', 'صورة جانبية للسيارة', (0, 0, 255)),    # أزرق
            ('interior_image', 'صورة داخلية للسيارة', (255, 255, 0))  # أصفر
        ]
        
        for image_type, description, color in image_types:
            try:
                # إنشاء صورة وهمية
                test_image = create_test_image(f"{image_type}.jpg", color)
                
                # إنشاء سجل للصورة
                img = CarInspectionImage.objects.create(
                    report=report,
                    image=test_image,
                    description=description,
                    inspection_detail=None  # صورة عامة
                )
                print(f"✅ تم إنشاء صورة {image_type}: {img.id}")
            except Exception as e:
                print(f"❌ خطأ في إنشاء صورة {image_type}: {str(e)}")
        
        # إنشاء عناصر تفاصيل الفحص
        conditions = ['excellent', 'good', 'fair', 'poor']
        
        for item in random.sample(inspection_items, min(len(inspection_items), 10)):
            try:
                # إنشاء تفصيل فحص عشوائي
                condition = random.choice(conditions)
                needs_repair = condition in ['fair', 'poor']
                notes = f"ملاحظات حول {item.name}" if needs_repair else ""
                
                detail = CarInspectionDetail.objects.create(
                    report=report,
                    inspection_item=item,
                    condition=condition,
                    notes=notes,
                    needs_repair=needs_repair
                )
                print(f"✅ تم إنشاء تفصيل فحص لعنصر '{item.name}' بحالة '{condition}'")
            except Exception as e:
                print(f"❌ خطأ في إنشاء تفصيل فحص لعنصر '{item.name}': {str(e)}")
        
        print(f"✅ تم إنشاء تقرير حالة السيارة بنجاح (ID: {report.id})")
        
        # طباعة تفاصيل التقرير
        print(f"معرف التقرير: {report.id}")
        print(f"السيارة: {report.car}")
        print(f"الحجز: {report.reservation}")
        print(f"نوع التقرير: {report.get_report_type_display()}")
        print(f"نوع الفحص: {report.get_inspection_type_display()}")
        print(f"المسافة المقطوعة: {report.mileage}")
        print(f"التاريخ: {report.date}")
        print(f"حالة السيارة: {report.get_car_condition_display()}")
        print(f"مستوى الوقود: {report.get_fuel_level_display()}")
        print(f"الملاحظات: {report.notes}")
        print(f"تم الإنشاء بواسطة: {report.created_by}")
        print(f"تاريخ الإنشاء: {report.created_at}")
        
        # طباعة عدد الصور وتفاصيل الفحص
        image_count = CarInspectionImage.objects.filter(report=report).count()
        detail_count = CarInspectionDetail.objects.filter(report=report).count()
        print(f"عدد الصور المرفقة: {image_count}")
        print(f"عدد عناصر الفحص: {detail_count}")
        
        return report
    except Exception as e:
        print(f"❌ خطأ في إنشاء تقرير حالة السيارة: {str(e)}")
        return None

if __name__ == "__main__":
    report = create_test_car_condition_report()
    if report:
        print("✅✅ تم إنشاء التقرير بنجاح!")
    else:
        print("❌❌ فشل إنشاء التقرير!")