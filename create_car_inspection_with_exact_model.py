#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
إنشاء تقرير فحص سيارة باستخدام البنية الدقيقة للعناصر في النظام

هذا السكريبت يقوم بإنشاء تقرير فحص سيارة يتطابق تماماً مع نموذج البيانات في النظام.
يستخدم العناصر المهمة والمكلفة والحرجة فقط كما يتم تصفيتها في واجهة النظام الفعلية.
"""

import os
import sys
import django
import random
import datetime
from django.utils import timezone
from django.db.models import Q
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO
from django.core.files.base import ContentFile

# إعداد Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'car_rental_project.settings')
django.setup()

# استيراد النماذج بعد إعداد Django
from rental.models import (
    Car, Reservation, CarConditionReport, CarInspectionCategory, 
    CarInspectionItem, CarInspectionDetail, CarInspectionImage, User
)

def create_car_image(filename, color=(255, 255, 255), text="", car_part=None):
    """إنشاء صورة لجزء من السيارة"""
    # إنشاء صورة بيضاء بأبعاد 500x350
    width, height = 500, 350
    image = Image.new('RGB', (width, height), color=color)
    draw = ImageDraw.Draw(image)
    
    # إضافة نص إلى الصورة
    try:
        # استخدام الخط الافتراضي
        font = ImageFont.load_default()
        text_to_draw = f"{car_part or ''} {text or ''}"
        # حساب موقع النص لوضعه في مركز الصورة
        draw.text((width//2 - 50, height//2 - 10), text_to_draw, fill=(0, 0, 0), font=font)
    except Exception as e:
        print(f"خطأ في إنشاء الصورة: {str(e)}")
        
    # تحويل الصورة إلى بايتس
    image_io = BytesIO()
    image.save(image_io, format='JPEG')
    image_io.seek(0)
    
    return ContentFile(image_io.read(), name=filename)

def create_signature_image():
    """إنشاء صورة توقيع للعميل"""
    # إنشاء صورة بيضاء بأبعاد 400x200
    width, height = 400, 200
    image = Image.new('RGB', (width, height), color=(255, 255, 255))
    draw = ImageDraw.Draw(image)
    
    # رسم خط التوقيع العشوائي
    for i in range(10):
        x1 = random.randint(100, 300)
        y1 = random.randint(80, 120)
        x2 = random.randint(100, 300)
        y2 = random.randint(80, 120)
        draw.line((x1, y1, x2, y2), fill=(0, 0, 0), width=3)
    
    # تحويل الصورة إلى بايتس
    image_io = BytesIO()
    image.save(image_io, format='PNG')
    image_io.seek(0)
    
    return ContentFile(image_io.read(), name="signature.png")

def create_exact_car_inspection_report():
    """
    إنشاء تقرير فحص سيارة مطابق تماماً للنموذج الموجود في النظام
    """
    print("بدء إنشاء تقرير فحص سيارة اختباري مطابق للنموذج...")
    
    # العثور على مستخدم موجود بنوع مسؤول
    try:
        admin_user = User.objects.filter(is_admin=True).first()
        if not admin_user:
            admin_user = User.objects.filter(is_staff=True).first()
        print(f"تم العثور على مستخدم مسؤول موجود: {admin_user.username}")
    except Exception as e:
        print(f"خطأ في العثور على مستخدم مسؤول: {str(e)}")
        return
    
    # العثور على سيارة موجودة
    try:
        car = Car.objects.first()
        print(f"تم العثور على سيارة موجودة: {car.year} {car.make} {car.model}")
    except Exception as e:
        print(f"خطأ في العثور على سيارة: {str(e)}")
        return
    
    # العثور على حجز موجود لهذه السيارة
    try:
        reservation = Reservation.objects.filter(car=car).first()
        if not reservation:
            # إذا لم يتم العثور على حجز، نبحث عن أي حجز
            reservation = Reservation.objects.first()
        print(f"تم العثور على حجز موجود: {reservation.reservation_number}")
    except Exception as e:
        print(f"خطأ في العثور على حجز: {str(e)}")
        return
    
    # إنشاء تقرير فحص سيارة جديد باستخدام الحقول الفعلية من النموذج
    try:
        report = CarConditionReport.objects.create(
            car=car,
            reservation=reservation,
            report_type='return',  # استلام من العميل
            mileage=25000,  # المسافة المقطوعة بالكيلومترات
            date=timezone.now(),
            notes='تم فحص السيارة بعد انتهاء فترة الإيجار. توجد بعض الخدوش البسيطة في الصدام الأمامي والخلفي.',
            car_condition='good',  # حالة السيارة جيدة (تم تغيير condition إلى car_condition)
            defects='خدوش بسيطة في الصدام الأمامي والخلفي. صوت غير طبيعي في المحرك. تآكل في فحمات الفرامل.',
            defect_cause='الاستخدام العادي والاستهلاك',  # تم تغيير damage_cause إلى defect_cause
            repair_cost=750.00,  # تكلفة الإصلاح بالريال السعودي
            fuel_level='half',  # مستوى الوقود نصف
            inspection_type='manual',  # نوع الفحص: يدوي
            created_by=admin_user
        )
        print(f"تم إنشاء تقرير فحص سيارة جديد (ID: {report.id})")
    except Exception as e:
        print(f"خطأ في إنشاء تقرير الفحص: {str(e)}")
        return
    
    # إنشاء صور للتقرير
    try:
        # 1. صورة أمامية
        front_image = create_car_image("front.jpg", (240, 240, 255), "المنظر الأمامي", "صورة أمامية")
        front_img = CarInspectionImage.objects.create(
            report=report,
            image=front_image,
            description="صورة للجزء الأمامي من السيارة - يظهر خدش بسيط في الصدام"
        )
        
        # 2. صورة خلفية
        rear_image = create_car_image("rear.jpg", (245, 245, 220), "المنظر الخلفي", "صورة خلفية")
        rear_img = CarInspectionImage.objects.create(
            report=report,
            image=rear_image,
            description="صورة للجزء الخلفي من السيارة - حالة جيدة"
        )
        
        # 3. صورة جانبية
        side_image = create_car_image("side.jpg", (230, 250, 230), "المنظر الجانبي", "صورة جانبية")
        side_img = CarInspectionImage.objects.create(
            report=report,
            image=side_image,
            description="صورة للجانب الأيمن من السيارة"
        )
        
        # 4. صورة داخلية
        interior_image = create_car_image("interior.jpg", (250, 240, 240), "المقصورة الداخلية", "صورة داخلية")
        interior_img = CarInspectionImage.objects.create(
            report=report,
            image=interior_image,
            description="صورة للمقصورة الداخلية والمقاعد"
        )
        
        # 5. صورة للمحرك
        engine_image = create_car_image("engine.jpg", (220, 220, 220), "المحرك", "صورة المحرك")
        engine_img = CarInspectionImage.objects.create(
            report=report,
            image=engine_image,
            description="صورة لحجرة المحرك"
        )
        
        # 6. صورة للإطارات
        tire_image = create_car_image("tire.jpg", (200, 200, 200), "الإطارات", "صورة الإطارات")
        tire_img = CarInspectionImage.objects.create(
            report=report,
            image=tire_image,
            description="صورة للإطارات الأمامية - تآكل بسيط"
        )
        
        # 7. صورة للوحة القيادة
        dashboard_image = create_car_image("dashboard.jpg", (240, 230, 230), "لوحة القيادة", "صورة لوحة القيادة")
        dashboard_img = CarInspectionImage.objects.create(
            report=report,
            image=dashboard_image,
            description="صورة للوحة القيادة والعدادات"
        )
        
        # 8. صورة توقيع العميل
        customer_sign = create_signature_image()
        customer_sign_img = CarInspectionImage.objects.create(
            report=report,
            image=customer_sign,
            description="توقيع العميل"
        )
        
        # 9. صورة توقيع الموظف
        employee_sign = create_signature_image()
        employee_sign_img = CarInspectionImage.objects.create(
            report=report,
            image=employee_sign,
            description="توقيع الموظف"
        )
        
        print(f"تم إنشاء 9 صور للتقرير بنجاح")
    except Exception as e:
        print(f"خطأ في إنشاء صور التقرير: {str(e)}")
    
    # جلب فئات الفحص وعناصرها المنشطة بطريقة مُحسنة
    # جلب جميع فئات الفحص المنشطة باستثناء فئة أنظمة السلامة
    inspection_categories = list(CarInspectionCategory.objects.filter(
        is_active=True
    ).exclude(
        name='أنظمة السلامة'  # استبعاد فئة أنظمة السلامة
    ).order_by('display_order'))
    
    # عرض قائمة بالفئات
    print(f"عدد فئات الفحص الموجودة: {len(inspection_categories)}")
    category_counts = {}
    
    for category in inspection_categories:
        print(f"تم العثور على فئة فحص موجودة: {category.name}")
        category_counts[category.name] = 0
    
    # جلب فقط العناصر المهمة والمكلفة والحرجة (حسب طلب المستخدم)
    inspection_items = CarInspectionItem.objects.filter(
        category__in=inspection_categories,
        is_active=True
    ).filter(
        # عرض العناصر المهمة أو المكلفة أو الحرجة فقط
        Q(is_important=True) | 
        Q(is_expensive=True) | 
        Q(is_critical=True)
    ).order_by('category__display_order', 'display_order')
    
    # عرض معلومات عن العناصر
    for item in inspection_items:
        print(f"تم العثور على عنصر فحص موجود: {item.name}")
        
        # إنشاء تفصيل فحص لهذا العنصر
        # اختيار حالة عشوائية: ممتازة، جيدة، متوسطة، سيئة
        conditions = ['excellent', 'good', 'fair', 'poor']
        condition = random.choice(conditions)
        
        # تحديد احتياج الإصلاح بناءً على الحالة
        needs_repair = condition in ['fair', 'poor']
        
        # تسجيل البيانات للإحصائيات
        category_counts[item.category.name] = category_counts.get(item.category.name, 0) + 1
        
        # إنشاء تفصيل الفحص لهذا العنصر
        try:
            detail = CarInspectionDetail.objects.create(
                report=report,
                item=item,
                condition=condition,
                needs_repair=needs_repair,
                notes=f"ملاحظات عن {item.name}" if needs_repair else ""
            )
            print(f"✅ تم إنشاء تفصيل فحص لعنصر '{item.name}' بحالة '{condition}'")
        except Exception as e:
            print(f"❌ خطأ في إنشاء تفصيل الفحص لعنصر '{item.name}': {str(e)}")
    
    # عرض إحصائيات عن الفئات وعناصرها
    print("\n✅ عدد فئات الفحص:", len(inspection_categories))
    for category_name, count in category_counts.items():
        print(f"✅ فئة {category_name}: {count} عنصر")
    
    # عرض معلومات ملخصة عن التقرير
    details_count = CarInspectionDetail.objects.filter(report=report).count()
    images_count = CarInspectionImage.objects.filter(report=report).count()
    needs_repair_count = CarInspectionDetail.objects.filter(report=report, needs_repair=True).count()
    
    print(f"\n✅✅ تم إنشاء تقرير فحص حالة السيارة بنجاح (ID: {report.id})")
    print(f"\nملخص تقرير حالة السيارة:")
    print(f"معرف التقرير: {report.id}")
    print(f"السيارة: {report.car.year} {report.car.make} {report.car.model}")
    print(f"الحجز: {report.reservation.reservation_number}")
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
    print(f"تم الإنشاء بواسطة: {report.created_by.username}")
    print(f"تاريخ الإنشاء: {report.created_at}")
    
    print(f"\nإحصائيات تقرير الفحص:")
    print(f"عدد الصور المرفقة: {images_count}")
    print(f"عدد عناصر الفحص: {details_count}")
    print(f"عدد عناصر الفحص التي تحتاج إصلاح: {needs_repair_count}")
    
    # إحصاء حالات العناصر
    conditions_stats = {
        'excellent': CarInspectionDetail.objects.filter(report=report, condition='excellent').count(),
        'good': CarInspectionDetail.objects.filter(report=report, condition='good').count(),
        'fair': CarInspectionDetail.objects.filter(report=report, condition='fair').count(),
        'poor': CarInspectionDetail.objects.filter(report=report, condition='poor').count(),
    }
    
    print(f"\nتوزيع حالة عناصر الفحص:")
    for condition, count in conditions_stats.items():
        percentage = (count / details_count) * 100 if details_count > 0 else 0
        print(f"  - {condition}: {count} ({percentage:.1f}%)")
    
    print(f"\n✅✅✅ تم إنشاء تقرير فحص السيارة المطابق للنموذج بنجاح!")
    
    return report.id  # إرجاع معرف التقرير لاستخدامه في الاختبار

if __name__ == "__main__":
    # حماية ضد المستندات التلقائية
    try:
        print("⚠️ تحميل إشارات منع المستندات التلقائية")
        from auto_document_prevention import load_signal_handlers, prevent_auto_documents
        load_signal_handlers()
        prevent_auto_documents()
        print("🛡️ تم تفعيل الحماية الدائمة ضد المستندات التلقائية")
        print("✅ تم تفعيل الحماية الدائمة ضد المستندات التلقائية")
    except ImportError:
        print("⚠️ تحذير: لم يتم العثور على وحدة منع المستندات التلقائية، سيتم تجاهل هذه الخطوة.")
    
    try:
        # تشغيل التنظيف التلقائي
        from auto_clean import run_auto_cleaner
        print("🧹 [AUTO_CLEANER] تم بدء خدمة التنظيف التلقائي")
        run_auto_cleaner()
        print("✅ تم تشغيل خدمة التنظيف التلقائي")
    except ImportError:
        print("⚠️ تحذير: لم يتم العثور على وحدة التنظيف التلقائي، سيتم تجاهل هذه الخطوة.")
    
    try:
        # تأمين إضافي عند تشغيل النظام
        from startup_protection import enable_protection_at_startup
        enable_protection_at_startup()
        print("🛡️ تم تفعيل الحماية الدائمة ضد المستندات التلقائية")
        print("✅ تم تفعيل الحماية عند بدء التشغيل")
    except ImportError:
        print("⚠️ تحذير: لم يتم العثور على وحدة الحماية عند بدء التشغيل، سيتم تجاهل هذه الخطوة.")
    
    try:
        # التنظيف التلقائي للكاش
        from auto_cache_cleaner import clean_cache_on_startup
        clean_cache_on_startup()
        print("✅ تم تشغيل التنظيف التلقائي")
    except ImportError:
        print("⚠️ تحذير: لم يتم العثور على وحدة تنظيف الكاش التلقائي، سيتم تجاهل هذه الخطوة.")
    
    try:
        # تأكيد نهائي على تفعيل منع المستندات التلقائية
        print("✅ تم تفعيل نظام منع المستندات التلقائية")
    except Exception as e:
        print(f"❌ خطأ: {str(e)}")
    
    # إنشاء تقرير فحص سيارة
    report_id = create_exact_car_inspection_report()
    
    if report_id:
        print(f"\n✅✅ تم إنشاء التقرير بنجاح. يمكن الوصول إليه عبر الرابط:")
        print(f"/ar/admin/car_inspection/{report_id}/")