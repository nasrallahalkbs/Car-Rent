"""
إنشاء سجلات نشاط للمسؤولين العاديين للتأكد من ظهورها في الصفحة المخصصة
"""
import os
import sys
import django
import random
from datetime import datetime, timedelta

# تهيئة بيئة Django
sys.path.append('.')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'car_rental_project.settings')
django.setup()

from django.utils import timezone
from rental.models_superadmin import AdminActivity, AdminUser, Role

def create_regular_admin_logs():
    """إنشاء سجلات نشاط للمسؤولين العاديين"""
    # العثور على المسؤولين العاديين (غير المشرفين الأعلى)
    regular_admins = AdminUser.objects.filter(is_superadmin=False)
    print(f"عدد المسؤولين العاديين: {regular_admins.count()}")
    
    # إذا لم يوجد مسؤولين عاديين، أنشئ واحداً
    if regular_admins.count() == 0:
        # نحتاج إلى إنشاء دور إذا لم يوجد
        if Role.objects.count() == 0:
            role = Role.objects.create(
                name="مسؤول المبيعات",
                description="دور مسؤول المبيعات والحجوزات"
            )
        else:
            role = Role.objects.first()
            
        from django.contrib.auth import get_user_model
        User = get_user_model()
        
        # إنشاء مستخدم جديد
        user = User.objects.create(
            username="admin_regular",
            email="admin_regular@example.com",
            first_name="مسؤول",
            last_name="عادي",
            is_staff=True,
            is_active=True
        )
        user.set_password("Admin123!")
        user.save()
        
        # إنشاء ملف المسؤول
        admin = AdminUser.objects.create(
            user=user,
            role=role,
            is_superadmin=False,
            is_deleted=False,
            notes="مسؤول عادي تم إنشاؤه للاختبار"
        )
        print(f"تم إنشاء مسؤول عادي جديد: {admin.user.username}")
        regular_admins = [admin]
    
    # أنواع الأنشطة المختلفة
    actions = [
        "تسجيل دخول",
        "تعديل حجز",
        "إضافة حجز",
        "إلغاء حجز",
        "عرض تقرير",
        "تصدير بيانات",
        "تحديث معلومات عميل",
        "مراجعة فواتير",
        "تغيير حالة سيارة",
        "الرد على استفسار"
    ]
    
    # تفاصيل الأنشطة
    details_templates = [
        "تم {} بواسطة المسؤول",
        "قام المسؤول ب{}",
        "{} للعميل رقم {}",
        "{} للسيارة رقم {}",
        "{} في قسم {}"
    ]
    
    # توليد بيانات عشوائية
    sections = ["الحجوزات", "السيارات", "العملاء", "التقارير", "الفواتير"]
    
    # عدد السجلات لكل مسؤول
    logs_count = 20
    activities_created = 0
    
    for admin in regular_admins:
        print(f"إنشاء سجلات للمسؤول: {admin.user.username}")
        
        # توليد سجلات متنوعة للمسؤول
        for i in range(logs_count):
            # اختيار عشوائي لنوع النشاط والتفاصيل
            action = random.choice(actions)
            
            # إنشاء التفاصيل
            detail_template = random.choice(details_templates)
            if "{}" in detail_template:
                if detail_template.count("{}") == 1:
                    details = detail_template.format(action.lower())
                elif detail_template.count("{}") == 2:
                    if "عميل" in detail_template:
                        details = detail_template.format(action.lower(), random.randint(1000, 9999))
                    elif "سيارة" in detail_template:
                        details = detail_template.format(action.lower(), random.randint(100, 999))
                    else:
                        details = detail_template.format(action.lower(), random.choice(sections))
            else:
                details = detail_template
            
            # إنشاء تاريخ عشوائي في آخر 30 يوم
            days_ago = random.randint(0, 30)
            hours_ago = random.randint(0, 23)
            minutes_ago = random.randint(0, 59)
            created_at = timezone.now() - timedelta(days=days_ago, hours=hours_ago, minutes=minutes_ago)
            
            # إنشاء السجل
            activity = AdminActivity.objects.create(
                admin=admin,
                action=action,
                details=details,
                ip_address="192.168.1." + str(random.randint(2, 254)),
                created_at=created_at,
                is_hidden=False,
                affected_item_type=random.choice([None, "reservation", "car", "customer"]),
                affected_item_id=random.randint(1, 1000) if random.random() > 0.3 else None
            )
            
            activities_created += 1
    
    print(f"تم إنشاء {activities_created} سجل نشاط للمسؤولين العاديين بنجاح")

if __name__ == "__main__":
    create_regular_admin_logs()