"""
إنشاء سجلات نشاط اختبارية للمسؤولين للتأكد من عمل نظام الإشعارات
"""
import os
import sys
import django
from datetime import datetime, timedelta

# تهيئة بيئة Django
sys.path.append('.')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'rental.settings')
django.setup()

from django.utils import timezone
from rental.models_superadmin import AdminActivity, AdminUser

def create_test_admin_activities():
    """إنشاء أنشطة اختبارية للمسؤولين"""
    # التحقق من وجود مسؤولين
    admins = AdminUser.objects.all()
    if not admins.exists():
        print("لا يوجد مسؤولون في النظام. يرجى إنشاء مسؤول أولاً.")
        return
    
    admin = admins.first()
    print(f"تم العثور على المسؤول: {admin.user.username} (ID: {admin.id})")
    
    # أنواع الأنشطة للاختبار
    activity_types = [
        {"action": "تسجيل دخول", "details": "تسجيل دخول المسؤول إلى النظام"},
        {"action": "إضافة مستخدم", "details": "إضافة مستخدم جديد باسم 'user123'"},
        {"action": "تحرير بيانات", "details": "تعديل بيانات حجز رقم 12345"},
        {"action": "الموافقة على تقييم", "details": "الموافقة على تقييم المستخدم 'user456'"},
        {"action": "رفض تقييم", "details": "رفض تقييم المستخدم 'user789'"},
        {"action": "تغيير إعدادات", "details": "تغيير إعدادات النظام: تفعيل المصادقة الثنائية"},
        {"action": "تسجيل خروج", "details": "تسجيل خروج المسؤول من النظام"},
    ]
    
    # إنشاء أنشطة بتواريخ مختلفة
    now = timezone.now()
    activities_count = 0
    
    for i, activity_type in enumerate(activity_types):
        # إنشاء نشاط في تاريخ مختلف (قبل عدة ساعات)
        created_at = now - timedelta(hours=i*2)
        
        activity = AdminActivity.objects.create(
            admin=admin,
            action=activity_type["action"],
            details=activity_type["details"],
            ip_address="127.0.0.1",
            created_at=created_at,
            is_hidden=False,
            affected_item_type="test_item" if i % 2 == 0 else None,
            affected_item_id=i+1000 if i % 2 == 0 else None
        )
        
        activities_count += 1
        print(f"تم إنشاء النشاط: {activity.action} (ID: {activity.id})")
    
    print(f"تم إنشاء {activities_count} نشاط اختباري بنجاح.")

if __name__ == "__main__":
    create_test_admin_activities()