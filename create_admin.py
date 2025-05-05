#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
سكربت لإنشاء حساب مسؤول عادي (Admin) للنظام

هذا السكربت سيقوم بإنشاء:
1. مستخدم جديد للمسؤول العادي
2. ملف تعريف مسؤول بدون صلاحية المسؤول الأعلى
"""

import os
import sys
import django

# إعداد بيئة Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'car_rental_project.settings')
django.setup()

# استيراد النماذج
from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password
from rental.models_superadmin import Role, AdminUser

# شعار التطبيق
logo = """
╭─────────────────────────────────────────────────────╮
│                                                     │
│                Admin Creator                        │
│                                                     │
│            إنشاء حساب المسؤول العادي               │
│                                                     │
╰─────────────────────────────────────────────────────╯
"""

def create_admin_user():
    """إنشاء مستخدم المسؤول العادي"""
    print("\n[ إنشاء حساب المسؤول العادي ]")
    
    # معلومات المستخدم الافتراضية
    default_username = "admin"
    default_password = "Admin@123"
    default_email = "admin@regular.com"
    
    # استخدام القيم الافتراضية مباشرة
    username = default_username
    password = default_password
    email = default_email
    first_name = "المسؤول"
    last_name = "العادي"
    
    # الحصول على نموذج المستخدم
    User = get_user_model()
    
    # التحقق من وجود المستخدم
    user_exists = User.objects.filter(username=username).exists()
    
    if user_exists:
        user = User.objects.get(username=username)
        print(f"  ℹ️ المستخدم {username} موجود بالفعل، سيتم تحديث معلوماته")
        
        # تحديث معلومات المستخدم
        user.email = email
        if first_name:
            user.first_name = first_name
        if last_name:
            user.last_name = last_name
        user.is_active = True
        user.is_staff = True
        user.is_admin = True
        
        # تحديث كلمة المرور
        user.password = make_password(password)
        
        user.save()
        print(f"  ✓ تم تحديث معلومات المستخدم: {username}")
    else:
        # إنشاء مستخدم جديد
        user = User.objects.create(
            username=username,
            email=email,
            first_name=first_name,
            last_name=last_name,
            password=make_password(password),
            is_active=True,
            is_staff=True,
            is_admin=True
        )
        print(f"  ✓ تم إنشاء مستخدم جديد: {username}")
    
    # الحصول على دور العضو العادي أو إنشاء واحد جديد
    role, created = Role.objects.get_or_create(
        name="مسؤول عادي",
        defaults={
            'description': 'دور المسؤول العادي بصلاحيات محدودة',
            'is_active': True
        }
    )
    
    # إنشاء أو تحديث ملف تعريف المسؤول
    admin_profile, admin_created = AdminUser.objects.get_or_create(
        user=user,
        defaults={
            'role': role,
            'is_superadmin': False, # تعيين is_superadmin إلى False
            'notes': 'تم إنشاء هذا الحساب تلقائياً باستخدام سكربت إنشاء المسؤول العادي.'
        }
    )
    
    # إذا كان الملف موجوداً بالفعل، تأكد من تحديث الدور وتعطيل صلاحية المسؤول الأعلى
    if not admin_created:
        admin_profile.role = role
        admin_profile.is_superadmin = False
        admin_profile.save()
        print(f"  ✓ تم تحديث ملف تعريف المسؤول: {username}")
    else:
        print(f"  ✓ تم إنشاء ملف تعريف المسؤول: {username}")
    
    return user, admin_profile

def main():
    print(logo)
    
    try:
        # إنشاء حساب المسؤول العادي
        user, admin_profile = create_admin_user()
        
        print("\n✅ تم إنشاء حساب المسؤول العادي بنجاح! ✅")
        print(f"\nتفاصيل الحساب:")
        print(f"  - اسم المستخدم: {user.username}")
        print(f"  - البريد الإلكتروني: {user.email}")
        print(f"  - الاسم: {user.get_full_name() or 'غير محدد'}")
        print(f"  - مسؤول عادي: نعم")
        print(f"  - مسؤول أعلى: لا")
        print(f"  - الدور: {admin_profile.role.name}")
        
        print("\nيمكنك الآن تسجيل الدخول إلى لوحة تحكم المسؤول العادي باستخدام هذه المعلومات.")
        print("رابط تسجيل الدخول: /superadmin/login/")
        
    except Exception as e:
        print(f"\n❌ حدث خطأ أثناء إنشاء حساب المسؤول العادي: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()