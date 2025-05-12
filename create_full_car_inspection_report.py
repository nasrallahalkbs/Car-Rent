#!/usr/bin/env python
"""
إنشاء تقرير فحص سيارة اختباري كامل مع جميع التفاصيل المطلوبة في النموذج
"""

import os
import django
import random
import tempfile
import string
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO
from django.utils import timezone
from django.core.files.uploadedfile import SimpleUploadedFile
from datetime import timedelta

# إعداد Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'car_rental_project.settings')
django.setup()

# استيراد النماذج بعد إعداد Django
from django.contrib.auth import get_user_model
from rental.models import (
    Car, 
    Reservation, 
    CarConditionReport, 
    CarInspectionImage, 
    CarInspectionItem, 
    CarInspectionDetail, 
    CarInspectionCategory,
    CustomerSignature
)

User = get_user_model()

def create_car_image(filename, color=(255, 255, 255), text="", car_part=None):
    """إنشاء صورة احترافية لسيارة (بشكل تخطيطي)"""
    # إنشاء صورة بيضاء أولاً
    width, height = 400, 300
    image = Image.new('RGB', (width, height), color=color)
    draw = ImageDraw.Draw(image)
    
    # رسم تخطيط بسيط لسيارة
    if car_part == "front":
        # رسم الواجهة الأمامية للسيارة
        draw.rectangle([100, 100, 300, 200], outline="black", width=2)  # هيكل السيارة
        draw.ellipse([130, 170, 170, 210], outline="black", width=2)    # العجلة اليسرى
        draw.ellipse([230, 170, 270, 210], outline="black", width=2)    # العجلة اليمنى
        draw.rectangle([140, 120, 260, 160], outline="black", width=2)  # الزجاج الأمامي
    elif car_part == "rear":
        # رسم الواجهة الخلفية للسيارة
        draw.rectangle([100, 100, 300, 200], outline="black", width=2)  # هيكل السيارة
        draw.ellipse([130, 170, 170, 210], outline="black", width=2)    # العجلة اليسرى
        draw.ellipse([230, 170, 270, 210], outline="black", width=2)    # العجلة اليمنى
        draw.rectangle([120, 130, 280, 160], outline="black", width=2)  # الزجاج الخلفي
    elif car_part == "side":
        # رسم الواجهة الجانبية للسيارة
        draw.rectangle([50, 130, 350, 200], outline="black", width=2)   # هيكل السيارة
        draw.ellipse([80, 180, 120, 220], outline="black", width=2)     # العجلة الأمامية
        draw.ellipse([280, 180, 320, 220], outline="black", width=2)    # العجلة الخلفية
        draw.rectangle([130, 100, 270, 150], outline="black", width=2)  # الزجاج الجانبي
    elif car_part == "interior":
        # رسم المقصورة الداخلية للسيارة
        draw.rectangle([50, 50, 350, 250], outline="black", width=2)    # إطار المقصورة
        draw.ellipse([150, 150, 250, 250], outline="black", width=2)    # عجلة القيادة
        draw.rectangle([50, 150, 350, 200], outline="black", width=2)   # لوحة القيادة
    else:
        # رسم تخطيط بسيط لجزء من السيارة
        draw.rectangle([100, 100, 300, 200], outline="black", width=2)
    
    # إضافة نص توضيحي
    draw.text((width//2 - 80, 20), f"{text}", fill="black")
    draw.text((width//2 - 80, height - 30), f"صورة {filename}", fill="black")
    
    # تحويل الصورة إلى بايت
    temp_file = BytesIO()
    image.save(temp_file, format='JPEG')
    temp_file.seek(0)
    
    # إنشاء ملف مرفوع وهمي
    return SimpleUploadedFile(
        name=filename,
        content=temp_file.read(),
        content_type='image/jpeg'
    )

def generate_random_signature():
    """إنشاء توقيع عشوائي كصورة"""
    # إنشاء صورة بيضاء
    width, height = 300, 150
    image = Image.new('RGB', (width, height), color=(255, 255, 255))
    draw = ImageDraw.Draw(image)
    
    # رسم خط توقيع عشوائي
    points = []
    x, y = 50, 75
    for i in range(20):
        x += random.randint(5, 15)
        y += random.randint(-10, 10)
        points.append((x, y))
    
    draw.line(points, fill="black", width=2)
    
    # تحويل الصورة إلى بايت
    temp_file = BytesIO()
    image.save(temp_file, format='PNG')
    temp_file.seek(0)
    
    # إنشاء ملف مرفوع وهمي
    return SimpleUploadedFile(
        name="signature.png",
        content=temp_file.read(),
        content_type='image/png'
    )

def create_full_car_inspection_report():
    """إنشاء تقرير فحص سيارة اختباري كامل مع جميع التفاصيل"""
    print("بدء إنشاء تقرير فحص سيارة اختباري كامل...")

    # البحث عن مستخدم موجود أو إنشاء مستخدم جديد (مسؤول)
    try:
        user = User.objects.filter(is_staff=True).first()
        if not user:
            user = User.objects.create_user(
                username="admin_test",
                password="Admin123!",
                email="admin_test@example.com",
                is_staff=True
            )
            print(f"تم إنشاء مستخدم مسؤول جديد: {user.username}")
        else:
            print(f"تم العثور على مستخدم مسؤول موجود: {user.username}")
    except Exception as e:
        print(f"خطأ في العثور على/إنشاء مستخدم مسؤول: {str(e)}")
        return

    # البحث عن مستخدم عادي أو إنشاء مستخدم جديد (عميل)
    try:
        customer = User.objects.filter(is_staff=False).first()
        if not customer:
            customer = User.objects.create_user(
                username="customer_test",
                password="Customer123!",
                email="customer_test@example.com",
                is_staff=False,
                first_name="عميل",
                last_name="اختباري"
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
                model="كامري",
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
        # قائمة بأسماء فئات الفحص الرئيسية
        inspection_categories = []
        category_names = [
            "المحرك", "نظام التعليق", "الفرامل", "الإطارات", 
            "الهيكل الخارجي", "المقصورة الداخلية", "أنظمة السلامة", 
            "نظام التكييف", "نظام الوقود", "الكهرباء"
        ]
        
        # إنشاء فئات الفحص
        for i, name in enumerate(category_names):
            category, created = CarInspectionCategory.objects.get_or_create(
                name=name,
                defaults={
                    'description': f'فحص {name}',
                    'display_order': i+1,
                    'is_active': True
                }
            )
            inspection_categories.append(category)
            if created:
                print(f"تم إنشاء فئة فحص جديدة: {category.name}")
            else:
                print(f"تم العثور على فئة فحص موجودة: {category.name}")
        
        # عناصر الفحص لكل فئة
        engine_items = [
            "المحرك - صوت عام", "حساسات المحرك", "زيت المحرك", 
            "نظام التبريد", "حزام المحرك", "خراطيم المحرك"
        ]
        suspension_items = [
            "نظام التعليق الأمامي", "نظام التعليق الخلفي", 
            "عمود التوازن", "مساعدات الصدمات"
        ]
        brakes_items = [
            "دواسة الفرامل", "فحمات الفرامل الأمامية", 
            "فحمات الفرامل الخلفية", "أسطوانات الفرامل"
        ]
        tires_items = [
            "الإطارات الأمامية", "الإطارات الخلفية", 
            "إطار احتياطي", "عجلات الألمنيوم"
        ]
        exterior_items = [
            "الصدام الأمامي", "الصدام الخلفي", "أبواب السيارة",
            "سقف السيارة", "الزجاج الأمامي", "المصابيح الأمامية",
            "المصابيح الخلفية", "المرايا الجانبية"
        ]
        interior_items = [
            "المقاعد", "لوحة القيادة", "عجلة القيادة", 
            "مرآة الرؤية الخلفية", "حزام الأمان", "السجاد"
        ]
        safety_items = [
            "نظام الوسائد الهوائية", "نظام مانع الانغلاق ABS", 
            "نظام الثبات الإلكتروني", "حساسات الركن"
        ]
        ac_items = [
            "مكيف الهواء", "مروحة التبريد", "لوحة التحكم بالتكييف"
        ]
        fuel_items = [
            "خزان الوقود", "مضخة الوقود", "مؤشر الوقود"
        ]
        electrical_items = [
            "البطارية", "نظام الإضاءة", "مؤشرات لوحة القيادة",
            "نظام الصوت", "نوافذ كهربائية"
        ]
        
        # قائمة بجميع عناصر الفحص مع فئاتها
        all_items_by_category = {
            "المحرك": engine_items,
            "نظام التعليق": suspension_items,
            "الفرامل": brakes_items,
            "الإطارات": tires_items,
            "الهيكل الخارجي": exterior_items,
            "المقصورة الداخلية": interior_items,
            "أنظمة السلامة": safety_items,
            "نظام التكييف": ac_items,
            "نظام الوقود": fuel_items,
            "الكهرباء": electrical_items
        }
        
        # إنشاء عناصر الفحص لكل فئة
        all_inspection_items = []
        for category in inspection_categories:
            if category.name in all_items_by_category:
                item_names = all_items_by_category[category.name]
                
                # التحقق من وجود العناصر أو إنشائها
                for i, item_name in enumerate(item_names):
                    item, created = CarInspectionItem.objects.get_or_create(
                        category=category,
                        name=item_name,
                        defaults={
                            'description': f'فحص {item_name}',
                            'is_active': True,
                            'display_order': i+1,
                            'is_important': i < 2  # جعل أول عنصرين مهمين
                        }
                    )
                    
                    all_inspection_items.append(item)
                    if created:
                        print(f"تم إنشاء عنصر فحص جديد: {item.name}")
        
        print(f"إجمالي عناصر الفحص: {len(all_inspection_items)}")
    
    except Exception as e:
        print(f"خطأ في التحقق من/إنشاء فئات وعناصر الفحص: {str(e)}")
        return

    # إنشاء تقرير حالة السيارة
    try:
        print(f"[{timezone.now()}] بدء عملية حفظ تقرير حالة السيارة...")
        
        # طباعة معلومات الحجز المرتبط
        print(f"الحجز المرتبط: {reservation.id}")
        print(f"حالة الحجز: {reservation.status}")
        
        print(f"معلومات التقرير قبل الحفظ - السيارة ID: {car.id}, الحجز ID: {reservation.id}")
        
        # بيانات افتراضية للتقرير
        report_data = {
            'car': car,
            'reservation': reservation,
            'report_type': 'return',  # استلام من العميل
            'inspection_type': 'visual',
            'mileage': 30500,  # قراءة عداد المسافات بالكيلومترات
            'date': timezone.now(),
            'car_condition': 'good',
            'fuel_level': 'half',
            'notes': f"""
            تم فحص السيارة بعد انتهاء فترة الإيجار من العميل {customer.get_full_name() or customer.username}
            نتائج الفحص:
            - حالة السيارة العامة جيدة
            - يوجد بعض الخدوش البسيطة في الصدام الأمامي
            - نظام الفرامل يحتاج إلى صيانة
            - مستوى الوقود نصف خزان
            - السيارة نظيفة بشكل عام
            """,
            'created_by': user
        }
        
        # إنشاء تقرير جديد
        report = CarConditionReport.objects.create(**report_data)
        
        print("\n=== ملخص بيانات التقرير ===")
        print(f"🚗 السيارة: {car.make} {car.model} (ID: {car.id})")
        print(f"📋 نوع التقرير: {report.get_report_type_display()}")
        print(f"📅 التاريخ: {report.date}")
        print(f"🔍 نوع الفحص: {report.get_inspection_type_display()}")
        print(f"🔢 عداد المسافات: {report.mileage} كم")
        print(f"⛽ مستوى الوقود: {report.get_fuel_level_display()}")
        print(f"📝 الملاحظات: {report.notes}")
        print("===========================================\n")
        
        # إنشاء صور للتقرير
        image_specs = [
            ('car_front.jpg', 'صورة أمامية للسيارة', (255, 255, 255), "front"),
            ('car_rear.jpg', 'صورة خلفية للسيارة', (255, 255, 255), "rear"),
            ('car_side.jpg', 'صورة جانبية للسيارة', (255, 255, 255), "side"),
            ('car_interior.jpg', 'صورة داخلية للسيارة', (255, 255, 255), "interior"),
            ('dashboard.jpg', 'صورة لوحة القيادة', (255, 255, 255), None),
            ('engine.jpg', 'صورة المحرك', (255, 255, 255), None),
            ('scratch_front.jpg', 'خدش في الصدام الأمامي', (255, 245, 245), None),  # لون وردي فاتح للخدش
            ('tires.jpg', 'صورة الإطارات', (255, 255, 255), None),
        ]
        
        for filename, description, color, car_part in image_specs:
            try:
                # إنشاء صورة
                image_file = create_car_image(filename, color, description, car_part)
                
                # إنشاء سجل للصورة
                img = CarInspectionImage.objects.create(
                    report=report,
                    image=image_file,
                    description=description,
                    inspection_detail=None  # صورة عامة
                )
                print(f"✅ تم إنشاء صورة {filename}: {img.id}")
            except Exception as e:
                print(f"❌ خطأ في إنشاء صورة {filename}: {str(e)}")
        
        # إنشاء عناصر تفاصيل الفحص
        conditions = {
            'excellent': 20,  # 20% ممتاز
            'good': 40,       # 40% جيد
            'fair': 30,       # 30% متوسط
            'poor': 10        # 10% سيء
        }
        
        # قائمة بجميع العناصر التي تم فحصها
        inspected_items = []
        
        # إنشاء تفاصيل فحص لجميع العناصر
        for item in all_inspection_items:
            try:
                # اختيار الحالة بناءً على نسب الاحتمال المحددة
                condition = random.choices(
                    list(conditions.keys()),
                    weights=list(conditions.values()),
                    k=1
                )[0]
                
                # تحديد ما إذا كان يحتاج إصلاح (الحالات fair و poor)
                needs_repair = condition in ['fair', 'poor']
                notes = f"ملاحظات: {item.name} بحالة {condition}" if needs_repair else ""
                
                # إنشاء تفصيل فحص
                detail = CarInspectionDetail.objects.create(
                    report=report,
                    inspection_item=item,
                    condition=condition,
                    notes=notes,
                    needs_repair=needs_repair
                )
                
                inspected_items.append(item)
                print(f"✅ تم إنشاء تفصيل فحص لعنصر '{item.name}' بحالة '{condition}'")
                
                # إضافة صورة لبعض عناصر الفحص التي تحتاج إصلاح (20% من العناصر)
                if needs_repair and random.random() < 0.2:
                    image_file = create_car_image(
                        f"{item.name.replace(' ', '_')}.jpg", 
                        (255, 245, 245),  # لون وردي فاتح للإشارة إلى الحاجة للإصلاح
                        f"مشكلة في {item.name}"
                    )
                    
                    img = CarInspectionImage.objects.create(
                        report=report,
                        image=image_file,
                        description=f"صورة توضح مشكلة في {item.name}",
                        inspection_detail=detail  # ربط الصورة بتفصيل الفحص
                    )
                    print(f"  📸 تم إضافة صورة لعنصر الفحص '{item.name}'")
            
            except Exception as e:
                print(f"❌ خطأ في إنشاء تفصيل فحص لعنصر '{item.name}': {str(e)}")
        
        # إنشاء توقيع العميل
        try:
            signature_image = generate_random_signature()
            
            signature = CustomerSignature.objects.create(
                report=report,
                signature=signature_image,
                name=customer.get_full_name() or customer.username,
                date=timezone.now(),
                agreement_text="أقر بصحة حالة السيارة الموضحة في هذا التقرير"
            )
            
            print(f"✅ تم إنشاء توقيع للعميل: {signature.name}")
        except Exception as e:
            print(f"❌ خطأ في إنشاء توقيع العميل: {str(e)}")
        
        # طباعة ملخص نهائي للتقرير
        print(f"\n✅✅ تم إنشاء تقرير فحص حالة السيارة بنجاح (ID: {report.id})")
        
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
        
        # طباعة عدد الصور وتفاصيل الفحص والعناصر الأخرى
        image_count = CarInspectionImage.objects.filter(report=report).count()
        detail_count = CarInspectionDetail.objects.filter(report=report).count()
        print(f"\nإحصائيات التقرير:")
        print(f"عدد الصور المرفقة: {image_count}")
        print(f"عدد عناصر الفحص: {detail_count}")
        print(f"عدد عناصر الفحص التي تحتاج إصلاح: {CarInspectionDetail.objects.filter(report=report, needs_repair=True).count()}")
        
        # إحصاءات حالة العناصر
        condition_stats = {}
        for condition in conditions.keys():
            count = CarInspectionDetail.objects.filter(report=report, condition=condition).count()
            percentage = (count / detail_count) * 100 if detail_count > 0 else 0
            condition_stats[condition] = (count, f"{percentage:.1f}%")
        
        print("\nتوزيع حالات عناصر الفحص:")
        for condition, (count, percentage) in condition_stats.items():
            condition_display = {
                'excellent': 'ممتاز',
                'good': 'جيد',
                'fair': 'متوسط',
                'poor': 'سيء'
            }.get(condition, condition)
            print(f"  - {condition_display}: {count} ({percentage})")
        
        return report
    except Exception as e:
        print(f"❌ خطأ في إنشاء تقرير حالة السيارة: {str(e)}")
        return None

if __name__ == "__main__":
    report = create_full_car_inspection_report()
    if report:
        print("\n✅✅✅ تم إنشاء التقرير الكامل بنجاح!")
    else:
        print("\n❌❌❌ فشل إنشاء التقرير!")