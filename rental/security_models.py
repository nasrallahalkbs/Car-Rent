"""
نماذج نظام الأمان والمصادقة الثنائية

هذا الملف يحتوي على نماذج قاعدة البيانات الخاصة بالأمان والمصادقة الثنائية
"""

from django.db import models
from django.utils import timezone
from django.conf import settings


class LoginAttempt(models.Model):
    """نموذج لتسجيل محاولات تسجيل الدخول"""
    
    STATUS_CHOICES = [
        ('success', 'نجاح'),
        ('failed', 'فشل'),
        ('locked', 'الحساب مقفل'),
    ]
    
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True, related_name='login_attempts')
    username = models.CharField(max_length=150)  # لتسجيل محاولات تسجيل الدخول حتى لو كان المستخدم غير موجود
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.CharField(max_length=512, blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES)
    timestamp = models.DateTimeField(auto_now_add=True)
    notes = models.CharField(max_length=255, blank=True, null=True)
    
    def __str__(self):
        return f"{self.username} - {self.status} - {self.timestamp}"
    
    class Meta:
        ordering = ['-timestamp']
        verbose_name = 'محاولة تسجيل دخول'
        verbose_name_plural = 'محاولات تسجيل الدخول'


class UserSecurity(models.Model):
    """نموذج معلومات أمان المستخدم"""
    
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='security')
    
    # المصادقة الثنائية
    two_factor_enabled = models.BooleanField(default=False)
    totp_secret = models.CharField(max_length=255, blank=True, null=True)
    backup_codes = models.JSONField(default=list, blank=True)
    
    # قفل الحساب
    failed_login_attempts = models.IntegerField(default=0)
    last_failed_login = models.DateTimeField(null=True, blank=True)
    locked_until = models.DateTimeField(null=True, blank=True)
    
    # تاريخ تغيير كلمة المرور
    password_changed_at = models.DateTimeField(auto_now_add=True)
    password_last_used = models.DateTimeField(null=True, blank=True)
    previous_passwords = models.JSONField(default=list, blank=True)  # يحتفظ بـ N من كلمات المرور السابقة
    
    # معلومات إضافية
    last_login_ip = models.GenericIPAddressField(null=True, blank=True)
    last_active = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Security for {self.user.username}"
    
    def is_account_locked(self):
        """التحقق مما إذا كان الحساب مقفلاً"""
        if not self.locked_until:
            return False
        return timezone.now() < self.locked_until
        
    def reset_failed_login_attempts(self):
        """إعادة تعيين محاولات تسجيل الدخول الفاشلة"""
        self.failed_login_attempts = 0
        self.last_failed_login = None
        self.locked_until = None
        self.save(update_fields=['failed_login_attempts', 'last_failed_login', 'locked_until'])
    
    def record_failed_login(self, request=None):
        """تسجيل محاولة تسجيل دخول فاشلة"""
        from .security import get_system_setting, get_client_ip, MAX_LOGIN_ATTEMPTS, LOCKOUT_DURATION_MINUTES
        
        # زيادة عدد محاولات تسجيل الدخول الفاشلة
        self.failed_login_attempts += 1
        self.last_failed_login = timezone.now()
        
        # التحقق مما إذا كان يجب قفل الحساب
        lockout_attempts = get_system_setting('account_lockout_attempts', MAX_LOGIN_ATTEMPTS)
        
        if self.failed_login_attempts >= lockout_attempts:
            # قفل الحساب
            lockout_minutes = get_system_setting('account_lockout_minutes', LOCKOUT_DURATION_MINUTES)
            self.locked_until = timezone.now() + timezone.timedelta(minutes=lockout_minutes)
            self.save(update_fields=['failed_login_attempts', 'last_failed_login', 'locked_until'])
            
            # تسجيل محاولة الدخول
            if request:
                # استخدام self.__class__.__module__ للوصول إلى النموذج من نفس الملف بدون دورة استيراد
                LoginAttempt.objects.create(
                    user=self.user,
                    username=self.user.username,
                    ip_address=get_client_ip(request),
                    user_agent=request.META.get('HTTP_USER_AGENT', ''),
                    status='locked',
                    notes=f'تم قفل الحساب بعد {self.failed_login_attempts} محاولات فاشلة'
                )
            
            return True  # تم قفل الحساب
        
        self.save(update_fields=['failed_login_attempts', 'last_failed_login'])
        
        # تسجيل محاولة الدخول
        if request:
            # نستخدم LoginAttempt مباشرة بدون استيراد من نفس الملف لتجنب مشاكل الاستيراد الدائري
            LoginAttempt.objects.create(
                user=self.user,
                username=self.user.username,
                ip_address=get_client_ip(request),
                user_agent=request.META.get('HTTP_USER_AGENT', ''),
                status='failed',
                notes=f'محاولة فاشلة {self.failed_login_attempts} من {lockout_attempts}'
            )
        
        return False  # لم يتم قفل الحساب بعد
    
    def get_totp_uri(self):
        """الحصول على URI TOTP لتطبيقات المصادقة"""
        import pyotp
        from .security import get_system_setting
        
        if not self.totp_secret:
            return None
        
        # استخدام اسم المستخدم واسم الموقع في URI
        totp = pyotp.TOTP(self.totp_secret)
        site_name = get_system_setting('site_name', 'Car Rental System')
        
        # استخدام اسم المستخدم واسم الموقع في URI
        return totp.provisioning_uri(name=self.user.username, issuer_name=site_name)
    
    def generate_backup_codes(self, count=8, force_regenerate=False):
        """توليد رموز احتياطية جديدة"""
        import string
        import random
        
        # إذا كانت هناك رموز احتياطية بالفعل ولم يتم طلب إعادة التوليد بالقوة، نرجع الرموز الموجودة
        if self.backup_codes and not force_regenerate:
            return self.backup_codes
            
        codes = []
        for _ in range(count):
            # توليد رمز من 8 أرقام
            code = ''.join(random.choices(string.digits, k=8))
            codes.append(code)
        
        self.backup_codes = codes
        self.save(update_fields=['backup_codes'])
        
        return codes
    
    def is_valid_backup_code(self, code):
        """التحقق من صحة رمز احتياطي"""
        if not self.backup_codes:
            return False
        
        if code in self.backup_codes:
            # استخدام الرمز وإزالته من القائمة
            self.backup_codes.remove(code)
            self.save(update_fields=['backup_codes'])
            
            return True
        
        return False
    
    class Meta:
        verbose_name = 'أمان المستخدم'
        verbose_name_plural = 'أمان المستخدمين'


class TwoFactorSession(models.Model):
    """نموذج لتتبع جلسات المصادقة الثنائية المؤقتة"""
    
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='two_factor_sessions')
    session_key = models.CharField(max_length=64, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    is_verified = models.BooleanField(default=False)
    
    def __str__(self):
        return f"2FA Session for {self.user.username}"
    
    def is_valid(self):
        """التحقق مما إذا كانت الجلسة صالحة (غير منتهية)"""
        return timezone.now() < self.expires_at and self.is_verified
    
    class Meta:
        verbose_name = 'جلسة المصادقة الثنائية'
        verbose_name_plural = 'جلسات المصادقة الثنائية'