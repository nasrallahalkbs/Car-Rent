"""
إضافة سجلات نشاط للمسؤولين العاديين بطريقة مباشرة
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
from django.db import connection  # استيراد الاتصال بقاعدة البيانات
from django.contrib.auth import get_user_model

# نُنشئ سجلات النشاط مباشرة باستخدام SQL
def create_regular_admin_logs_with_sql():
    """إضافة سجلات نشاط للمسؤولين العاديين باستخدام SQL مباشرة"""
    print("بدء إنشاء سجلات نشاط المسؤولين العاديين...")
    
    # التحقق من وجود جدول سجلات النشاط والمسؤولين
    with connection.cursor() as cursor:
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND (name='rental_adminactivity' OR name='rental_adminuser')")
        tables = cursor.fetchall()
        tables = [t[0] for t in tables]
        
        if 'rental_adminactivity' not in tables or 'rental_adminuser' not in tables:
            print(f"الجداول المطلوبة غير موجودة. الجداول المتوفرة: {tables}")
            return False
        
        # الحصول على معلومات المسؤولين
        cursor.execute("""
            SELECT au.id, u.username, au.is_superadmin
            FROM rental_adminuser au
            JOIN rental_user u ON au.user_id = u.id
        """)
        admins = cursor.fetchall()
        
        regular_admins = [admin for admin in admins if admin[2] == 0]  # فلترة المسؤولين العاديين فقط
        
        print(f"المسؤولين العاديين: {len(regular_admins)} من إجمالي {len(admins)}")
        
        # إذا لم يوجد مسؤولين عاديين، أنشئ واحداً
        if not regular_admins:
            print("لا يوجد مسؤولين عاديين. سيتم إنشاء مسؤول عادي...")
            
            # التحقق من وجود دور
            cursor.execute("SELECT id FROM rental_role LIMIT 1")
            roles = cursor.fetchall()
            
            if not roles:
                print("إنشاء دور جديد...")
                cursor.execute("""
                    INSERT INTO rental_role (name, description, created_at, updated_at)
                    VALUES ('مسؤول المبيعات', 'دور مسؤول المبيعات والحجوزات', datetime('now'), datetime('now'))
                """)
                connection.commit()
                
                cursor.execute("SELECT id FROM rental_role LIMIT 1")
                role_id = cursor.fetchone()[0]
            else:
                role_id = roles[0][0]
            
            # إنشاء مستخدم جديد
            User = get_user_model()
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
            cursor.execute("""
                INSERT INTO rental_adminuser 
                (user_id, role_id, is_superadmin, last_login_ip, is_deleted, notes, created_at, updated_at)
                VALUES (?, ?, 0, '127.0.0.1', 0, 'مسؤول عادي تم إنشاؤه للاختبار', datetime('now'), datetime('now'))
            """, [user.id, role_id])
            connection.commit()
            
            # الحصول على معرف المسؤول المنشأ
            cursor.execute("SELECT id FROM rental_adminuser WHERE user_id = ?", [user.id])
            admin_id = cursor.fetchone()[0]
            
            regular_admins = [(admin_id, user.username, 0)]
        
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
            "تم {} للعميل",
            "قام المسؤول ب{}",
            "{} للعميل رقم {}",
            "{} للسيارة رقم {}",
            "{} في قسم {}"
        ]
        
        # أقسام النظام
        sections = ["الحجوزات", "السيارات", "العملاء", "التقارير", "الفواتير"]
        
        # عدد السجلات لكل مسؤول
        logs_count = 20
        activities_created = 0
        
        for admin_id, username, _ in regular_admins:
            print(f"إنشاء سجلات للمسؤول: {username} (ID: {admin_id})")
            
            # توليد سجلات متنوعة للمسؤول
            for i in range(logs_count):
                # اختيار عشوائي لنوع النشاط والتفاصيل
                action = random.choice(actions)
                
                # إنشاء التفاصيل
                detail_template = random.choice(details_templates)
                
                if "{}" in detail_template:
                    if detail_template.count("{}") == 1:
                        details = detail_template.format(action.lower())
                    else:
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
                created_at = (timezone.now() - timedelta(days=days_ago, hours=hours_ago, minutes=minutes_ago)).strftime("%Y-%m-%d %H:%M:%S")
                
                # تحديد إذا كان النشاط يتعلق بعنصر معين
                has_affected_item = random.random() > 0.3
                affected_item_type = random.choice(["reservation", "car", "customer", None]) if has_affected_item else None
                affected_item_id = random.randint(1, 1000) if affected_item_type else None
                
                # إنشاء عنوان IP عشوائي
                ip_address = f"192.168.1.{random.randint(2, 254)}"
                
                # إدراج السجل في قاعدة البيانات
                cursor.execute("""
                    INSERT INTO rental_adminactivity 
                    (admin_id, action, details, ip_address, created_at, is_hidden, affected_item_type, affected_item_id)
                    VALUES (?, ?, ?, ?, ?, 0, ?, ?)
                """, [admin_id, action, details, ip_address, created_at, affected_item_type, affected_item_id])
                
                activities_created += 1
            
            # التزام بالتغييرات بعد كل مسؤول
            connection.commit()
        
        print(f"تم إنشاء {activities_created} سجل نشاط للمسؤولين العاديين بنجاح")
        return True

if __name__ == "__main__":
    create_regular_admin_logs_with_sql()