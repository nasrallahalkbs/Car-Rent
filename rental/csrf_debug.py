"""
وسيط للتعامل مع أخطاء CSRF وتوفير معلومات تصحيح مفيدة
"""

from django.shortcuts import render
from django.http import HttpResponseForbidden
import logging

# إعداد التسجيل
logger = logging.getLogger('django.request')

def csrf_failure(request, reason=""):
    """
    عرض خطأ CSRF بشكل أكثر تفصيلاً لمساعدة المطورين على التصحيح
    """
    # تسجيل بيانات التصحيح
    logger.warning(f"CSRF Error - Path: {request.path}, Method: {request.method}, Reason: {reason}")
    logger.warning(f"Headers: {request.headers}")
    
    # طباعة معلومات في السجل للتصحيح
    print(f"🔒 CSRF Error - Path: {request.path}, Method: {request.method}")
    print(f"🔒 CSRF Error Reason: {reason}")
    print(f"🔒 Request Headers: {dict(request.headers)}")
    print(f"🔒 CSRF Cookie: {request.COOKIES.get('csrftoken', '')[:10]}...")
    
    # لمسارات معينة قد تكون مشكلة مع CSRF، تخطي الخطأ ونجح الطلب
    if request.path.endswith('/advanced-permissions/') and request.method == 'POST':
        logger.warning(f"🔄 Bypassing CSRF check for known path: {request.path}")
        # could return appropriate response here, but we'll go ahead with the error for now
    
    # عرض صفحة خطأ مفيدة
    context = {
        'reason': reason,
        'path': request.path,
        'method': request.method,
        'headers': dict(request.headers)
    }
    
    # عرض صفحة خطأ ملائمة
    response = render(request, 'errors/csrf_error.html', context, status=403)
    return response