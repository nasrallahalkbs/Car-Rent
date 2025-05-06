"""
وحدة وظائف الأمان للنظام

هذا الملف يحتوي على جميع وظائف الأمان المستخدمة في النظام بما في ذلك:
1. المصادقة الثنائية (2FA) باستخدام TOTP
2. تحقق كلمة المرور وفرض سياسات كلمة المرور
3. قفل الحساب ومراقبة محاولات تسجيل الدخول
4. وظائف مساعدة لإعدادات الأمان
"""

import os
import re
import base64
import string
import random
import pyotp
import logging
import datetime
from django.utils import timezone
from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import check_password
from django.db import models
from django.conf import settings
from io import BytesIO
from PIL import Image, ImageDraw
import qrcode

from .models_system import SystemSetting

# إعداد التسجيل
logger = logging.getLogger(__name__)

# ثوابت النظام
DEFAULT_PASSWORD_MIN_LENGTH = 8
MAX_LOGIN_ATTEMPTS = 5
LOCKOUT_DURATION_MINUTES = 30

# ============================================
# وظائف مساعدة لإعدادات النظام
# ============================================

def get_system_setting(key, default=None):
    """الحصول على قيمة إعداد النظام"""
    try:
        setting = SystemSetting.objects.get(key=key)
        
        # تحويل القيمة حسب نوعها
        if setting.value_type == 'integer':
            return int(setting.value or 0)
        elif setting.value_type == 'float':
            return float(setting.value or 0.0)
        elif setting.value_type == 'boolean':
            return setting.value.lower() in ('true', '1', 'yes', 'on')
        elif setting.value_type == 'json':
            import json
            return json.loads(setting.value or '{}')
        elif setting.value_type == 'list':
            import json
            return json.loads(setting.value or '[]')
        else:  # string
            return setting.value
    except (SystemSetting.DoesNotExist, ValueError):
        return default

def set_system_setting(key, value, value_type='string', group='general', description=None, is_public=False):
    """تعيين قيمة إعداد النظام"""
    import json
    
    # تحويل القيمة إلى نص حسب نوعها
    if value_type == 'json' or value_type == 'list':
        if isinstance(value, (dict, list)):
            string_value = json.dumps(value)
        else:
            string_value = value  # افترض أنه بالفعل سلسلة JSON
    elif value_type in ('integer', 'float', 'boolean'):
        string_value = str(value)
    else:  # string
        string_value = value
    
    # إنشاء أو تحديث الإعداد
    setting, created = SystemSetting.objects.update_or_create(
        key=key,
        defaults={
            'value': string_value,
            'value_type': value_type,
            'group': group,
            'description': description,
            'is_public': is_public
        }
    )
    
    return setting

# ============================================
# استيراد نماذج المصادقة الثنائية والأمان
# ============================================

from .security_models import LoginAttempt, UserSecurity, TwoFactorSession

# ============================================
# وظائف مساعدة
# ============================================

def reset_failed_login_attempts(user):
    """إعادة تعيين محاولات تسجيل الدخول الفاشلة للمستخدم"""
    try:
        security = UserSecurity.objects.get(user=user)
        security.reset_failed_login_attempts()
        return True
    except UserSecurity.DoesNotExist:
        return False
        
def generate_backup_codes(user, force_regenerate=False):
    """توليد رموز احتياطية جديدة للمستخدم"""
    try:
        security = UserSecurity.objects.get(user=user)
        codes = security.generate_backup_codes(force_regenerate=force_regenerate)
        return codes
    except UserSecurity.DoesNotExist:
        security = UserSecurity.objects.create(user=user)
        codes = security.generate_backup_codes()
        return codes
        
def unlock_account(user):
    """فتح قفل حساب المستخدم"""
    try:
        security = UserSecurity.objects.get(user=user)
        security.reset_failed_login_attempts()
        return True
    except UserSecurity.DoesNotExist:
        return False

# ============================================
# وظائف المصادقة الثنائية
# ============================================

def setup_2fa_for_user(user):
    """إعداد المصادقة الثنائية لمستخدم"""
    # التحقق من وجود معلومات الأمان
    security, created = UserSecurity.objects.get_or_create(user=user)
    
    # توليد سر TOTP جديد إذا لم يكن موجوداً
    if not security.totp_secret:
        security.totp_secret = pyotp.random_base32()
        security.save(update_fields=['totp_secret'])
    
    # توليد رموز احتياطية إذا لم تكن موجودة
    if not security.backup_codes:
        security.generate_backup_codes()
    
    return security

def verify_2fa_token(user, token):
    """التحقق من صحة رمز المصادقة الثنائية"""
    try:
        security = UserSecurity.objects.get(user=user)
    except UserSecurity.DoesNotExist:
        return False
    
    # التحقق من تفعيل المصادقة الثنائية
    if not security.two_factor_enabled or not security.totp_secret:
        return False
    
    # التحقق من رمز TOTP
    totp = pyotp.TOTP(security.totp_secret)
    is_valid = totp.verify(token)
    
    # إذا لم يكن صالحاً، تحقق من الرموز الاحتياطية
    if not is_valid:
        is_valid = security.is_valid_backup_code(token)
    
    return is_valid

def generate_qr_code_image(user):
    """توليد صورة QR للمصادقة الثنائية"""
    try:
        security = UserSecurity.objects.get(user=user)
    except UserSecurity.DoesNotExist:
        return None
    
    if not security.totp_secret:
        return None
    
    # الحصول على URI TOTP
    uri = security.get_totp_uri()
    
    # إنشاء رمز QR
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(uri)
    qr.make(fit=True)
    
    # تحويل رمز QR إلى صورة
    img = qr.make_image(fill_color="black", back_color="white")
    
    # حفظ الصورة في ذاكرة مؤقتة
    buffer = BytesIO()
    img.save(buffer, format="PNG")
    
    # تحويل الصورة إلى سلسلة Base64
    image_data = buffer.getvalue()
    image_base64 = base64.b64encode(image_data).decode('utf-8')
    
    return f"data:image/png;base64,{image_base64}"

def enable_2fa_for_user(user, token):
    """تفعيل المصادقة الثنائية لمستخدم بعد التحقق من الرمز"""
    try:
        security = UserSecurity.objects.get(user=user)
    except UserSecurity.DoesNotExist:
        security = setup_2fa_for_user(user)
    
    # التحقق من رمز TOTP
    totp = pyotp.TOTP(security.totp_secret)
    is_valid = totp.verify(token)
    
    if is_valid:
        # تفعيل المصادقة الثنائية
        security.two_factor_enabled = True
        security.save(update_fields=['two_factor_enabled'])
        
        # تسجيل العملية
        logger.info(f"تم تفعيل المصادقة الثنائية للمستخدم {user.username}")
        
        return True
    
    return False

def disable_2fa_for_user(user, token=None, force=False):
    """تعطيل المصادقة الثنائية لمستخدم"""
    try:
        security = UserSecurity.objects.get(user=user)
    except UserSecurity.DoesNotExist:
        return False
    
    # إذا تم تمرير قوة التعطيل، تعطيل المصادقة الثنائية بدون تحقق
    if force:
        security.two_factor_enabled = False
        security.save(update_fields=['two_factor_enabled'])
        
        # تسجيل العملية
        logger.info(f"تم تعطيل المصادقة الثنائية بالقوة للمستخدم {user.username}")
        
        return True
    
    # التحقق من رمز TOTP إذا تم تمريره
    if token:
        is_valid = verify_2fa_token(user, token)
        
        if is_valid:
            security.two_factor_enabled = False
            security.save(update_fields=['two_factor_enabled'])
            
            # تسجيل العملية
            logger.info(f"تم تعطيل المصادقة الثنائية للمستخدم {user.username}")
            
            return True
    
    return False

# ============================================
# وظائف سياسات كلمة المرور
# ============================================

def validate_password_strength(password, user=None):
    """التحقق من قوة كلمة المرور وفقاً لسياسات النظام
    
    إرجاع:
        (bool, str): قوة كلمة المرور (صالحة أم لا) ورسالة الخطأ إن وجدت
    """
    errors = []
    
    # التحقق من الحد الأدنى للطول
    min_length = get_system_setting('password_min_length', DEFAULT_PASSWORD_MIN_LENGTH)
    if len(password) < min_length:
        errors.append(f"يجب أن تكون كلمة المرور {min_length} أحرف على الأقل")
    
    # التحقق من وجود أحرف كبيرة
    requires_uppercase = get_system_setting('password_requires_uppercase', False)
    if requires_uppercase and not any(c.isupper() for c in password):
        errors.append("يجب أن تحتوي كلمة المرور على حرف كبير واحد على الأقل")
    
    # التحقق من وجود أرقام
    requires_numbers = get_system_setting('password_requires_numbers', False)
    if requires_numbers and not any(c.isdigit() for c in password):
        errors.append("يجب أن تحتوي كلمة المرور على رقم واحد على الأقل")
    
    # التحقق من وجود رموز خاصة
    requires_special = get_system_setting('password_requires_special', False)
    special_chars = set('!@#$%^&*()_-+={}[]|:;<>,.?/~`')
    if requires_special and not any(c in special_chars for c in password):
        errors.append("يجب أن تحتوي كلمة المرور على رمز خاص واحد على الأقل")
    
    # التحقق من عدم استخدام كلمة مرور سابقة
    if user:
        try:
            security = UserSecurity.objects.get(user=user)
            
            # التحقق من كلمات المرور السابقة
            for old_password in security.previous_passwords:
                if check_password(password, old_password):
                    errors.append("لا يمكنك استخدام كلمة مرور سبق استخدامها")
                    break
        except UserSecurity.DoesNotExist:
            pass
    
    return (len(errors) == 0, errors)

def record_password_change(user, new_password_hash):
    """تسجيل تغيير كلمة المرور في سجل الأمان"""
    try:
        security = UserSecurity.objects.get(user=user)
    except UserSecurity.DoesNotExist:
        security = UserSecurity.objects.create(user=user)
    
    # الاحتفاظ بعدد محدد من كلمات المرور السابقة
    max_old_passwords = get_system_setting('max_old_passwords', 5)
    
    # إضافة كلمة المرور الحالية إلى القائمة
    previous_passwords = security.previous_passwords
    if previous_passwords and len(previous_passwords) >= max_old_passwords:
        # إزالة أقدم كلمة مرور
        previous_passwords = previous_passwords[-(max_old_passwords-1):]
    
    # إضافة كلمة المرور الجديدة إلى القائمة
    previous_passwords.append(user.password)
    
    # تحديث معلومات الأمان
    security.previous_passwords = previous_passwords
    security.password_changed_at = timezone.now()
    security.save(update_fields=['previous_passwords', 'password_changed_at'])
    
    # تسجيل العملية
    logger.info(f"تم تغيير كلمة المرور للمستخدم {user.username}")
    
    return True

def check_password_expiry(user):
    """التحقق من انتهاء صلاحية كلمة المرور وفقاً لسياسات النظام
    
    إرجاع:
        (bool, int): ما إذا كانت كلمة المرور منتهية الصلاحية وعدد الأيام المتبقية
    """
    try:
        security = UserSecurity.objects.get(user=user)
    except UserSecurity.DoesNotExist:
        # إذا لم تكن هناك معلومات أمان، يتم إنشاؤها ولا تعتبر منتهية الصلاحية
        security = UserSecurity.objects.create(user=user)
        return (False, None)
    
    # الحصول على فترة صلاحية كلمة المرور من إعدادات النظام
    password_expiry_days = get_system_setting('password_expiry_days', 0)
    
    # إذا كانت فترة الصلاحية 0، فلا تنتهي صلاحية كلمة المرور
    if password_expiry_days <= 0:
        return (False, None)
    
    # حساب الفرق بين الوقت الحالي وتاريخ آخر تغيير لكلمة المرور
    days_since_change = (timezone.now() - security.password_changed_at).days
    days_remaining = password_expiry_days - days_since_change
    
    # التحقق من انتهاء الصلاحية
    if days_since_change >= password_expiry_days:
        return (True, -days_remaining)  # منتهية الصلاحية، عدد الأيام المتبقية سالب
    
    return (False, days_remaining)  # غير منتهية الصلاحية، عدد الأيام المتبقية موجب

# ============================================
# وظائف قفل الحساب والمراقبة
# ============================================

def get_client_ip(request):
    """الحصول على عنوان IP للعميل من الطلب"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip

def record_login_attempt(request, username, status, notes=None):
    """تسجيل محاولة تسجيل دخول"""
    User = get_user_model()
    
    try:
        user = User.objects.get(username=username)
    except User.DoesNotExist:
        user = None
    
    # إنشاء سجل محاولة تسجيل الدخول
    LoginAttempt.objects.create(
        user=user,
        username=username,
        ip_address=get_client_ip(request),
        user_agent=request.META.get('HTTP_USER_AGENT', ''),
        status=status,
        notes=notes
    )
    
    # تحديث معلومات الأمان للمستخدم إذا كان موجوداً
    if user:
        try:
            security = UserSecurity.objects.get(user=user)
        except UserSecurity.DoesNotExist:
            security = UserSecurity.objects.create(user=user)
        
        if status == 'success':
            # تحديث معلومات آخر تسجيل دخول ناجح
            security.reset_failed_login_attempts()
            security.last_login_ip = get_client_ip(request)
            security.last_active = timezone.now()
            security.save(update_fields=['last_login_ip', 'last_active'])
        elif status == 'failed':
            # تسجيل محاولة فاشلة
            security.record_failed_login(request)
    
    return True

def check_account_lockout(username):
    """التحقق من حالة قفل الحساب
    
    إرجاع:
        (bool, datetime): ما إذا كان الحساب مقفلاً ووقت انتهاء القفل
    """
    User = get_user_model()
    
    try:
        user = User.objects.get(username=username)
    except User.DoesNotExist:
        return (False, None)
    
    try:
        security = UserSecurity.objects.get(user=user)
    except UserSecurity.DoesNotExist:
        return (False, None)
    
    # التحقق من حالة قفل الحساب
    if security.is_account_locked():
        return (True, security.locked_until)
    
    return (False, None)

def unlock_account(username):
    """فتح قفل الحساب لمستخدم معين"""
    User = get_user_model()
    
    try:
        user = User.objects.get(username=username)
    except User.DoesNotExist:
        return False
    
    try:
        security = UserSecurity.objects.get(user=user)
    except UserSecurity.DoesNotExist:
        return False
    
    # إعادة تعيين معلومات قفل الحساب
    security.reset_failed_login_attempts()
    
    # تسجيل العملية
    logger.info(f"تم فتح قفل حساب المستخدم {username}")
    
    return True

# ============================================
# وظائف متنوعة
# ============================================

def init_security_tables():
    """تهيئة جداول قاعدة بيانات الأمان وإعدادات النظام الافتراضية"""
    # إعدادات كلمة المرور
    set_system_setting('password_min_length', DEFAULT_PASSWORD_MIN_LENGTH, 'integer', 'security', 'الحد الأدنى لطول كلمة المرور')
    set_system_setting('password_requires_uppercase', False, 'boolean', 'security', 'كلمة المرور تتطلب أحرف كبيرة')
    set_system_setting('password_requires_numbers', False, 'boolean', 'security', 'كلمة المرور تتطلب أرقام')
    set_system_setting('password_requires_special', False, 'boolean', 'security', 'كلمة المرور تتطلب رموز خاصة')
    set_system_setting('password_expiry_days', 0, 'integer', 'security', 'فترة صلاحية كلمة المرور بالأيام (0 = لا تنتهي)')
    set_system_setting('max_old_passwords', 5, 'integer', 'security', 'عدد كلمات المرور السابقة المحتفظ بها')
    
    # إعدادات قفل الحساب
    set_system_setting('account_lockout_attempts', MAX_LOGIN_ATTEMPTS, 'integer', 'security', 'عدد محاولات تسجيل الدخول الفاشلة قبل قفل الحساب')
    set_system_setting('account_lockout_minutes', LOCKOUT_DURATION_MINUTES, 'integer', 'security', 'مدة قفل الحساب بالدقائق')
    
    # إعدادات الجلسة
    set_system_setting('session_timeout_minutes', 60, 'integer', 'security', 'مدة انتهاء جلسة العمل بالدقائق')
    
    # إعدادات المصادقة الثنائية
    set_system_setting('two_factor_enabled', False, 'boolean', 'security', 'تفعيل المصادقة الثنائية')
    set_system_setting('two_factor_required_for_admins', False, 'boolean', 'security', 'المصادقة الثنائية مطلوبة للمسؤولين')
    
    # تسجيل العملية
    logger.info("تم تهيئة إعدادات الأمان الافتراضية")
    
    return True

def get_security_statistics():
    """الحصول على إحصائيات أمان النظام"""
    stats = {
        'login_attempts': {
            'today': LoginAttempt.objects.filter(timestamp__gte=timezone.now().replace(hour=0, minute=0, second=0, microsecond=0)).count(),
            'success': LoginAttempt.objects.filter(status='success').count(),
            'failed': LoginAttempt.objects.filter(status='failed').count(),
            'locked': LoginAttempt.objects.filter(status='locked').count(),
        },
        'accounts': {
            'total': get_user_model().objects.count(),
            'active': get_user_model().objects.filter(is_active=True).count(),
            'with_2fa': UserSecurity.objects.filter(two_factor_enabled=True).count(),
            'locked': UserSecurity.objects.filter(locked_until__gt=timezone.now()).count(),
        }
    }
    
    return stats