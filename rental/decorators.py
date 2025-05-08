
"""
المزخرفات المستخدمة في التطبيق
"""

from django.shortcuts import redirect
from django.contrib import messages
from django.utils.translation import gettext as _
from functools import wraps
from .models_superadmin import AdminUser
from .admin_permissions_helpers import get_admin_permissions
import logging

# إعداد التسجيل
logger = logging.getLogger('django.request')

def superadmin_required(function):
    @wraps(function)
    def wrapper(request, *args, **kwargs):
        # التحقق من تسجيل الدخول
        if not request.user.is_authenticated:
            messages.error(request, _("يجب تسجيل الدخول للوصول إلى لوحة تحكم المسؤول الأعلى"))
            return redirect('superadmin_login')

        # التحقق من وجود بروفايل مسؤول أعلى صالح
        try:
            admin_profile = AdminUser.objects.get(user=request.user)
            if not admin_profile.is_superadmin:
                messages.error(request, _("ليس لديك صلاحيات المسؤول الأعلى"))
                return redirect('index')
                
            # إضافة معلومات المسؤول للطلب حتى تكون متاحة في القوالب
            request.admin_profile = admin_profile
            return function(request, *args, **kwargs)
        except AdminUser.DoesNotExist:
            messages.error(request, _("ليس لديك حساب مسؤول أعلى"))
            return redirect('index')
    
    return wrapper

def admin_required(view_func):
    """
    مزخرف للتحقق من أن المستخدم هو مسؤول
    """
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        # التحقق من أن المستخدم مسجل الدخول وهو مسؤول
        if not request.user.is_authenticated:
            messages.error(request, "يجب تسجيل الدخول أولاً")
            return redirect('login')

        if not request.user.is_staff and not request.user.is_superuser:
            messages.error(request, "ليس لديك صلاحية للوصول إلى هذه الصفحة")
            return redirect('index')

        return view_func(request, *args, **kwargs)
    return _wrapped_view

def permission_required(section, permission):
    """
    مزخرف للتحقق من أن المستخدم يملك صلاحية محددة

    المعلمات:
    - section: قسم الصلاحية (dashboard, reservations, customers, etc.)
    - permission: اسم الصلاحية (view_reservations, create_reservations, etc.)
    """
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            # طباعة معلومات التصحيح
            print(f"Admin check for {section}:{permission}, authenticated: {request.user.is_authenticated}")
            
            # المسؤول الأعلى لديه جميع الصلاحيات
            try:
                if request.user.is_authenticated:
                    admin_user = AdminUser.objects.get(user=request.user)
                    if admin_user.is_superadmin:
                        return view_func(request, *args, **kwargs)
                    
                    # الحصول على صلاحيات المسؤول
                    admin_permissions = get_admin_permissions(admin_user.id)
                    print(f"Admin ID: {admin_user.id}, Permissions: {admin_permissions}")
                    
                    # التحقق من الصلاحية
                    if section in admin_permissions and permission in admin_permissions[section]:
                        return view_func(request, *args, **kwargs)
                    
                    # إذا لم يكن لديه الصلاحية
                    messages.error(request, _("ليس لديك صلاحية للوصول إلى هذه الصفحة"))
                    # إعادة التوجيه إلى لوحة تحكم المسؤول
                    return redirect('admin_dashboard')
                    
            except AdminUser.DoesNotExist:
                pass
            except Exception as e:
                logger.error(f"خطأ في التحقق من الصلاحيات: {e}")
            
            # إذا لم يكن مسؤولاً أو ليس لديه صلاحية، نعيده إلى صفحة تسجيل الدخول
            messages.error(request, _("يجب تسجيل الدخول كمسؤول أو الحصول على الصلاحيات المناسبة"))
            return redirect('login')
            
        return _wrapped_view
    
    return decorator

def check_permission(request, section, permission):
    """
    التحقق من صلاحية محددة للمستخدم الحالي

    المعلمات:
    - request: طلب HTTP
    - section: قسم الصلاحية (dashboard, reservations, customers, etc.)
    - permission: اسم الصلاحية (view_reservations, create_reservations, etc.)

    تعيد:
    - True إذا كان المستخدم يملك الصلاحية
    - False إذا لم يكن المستخدم يملك الصلاحية
    """
    # المسؤول الأعلى لديه جميع الصلاحيات
    try:
        if request.user.is_authenticated:
            admin_user = AdminUser.objects.get(user=request.user)
            if admin_user.is_superadmin:
                return True
            
            # الحصول على صلاحيات المسؤول
            admin_permissions = get_admin_permissions(admin_user.id)
            
            # التحقق من الصلاحية
            return section in admin_permissions and permission in admin_permissions[section]
                
    except AdminUser.DoesNotExist:
        pass
    except Exception as e:
        logger.error(f"خطأ في التحقق من الصلاحيات: {e}")
    
    return False
