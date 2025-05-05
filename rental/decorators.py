"""
المزخرفات المستخدمة في التطبيق
"""

from django.shortcuts import redirect
from django.contrib import messages
from django.utils.translation import gettext as _
from functools import wraps
from .models_superadmin import AdminUser

def superadmin_required(function):
    @wraps(function)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.error(request, _("يجب تسجيل الدخول للوصول إلى لوحة تحكم المسؤول الأعلى"))
            return redirect('superadmin_login')

        try:
            admin_profile = AdminUser.objects.get(user=request.user)
            if not admin_profile.is_superadmin:
                messages.error(request, _("ليس لديك صلاحيات المسؤول الأعلى"))
                return redirect('index')
        except AdminUser.DoesNotExist:
            messages.error(request, _("ليس لديك حساب مسؤول أعلى"))
            return redirect('index')

        return function(request, *args, **kwargs)
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