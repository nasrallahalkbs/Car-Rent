from django.db import models
from django.utils.translation import gettext_lazy as _
from django.conf import settings

class Permission(models.Model):
    """نموذج الصلاحيات الخاصة بالنظام"""
    name = models.CharField(max_length=100, verbose_name=_('اسم الصلاحية'))
    codename = models.CharField(max_length=100, unique=True, verbose_name=_('رمز الصلاحية'))
    description = models.TextField(verbose_name=_('وصف الصلاحية'))
    
    def __str__(self):
        return self.name
        
    class Meta:
        verbose_name = _('صلاحية')
        verbose_name_plural = _('الصلاحيات')

class Role(models.Model):
    """نموذج الأدوار للمستخدمين"""
    name = models.CharField(max_length=100, verbose_name=_('اسم الدور'))
    permissions = models.ManyToManyField(Permission, verbose_name=_('الصلاحيات'))
    description = models.TextField(blank=True, null=True, verbose_name=_('وصف الدور'))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('تاريخ الإنشاء'))
    is_active = models.BooleanField(default=True, verbose_name=_('نشط'))
    
    def __str__(self):
        return self.name
        
    class Meta:
        verbose_name = _('دور')
        verbose_name_plural = _('الأدوار')

class AdminUser(models.Model):
    """نموذج معلومات إضافية للمسؤولين"""
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='admin_profile', verbose_name=_('المستخدم'))
    role = models.ForeignKey(Role, on_delete=models.SET_NULL, null=True, verbose_name=_('الدور'))
    is_superadmin = models.BooleanField(default=False, verbose_name=_('مسؤول أعلى'))
    last_login_ip = models.GenericIPAddressField(null=True, blank=True, verbose_name=_('آخر IP للدخول'))
    notes = models.TextField(blank=True, null=True, verbose_name=_('ملاحظات'))
    access_token = models.CharField(max_length=255, blank=True, null=True, verbose_name=_('رمز الوصول'))
    
    # الحقول الجديدة
    full_name = models.CharField(max_length=255, blank=True, null=True, verbose_name=_('الاسم الكامل'))
    phone_number = models.CharField(max_length=20, blank=True, null=True, verbose_name=_('رقم الهاتف'))
    current_job = models.CharField(max_length=255, blank=True, null=True, verbose_name=_('الوظيفة الحالية'))
    qualification = models.CharField(max_length=255, blank=True, null=True, verbose_name=_('المؤهل'))
    department = models.CharField(max_length=255, blank=True, null=True, verbose_name=_('القسم'))
    
    def __str__(self):
        if self.full_name:
            return self.full_name
        return self.user.username
        
    class Meta:
        verbose_name = _('مسؤول')
        verbose_name_plural = _('المسؤولين')

class AdminActivity(models.Model):
    """نموذج لتسجيل نشاط المسؤولين"""
    admin = models.ForeignKey(AdminUser, on_delete=models.CASCADE, related_name='activities', verbose_name=_('المسؤول'))
    action = models.CharField(max_length=255, verbose_name=_('الإجراء'))
    details = models.TextField(blank=True, null=True, verbose_name=_('التفاصيل'))
    ip_address = models.GenericIPAddressField(verbose_name=_('عنوان IP'))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('تاريخ الإجراء'))
    
    def __str__(self):
        return f"{self.admin} - {self.action}"
        
    class Meta:
        verbose_name = _('نشاط المسؤول')
        verbose_name_plural = _('أنشطة المسؤولين')
        ordering = ['-created_at']

class ReviewManagement(models.Model):
    """نموذج لإدارة التقييمات"""
    STATUS_CHOICES = [
        ('pending', _('قيد المراجعة')),
        ('approved', _('موافق عليه')),
        ('rejected', _('مرفوض')),
        ('flagged', _('تم تمييزه')),
    ]
    
    review_id = models.IntegerField(verbose_name=_('معرف التقييم الأصلي'))
    admin = models.ForeignKey(AdminUser, on_delete=models.CASCADE, related_name='managed_reviews', verbose_name=_('المسؤول'))
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name=_('الحالة'))
    admin_notes = models.TextField(blank=True, null=True, verbose_name=_('ملاحظات المسؤول'))
    action_date = models.DateTimeField(auto_now=True, verbose_name=_('تاريخ الإجراء'))
    
    def __str__(self):
        return f"Review #{self.review_id} - {self.get_status_display()}"
        
    class Meta:
        verbose_name = _('إدارة تقييم')
        verbose_name_plural = _('إدارة التقييمات')
