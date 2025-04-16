"""
وحدة debug مخصصة لإصلاح مشكلة CSRF في بيئة Replit
"""

import os
import socket
from django.http import HttpRequest, JsonResponse, HttpResponse
from django.middleware.csrf import get_token
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings

@csrf_exempt
def csrf_debug_view(request):
    """
    عرض معلومات تصحيح الأخطاء المتعلقة بـ CSRF
    """
    from django.http import JsonResponse
    
    # طلب إنشاء رمز CSRF وإرجاعه
    csrf_token = get_token(request)
    
    # التحقق من وجود رمز CSRF في الطلب
    csrf_cookie = request.COOKIES.get('csrftoken', None)
    csrf_header = request.META.get('HTTP_X_CSRFTOKEN', None)
    csrf_post = request.POST.get('csrfmiddlewaretoken', None)
    
    # إرجاع البيانات كاستجابة JSON
    return JsonResponse({
        'csrf_token': csrf_token,
        'csrf_cookie_exists': csrf_cookie is not None,
        'csrf_header_exists': csrf_header is not None,
        'csrf_post_exists': csrf_post is not None,
        'csrf_cookie': csrf_cookie if csrf_cookie else 'Not found',
        'all_cookies': list(request.COOKIES.keys()),
        'session_key': request.session.session_key if hasattr(request, 'session') and hasattr(request.session, 'session_key') else None,
    })