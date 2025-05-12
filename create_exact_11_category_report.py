#!/usr/bin/env python
"""
إنشاء تقرير فحص سيارة اختباري مطابق تماماً لنموذج البيانات مع الـ 11 فئة الموجودة في النظام
"""

import os
import django
import random
from PIL import Image, ImageDraw
from io import BytesIO
from django.utils import timezone
from django.core.files.uploadedfile import SimpleUploadedFile
from datetime import timedelta
import uuid

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
    """إنشاء صورة لجزء من السيارة"""
    # إنشاء صورة بيضاء
    width, height = 400, 300
    image = Image.new('RGB', (width, height), color=color)
    draw = ImageDraw.Draw(image)
    
    # رسم تخطيط بسيط
    if car_part == "front":
        # رسم الواجهة الأمامية للسيارة
        draw.rectangle([100, 100, 300, 200], outline="black", width=2)  # هيكل السيارة
        draw.ellipse([130, 170, 170, 210], outline="black", width=2)    # العجلة اليسرى
        draw.ellipse([230, 170, 270, 210], outline="black", width=2)    # العجلة اليمنى
    elif car_part == "rear":
        # رسم الواجهة الخلفية للسيارة
        draw.rectangle([100, 100, 300, 200], outline="black", width=2)  # هيكل السيارة
        draw.ellipse([130, 170, 170, 210], outline="black", width=2)    # العجلة اليسرى
        draw.ellipse([230, 170, 270, 210], outline="black", width=2)    # العجلة اليمنى
    elif car_part == "side":
        # رسم الواجهة الجانبية للسيارة
        draw.rectangle([50, 130, 350, 200], outline="black", width=2)   # هيكل السيارة
        draw.ellipse([80, 180, 120, 220], outline="black", width=2)     # العجلة الأمامية
        draw.ellipse([280, 180, 320, 220], outline="black", width=2)    # العجلة الخلفية
    else:
        # رسم تخطيط عام
        draw.rectangle([100, 100, 300, 200], outline="black", width=2)
    
    # إضافة نص توضيحي
    draw.text((width//2 - 80, 20), f"{text}", fill="black")
    
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

def create_signature_image():
    """إنشاء صورة توقيع للعميل"""
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

def create_exact_car_inspection_report():
    """إنشاء تقرير فحص سيارة مطابق تماماً للنموذج الموجود مع 11 فئة فحص"""
    print("بدء إنشاء تقرير فحص سيارة اختباري مطابق للنموذج...")

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
            print(f"تم إنشاء مستخدم مسؤول جديد: {user.username}")
        else:
            print(f"تم العثور على مستخدم مسؤول موجود: {user.username}")
    except Exception as e:
        print(f"خطأ في العثور على/إنشاء مستخدم: {str(e)}")
        return

    # البحث عن مستخدم عادي (عميل) أو إنشائه
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
                model="كامري",
                year=2023,
                color="أبيض",
                license_plate="أ ب ج 1234",
                daily_rate=200.0,
                category="Mid-size",
                seats=5,
                transmission="Automatic",
                fuel_type="Gas",
                features="مكيف هواء, نظام صوتي, كاميرا خلفية",
                is_available=True,
                status="available"
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
                total_price=car.daily_rate * 6,  # 6 أيام
                status="completed",
                payment_status="paid"
            )
            print(f"تم إنشاء حجز جديد: {reservation}")
        else:
            print(f"تم العثور على حجز موجود: {reservation}")
            
    except Exception as e:
        print(f"خطأ في العثور على/إنشاء حجز: {str(e)}")
        return

    # التحقق من وجود فئات الفحص وإنشائها إذا لزم الأمر
    try:
        # الحصول على الفئات الحالية من قاعدة البيانات
        existing_categories = {cat.name: cat for cat in CarInspectionCategory.objects.all()}
        print(f"عدد فئات الفحص الموجودة: {len(existing_categories)}")
        
        # تحديد الـ 11 فئة المطلوبة بالضبط
        required_categories = [
            "الهيكل الخارجي",
            "المحرك",
            "نظام الفرامل",
            "نظام التعليق",
            "الفرامل",
            "الأنظمة الكهربائية",
            "الإطارات",
            "المقصورة الداخلية",
            "نظام التكييف",
            "نظام الوقود",
            "الكهرباء"
        ]
        
        categories = {}
        
        # إنشاء الفئات المطلوبة إذا لم تكن موجودة
        for i, name in enumerate(required_categories):
            if name in existing_categories:
                categories[name] = existing_categories[name]
                print(f"تم العثور على فئة فحص موجودة: {name}")
            else:
                category = CarInspectionCategory.objects.create(
                    name=name,
                    description=f'فحص {name}',
                    display_order=i+1,
                    is_active=True
                )
                categories[name] = category
                print(f"تم إنشاء فئة فحص جديدة: {name}")
        
        # إنشاء عناصر الفحص لكل فئة إذا لم تكن موجودة
        items_data = {
            "الهيكل الخارجي": ["الصدام الأمامي", "الصدام الخلفي", "أبواب السيارة", "المصابيح الأمامية", "المصابيح الخلفية"],
            "المحرك": ["المحرك - صوت عام", "حساسات المحرك", "زيت المحرك", "نظام التبريد", "حزام المحرك", "خراطيم المحرك"],
            "نظام الفرامل": ["اسطوانة الفرامل الرئيسية", "أقراص الفرامل", "نظام الفرامل الهيدروليكي"],
            "نظام التعليق": ["نظام التعليق الأمامي", "نظام التعليق الخلفي", "مساعدات الصدمات", "عمود التوازن"],
            "الفرامل": ["دواسة الفرامل", "فحمات الفرامل الأمامية", "فحمات الفرامل الخلفية"],
            "الأنظمة الكهربائية": ["نظام التوجيه", "كمبيوتر السيارة", "نظام التشغيل"],
            "الإطارات": ["الإطارات الأمامية", "الإطارات الخلفية", "إطار احتياطي"],
            "المقصورة الداخلية": ["المقاعد", "لوحة القيادة", "عجلة القيادة", "مرآة الرؤية الخلفية", "حزام الأمان"],
            "نظام التكييف": ["مكيف الهواء", "مروحة التبريد", "لوحة التحكم بالتكييف"],
            "نظام الوقود": ["خزان الوقود", "مضخة الوقود", "مؤشر الوقود"],
            "الكهرباء": ["البطارية", "نظام الإضاءة", "مؤشرات لوحة القيادة", "نظام الصوت"]
        }
        
        # إنشاء أو استخدام عناصر الفحص الموجودة
        created_items = {}
        
        for category_name, item_names in items_data.items():
            if category_name in categories:
                category = categories[category_name]
                existing_items = {item.name: item for item in CarInspectionItem.objects.filter(category=category)}
                
                for i, item_name in enumerate(item_names):
                    if item_name in existing_items:
                        created_items[item_name] = existing_items[item_name]
                        print(f"تم العثور على عنصر فحص موجود: {item_name}")
                    else:
                        item = CarInspectionItem.objects.create(
                            category=category,
                            name=item_name,
                            description=f'فحص {item_name}',
                            display_order=i+1,
                            is_required=True,
                            is_active=True,
                            is_important=i < 2,  # أول عنصرين مهمين في كل فئة
                            is_expensive=i == 1,  # العنصر الثاني مكلف في كل فئة
                            is_critical=i == 0   # العنصر الأول حرج في كل فئة
                        )
                        created_items[item_name] = item
                        print(f"تم إنشاء عنصر فحص جديد: {item_name}")
            else:
                print(f"فئة الفحص غير موجودة: {category_name}")
                
        # طباعة إحصائيات عدد عناصر الفحص لكل فئة
        for category_name in required_categories:
            if category_name in categories:
                category = categories[category_name]
                count = CarInspectionItem.objects.filter(category=category).count()
                print(f"✅ فئة {category_name}: {count} عنصر")
    
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
        
        # إنشاء تقرير حالة السيارة
        report = CarConditionReport.objects.create(
            car=car,
            reservation=reservation,
            report_type='return',  # استلام من العميل
            mileage=25000,  # المسافة المقطوعة بالكيلومترات
            date=timezone.now(),
            car_condition='good',  # جيدة
            fuel_level='half',  # نصف
            notes="تم فحص السيارة بعد انتهاء فترة الإيجار. توجد بعض الخدوش البسيطة في الصدام الأمامي والخلفي.",
            defects="خدوش بسيطة في الصدام الأمامي والخلفي. صوت غير طبيعي في المحرك. تآكل في فحمات الفرامل.",
            defect_cause="الاستخدام العادي والاستهلاك",
            repair_cost=750.00,
            maintenance_type='regular',  # صيانة دورية
            inspection_type='manual',  # فحص يدوي
            is_electronic_inspection=False,
            created_by=user
        )
        
        print(f"✅ تم إنشاء تقرير حالة السيارة بنجاح (ID: {report.id})")
        
        # إنشاء صور للتقرير
        image_specs = [
            ('front.jpg', 'صورة أمامية للسيارة', "front"),
            ('rear.jpg', 'صورة خلفية للسيارة', "rear"),
            ('side.jpg', 'صورة جانبية للسيارة', "side"),
            ('interior.jpg', 'صورة داخلية للسيارة', None),
            ('engine.jpg', 'صورة المحرك', None),
            ('brakes.jpg', 'صورة الفرامل', None),
            ('tires.jpg', 'صورة الإطارات', None),
            ('scratches.jpg', 'صورة الخدوش', None),
            ('dashboard.jpg', 'صورة لوحة القيادة', None)
        ]
        
        for i, (filename, description, car_part) in enumerate(image_specs):
            try:
                # إنشاء صورة
                image_file = create_car_image(filename, color=(255, 255, 255), text=description, car_part=car_part)
                
                # إنشاء سجل للصورة
                img = CarInspectionImage.objects.create(
                    report=report,
                    image=image_file,
                    description=description
                )
                print(f"✅ تم إنشاء صورة {filename}: {img.id}")
            except Exception as e:
                print(f"❌ خطأ في إنشاء صورة {filename}: {str(e)}")
        
        # إنشاء تفاصيل الفحص
        condition_mapping = {
            0: 'excellent',  # ممتازة
            1: 'good',       # جيدة
            2: 'fair',       # متوسطة
            3: 'poor'        # سيئة
        }
        
        # اختيار عدد من العناصر للفحص من كل فئة (على الأقل 2 من كل فئة)
        selected_items = []
        for category_name in required_categories:
            if category_name in categories:
                category = categories[category_name]
                items = list(CarInspectionItem.objects.filter(category=category))
                # اختر على الأقل 2 عناصر من كل فئة أو كل العناصر إذا كان عددها أقل من 2
                num_to_select = max(2, min(len(items), 3))
                selected = random.sample(items, num_to_select) if len(items) >= num_to_select else items
                selected_items.extend(selected)
        
        print(f"تم اختيار {len(selected_items)} عنصر للفحص")
        
        for item in selected_items:
            try:
                # اختيار حالة عشوائية
                condition_index = random.randint(0, 3)
                condition = condition_mapping[condition_index]
                
                # تحديد ما إذا كان يحتاج إصلاح (الحالات fair و poor)
                needs_repair = condition in ['fair', 'poor']
                
                # إنشاء ملاحظات حسب الحالة
                notes = ""
                if condition == 'excellent':
                    notes = f"{item.name} بحالة ممتازة"
                elif condition == 'good':
                    notes = f"{item.name} بحالة جيدة"
                elif condition == 'fair':
                    notes = f"{item.name} بحالة متوسطة - يحتاج فحص"
                elif condition == 'poor':
                    notes = f"{item.name} بحالة سيئة - يحتاج إصلاح"
                
                # بيانات إضافية للإصلاح إذا لزم الأمر
                repair_description = f"إصلاح {item.name}" if needs_repair else ""
                repair_parts = f"قطع غيار {item.name}" if needs_repair else ""
                repair_cost = random.randint(100, 1000) if needs_repair else None
                labor_cost = random.randint(50, 200) if needs_repair else None
                repair_status = 'needed' if needs_repair else 'not_needed'
                
                # إنشاء تفصيل فحص
                detail = CarInspectionDetail.objects.create(
                    report=report,
                    inspection_item=item,
                    condition=condition,
                    notes=notes,
                    needs_repair=needs_repair,
                    repair_description=repair_description,
                    repair_parts=repair_parts,
                    repair_cost=repair_cost,
                    labor_cost=labor_cost,
                    repair_status=repair_status
                )
                
                print(f"✅ تم إنشاء تفصيل فحص لعنصر '{item.name}' بحالة '{condition}'")
                
                # إضافة صورة لبعض العناصر التي تحتاج إصلاح
                if needs_repair and random.random() < 0.3:  # 30% فقط من العناصر التي تحتاج إصلاح
                    image_file = create_car_image(
                        f"{item.name.replace(' ', '_')}.jpg", 
                        color=(255, 245, 245),
                        text=f"مشكلة في {item.name}"
                    )
                    
                    img = CarInspectionImage.objects.create(
                        report=report,
                        image=image_file,
                        description=f"صورة توضح مشكلة في {item.name}",
                        inspection_detail=detail
                    )
                    print(f"  📸 تم إضافة صورة لعنصر الفحص '{item.name}'")
            
            except Exception as e:
                print(f"❌ خطأ في إنشاء تفصيل فحص لعنصر '{item.name}': {str(e)}")
        
        # إنشاء توقيع العميل
        try:
            signature_image = create_signature_image()
            
            signature = CustomerSignature.objects.create(
                report=report,
                signature=signature_image,
                is_customer=True,
                signed_by_name=customer.get_full_name() or customer.username
            )
            
            print(f"✅ تم إنشاء توقيع للعميل: {signature.signed_by_name}")
            
            # إنشاء توقيع الموظف المسؤول
            employee_signature = create_signature_image()
            
            emp_signature = CustomerSignature.objects.create(
                report=report,
                signature=employee_signature,
                is_customer=False,
                signed_by_name=user.get_full_name() or user.username
            )
            
            print(f"✅ تم إنشاء توقيع للموظف: {emp_signature.signed_by_name}")
        except Exception as e:
            print(f"❌ خطأ في إنشاء التوقيعات: {str(e)}")
        
        # طباعة ملخص نهائي للتقرير
        print(f"\n✅✅ تم إنشاء تقرير فحص حالة السيارة بنجاح (ID: {report.id})")
        
        # طباعة تفاصيل التقرير
        print(f"\nملخص تقرير حالة السيارة:")
        print(f"معرف التقرير: {report.id}")
        print(f"السيارة: {report.car}")
        print(f"الحجز: {report.reservation}")
        print(f"نوع التقرير: {report.get_report_type_display()}")
        print(f"المسافة المقطوعة: {report.mileage} كم")
        print(f"التاريخ: {report.date}")
        print(f"حالة السيارة: {report.get_car_condition_display()}")
        print(f"مستوى الوقود: {report.get_fuel_level_display()}")
        print(f"الملاحظات: {report.notes}")
        print(f"الأعطال: {report.defects}")
        print(f"سبب العطل: {report.defect_cause}")
        print(f"تكلفة الإصلاح: {report.repair_cost}")
        print(f"نوع الفحص: {report.get_inspection_type_display()}")
        print(f"تم الإنشاء بواسطة: {report.created_by}")
        print(f"تاريخ الإنشاء: {report.created_at}")
        
        # طباعة إحصائيات
        image_count = CarInspectionImage.objects.filter(report=report).count()
        detail_count = CarInspectionDetail.objects.filter(report=report).count()
        repair_count = CarInspectionDetail.objects.filter(report=report, needs_repair=True).count()
        
        print(f"\nإحصائيات تقرير الفحص:")
        print(f"عدد الصور المرفقة: {image_count}")
        print(f"عدد عناصر الفحص: {detail_count}")
        print(f"عدد عناصر الفحص التي تحتاج إصلاح: {repair_count}")
        
        # إحصائيات حالة العناصر
        conditions = ['excellent', 'good', 'fair', 'poor']
        condition_counts = {}
        
        for condition in conditions:
            count = CarInspectionDetail.objects.filter(report=report, condition=condition).count()
            condition_counts[condition] = count
        
        print("\nتوزيع حالة عناصر الفحص:")
        for condition, count in condition_counts.items():
            percentage = count / detail_count * 100 if detail_count > 0 else 0
            condition_display = dict(CarInspectionItem.CONDITION_CHOICES).get(condition, condition)
            print(f"  - {condition_display}: {count} ({percentage:.1f}%)")
            
        # إحصائيات عناصر الفحص حسب الفئة
        print("\nتوزيع عناصر الفحص حسب الفئات:")
        for category_name in required_categories:
            if category_name in categories:
                category = categories[category_name]
                count = CarInspectionDetail.objects.filter(
                    report=report, 
                    inspection_item__category=category
                ).count()
                percentage = count / detail_count * 100 if detail_count > 0 else 0
                print(f"  - {category.name}: {count} ({percentage:.1f}%)")
        
        return report
        
    except Exception as e:
        print(f"❌ خطأ في إنشاء تقرير حالة السيارة: {str(e)}")
        return None

if __name__ == "__main__":
    report = create_exact_car_inspection_report()
    if report:
        print("\n✅✅✅ تم إنشاء تقرير فحص السيارة المطابق للنموذج بنجاح!")
    else:
        print("\n❌❌❌ فشل إنشاء التقرير!")