from django import forms
from django.core.validators import MinValueValidator
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.utils import timezone
from datetime import date

from .models import User, Car, Review

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
                 'image_url', 'image', 'is_available']
        widgets = {
            'year': forms.NumberInput(attrs={'min': 2000, 'max': date.today().year + 1}),
            'features': forms.TextInput(attrs={'placeholder': 'مثل: GPS، بلوتوث، كاميرا خلفية'}),
            'image_url': forms.URLInput(attrs={'placeholder': 'رابط الصورة (اختياري إذا قمت بتحميل ملف)'}),
            'image': forms.FileInput(attrs={'class': 'form-control', 'accept': 'image/*'}),
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