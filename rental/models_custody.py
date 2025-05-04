from django.db import models
from django.utils.translation import gettext_lazy as _
from django.conf import settings
from django.utils import timezone

class CustomerGuarantee(models.Model):
    """نموذج ضمانة/عهدة العميل"""
    
    GUARANTEE_TYPE_CHOICES = [
        ('cash', _('نقدي')),
        ('credit_card', _('بطاقة ائتمانية')),
        ('property', _('مستند عقاري')),
        ('bank_deposit', _('وديعة بنكية')),
        ('insurance', _('بطاقة تأمين')),
        ('other', _('أخرى')),
    ]
    
    GUARANTEE_STATUS_CHOICES = [
        ('active', _('نشطة')),
        ('returned', _('مستردة')),
        ('partially_returned', _('مستردة جزئياً')),
        ('withheld', _('محتجزة')),
        ('claimed', _('مطالب بها')),
    ]
    
    # بيانات أساسية
    name = models.CharField(
        max_length=255,
        verbose_name=_('اسم العهدة')
    )
    
    guarantee_type = models.CharField(
        max_length=50,
        choices=GUARANTEE_TYPE_CHOICES,
        verbose_name=_('نوع العهدة')
    )
    
    category = models.CharField(
        max_length=100,
        blank=True,
        null=True, 
        verbose_name=_('فئة العهدة')
    )
    
    handover_date = models.DateField(
        default=timezone.now,
        verbose_name=_('تاريخ تسليم العهدة')
    )
    
    return_date = models.DateField(
        blank=True,
        null=True,
        verbose_name=_('تاريخ استرداد العهدة')
    )
    
    description = models.TextField(
        blank=True, 
        null=True,
        verbose_name=_('وصف العهدة')
    )
    
    notes = models.TextField(
        blank=True, 
        null=True,
        verbose_name=_('ملاحظات')
    )
    
    identifier = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name=_('معرف العهدة')
    )
    
    value = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        verbose_name=_('قيمة العهدة')
    )
    
    status = models.CharField(
        max_length=20,
        choices=GUARANTEE_STATUS_CHOICES,
        default='active',
        verbose_name=_('حالة العهدة')
    )
    
    # العلاقات
    reservation = models.ForeignKey(
        'Reservation',
        on_delete=models.PROTECT,
        related_name='guarantees',
        verbose_name=_('رقم الحجز')
    )
    
    customer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name='guarantees',
        verbose_name=_('العميل')
    )
    
    car = models.ForeignKey(
        'Car',
        on_delete=models.PROTECT,
        related_name='guarantees',
        null=True,
        blank=True,
        verbose_name=_('السيارة')
    )
    
    # تفاصيل استرداد العهدة
    deductions = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        verbose_name=_('مبلغ الخصومات')
    )
    
    deduction_reason = models.TextField(
        blank=True, 
        null=True,
        verbose_name=_('سبب الخصم')
    )
    
    returned_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name=_('المبلغ المسترد')
    )
    
    # بيانات النظام
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name='guarantees_created',
        verbose_name=_('تم الإنشاء بواسطة')
    )
    
    returned_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name='guarantees_returned',
        null=True,
        blank=True,
        verbose_name=_('تم الاسترداد بواسطة')
    )
    
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_('تاريخ الإنشاء')
    )
    
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name=_('تاريخ التحديث')
    )
    
    def __str__(self):
        return f"{self.name} - {self.customer.get_full_name()} ({self.reservation.reservation_number})"
    
    class Meta:
        verbose_name = _('عهدة العميل')
        verbose_name_plural = _('عهدات العملاء')
        ordering = ['-created_at']
        
    def save(self, *args, **kwargs):
        # حساب المبلغ المسترد عند الاسترداد
        if self.status in ['returned', 'partially_returned'] and self.return_date:
            self.returned_amount = self.value - self.deductions
        
        super().save(*args, **kwargs)