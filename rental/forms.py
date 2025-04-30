from django import forms
from django.core.validators import MinValueValidator
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.utils import timezone
from datetime import date
from django.utils.translation import gettext_lazy as _

from .models import (
    User, Car, Review, CarConditionReport, Reservation,
    CarInspectionCategory, CarInspectionItem, CarInspectionDetail,
    CarInspectionImage, CustomerSignature
)

class LoginForm(AuthenticationForm):
    """User login form"""
    username = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control'}))
    
    class Meta:
        model = User
        fields = ['username', 'password']

class RegisterForm(UserCreationForm):
    """User registration form"""
    first_name = forms.CharField(max_length=30, required=True)
    last_name = forms.CharField(max_length=30, required=True)
    email = forms.EmailField(required=True)
    phone = forms.CharField(max_length=20, required=True)
    
    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'phone', 'password1', 'password2']

class CarSearchForm(forms.Form):
    """Form for searching cars"""
    CATEGORY_CHOICES = [
        ('', 'All Types'),
        ('Economy', 'Economy'),
        ('Compact', 'Compact'),
        ('Mid-size', 'Mid-size'),
        ('Luxury', 'Luxury'),
        ('SUV', 'SUV'),
        ('Truck', 'Truck')
    ]
    
    TRANSMISSION_CHOICES = [
        ('', 'Any'),
        ('Automatic', 'Automatic'),
        ('Manual', 'Manual')
    ]
    
    FUEL_TYPE_CHOICES = [
        ('', 'Any'),
        ('Gas', 'Gas'),
        ('Diesel', 'Diesel'),
        ('Electric', 'Electric'),
        ('Hybrid', 'Hybrid')
    ]
    
    category = forms.ChoiceField(choices=CATEGORY_CHOICES, required=False)
    transmission = forms.ChoiceField(choices=TRANSMISSION_CHOICES, required=False)
    fuel_type = forms.ChoiceField(choices=FUEL_TYPE_CHOICES, required=False)
    min_price = forms.FloatField(required=False, validators=[MinValueValidator(0)])
    max_price = forms.FloatField(required=False, validators=[MinValueValidator(0)])

class ReservationForm(forms.Form):
    """Form for reserving a car"""
    car_id = forms.IntegerField(widget=forms.HiddenInput())
    start_date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}), required=True)
    end_date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}), required=True)
    
    def clean_start_date(self):
        start_date = self.cleaned_data.get('start_date')
        today = date.today()
        
        if start_date < today:
            raise forms.ValidationError("Pick-up date cannot be in the past")
        
        return start_date
    
    def clean_end_date(self):
        end_date = self.cleaned_data.get('end_date')
        start_date = self.cleaned_data.get('start_date')
        
        if start_date and end_date < start_date:
            raise forms.ValidationError("Return date must be after the pick-up date")
        
        return end_date

class CheckoutForm(forms.Form):
    """Form for checkout and payment"""
    # Generate choices for expiry months and years
    MONTH_CHOICES = [(str(i), str(i).zfill(2)) for i in range(1, 13)]
    YEAR_CHOICES = [(str(i), str(i)) for i in range(date.today().year, date.today().year + 11)]
    
    # Card type choices
    CARD_TYPE_CHOICES = [
        ('visa', 'Visa'),
        ('mastercard', 'MasterCard'),
        ('amex', 'American Express'),
        ('discover', 'Discover')
    ]
    
    card_type = forms.ChoiceField(
        choices=CARD_TYPE_CHOICES,
        required=True,
        widget=forms.RadioSelect(attrs={'class': 'card-type-radio'})
    )
    
    card_number = forms.CharField(
        max_length=16, 
        min_length=16, 
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control', 
            'placeholder': '•••• •••• •••• ••••',
            'autocomplete': 'cc-number',
            'data-card-field': 'number'
        }),
        label='Card Number'
    )
    
    card_name = forms.CharField(
        max_length=100, 
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control', 
            'placeholder': 'Name on card',
            'autocomplete': 'cc-name',
            'data-card-field': 'name'
        }),
        label='Cardholder Name'
    )
    
    expiry_month = forms.ChoiceField(
        choices=MONTH_CHOICES, 
        required=True,
        widget=forms.Select(attrs={
            'class': 'form-select',
            'data-card-field': 'expiry-month'
        }),
        label='Month'
    )
    
    expiry_year = forms.ChoiceField(
        choices=YEAR_CHOICES, 
        required=True,
        widget=forms.Select(attrs={
            'class': 'form-select',
            'data-card-field': 'expiry-year'
        }),
        label='Year'
    )
    
    cvv = forms.CharField(
        max_length=4, 
        min_length=3, 
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control', 
            'placeholder': '•••',
            'autocomplete': 'cc-csc',
            'data-card-field': 'cvv'
        }),
        label='CVV'
    )

class ReviewForm(forms.ModelForm):
    """Form for reviewing a car rental"""
    RATING_CHOICES = [(str(i), str(i)) for i in range(1, 6)]
    
    rating = forms.ChoiceField(choices=RATING_CHOICES, required=True)
    
    class Meta:
        model = Review
        fields = ['rating', 'comment']

class CarForm(forms.ModelForm):
    """Form for adding/editing cars (admin use)"""
    class Meta:
        model = Car
        fields = ['make', 'model', 'year', 'color', 'license_plate', 'daily_rate', 
                 'category', 'seats', 'transmission', 'fuel_type', 'features', 
                 'image_url', 'image', 'status', 'is_available']
        widgets = {
            'make': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'مثل: تويوتا، فورد، هوندا',
            }),
            'model': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'مثل: كامري، F-150، سيفيك',
            }),
            'year': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 2000,
                'max': date.today().year + 1,
                'placeholder': f'بين 2000 و {date.today().year + 1}',
            }),
            'color': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'مثل: أبيض، أسود، أحمر',
            }),
            'license_plate': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'رقم لوحة السيارة',
            }),
            'daily_rate': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 0,
                'step': 0.1,
                'placeholder': 'السعر اليومي (د.ك)',
            }),
            'category': forms.Select(attrs={
                'class': 'form-select',
            }),
            'seats': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 1,
                'max': 15,
                'placeholder': 'عدد المقاعد',
            }),
            'transmission': forms.Select(attrs={
                'class': 'form-select',
            }),
            'fuel_type': forms.Select(attrs={
                'class': 'form-select',
            }),
            'features': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'مثل: كاميرا خلفية، نظام ملاحة، GPS',
            }),
            'image_url': forms.URLInput(attrs={
                'class': 'form-control',
                'placeholder': 'رابط الصورة من الإنترنت (اختياري)',
            }),
            'image': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*',
            }),
            'is_available': forms.CheckboxInput(attrs={
                'class': 'form-check-input me-2',
            }),
            'status': forms.Select(attrs={
                'class': 'form-select',
            }),
        }

class ProfileForm(forms.ModelForm):
    """Form for updating user profile"""
    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'phone']

class PasswordChangeForm(forms.Form):
    """Form for changing user password"""
    current_password = forms.CharField(widget=forms.PasswordInput(), label="Current Password")
    new_password = forms.CharField(widget=forms.PasswordInput(), label="New Password")
    confirm_password = forms.CharField(widget=forms.PasswordInput(), label="Confirm New Password")
    
    def clean(self):
        cleaned_data = super().clean()
        new_password = cleaned_data.get('new_password')
        confirm_password = cleaned_data.get('confirm_password')
        
        if new_password and confirm_password:
            if new_password != confirm_password:
                raise forms.ValidationError("New passwords do not match")
        
        return cleaned_data

class ManualPaymentForm(forms.Form):
    """Form for entering manual payments"""
    PAYMENT_METHODS = [
        ('visa', 'Visa'),
        ('mastercard', 'MasterCard'),
        ('amex', 'American Express'),
        ('discover', 'Discover'),
        ('cash', 'Cash'),
        ('bank_transfer', 'Bank Transfer'),
    ]
    
    amount = forms.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        min_value=0.01,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'})
    )
    
    payment_method = forms.ChoiceField(
        choices=PAYMENT_METHODS,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    reference_number = forms.CharField(
        max_length=50, 
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    
    notes = forms.CharField(
        max_length=500,
        required=False,
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3})
    )
    

class CarConditionReportForm(forms.ModelForm):
    """نموذج توثيق حالة السيارة الأساسي"""
    
    class Meta:
        model = CarConditionReport
        fields = [
            'reservation', 'car', 'report_type', 'mileage', 'date',
            'notes', 'defects', 'defect_cause', 'car_condition',
            'repair_cost', 'fuel_level', 'maintenance_type'
        ]
        widgets = {
            'reservation': forms.Select(attrs={
                'class': 'form-select',
                'id': 'reservation-select',
            }),
            'car': forms.Select(attrs={
                'class': 'form-select',
                'id': 'car-select',
            }),
            'report_type': forms.Select(attrs={
                'class': 'form-select',
            }),
            'mileage': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 0,
                'placeholder': 'المسافة المقطوعة بالكيلومتر',
            }),
            'date': forms.DateTimeInput(attrs={
                'class': 'form-control',
                'type': 'datetime-local',
            }),
            'notes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'ملاحظات عامة حول حالة السيارة',
            }),
            'defects': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'وصف الأعطال أو الأضرار إن وجدت',
            }),
            'defect_cause': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 2,
                'placeholder': 'سبب العطل أو الضرر',
            }),
            'car_condition': forms.Select(attrs={
                'class': 'form-select',
            }),
            'repair_cost': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 0,
                'step': '0.01',
                'placeholder': 'تكلفة الإصلاح المقدرة',
            }),
            'fuel_level': forms.Select(attrs={
                'class': 'form-select',
            }),
            'maintenance_type': forms.Select(attrs={
                'class': 'form-select',
            }),
        }
    
    def __init__(self, *args, **kwargs):
        current_user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        # تحديث الاختيارات للحجوزات
        active_statuses = ['pending', 'confirmed']
        self.fields['reservation'].queryset = Reservation.objects.filter(
            status__in=active_statuses
        ).order_by('-created_at')
        
        # إضافة حقل مخفي لمن قام بإنشاء التقرير
        if current_user:
            self.instance.created_by = current_user
            
    def clean(self):
        cleaned_data = super().clean()
        # التأكد من أن الحجز والسيارة متطابقان
        reservation = cleaned_data.get('reservation')
        car = cleaned_data.get('car')
        
        if reservation and car and reservation.car.id != car.id:
            self.add_error('car', 'السيارة المحددة لا تتطابق مع السيارة في الحجز')
            
        return cleaned_data


class CarInspectionCategoryForm(forms.ModelForm):
    """نموذج لإضافة أو تعديل فئات فحص السيارة"""
    
    class Meta:
        model = CarInspectionCategory
        fields = ['name', 'description', 'display_order', 'is_active']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'اسم الفئة مثل: الهيكل الخارجي، المحرك، إلخ',
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'وصف مختصر للفئة',
            }),
            'display_order': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 0,
                'placeholder': 'ترتيب العرض (الأرقام الأصغر تظهر أولاً)',
            }),
            'is_active': forms.CheckboxInput(attrs={
                'class': 'form-check-input',
            }),
        }


class CarInspectionItemForm(forms.ModelForm):
    """نموذج لإضافة أو تعديل عناصر فحص السيارة"""
    
    class Meta:
        model = CarInspectionItem
        fields = ['category', 'name', 'description', 'display_order', 'is_required', 'is_active']
        widgets = {
            'category': forms.Select(attrs={
                'class': 'form-select',
            }),
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'اسم العنصر مثل: المحرك، الفرامل، إلخ',
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 2,
                'placeholder': 'وصف مختصر للعنصر',
            }),
            'display_order': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 0,
                'placeholder': 'ترتيب العرض (الأرقام الأصغر تظهر أولاً)',
            }),
            'is_required': forms.CheckboxInput(attrs={
                'class': 'form-check-input',
            }),
            'is_active': forms.CheckboxInput(attrs={
                'class': 'form-check-input',
            }),
        }


class CarInspectionDetailForm(forms.ModelForm):
    """نموذج لتوثيق حالة عنصر محدد في تقرير الفحص"""
    
    class Meta:
        model = CarInspectionDetail
        fields = [
            'inspection_item', 'condition', 'notes', 
            'needs_repair', 'repair_status', 'repair_description', 
            'repair_parts', 'repair_cost', 'labor_cost', 
            'repair_date', 'repair_workshop'
        ]
        widgets = {
            'inspection_item': forms.Select(attrs={
                'class': 'form-select',
                'disabled': 'disabled',  # سيتم تعبئته تلقائياً
            }),
            'condition': forms.Select(attrs={
                'class': 'form-select condition-select',
            }),
            'notes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 2,
                'placeholder': 'ملاحظات إضافية عن حالة هذا العنصر',
            }),
            'needs_repair': forms.CheckboxInput(attrs={
                'class': 'form-check-input',
            }),
            'repair_status': forms.Select(attrs={
                'class': 'form-select',
            }),
            'repair_description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 2,
                'placeholder': 'وصف الإصلاحات المطلوبة',
            }),
            'repair_parts': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 2,
                'placeholder': 'قطع الغيار المطلوبة',
            }),
            'repair_cost': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 0,
                'step': '0.01',
                'placeholder': 'تكلفة قطع الغيار',
            }),
            'labor_cost': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 0,
                'step': '0.01',
                'placeholder': 'تكلفة العمالة',
            }),
            'repair_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date',
            }),
            'repair_workshop': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'اسم ورشة الإصلاح',
            }),
        }


class CarInspectionImageForm(forms.ModelForm):
    """نموذج لإضافة صور لتقرير حالة السيارة"""
    
    class Meta:
        model = CarInspectionImage
        fields = ['image', 'description', 'inspection_detail']
        widgets = {
            'image': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*',
                'capture': 'camera',  # للسماح باستخدام الكاميرا في الأجهزة المحمولة
            }),
            'description': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'وصف مختصر للصورة',
            }),
            'inspection_detail': forms.Select(attrs={
                'class': 'form-select',
            }),
        }


class CarRepairForm(forms.ModelForm):
    """نموذج إضافة الإصلاحات والتكاليف المطلوبة للعنصر"""
    
    class Meta:
        model = CarInspectionDetail
        fields = [
            'needs_repair', 'repair_description', 'repair_parts', 
            'repair_cost', 'labor_cost', 'repair_status', 
            'repair_date', 'repair_workshop'
        ]
        widgets = {
            'needs_repair': forms.CheckboxInput(attrs={
                'class': 'form-check-input',
                'onchange': 'toggleRepairFields(this)',
            }),
            'repair_description': forms.Textarea(attrs={
                'class': 'form-control repair-field',
                'rows': 3,
                'placeholder': 'وصف الإصلاح المطلوب بالتفصيل',
            }),
            'repair_parts': forms.Textarea(attrs={
                'class': 'form-control repair-field',
                'rows': 3,
                'placeholder': 'قطع الغيار المطلوبة، اكتب كل قطعة في سطر',
            }),
            'repair_cost': forms.NumberInput(attrs={
                'class': 'form-control repair-field',
                'min': 0,
                'step': 0.01,
                'placeholder': 'تكلفة قطع الغيار',
                'onchange': 'calculateTotalCost()',
            }),
            'labor_cost': forms.NumberInput(attrs={
                'class': 'form-control repair-field',
                'min': 0,
                'step': 0.01,
                'placeholder': 'تكلفة اليد العاملة',
                'onchange': 'calculateTotalCost()',
            }),
            'repair_status': forms.Select(attrs={
                'class': 'form-select repair-field',
            }),
            'repair_date': forms.DateInput(attrs={
                'class': 'form-control repair-field',
                'type': 'date',
            }),
            'repair_workshop': forms.TextInput(attrs={
                'class': 'form-control repair-field',
                'placeholder': 'الورشة المسؤولة عن الإصلاح',
            }),
        }


class CustomerSignatureForm(forms.ModelForm):
    """نموذج لتوثيق توقيع العميل أو الموظف"""
    
    signature_data = forms.CharField(
        widget=forms.HiddenInput(),
        required=True,
        help_text=_('بيانات التوقيع الرقمي')
    )
    
    class Meta:
        model = CustomerSignature
        fields = ['is_customer', 'signed_by_name']
        widgets = {
            'is_customer': forms.HiddenInput(),  # سيتم تحديده عند إنشاء النموذج
            'signed_by_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'الاسم الكامل للموقّع',
                'required': 'required',
            }),
        }
    
    def save(self, commit=True):
        instance = super().save(commit=False)
        
        # تحويل بيانات التوقيع من base64 إلى صورة
        if 'signature_data' in self.cleaned_data and self.cleaned_data['signature_data']:
            import base64
            from django.core.files.base import ContentFile
            
            signature_data = self.cleaned_data['signature_data']
            if signature_data.startswith('data:image'):
                # استخراج البيانات من رمز base64
                format, signature_data = signature_data.split(';base64,')
                ext = format.split('/')[-1]
                
                # إنشاء ملف من البيانات
                signature_file = ContentFile(base64.b64decode(signature_data), name=f'signature.{ext}')
                instance.signature = signature_file
        
        if commit:
            instance.save()
        
        return instance


class CompleteCarInspectionForm(forms.Form):
    """نموذج شامل لتوثيق تقرير حالة السيارة مع جميع تفاصيل الفحص"""
    
    # البيانات الأساسية للتقرير
    reservation = forms.ModelChoiceField(
        queryset=Reservation.objects.filter(status__in=['pending', 'confirmed']),
        widget=forms.Select(attrs={'class': 'form-select'}),
        required=False,
        label=_('الحجز')
    )
    
    car = forms.ModelChoiceField(
        queryset=Car.objects.all(),
        widget=forms.Select(attrs={'class': 'form-select'}),
        label=_('السيارة')
    )
    
    report_type = forms.ChoiceField(
        choices=CarConditionReport.REPORT_TYPE_CHOICES,
        widget=forms.Select(attrs={'class': 'form-select'}),
        label=_('نوع التقرير')
    )
    
    mileage = forms.IntegerField(
        min_value=0,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': _('المسافة المقطوعة بالكيلومتر')
        }),
        label=_('العداد (كم)')
    )
    
    date = forms.DateTimeField(
        widget=forms.DateTimeInput(attrs={
            'class': 'form-control',
            'type': 'datetime-local'
        }),
        initial=timezone.now,
        label=_('تاريخ ووقت الفحص')
    )
    
    fuel_level = forms.ChoiceField(
        choices=CarConditionReport.FUEL_LEVEL_CHOICES,
        widget=forms.Select(attrs={'class': 'form-select'}),
        label=_('مستوى الوقود')
    )
    
    car_condition = forms.ChoiceField(
        choices=CarConditionReport.CAR_CONDITION_CHOICES,
        widget=forms.Select(attrs={'class': 'form-select'}),
        label=_('حالة السيارة العامة')
    )
    
    notes = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 3,
            'placeholder': _('ملاحظات عامة حول حالة السيارة')
        }),
        required=False,
        label=_('ملاحظات عامة')
    )
    
    # تفاصيل الأضرار
    defects = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 3,
            'placeholder': _('وصف الأعطال أو الأضرار إن وجدت')
        }),
        required=False,
        label=_('الأضرار')
    )
    
    defect_cause = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 2,
            'placeholder': _('سبب العطل أو الضرر')
        }),
        required=False,
        label=_('سبب الضرر')
    )
    
    repair_cost = forms.DecimalField(
        decimal_places=2,
        required=False,
        min_value=0,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'step': '0.01',
            'placeholder': _('تكلفة الإصلاح المقدرة')
        }),
        label=_('تكلفة الإصلاح المقدرة')
    )
    
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        # إضافة حقول ديناميكية لعناصر الفحص
        categories = CarInspectionCategory.objects.filter(is_active=True).order_by('display_order')
        
        for category in categories:
            items = CarInspectionItem.objects.filter(
                category=category,
                is_active=True
            ).order_by('display_order')
            
            for item in items:
                field_name = f'item_{item.id}'
                
                # إضافة حقل حالة العنصر
                self.fields[field_name] = forms.ChoiceField(
                    choices=CarInspectionItem.CONDITION_CHOICES,
                    widget=forms.Select(attrs={
                        'class': 'form-select inspection-condition',
                        'data-item-id': item.id,
                        'data-category-id': category.id,
                    }),
                    required=item.is_required,
                    label=item.name
                )
                
                # إضافة حقل ملاحظات لكل عنصر
                self.fields[f'{field_name}_notes'] = forms.CharField(
                    widget=forms.Textarea(attrs={
                        'class': 'form-control',
                        'rows': 2,
                        'placeholder': _('ملاحظات عن هذا العنصر'),
                        'data-item-id': item.id,
                    }),
                    required=False,
                    label=f'{item.name} - ملاحظات'
                )
    
    def save(self):
        """حفظ تقرير حالة السيارة مع كافة التفاصيل"""
        # إنشاء التقرير الأساسي
        report = CarConditionReport(
            reservation=self.cleaned_data.get('reservation'),
            car=self.cleaned_data.get('car'),
            report_type=self.cleaned_data.get('report_type'),
            mileage=self.cleaned_data.get('mileage'),
            date=self.cleaned_data.get('date'),
            fuel_level=self.cleaned_data.get('fuel_level'),
            car_condition=self.cleaned_data.get('car_condition'),
            notes=self.cleaned_data.get('notes'),
            defects=self.cleaned_data.get('defects'),
            defect_cause=self.cleaned_data.get('defect_cause'),
            repair_cost=self.cleaned_data.get('repair_cost') or 0,
            created_by=self.user
        )
        report.save()
        
        # حفظ تفاصيل الفحص
        for field_name, value in self.cleaned_data.items():
            if field_name.startswith('item_') and not field_name.endswith('_notes'):
                item_id = int(field_name.split('_')[1])
                notes_field = f'{field_name}_notes'
                
                inspection_detail = CarInspectionDetail(
                    report=report,
                    inspection_item_id=item_id,
                    condition=value,
                    notes=self.cleaned_data.get(notes_field, '')
                )
                inspection_detail.save()
        
        return report


class SiteSettingsForm(forms.ModelForm):
    """نموذج تحرير إعدادات الموقع"""
    class Meta:
        from .models import SiteSettings
        model = SiteSettings
        exclude = ['created_at', 'updated_at']
        
        widgets = {
            # إعدادات عامة
            'site_name': forms.TextInput(attrs={'class': 'form-control', 'dir': 'auto'}),
            'site_description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'dir': 'auto'}),
            'site_logo': forms.FileInput(attrs={'class': 'form-control', 'accept': 'image/*'}),
            'site_favicon': forms.FileInput(attrs={'class': 'form-control', 'accept': 'image/*'}),
            
            # معلومات الاتصال
            'site_email': forms.EmailInput(attrs={'class': 'form-control', 'dir': 'ltr'}),
            'site_phone': forms.TextInput(attrs={'class': 'form-control', 'dir': 'ltr'}),
            'site_address': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'dir': 'auto'}),
            
            # وسائل التواصل الاجتماعي
            'facebook_url': forms.URLInput(attrs={'class': 'form-control', 'dir': 'ltr'}),
            'twitter_url': forms.URLInput(attrs={'class': 'form-control', 'dir': 'ltr'}),
            'instagram_url': forms.URLInput(attrs={'class': 'form-control', 'dir': 'ltr'}),
            'tiktok_url': forms.URLInput(attrs={'class': 'form-control', 'dir': 'ltr'}),
            'youtube_url': forms.URLInput(attrs={'class': 'form-control', 'dir': 'ltr'}),
            
            # إعدادات API
            'google_maps_api_key': forms.TextInput(attrs={'class': 'form-control', 'dir': 'ltr'}),
            'payment_gateway_api_key': forms.TextInput(attrs={'class': 'form-control', 'dir': 'ltr'}),
            
            # إعدادات الحجز
            'booking_start_time': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
            'booking_end_time': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
            'min_booking_days': forms.NumberInput(attrs={'class': 'form-control', 'min': 1}),
            'max_booking_days': forms.NumberInput(attrs={'class': 'form-control', 'min': 1}),
            
            # إعدادات المظهر
            'primary_color': forms.TextInput(attrs={'class': 'form-control', 'type': 'color', 'style': 'height: 40px;'}),
            'secondary_color': forms.TextInput(attrs={'class': 'form-control', 'type': 'color', 'style': 'height: 40px;'}),
            'enable_dark_mode': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            
            # إعدادات الأمان
            'enable_two_factor_auth': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'booking_confirmation_expiry_hours': forms.NumberInput(attrs={'class': 'form-control', 'min': 1}),
            'session_timeout_minutes': forms.NumberInput(attrs={'class': 'form-control', 'min': 5}),
            
            # إعدادات الحجز
            'enable_deposit': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'deposit_percentage': forms.NumberInput(attrs={'class': 'form-control', 'min': 0, 'max': 100}),
            'enable_automatic_reservation_expiry': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            
            # إعدادات النظام
            'maintenance_mode': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'enable_debug_mode': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'cache_timeout_minutes': forms.NumberInput(attrs={'class': 'form-control', 'min': 1}),
            
            # إعدادات الإشعارات
            'enable_email_notifications': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'enable_sms_notifications': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'admin_notification_email': forms.EmailInput(attrs={'class': 'form-control', 'dir': 'ltr'}),
            
            # ترجمة وتدويل
            'default_language': forms.Select(attrs={'class': 'form-select'}),
            'default_timezone': forms.TextInput(attrs={'class': 'form-control', 'dir': 'ltr'}),
        }