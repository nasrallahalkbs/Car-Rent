
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
        # التحقق من أن المستخدم مسجل الدخول أولاً قبل فحص أي شيء آخر
        if not request.user.is_authenticated:
            # لا نضيف رسالة خطأ عند إعادة توجيه المستخدم لصفحة تسجيل الدخول
            return redirect('login')

        # للتسجيل فقط
        print(f"Admin check for admin, authenticated: {request.user.is_authenticated}")

        # الفحص إذا كان مسؤول
        is_admin = False
        try:
            # التحقق من نموذج AdminUser
            admin_user = AdminUser.objects.get(user=request.user)
            is_admin = True
        except AdminUser.DoesNotExist:
            # ليس مسؤولاً من نموذج AdminUser
            is_admin = False
        
        # التحقق من خصائص النظام إذا كانت متوفرة
        if hasattr(request.user, 'is_admin') and request.user.is_admin:
            is_admin = True
        
        # التحقق من معلمات Django العادية
        if request.user.is_staff or request.user.is_superuser:
            is_admin = True
        
        # السماح بالوصول إذا كان مسؤولاً
        if is_admin:
            return view_func(request, *args, **kwargs)
        
        # ليس مسؤولاً، نوجهه للصفحة الرئيسية بدون رسائل خطأ
        return redirect('index')

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
            # للتسجيل فقط: طباعة معلومات التصحيح
            print(f"Admin check for {section}:{permission}, authenticated: {request.user.is_authenticated}")
            
            # التحقق من أن المستخدم مسؤول أولاً
            if not request.user.is_authenticated:
                # إذا لم يكن مسجل الدخول، نوجهه لصفحة تسجيل الدخول بدون عرض رسائل خطأ
                return redirect('login')
            
            # تحقق إضافي للمسؤول الأعلى - له جميع الصلاحيات
            try:
                admin_user = AdminUser.objects.get(user=request.user)
                
                # المسؤول الأعلى لديه جميع الصلاحيات
                if admin_user.is_superadmin:
                    return view_func(request, *args, **kwargs)
                
                # تحقق من الصلاحية للمسؤول العادي
                admin_permissions = get_admin_permissions(admin_user.id)
                print(f"Admin ID: {admin_user.id}, Permissions: {admin_permissions}")
                
                # التحقق من الصلاحية (إذا كان لديه الصلاحية المطلوبة)
                if section in admin_permissions and permission in admin_permissions[section]:
                    print(f"Checking permissions for {section} {permission}")
                    return view_func(request, *args, **kwargs)
                
                # إذا وصلنا إلى هنا، فالمستخدم مسؤول ولكن ليس لديه الصلاحية
                if section == "reservations" and permission == "view_reservations":
                    messages.error(request, _("ليس لديك صلاحية لمشاهدة الحجوزات"))
                else:
                    messages.error(request, _("ليس لديك صلاحية للوصول إلى هذه الصفحة"))
                
                # نوجهه للوحة تحكم المسؤول
                return redirect('admin_index')
                
            except AdminUser.DoesNotExist:
                # رجع للصفحة الرئيسية بدون عرض رسالة خطأ - غير مسؤول
                return redirect('index')
            except Exception as e:
                # تسجيل الخطأ فقط دون عرضه للمستخدم
                logger.error(f"خطأ في التحقق من الصلاحيات: {e}")
                # إعادة توجيه آمن للصفحة الرئيسية
                return redirect('index')
            
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
    # إذا لم يكن مسجل الدخول، فليس لديه أي صلاحيات
    if not request.user.is_authenticated:
        return False
    
    # المسؤول الأعلى والمسؤول العادي
    try:
        # الحصول على معلومات المسؤول
        admin_user = AdminUser.objects.get(user=request.user)
        
        # المسؤول الأعلى لديه جميع الصلاحيات
        if admin_user.is_superadmin:
            return True
        
        # للمسؤول العادي، نتحقق من الصلاحيات المحددة
        admin_permissions = get_admin_permissions(admin_user.id)
        
        # للتصحيح
        if not admin_permissions:
            logger.warning(f"لم يتم العثور على صلاحيات للمسؤول {admin_user.id}")
            return False
            
        # التحقق من الصلاحية
        has_perm = section in admin_permissions and permission in admin_permissions[section]
        
        # للتصحيح
        if not has_perm:
            logger.debug(f"المسؤول {admin_user.id} ليس لديه صلاحية {section}:{permission}")
            
        return has_perm
        
    except AdminUser.DoesNotExist:
        # ليس مسؤولاً - ننتقل للفحوصات الإضافية أدناه
        pass
    except Exception as e:
        logger.error(f"خطأ في التحقق من صلاحيات المسؤول: {e}")
    
    # فحص إضافي لصلاحيات Django المدمجة (superuser و staff)
    if request.user.is_superuser:
        return True
        
    # إذا وصلنا إلى هنا، فالمستخدم لا يملك الصلاحية المطلوبة
    return False
