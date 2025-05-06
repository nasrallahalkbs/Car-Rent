from django.db import models
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from django.conf import settings

class SystemBackup(models.Model):
    """نموذج لتخزين معلومات النسخ الاحتياطي للنظام"""
    STATUS_CHOICES = [
        ('pending', _('قيد الإنشاء')),
        ('completed', _('مكتمل')),
        ('failed', _('فشل')),
        ('restored', _('تمت الاستعادة')),
    ]
    
    name = models.CharField(max_length=255, verbose_name=_('اسم النسخة الاحتياطية'))
    file_path = models.CharField(max_length=500, verbose_name=_('مسار الملف'))
    file_size = models.BigIntegerField(default=0, verbose_name=_('حجم الملف'))
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name=_('الحالة'))
    notes = models.TextField(blank=True, null=True, verbose_name=_('ملاحظات'))
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='created_backups', verbose_name=_('أنشئت بواسطة'))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('تاريخ الإنشاء'))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_('تاريخ التحديث'))
    
    def __str__(self):
        return self.name
        
    class Meta:
        verbose_name = _('نسخة احتياطية')
        verbose_name_plural = _('النسخ الاحتياطية')
        ordering = ['-created_at']

class ScheduledJob(models.Model):
    """نموذج لتخزين معلومات المهام المجدولة"""
    JOB_TYPE_CHOICES = [
        ('backup', _('نسخ احتياطي')),
        ('cleanup', _('تنظيف')),
        ('report', _('تقرير')),
        ('custom', _('مخصص')),
    ]
    
    INTERVAL_CHOICES = [
        ('hourly', _('كل ساعة')),
        ('daily', _('يومي')),
        ('weekly', _('أسبوعي')),
        ('monthly', _('شهري')),
        ('custom', _('مخصص')),
    ]
    
    name = models.CharField(max_length=255, verbose_name=_('اسم المهمة'))
    job_type = models.CharField(max_length=20, choices=JOB_TYPE_CHOICES, default='backup', verbose_name=_('نوع المهمة'))
    function_name = models.CharField(max_length=255, verbose_name=_('اسم الوظيفة'))
    args = models.JSONField(blank=True, null=True, verbose_name=_('المعاملات'))
    interval_type = models.CharField(max_length=20, choices=INTERVAL_CHOICES, default='daily', verbose_name=_('نوع الفاصل الزمني'))
    interval_value = models.IntegerField(default=1, verbose_name=_('قيمة الفاصل الزمني'))
    cron_expression = models.CharField(max_length=100, blank=True, null=True, verbose_name=_('تعبير cron'))
    next_run = models.DateTimeField(verbose_name=_('التشغيل التالي'))
    last_run = models.DateTimeField(null=True, blank=True, verbose_name=_('آخر تشغيل'))
    is_active = models.BooleanField(default=True, verbose_name=_('نشط'))
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='created_jobs', verbose_name=_('أنشئت بواسطة'))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('تاريخ الإنشاء'))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_('تاريخ التحديث'))
    
    def __str__(self):
        return self.name
        
    class Meta:
        verbose_name = _('مهمة مجدولة')
        verbose_name_plural = _('المهام المجدولة')
        ordering = ['next_run']

class SystemSetting(models.Model):
    """نموذج لتخزين إعدادات النظام"""
    GROUP_CHOICES = [
        ('general', _('عام')),
        ('security', _('الأمان')),
        ('notifications', _('الإشعارات')),
        ('backup', _('النسخ الاحتياطي')),
        ('appearance', _('المظهر')),
        ('email', _('البريد الإلكتروني')),
        ('other', _('أخرى')),
    ]
    
    TYPE_CHOICES = [
        ('string', _('نص')),
        ('integer', _('عدد صحيح')),
        ('float', _('عدد عشري')),
        ('boolean', _('منطقي')),
        ('json', _('JSON')),
        ('list', _('قائمة')),
    ]
    
    key = models.CharField(max_length=100, unique=True, verbose_name=_('المفتاح'))
    value = models.TextField(blank=True, null=True, verbose_name=_('القيمة'))
    value_type = models.CharField(max_length=20, choices=TYPE_CHOICES, default='string', verbose_name=_('نوع القيمة'))
    group = models.CharField(max_length=20, choices=GROUP_CHOICES, default='general', verbose_name=_('المجموعة'))
    description = models.TextField(blank=True, null=True, verbose_name=_('الوصف'))
    is_public = models.BooleanField(default=False, verbose_name=_('عام'))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('تاريخ الإنشاء'))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_('تاريخ التحديث'))
    
    def __str__(self):
        return f"{self.key} ({self.get_group_display()})"
        
    class Meta:
        verbose_name = _('إعداد النظام')
        verbose_name_plural = _('إعدادات النظام')
        ordering = ['group', 'key']

class SystemIssue(models.Model):
    """نموذج لتخزين مشاكل النظام المكتشفة"""
    SEVERITY_CHOICES = [
        ('low', _('منخفضة')),
        ('medium', _('متوسطة')),
        ('high', _('عالية')),
        ('critical', _('حرجة')),
    ]
    
    STATUS_CHOICES = [
        ('new', _('جديدة')),
        ('in_progress', _('قيد المعالجة')),
        ('fixed', _('تم الإصلاح')),
        ('wont_fix', _('لن يتم الإصلاح')),
    ]
    
    title = models.CharField(max_length=255, verbose_name=_('العنوان'))
    description = models.TextField(verbose_name=_('الوصف'))
    area = models.CharField(max_length=100, verbose_name=_('المنطقة'))
    severity = models.CharField(max_length=20, choices=SEVERITY_CHOICES, default='medium', verbose_name=_('الخطورة'))
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='new', verbose_name=_('الحالة'))
    detected_at = models.DateTimeField(auto_now_add=True, verbose_name=_('تاريخ الاكتشاف'))
    fixed_at = models.DateTimeField(null=True, blank=True, verbose_name=_('تاريخ الإصلاح'))
    fixed_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='fixed_issues', verbose_name=_('تم إصلاحه بواسطة'))
    fix_notes = models.TextField(blank=True, null=True, verbose_name=_('ملاحظات الإصلاح'))
    
    def __str__(self):
        return self.title
        
    class Meta:
        verbose_name = _('مشكلة في النظام')
        verbose_name_plural = _('مشاكل النظام')
        ordering = ['-detected_at']

class SystemNotification(models.Model):
    """نموذج لتخزين إشعارات النظام"""
    TYPE_CHOICES = [
        ('info', _('معلومات')),
        ('warning', _('تحذير')),
        ('error', _('خطأ')),
        ('success', _('نجاح')),
    ]
    
    title = models.CharField(max_length=255, verbose_name=_('العنوان'))
    message = models.TextField(verbose_name=_('الرسالة'))
    notification_type = models.CharField(max_length=20, choices=TYPE_CHOICES, default='info', verbose_name=_('النوع'))
    icon = models.CharField(max_length=50, blank=True, null=True, verbose_name=_('الأيقونة'))
    link = models.CharField(max_length=255, blank=True, null=True, verbose_name=_('الرابط'))
    is_public = models.BooleanField(default=False, verbose_name=_('عام'))
    is_read = models.BooleanField(default=False, verbose_name=_('مقروء'))
    target_users = models.ManyToManyField(settings.AUTH_USER_MODEL, blank=True, related_name='notifications', verbose_name=_('المستخدمين المستهدفين'))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('تاريخ الإنشاء'))
    
    def __str__(self):
        return self.title
        
    class Meta:
        verbose_name = _('إشعار النظام')
        verbose_name_plural = _('إشعارات النظام')
        ordering = ['-created_at']
