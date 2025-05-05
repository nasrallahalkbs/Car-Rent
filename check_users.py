#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
التحقق من المستخدمين وأنواعهم في النظام
"""

import os
import django

# إعداد بيئة Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'car_rental_project.settings')
django.setup()

# استيراد النماذج
from django.contrib.auth import get_user_model
from rental.models_superadmin import AdminUser

# الحصول على نموذج المستخدم
User = get_user_model()

print("\n[ قائمة المستخدمين في النظام ]\n")

# الحصول على جميع المستخدمين
users = User.objects.all()

for user in users:
    is_admin = getattr(user, 'is_admin', False)
    is_staff = user.is_staff
    
    try:
        admin_profile = user.admin_profile
        is_superadmin = admin_profile.is_superadmin
        role_name = admin_profile.role.name if admin_profile.role else "بدون دور"
    except (AdminUser.DoesNotExist, AttributeError):
        is_superadmin = False
        role_name = "لا يوجد"
    
    print(f"اسم المستخدم: {user.username}")
    print(f"البريد الإلكتروني: {user.email}")
    print(f"الاسم: {user.get_full_name() or 'غير محدد'}")
    print(f"حالة النشاط: {'نشط' if user.is_active else 'غير نشط'}")
    print(f"مسؤول عادي: {'نعم' if is_admin else 'لا'}")
    print(f"طاقم عمل: {'نعم' if is_staff else 'لا'}")
    print(f"مسؤول أعلى: {'نعم' if is_superadmin else 'لا'}")
    print(f"الدور: {role_name}")
    print("-" * 50)