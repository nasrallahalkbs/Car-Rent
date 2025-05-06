from django.db import models
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from django.conf import settings

class SystemSetting(models.Model):
    """نموذج إعدادات النظام"""
    
    GROUP_CHOICES = [
        ('general', _('إعدادات عامة')),
        ('security', _('الأمان')),
        ('notifications', _('الإشعارات')),
        ('backup', _('النسخ الاحتياطي')),
        ('email', _('البريد الإلكتروني')),
        ('business', _('بيانات الأعمال')),
        ('appearance', _('المظهر')),
        ('other', _('أخرى')),
    ]
    
    VALUE_TYPES = [
        ('string', _('نص')),
        ('integer', _('رقم صحيح')),
        ('float', _('رقم عشري')),
        ('boolean', _('منطقي')),
        ('json', _('JSON')),
        ('list', _('قائمة')),
    ]
    
    key = models.CharField(max_length=100, unique=True, verbose_name=_('المفتاح'))
    value = models.TextField(blank=True, null=True, verbose_name=_('القيمة'))
    value_type = models.CharField(max_length=20, choices=VALUE_TYPES, default='string', verbose_name=_('نوع القيمة'))
    group = models.CharField(max_length=20, choices=GROUP_CHOICES, default='general', verbose_name=_('المجموعة'))
    description = models.CharField(max_length=255, blank=True, null=True, verbose_name=_('الوصف'))
    is_public = models.BooleanField(default=False, verbose_name=_('عام'))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('تاريخ الإنشاء'))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_('تاريخ التعديل'))
    
    def __str__(self):
        return f"{self.key}: {self.value}"
    
    class Meta:
        verbose_name = _('إعداد النظام')
        verbose_name_plural = _('إعدادات النظام')
        ordering = ['group', 'key']

class SystemBackup(models.Model):
    """نموذج النسخ الاحتياطية للنظام"""
    
    STATUS_CHOICES = [
        ('pending', _('قيد الإنشاء')),
        ('completed', _('مكتمل')),
        ('failed', _('فشل')),
        ('restored', _('تمت الاستعادة')),
    ]
    
    name = models.CharField(max_length=100, verbose_name=_('الاسم'))
    file_path = models.CharField(max_length=255, verbose_name=_('مسار الملف'))
    file_size = models.BigIntegerField(default=0, verbose_name=_('حجم الملف'))
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name=_('الحالة'))
    notes = models.TextField(blank=True, null=True, verbose_name=_('ملاحظات'))
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, verbose_name=_('بواسطة'))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('تاريخ الإنشاء'))
    
    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name = _('نسخة احتياطية')
        verbose_name_plural = _('النسخ الاحتياطية')
        ordering = ['-created_at']

class ScheduledJob(models.Model):
    """نموذج المهام المجدولة"""
    
    JOB_TYPE_CHOICES = [
        ('backup', _('نسخ احتياطي')),
        ('cleanup', _('تنظيف')),
        ('report', _('تقرير')),
        ('custom', _('مخصص')),
    ]
    
    INTERVAL_CHOICES = [
        ('hourly', _('ساعي')),
        ('daily', _('يومي')),
        ('weekly', _('أسبوعي')),
        ('monthly', _('شهري')),
        ('custom', _('مخصص')),
    ]
    
    name = models.CharField(max_length=100, verbose_name=_('الاسم'))
    job_type = models.CharField(max_length=20, choices=JOB_TYPE_CHOICES, verbose_name=_('نوع المهمة'))
    function_name = models.CharField(max_length=100, verbose_name=_('اسم الدالة'))
    args = models.JSONField(default=dict, blank=True, verbose_name=_('معاملات'))
    interval_type = models.CharField(max_length=20, choices=INTERVAL_CHOICES, default='daily', verbose_name=_('نوع الفاصل الزمني'))
    interval_value = models.IntegerField(default=1, verbose_name=_('قيمة الفاصل الزمني'))
    cron_expression = models.CharField(max_length=100, blank=True, null=True, verbose_name=_('تعبير Cron'))
    is_active = models.BooleanField(default=True, verbose_name=_('نشط'))
    next_run = models.DateTimeField(verbose_name=_('التشغيل التالي'))
    last_run = models.DateTimeField(null=True, blank=True, verbose_name=_('آخر تشغيل'))
    last_status = models.CharField(max_length=20, blank=True, null=True, verbose_name=_('آخر حالة'))
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, verbose_name=_('بواسطة'))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('تاريخ الإنشاء'))
    
    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name = _('مهمة مجدولة')
        verbose_name_plural = _('المهام المجدولة')
        ordering = ['next_run']

class SystemIssue(models.Model):
    """نموذج مشاكل النظام"""
    
    SEVERITY_CHOICES = [
        ('critical', _('حرجة')),
        ('high', _('عالية')),
        ('medium', _('متوسطة')),
        ('low', _('منخفضة')),
    ]
    
    STATUS_CHOICES = [
        ('new', _('جديدة')),
        ('in_progress', _('قيد المعالجة')),
        ('fixed', _('تم الإصلاح')),
    ]
    
    title = models.CharField(max_length=255, verbose_name=_('العنوان'))
    description = models.TextField(verbose_name=_('الوصف'))
    area = models.CharField(max_length=50, verbose_name=_('المنطقة'))
    severity = models.CharField(max_length=20, choices=SEVERITY_CHOICES, default='medium', verbose_name=_('الخطورة'))
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='new', verbose_name=_('الحالة'))
    detected_at = models.DateTimeField(auto_now_add=True, verbose_name=_('تاريخ الاكتشاف'))
    fixed_at = models.DateTimeField(null=True, blank=True, verbose_name=_('تاريخ الإصلاح'))
    fixed_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, verbose_name=_('تم الإصلاح بواسطة'))
    fix_notes = models.TextField(blank=True, null=True, verbose_name=_('ملاحظات الإصلاح'))
    stack_trace = models.TextField(blank=True, null=True, verbose_name=_('تتبع المكدس'))
    
    def __str__(self):
        return self.title
    
    class Meta:
        verbose_name = _('مشكلة النظام')
        verbose_name_plural = _('مشاكل النظام')
        ordering = ['-detected_at']

class SystemNotification(models.Model):
    """نموذج إشعارات النظام"""
    
    TYPE_CHOICES = [
        ('info', _('معلومات')),
        ('success', _('نجاح')),
        ('warning', _('تحذير')),
        ('error', _('خطأ')),
    ]
    
    title = models.CharField(max_length=255, verbose_name=_('العنوان'))
    message = models.TextField(verbose_name=_('الرسالة'))
    notification_type = models.CharField(max_length=20, choices=TYPE_CHOICES, default='info', verbose_name=_('نوع الإشعار'))
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True, verbose_name=_('المستخدم'))
    is_read = models.BooleanField(default=False, verbose_name=_('مقروء'))
    is_system_wide = models.BooleanField(default=False, verbose_name=_('على مستوى النظام'))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('تاريخ الإنشاء'))
    expires_at = models.DateTimeField(null=True, blank=True, verbose_name=_('تاريخ الانتهاء'))
    link = models.CharField(max_length=255, blank=True, null=True, verbose_name=_('رابط'))
    related_object_type = models.CharField(max_length=50, blank=True, null=True, verbose_name=_('نوع الكائن المرتبط'))
    related_object_id = models.IntegerField(blank=True, null=True, verbose_name=_('معرف الكائن المرتبط'))
    
    def __str__(self):
        return self.title
    
    class Meta:
        verbose_name = _('إشعار النظام')
        verbose_name_plural = _('إشعارات النظام')
        ordering = ['-created_at']
        
    @property
    def is_expired(self):
        if self.expires_at:
            return timezone.now() > self.expires_at
        return False