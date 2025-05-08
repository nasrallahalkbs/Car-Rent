"""
وحدة مخصصة للتعامل مع رسائل المسؤولين وإخفائها عن المستخدمين العاديين

هذا الملف يحتوي على دوال مساعدة للتعامل مع رسائل النظام بحيث يتم عرضها فقط في لوحة التحكم
وليس في واجهة المستخدم العادية.
"""

from django.contrib import messages
from .models_superadmin import AdminUser
import logging

logger = logging.getLogger(__name__)

def is_admin_user(request):
    """
    التحقق مما إذا كان المستخدم مسؤولاً
    
    المعلمات:
    - request: كائن طلب HTTP
    
    العائد:
    - True إذا كان المستخدم مسؤولاً
    - False إذا لم يكن المستخدم مسؤولاً
    """
    # التحقق من أن المستخدم مسجل الدخول
    if not request.user.is_authenticated:
        return False
    
    # التحقق من خصائص النظام المباشرة
    if request.user.is_staff or request.user.is_superuser:
        return True
    
    # التحقق من خاصية is_admin إذا كانت موجودة
    if hasattr(request.user, 'is_admin') and request.user.is_admin:
        return True
    
    # التحقق من وجود سجل AdminUser مرتبط بالمستخدم
    try:
        admin_user = AdminUser.objects.get(user=request.user)
        return True
    except Exception:
        return False

def admin_error(request, message):
    """
    إضافة رسالة خطأ فقط إذا كان المستخدم مسؤولاً
    
    المعلمات:
    - request: كائن طلب HTTP
    - message: نص الرسالة
    """
    if is_admin_user(request):
        messages.error(request, message)
    else:
        # تسجيل الرسالة في السجل فقط للتصحيح دون إظهارها للمستخدم
        logger.warning(f"تم إخفاء رسالة الخطأ عن المستخدم العادي: {message}")

def admin_warning(request, message):
    """
    إضافة رسالة تحذير فقط إذا كان المستخدم مسؤولاً
    
    المعلمات:
    - request: كائن طلب HTTP
    - message: نص الرسالة
    """
    if is_admin_user(request):
        messages.warning(request, message)
    else:
        # تسجيل الرسالة في السجل فقط للتصحيح دون إظهارها للمستخدم
        logger.warning(f"تم إخفاء رسالة التحذير عن المستخدم العادي: {message}")

def admin_info(request, message):
    """
    إضافة رسالة معلومات فقط إذا كان المستخدم مسؤولاً
    
    المعلمات:
    - request: كائن طلب HTTP
    - message: نص الرسالة
    """
    if is_admin_user(request):
        messages.info(request, message)
    else:
        # تسجيل الرسالة في السجل فقط للتصحيح دون إظهارها للمستخدم
        logger.debug(f"تم إخفاء رسالة المعلومات عن المستخدم العادي: {message}")

def admin_success(request, message):
    """
    إضافة رسالة نجاح فقط إذا كان المستخدم مسؤولاً
    
    المعلمات:
    - request: كائن طلب HTTP
    - message: نص الرسالة
    """
    if is_admin_user(request):
        messages.success(request, message)
    else:
        # تسجيل الرسالة في السجل فقط للتصحيح دون إظهارها للمستخدم
        logger.debug(f"تم إخفاء رسالة النجاح عن المستخدم العادي: {message}")