"""
تهيئة نظام الأمان والمصادقة الثنائية

هذا السكريبت يقوم بتهيئة جداول الأمان وإنشاء الإعدادات الافتراضية
"""
import os
import sys
import django

# إعداد بيئة Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'car_rental_project.settings')
django.setup()

from rental.security import init_security_tables
from rental.security_models import UserSecurity, LoginAttempt, TwoFactorSession
from django.contrib.auth import get_user_model
from django.db.utils import OperationalError

def initialize_security_system():
    """تهيئة نظام الأمان بالكامل"""
    print("⏳ جاري تهيئة نظام الأمان...")
    
    try:
        # تهيئة جداول الأمان
        init_security_tables()
        print("✅ تم تهيئة إعدادات الأمان الافتراضية")
        
        # التأكد من وجود سجل أمان لكل مستخدم
        User = get_user_model()
        users_without_security = 0
        
        for user in User.objects.all():
            security, created = UserSecurity.objects.get_or_create(user=user)
            if created:
                users_without_security += 1
        
        print(f"✅ تم إنشاء سجلات أمان لـ {users_without_security} مستخدم")
        
        # إحصائيات
        print("\n📊 إحصائيات النظام:")
        print(f"  - عدد المستخدمين: {User.objects.count()}")
        print(f"  - عدد سجلات الأمان: {UserSecurity.objects.count()}")
        print(f"  - عدد محاولات تسجيل الدخول: {LoginAttempt.objects.count()}")
        print(f"  - عدد جلسات المصادقة الثنائية: {TwoFactorSession.objects.count()}")
        
        return True
    
    except OperationalError as e:
        print(f"❌ خطأ في قاعدة البيانات: {str(e)}")
        print("❗ تأكد من تنفيذ الأمر python manage.py migrate قبل تشغيل هذا السكريبت")
        return False
    
    except Exception as e:
        print(f"❌ خطأ غير متوقع: {str(e)}")
        return False

if __name__ == "__main__":
    # تنفيذ السكريبت
    if initialize_security_system():
        print("\n✅ تم تهيئة نظام الأمان بنجاح!")
        sys.exit(0)
    else:
        print("\n❌ فشل تهيئة نظام الأمان")
        sys.exit(1)