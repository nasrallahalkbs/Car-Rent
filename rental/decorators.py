"""
المزخرفات المستخدمة في التطبيق
"""

from django.shortcuts import redirect
from django.contrib import messages
from functools import wraps


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