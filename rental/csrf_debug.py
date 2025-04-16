"""
وحدة debug مخصصة لإصلاح مشكلة CSRF في بيئة Replit
"""

import os
import re
import socket
from django.http import HttpRequest, JsonResponse, HttpResponse
from django.middleware.csrf import get_token
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from django.shortcuts import render
from django.utils.translation import gettext_lazy as _

def add_current_host_to_trusted_origins():
    """
    إضافة المضيف الحالي إلى قائمة النطاقات الموثوقة CSRF_TRUSTED_ORIGINS
    """
    # الحصول على معلومات Replit من متغيرات البيئة
    replit_id = os.environ.get('REPL_ID', '')
    replit_slug = os.environ.get('REPL_SLUG', '')
    replit_owner = os.environ.get('REPL_OWNER', '')
    
    # قائمة بالنطاقات المحتملة التي تستند إلى معرف REPL
    possible_domains = []
    
    if replit_id:
        # نطاقات تعتمد على معرف REPL
        wildcard_domains = [
            f'https://{replit_id}-*.*.replit.dev',
            f'https://{replit_id}-*.*.replit.dev:*',
        ]
        
        # إضافة أنماط أكثر تحديدًا
        specific_domains = [
            f'https://{replit_id}-00-26n4b48jep28q.sisko.replit.dev',
            f'https://{replit_id}-00-26n4b48jep28q.sisko.replit.dev:8000',
        ]
        
        possible_domains.extend(wildcard_domains)
        possible_domains.extend(specific_domains)
    
    # إضافة النطاقات المحتملة إلى قائمة النطاقات الموثوقة
    for domain in possible_domains:
        if domain not in settings.CSRF_TRUSTED_ORIGINS:
            settings.CSRF_TRUSTED_ORIGINS.append(domain)
    
    # إضافة نطاق عام للتغطية الشاملة
    if replit_id:
        general_pattern = f'https://{replit_id}-*'
        if general_pattern not in settings.CSRF_TRUSTED_ORIGINS:
            settings.CSRF_TRUSTED_ORIGINS.append(general_pattern)
    
    return settings.CSRF_TRUSTED_ORIGINS

def csrf_failure(request, reason=""):
    """
    دالة تعامل مخصصة مع أخطاء CSRF
    تعرض صفحة خطأ ودية مع معلومات وروابط مفيدة للتصحيح
    """
    # تحديث النطاقات الموثوقة ديناميكيًا
    add_current_host_to_trusted_origins()
    
    # الحصول على معلومات المضيف والطلب
    hostname = socket.gethostname()
    replit_id = os.environ.get('REPL_ID', 'غير متاح')
    origin = request.headers.get('Origin', 'غير متاح')
    referer = request.headers.get('Referer', 'غير متاح')
    
    # محاولة العثور على معلومات إضافية للسبب
    error_context = {
        'reason': reason,
        'hostname': hostname,
        'replit_id': replit_id,
        'origin': origin,
        'referer': referer,
        'csrf_token': get_token(request),
        'csrf_cookie': request.COOKIES.get('csrftoken', 'غير موجود'),
        'csrf_trusted_origins': settings.CSRF_TRUSTED_ORIGINS,
    }
    
    # تصحيح المشكلة تلقائيًا إذا لم يكن ضمن النطاقات الموثوقة
    if origin != 'غير متاح':
        origin_found = False
        for trusted_origin in settings.CSRF_TRUSTED_ORIGINS:
            # تحويل أنماط النطاقات مع العلامة النجمية إلى تعبيرات منتظمة للمطابقة
            if '*' in trusted_origin:
                pattern = trusted_origin.replace('.', '\\.').replace('*', '.*')
                regex = re.compile(pattern)
                if regex.match(origin):
                    origin_found = True
                    break
            elif trusted_origin == origin:
                origin_found = True
                break
        
        # إضافة النطاق إلى القائمة إذا لم يكن موجودًا
        if not origin_found:
            settings.CSRF_TRUSTED_ORIGINS.append(origin)
            error_context['auto_fixed'] = True
    
    return render(request, '403_csrf.html', error_context)

def csrf_debug_page(request):
    """
    عرض صفحة HTML لتصحيح أخطاء CSRF
    """
    return render(request, 'csrf_debug.html')

@csrf_exempt
def csrf_debug_view(request):
    """
    عرض معلومات تصحيح الأخطاء المتعلقة بـ CSRF
    """
    # تحديث النطاقات الموثوقة
    trusted_origins = add_current_host_to_trusted_origins()
    
    # طلب إنشاء رمز CSRF وإرجاعه
    csrf_token = get_token(request)
    
    # الحصول على معلومات المضيف والطلب
    hostname = socket.gethostname()
    replit_id = os.environ.get('REPL_ID', 'Not available')
    replit_slug = os.environ.get('REPL_SLUG', 'Not available')
    replit_owner = os.environ.get('REPL_OWNER', 'Not available')
    origin = request.headers.get('Origin', 'Not available')
    referer = request.headers.get('Referer', 'Not available')
    user_agent = request.headers.get('User-Agent', 'Not available')
    
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
        'hostname': hostname,
        'replit_info': {
            'replit_id': replit_id,
            'replit_slug': replit_slug,
            'replit_owner': replit_owner,
        },
        'request_info': {
            'origin': origin,
            'referer': referer,
            'user_agent': user_agent,
            'method': request.method,
            'is_secure': request.is_secure(),
            'is_ajax': request.headers.get('X-Requested-With') == 'XMLHttpRequest',
        },
        'csrf_settings': {
            'csrf_cookie_name': settings.CSRF_COOKIE_NAME,
            'csrf_use_sessions': settings.CSRF_USE_SESSIONS,
            'csrf_cookie_secure': settings.CSRF_COOKIE_SECURE,
            'csrf_cookie_httponly': settings.CSRF_COOKIE_HTTPONLY,
            'csrf_cookie_samesite': settings.CSRF_COOKIE_SAMESITE,
        },
        'csrf_trusted_origins': trusted_origins,
    })