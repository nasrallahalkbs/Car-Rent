#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
سكربت لإنشاء حساب مسؤول أعلى (Super Admin) للنظام

هذا السكربت سيقوم بإنشاء:
1. مستخدم جديد
2. ملف تعريف مسؤول مع صلاحية المسؤول الأعلى
3. دور جديد مع جميع الصلاحيات
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
from rental.models_superadmin import Permission, Role, AdminUser

# شعار التطبيق
logo = """
╭─────────────────────────────────────────────────────╮
│                                                     │
│               Super Admin Creator                   │
│                                                     │
│            إنشاء حساب المسؤول الأعلى               │
│                                                     │
╰─────────────────────────────────────────────────────╯
"""

def create_default_permissions():
    """إنشاء الصلاحيات الافتراضية"""
    print("\n[ إنشاء الصلاحيات الافتراضية ]")
    
    permissions = [
        {
            'name': 'إدارة المستخدمين',
            'codename': 'manage_users',
            'description': 'القدرة على إدارة المستخدمين (إضافة، تعديل، حذف)'
        },
        {
            'name': 'إدارة المسؤولين',
            'codename': 'manage_admins',
            'description': 'القدرة على إدارة المسؤولين وصلاحياتهم'
        },
        {
            'name': 'إدارة الأدوار',
            'codename': 'manage_roles',
            'description': 'القدرة على إدارة الأدوار وتخصيص الصلاحيات'
        },
        {
            'name': 'إدارة التقييمات',
            'codename': 'manage_reviews',
            'description': 'القدرة على إدارة تقييمات المستخدمين للسيارات'
        },
        {
            'name': 'عرض السجلات',
            'codename': 'view_logs',
            'description': 'القدرة على الوصول لسجلات النظام وعرضها'
        },
        {
            'name': 'الوصول للإعدادات',
            'codename': 'access_settings',
            'description': 'القدرة على الوصول لإعدادات النظام وتعديلها'
        }
    ]
    
    created_permissions = []
    for perm_data in permissions:
        perm, created = Permission.objects.get_or_create(
            codename=perm_data['codename'],
            defaults={
                'name': perm_data['name'],
                'description': perm_data['description']
            }
        )
        created_permissions.append(perm)
        if created:
            print(f"  ✓ تم إنشاء صلاحية: {perm.name}")
        else:
            print(f"  ✓ الصلاحية موجودة بالفعل: {perm.name}")
    
    return created_permissions

def create_superadmin_role(permissions):
    """إنشاء دور المسؤول الأعلى مع كل الصلاحيات"""
    print("\n[ إنشاء دور المسؤول الأعلى ]")
    
    role, created = Role.objects.get_or_create(
        name="المسؤول الأعلى",
        defaults={
            'description': 'دور المسؤول الأعلى مع كامل الصلاحيات',
            'is_active': True
        }
    )
    
    # إضافة جميع الصلاحيات للدور
    role.permissions.set(permissions)
    role.save()
    
    if created:
        print(f"  ✓ تم إنشاء دور: {role.name}")
    else:
        print(f"  ✓ تم تحديث دور: {role.name}")
    
    print(f"  ✓ تم تعيين {len(permissions)} صلاحية للدور")
    
    return role

def create_superadmin_user(role):
    """إنشاء مستخدم المسؤول الأعلى"""
    print("\n[ إنشاء حساب المسؤول الأعلى ]")
    
    # معلومات المستخدم الافتراضية
    default_username = "superadmin"
    default_password = "Admin@12345"
    default_email = "admin@admin.com"
    
    # استخدام القيم الافتراضية مباشرة بدلاً من طلب المدخلات
    username = default_username
    password = default_password
    email = default_email
    first_name = "المسؤول"
    last_name = "الأعلى"
    
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
        
        # تحديث كلمة المرور دائماً
        if True:
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
    
    # إنشاء أو تحديث ملف تعريف المسؤول
    admin_profile, created = AdminUser.objects.get_or_create(
        user=user,
        defaults={
            'role': role,
            'is_superadmin': True,
            'notes': 'تم إنشاء هذا الحساب تلقائياً باستخدام سكربت إنشاء المسؤول الأعلى.'
        }
    )
    
    # إذا كان الملف موجوداً بالفعل، تأكد من تحديث الدور وتفعيل صلاحية المسؤول الأعلى
    if not created:
        admin_profile.role = role
        admin_profile.is_superadmin = True
        admin_profile.save()
        print(f"  ✓ تم تحديث ملف تعريف المسؤول: {username}")
    else:
        print(f"  ✓ تم إنشاء ملف تعريف المسؤول: {username}")
    
    return user, admin_profile

def main():
    print(logo)
    
    try:
        # إنشاء الصلاحيات الافتراضية
        permissions = create_default_permissions()
        
        # إنشاء دور المسؤول الأعلى
        role = create_superadmin_role(permissions)
        
        # إنشاء حساب المسؤول الأعلى
        user, admin_profile = create_superadmin_user(role)
        
        print("\n✅ تم إنشاء حساب المسؤول الأعلى بنجاح! ✅")
        print(f"\nتفاصيل الحساب:")
        print(f"  - اسم المستخدم: {user.username}")
        print(f"  - البريد الإلكتروني: {user.email}")
        print(f"  - الاسم: {user.get_full_name() or 'غير محدد'}")
        print(f"  - مسؤول أعلى: نعم")
        print(f"  - الدور: {admin_profile.role.name}")
        print(f"  - عدد الصلاحيات: {admin_profile.role.permissions.count()}")
        
        print("\nيمكنك الآن تسجيل الدخول إلى لوحة تحكم المسؤول الأعلى باستخدام هذه المعلومات.")
        print("رابط تسجيل الدخول: /superadmin/login/")
        
    except Exception as e:
        print(f"\n❌ حدث خطأ أثناء إنشاء حساب المسؤول الأعلى: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
