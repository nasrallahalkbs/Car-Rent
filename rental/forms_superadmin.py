from django import forms
from django.utils.translation import gettext_lazy as _
from .models import User
from .models_superadmin import Permission, Role, AdminUser, ReviewManagement

class PermissionForm(forms.ModelForm):
    """نموذج الصلاحيات"""
    class Meta:
        model = Permission
        fields = ['name', 'codename', 'description']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': _('اسم الصلاحية')}),
            'codename': forms.TextInput(attrs={'class': 'form-control', 'placeholder': _('رمز الصلاحية')}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': _('وصف الصلاحية')}),
        }

class RoleForm(forms.ModelForm):
    """نموذج الأدوار"""
    permissions = forms.ModelMultipleChoiceField(
        queryset=Permission.objects.all(),
        widget=forms.CheckboxSelectMultiple(attrs={'class': 'permission-checkbox-list'}),
        required=False,
        label=_('الصلاحيات')
    )
    
    class Meta:
        model = Role
        fields = ['name', 'permissions', 'description', 'is_active']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': _('اسم الدور')}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': _('وصف الدور')}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

class AdminUserForm(forms.ModelForm):
    """نموذج المسؤولين"""
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': _('كلمة المرور')}),
        required=False,
        label=_('كلمة المرور')
    )
    confirm_password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': _('تأكيد كلمة المرور')}),
        required=False,
        label=_('تأكيد كلمة المرور')
    )
    
    class Meta:
        model = AdminUser
        fields = ['user', 'role', 'is_superadmin', 'notes']
        widgets = {
            'user': forms.Select(attrs={'class': 'form-select'}),
            'role': forms.Select(attrs={'class': 'form-select'}),
            'is_superadmin': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': _('ملاحظات')}),
        }
    
    def __init__(self, *args, **kwargs):
        self.new_user = kwargs.pop('new_user', False)
        super(AdminUserForm, self).__init__(*args, **kwargs)
        
        if not self.new_user and self.instance.pk:
            # إذا كان تعديل لمسؤول موجود
            self.fields['password'].required = False
            self.fields['confirm_password'].required = False
            self.fields['user'].widget.attrs['readonly'] = True
        else:
            # إذا كان إنشاء مسؤول جديد
            self.fields['password'].required = True
            self.fields['confirm_password'].required = True
    
    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')
        
        if password and confirm_password and password != confirm_password:
            raise forms.ValidationError(_('كلمات المرور غير متطابقة'))
        
        return cleaned_data

class ReviewManagementForm(forms.ModelForm):
    """نموذج إدارة التقييمات"""
    class Meta:
        model = ReviewManagement
        fields = ['status', 'admin_notes']
        widgets = {
            'status': forms.Select(attrs={'class': 'form-select'}),
            'admin_notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': _('ملاحظات المسؤول')}),
        }

class SuperAdminLoginForm(forms.Form):
    """نموذج تسجيل دخول المسؤول الأعلى"""
    username = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': _('اسم المستخدم')}),
        label=_('اسم المستخدم'),
        max_length=150
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': _('كلمة المرور')}),
        label=_('كلمة المرور')
    )
    remember_me = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        label=_('تذكرني')
    )
