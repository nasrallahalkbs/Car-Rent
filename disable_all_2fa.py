"""
تعطيل المصادقة الثنائية لجميع المستخدمين
"""
import os
import django

# إعداد بيئة Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'car_rental_project.settings')
django.setup()

from rental.models import User
from rental.security_models import UserSecurity

def disable_all_2fa():
    """تعطيل المصادقة الثنائية لجميع المستخدمين"""
    # تحديث سجلات UserSecurity بشكل فردي
    count = 0
    for security in UserSecurity.objects.filter(two_factor_enabled=True):
        security.two_factor_enabled = False
        security.totp_secret = ""  # استخدام سلسلة فارغة بدلاً من None
        if security.backup_codes is None:
            security.backup_codes = "[]"  # استخدام مصفوفة فارغة
        security.save()
        count += 1
    
    print(f"تم تعطيل المصادقة الثنائية لـ {count} مستخدم")
    
    # إظهار قائمة المستخدمين
    users = User.objects.all()
    print("\nقائمة المستخدمين:")
    for user in users:
        try:
            security = UserSecurity.objects.get(user=user)
            status = "✓" if security.two_factor_enabled else "✗"
        except UserSecurity.DoesNotExist:
            status = "✗"
        
        print(f"- {user.username}: المصادقة الثنائية {status}")

if __name__ == "__main__":
    disable_all_2fa()