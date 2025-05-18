from django import forms
from django.utils.translation import gettext_lazy as _
from rental.models_custody import CustomerGuarantee
from rental.models import Reservation, Car
import datetime

class CustomerGuaranteeForm(forms.ModelForm):
    """نموذج إضافة وتعديل عهدة العميل"""
    
    class Meta:
        model = CustomerGuarantee
        fields = [
            'name', 'guarantee_type', 'category', 'handover_date', 
            'description', 'value', 'notes', 'reservation', 'identifier',
            'credit_card_info', 'property_description', 'insurance_policy_number'
        ]
        widgets = {
            'handover_date': forms.DateInput(attrs={'type': 'date'}),
            'description': forms.Textarea(attrs={'rows': 3}),
            'notes': forms.Textarea(attrs={'rows': 3}),
        }
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # تعديل الحقول لتكون أكثر سهولة في الاستخدام
        
        # حقل الوصف مطلوب الآن
        self.fields['description'].required = True
        
        # اختيار الحجز
        self.fields['reservation'].widget.attrs.update({'class': 'select2'})
        self.fields['reservation'].queryset = Reservation.objects.filter(
            status__in=['confirmed', 'completed']
        ).order_by('-created_at')
        
        # إضافة فئات فرعية لكل نوع عهدة
        self.fields['category'].widget.attrs.update({
            'placeholder': _('أدخل فئة العهدة مثل: وثيقة تأمين شامل، رخصة قيادة دولية، إلخ')
        })
        
        # تحديث سلوك الحقول عند التغيير
        self.fields['guarantee_type'].widget.attrs.update({
            'onchange': 'toggleCustomFields()'
        })
        
        self.fields['reservation'].widget.attrs.update({
            'onchange': 'updateReservationData()'
        })
        
        # تخصيص حقول نوع العهدة
        self.fields['credit_card_info'].widget.attrs.update({
            'placeholder': _('أدخل معلومات البطاقة الائتمانية (رقم البطاقة، اسم صاحب البطاقة، تاريخ الانتهاء)')
        })
        
        self.fields['property_description'].widget.attrs.update({
            'placeholder': _('أدخل وصف الممتلكات العقارية (نوع العقار، الموقع، القيمة التقديرية)')
        })
        
        self.fields['insurance_policy_number'].widget.attrs.update({
            'placeholder': _('أدخل رقم بوليصة التأمين')
        })
    
    def clean(self):
        cleaned_data = super().clean()
        
        # التحقق من وجود تاريخ استلام العهدة
        handover_date = cleaned_data.get('handover_date')
        if handover_date and handover_date > datetime.date.today():
            self.add_error('handover_date', _('لا يمكن أن يكون تاريخ تسليم العهدة في المستقبل'))
        
        # التحقق من القيمة المالية
        value = cleaned_data.get('value')
        if value and value < 0:
            self.add_error('value', _('يجب أن تكون قيمة العهدة أكبر من أو تساوي الصفر'))
            
        # تعبئة بيانات العميل والسيارة تلقائيًا من الحجز
        reservation = cleaned_data.get('reservation')
        if reservation:
            # تعيين العميل تلقائيًا من الحجز
            cleaned_data['customer'] = reservation.user
            # تعيين السيارة تلقائيًا من الحجز
            cleaned_data['car'] = reservation.car
        
        return cleaned_data


class CustomerGuaranteeReturnForm(forms.ModelForm):
    """نموذج استرداد عهدة العميل"""
    
    class Meta:
        model = CustomerGuarantee
        fields = [
            'return_date', 'status', 'deductions', 'deduction_reason', 'notes'
        ]
        widgets = {
            'return_date': forms.DateInput(attrs={'type': 'date'}),
            'deduction_reason': forms.Textarea(attrs={'rows': 3}),
            'notes': forms.Textarea(attrs={'rows': 3}),
        }
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # تعيين تاريخ الاسترداد ليكون اليوم افتراضيًا
        self.fields['return_date'].initial = datetime.date.today()
        
        # تقييد اختيارات الحالة
        self.fields['status'].choices = [
            ('returned', _('مستردة')),
            ('partially_returned', _('مستردة جزئياً')),
            ('withheld', _('محتجزة')),
        ]
        
        # إضافة ملاحظة توضيحية للخصومات
        self.fields['deductions'].help_text = _('أدخل قيمة الخصومات إن وجدت')
        self.fields['deduction_reason'].help_text = _('أدخل سبب الخصم')
    
    def clean(self):
        cleaned_data = super().clean()
        
        # التحقق من تاريخ الاسترداد
        return_date = cleaned_data.get('return_date')
        if return_date and return_date > datetime.date.today():
            self.add_error('return_date', _('لا يمكن أن يكون تاريخ استرداد العهدة في المستقبل'))
            
        # التحقق من تواريخ الاستلام والاسترداد
        instance = self.instance
        if return_date and instance.handover_date and return_date < instance.handover_date:
            self.add_error('return_date', _('تاريخ الاسترداد لا يمكن أن يكون قبل تاريخ التسليم'))
            
        # التحقق من قيمة الخصومات
        deductions = cleaned_data.get('deductions')
        if deductions:
            if deductions < 0:
                self.add_error('deductions', _('يجب أن تكون قيمة الخصومات أكبر من أو تساوي الصفر'))
            
            # إذا كانت هناك خصومات، يجب تقديم سبب الخصم
            deduction_reason = cleaned_data.get('deduction_reason')
            if not deduction_reason:
                self.add_error('deduction_reason', _('يجب تقديم سبب للخصم'))
                
            # التحقق من أن الخصومات لا تتجاوز قيمة العهدة
            if deductions > instance.value:
                self.add_error('deductions', _('لا يمكن أن تتجاوز الخصومات قيمة العهدة'))
                
        # إذا كانت الحالة "محتجزة"، يجب تقديم سبب
        status = cleaned_data.get('status')
        if status == 'withheld' and not cleaned_data.get('notes'):
            self.add_error('notes', _('يجب تقديم سبب احتجاز العهدة'))
            
        return cleaned_data


class CustomerGuaranteeFilterForm(forms.Form):
    """نموذج تصفية وبحث عهدات العملاء"""
    
    STATUS_CHOICES = [
        ('', _('الكل')),
        ('active', _('نشطة')),
        ('returned', _('مستردة')),
        ('partially_returned', _('مستردة جزئياً')),
        ('withheld', _('محتجزة')),
        ('claimed', _('مطالب بها')),
    ]
    
    GUARANTEE_TYPE_CHOICES = [
        ('', _('الكل')),
        ('cash', _('نقدي')),
        ('credit_card', _('بطاقة ائتمانية')),
        ('property', _('مستند عقاري')),
        ('bank_deposit', _('وديعة بنكية')),
        ('insurance', _('بطاقة تأمين')),
        ('other', _('أخرى')),
    ]
    
    search = forms.CharField(
        required=False,
        label=_('بحث'),
        widget=forms.TextInput(attrs={'placeholder': _('اسم العميل، رقم الحجز، معرّف...')})
    )
    
    status = forms.ChoiceField(
        required=False,
        label=_('الحالة'),
        choices=STATUS_CHOICES
    )
    
    guarantee_type = forms.ChoiceField(
        required=False,
        label=_('نوع العهدة'),
        choices=GUARANTEE_TYPE_CHOICES
    )
    
    date_from = forms.DateField(
        required=False,
        label=_('من تاريخ'),
        widget=forms.DateInput(attrs={'type': 'date'})
    )
    
    date_to = forms.DateField(
        required=False,
        label=_('إلى تاريخ'),
        widget=forms.DateInput(attrs={'type': 'date'})
    )
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # إضافة الفئات والأنماط للحقول
        for field_name, field in self.fields.items():
            field.widget.attrs.update({'class': 'form-control form-control-sm'})