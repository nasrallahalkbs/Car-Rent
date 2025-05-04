from django.db import models
from django.utils.translation import gettext_lazy as _
from django.conf import settings
from .models import Reservation, Car

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
    
    # العلاقات الأساسية
    customer = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.PROTECT,
        related_name='guarantees',
        verbose_name=_('العميل')
    )
    
    reservation = models.ForeignKey(
        Reservation, 
        on_delete=models.PROTECT,
        related_name='guarantees',
        verbose_name=_('الحجز')
    )
    
    car = models.ForeignKey(
        Car, 
        on_delete=models.PROTECT,
        related_name='guarantees',
        null=True,
        blank=True,
        verbose_name=_('السيارة')
    )
    
    # بيانات العهدة الأساسية
    guarantee_type = models.CharField(
        max_length=50,
        choices=GUARANTEE_TYPE_CHOICES,
        verbose_name=_('نوع الضمانة')
    )
    
    guarantee_identifier = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name=_('معرف الضمانة')
    )
    
    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        blank=True,
        null=True,
        verbose_name=_('قيمة الضمانة')
    )
    
    currency = models.CharField(
        max_length=10,
        default='SAR',
        verbose_name=_('العملة')
    )
    
    # تفاصيل حسب نوع الضمانة
    # للضمانة المالية
    payment_method = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        verbose_name=_('طريقة الدفع')
    )
    
    # للمستند العقاري
    property_document_type = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name=_('نوع المستند العقاري')
    )
    
    property_document_number = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name=_('رقم المستند العقاري')
    )
    
    # للوديعة البنكية
    bank_name = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name=_('اسم البنك')
    )
    
    bank_account_number = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        verbose_name=_('رقم الحساب البنكي')
    )
    
    # لبطاقة التأمين
    insurance_company = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name=_('شركة التأمين')
    )
    
    insurance_policy_number = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name=_('رقم بوليصة التأمين')
    )
    
    insurance_expiry_date = models.DateField(
        blank=True,
        null=True,
        verbose_name=_('تاريخ انتهاء التأمين')
    )
    
    # للضمانات الأخرى
    other_guarantee_description = models.TextField(
        blank=True,
        null=True,
        verbose_name=_('وصف الضمانة الأخرى')
    )
    
    # تواريخ وحالة
    issue_date = models.DateField(
        verbose_name=_('تاريخ الإصدار')
    )
    
    return_date = models.DateField(
        blank=True,
        null=True,
        verbose_name=_('تاريخ الاسترداد')
    )
    
    status = models.CharField(
        max_length=20,
        choices=GUARANTEE_STATUS_CHOICES,
        default='active',
        verbose_name=_('حالة الضمانة')
    )
    
    # تفاصيل المطالبة (إن وجدت)
    claim_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        blank=True,
        null=True,
        verbose_name=_('قيمة المطالبة')
    )
    
    claim_reason = models.TextField(
        blank=True,
        null=True,
        verbose_name=_('سبب المطالبة')
    )
    
    claim_date = models.DateField(
        blank=True,
        null=True,
        verbose_name=_('تاريخ المطالبة')
    )
    
    # الموظفين المسؤولين
    staff_received = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.PROTECT,
        related_name='guarantees_received',
        blank=True,
        null=True,
        verbose_name=_('موظف الاستلام')
    )
    
    staff_returned = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.PROTECT,
        related_name='guarantees_returned',
        blank=True,
        null=True,
        verbose_name=_('موظف الإرجاع')
    )
    
    # ملاحظات
    notes = models.TextField(
        blank=True,
        null=True,
        verbose_name=_('ملاحظات')
    )
    
    # بيانات النظام
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_('تاريخ الإنشاء')
    )
    
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name=_('تاريخ التحديث')
    )
    
    def __str__(self):
        return f"{self.get_guarantee_type_display()} - {self.customer.get_full_name()} - {self.reservation.reservation_number}"
    
    class Meta:
        verbose_name = _('ضمانة العميل')
        verbose_name_plural = _('ضمانات العملاء')
        ordering = ['-created_at']