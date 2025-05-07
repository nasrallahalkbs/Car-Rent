import json
import pyotp
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.utils.translation import gettext as _
from django.forms import modelform_factory
from django.conf import settings

from .models_system import SystemSetting
from .models_superadmin import AdminUser, Role, Permission
from .models import User

# الدالة المساعدة للتحقق من صلاحيات المسؤول الأعلى
def is_superadmin(user):
    try:
        admin_user = AdminUser.objects.get(user=user)
        return admin_user.is_superadmin
    except AdminUser.DoesNotExist:
        return False

# دالة للحصول على قيمة إعداد النظام
def get_system_setting(key, default=None):
    try:
        setting = SystemSetting.objects.get(key=key)
        
        # تحويل القيمة حسب نوعها
        if setting.value_type == 'integer':
            return int(setting.value or 0)
        elif setting.value_type == 'float':
            return float(setting.value or 0.0)
        elif setting.value_type == 'boolean':
            return setting.value.lower() in ('true', '1', 'yes', 'on')
        elif setting.value_type == 'json':
            return json.loads(setting.value or '{}')
        elif setting.value_type == 'list':
            return json.loads(setting.value or '[]')
        else:  # string
            return setting.value
    except (SystemSetting.DoesNotExist, ValueError, json.JSONDecodeError):
        return default

# دالة لتعيين قيمة إعداد النظام
def set_system_setting(key, value, value_type='string', group='general', description=None, is_public=False):
    # تحويل القيمة إلى نص حسب نوعها
    if value_type == 'json' or value_type == 'list':
        if isinstance(value, (dict, list)):
            string_value = json.dumps(value)
        else:
            string_value = value  # افترض أنه بالفعل سلسلة JSON
    elif value_type in ('integer', 'float', 'boolean'):
        string_value = str(value)
    else:  # string
        string_value = value
    
    # إنشاء أو تحديث الإعداد
    setting, created = SystemSetting.objects.update_or_create(
        key=key,
        defaults={
            'value': string_value,
            'value_type': value_type,
            'group': group,
            'description': description,
            'is_public': is_public
        }
    )
    
    return setting

@login_required
def system_settings(request):
    """صفحة إعدادات النظام الرئيسية"""
    if not is_superadmin(request.user):
        messages.error(request, _('ليس لديك صلاحية الوصول إلى إعدادات النظام'))
        return redirect('superadmin_dashboard')
    
    # الحصول على قائمة الإعدادات مرتبة حسب المجموعة
    all_settings = SystemSetting.objects.all().order_by('group', 'key')
    
    # تجميع الإعدادات حسب المجموعة
    grouped_settings = {}
    for setting in all_settings:
        if setting.group not in grouped_settings:
            grouped_settings[setting.group] = []
        grouped_settings[setting.group].append(setting)
    
    if request.method == 'POST':
        # تحديث الإعدادات المقدمة
        for key, value in request.POST.items():
            if key.startswith('setting_'):
                setting_key = key[8:]  # إزالة البادئة 'setting_'
                try:
                    setting = SystemSetting.objects.get(key=setting_key)
                    
                    # تحويل القيمة حسب نوعها
                    if setting.value_type == 'boolean':
                        # مربعات الاختيار ترسل قيمة فقط إذا كانت مختارة
                        setting.value = 'true'
                    else:
                        setting.value = value
                    
                    setting.save()
                except SystemSetting.DoesNotExist:
                    pass  # تجاهل الإعدادات غير الموجودة
        
        # معالجة خاصة للإعدادات المنطقية غير المرسلة
        for setting in all_settings:
            if setting.value_type == 'boolean':
                checkbox_name = f'setting_{setting.key}'
                if checkbox_name not in request.POST:
                    setting.value = 'false'
                    setting.save()
        
        messages.success(request, _('تم حفظ الإعدادات بنجاح'))
        return redirect('superadmin_settings')
    
    # إعداد السياق
    context = {
        'grouped_settings': grouped_settings,
        'setting_groups': dict(SystemSetting.GROUP_CHOICES),
        'title': _('إعدادات النظام'),
    }
    
    return render(request, 'superadmin/settings/index.html', context)

@login_required
def security_settings(request):
    """إعدادات الأمان"""
    if not is_superadmin(request.user):
        messages.error(request, _('ليس لديك صلاحية الوصول إلى إعدادات الأمان'))
        return redirect('superadmin_dashboard')
    
    # استيراد وحدة الأمان
    from .security import get_system_setting, set_system_setting, get_security_statistics, init_security_tables
    
    # التأكد من تهيئة جداول وإعدادات الأمان
    init_security_tables()
    
    # الحصول على إعدادات الأمان الحالية
    security_settings = SystemSetting.objects.filter(group='security').order_by('key')
    
    # إعدادات المصادقة الثنائية
    two_factor_enabled = get_system_setting('two_factor_enabled', False)
    two_factor_required = get_system_setting('two_factor_required_for_admins', False)
    
    # إحصائيات الأمان
    security_stats = get_security_statistics()
    
    if request.method == 'POST':
        action = request.POST.get('action')
        print(f"DEBUG POST: Received action = {action}")
        print(f"DEBUG POST: POST data = {dict(request.POST)}")
        
        if action == 'update_session_timeout':
            # معالجة تحديث وقت انتهاء الجلسة فقط
            session_timeout_minutes = request.POST.get('session_timeout_minutes', '60')
            print(f"DEBUG POST: Processing session timeout update: {session_timeout_minutes}")
            
            try:
                session_timeout_minutes = int(session_timeout_minutes)
                # التحقق من صحة القيمة
                if session_timeout_minutes < 15 or session_timeout_minutes > 1440:
                    session_timeout_minutes = 60  # القيمة الافتراضية
            except ValueError:
                messages.error(request, _('الرجاء إدخال قيمة صحيحة لوقت انتهاء الجلسة'))
                return redirect('superadmin_security_settings')
            
            # حفظ الإعداد
            set_system_setting('session_timeout_minutes', session_timeout_minutes,
                             'integer', 'security', _('مدة انتهاء جلسة العمل بالدقائق'))
            
            messages.success(request, _('تم تحديث وقت انتهاء الجلسة بنجاح'))
            return redirect('superadmin_security_settings')
            
        elif action == 'update_security_settings':
            # طباعة تشخيصية لبيانات الفورم
            print("DEBUG POST: Processing security settings update")
            
            # تحديث إعدادات الأمان العامة
            set_system_setting('password_min_length', request.POST.get('password_min_length', '8'),
                              'integer', 'security', _('الحد الأدنى لطول كلمة المرور'))
            
            set_system_setting('password_requires_uppercase', 'true' if 'password_requires_uppercase' in request.POST else 'false',
                              'boolean', 'security', _('كلمة المرور تتطلب أحرف كبيرة'))
            
            set_system_setting('password_requires_numbers', 'true' if 'password_requires_numbers' in request.POST else 'false',
                              'boolean', 'security', _('كلمة المرور تتطلب أرقام'))
            
            set_system_setting('password_requires_special', 'true' if 'password_requires_special' in request.POST else 'false',
                              'boolean', 'security', _('كلمة المرور تتطلب رموز خاصة'))
            
            set_system_setting('password_expiry_days', request.POST.get('password_expiry_days', '0'),
                              'integer', 'security', _('فترة صلاحية كلمة المرور بالأيام (0 = لا تنتهي)'))
                              
            set_system_setting('max_old_passwords', request.POST.get('max_old_passwords', '5'),
                              'integer', 'security', _('عدد كلمات المرور السابقة المحتفظ بها'))
            
            # المعالجة الصريحة لإعدادات قفل الحساب
            account_lockout_attempts = request.POST.get('account_lockout_attempts', '5')
            account_lockout_minutes = request.POST.get('account_lockout_minutes', '30')
            
            print(f"DEBUG POST: account_lockout_attempts = {account_lockout_attempts}")
            print(f"DEBUG POST: account_lockout_minutes = {account_lockout_minutes}")
            
            # التحقق من صحة القيم وتحويلها إلى أرقام صحيحة
            try:
                account_lockout_attempts = int(account_lockout_attempts)
                account_lockout_minutes = int(account_lockout_minutes)
            except ValueError:
                messages.error(request, _('الرجاء إدخال قيم صحيحة للأرقام'))
                return redirect('superadmin_security_settings')

            # حفظ الإعدادات
            set_system_setting('account_lockout_attempts', account_lockout_attempts,
                              'integer', 'security', _('عدد محاولات تسجيل الدخول الفاشلة قبل قفل الحساب'))
            
            set_system_setting('account_lockout_minutes', account_lockout_minutes,
                              'integer', 'security', _('مدة قفل الحساب بالدقائق'))
            
            # طباعة القيم للتأكد من أنها تم حفظها بشكل صحيح
            print(f"DEBUG: account_lockout_attempts = {request.POST.get('account_lockout_attempts')}")
            print(f"DEBUG: account_lockout_minutes = {request.POST.get('account_lockout_minutes')}")
            
            # تحقق من قيم الإعدادات بعد الحفظ
            from .security import get_system_setting
            print(f"DEBUG AFTER SAVE: account_lockout_attempts = {get_system_setting('account_lockout_attempts')}")
            print(f"DEBUG AFTER SAVE: account_lockout_minutes = {get_system_setting('account_lockout_minutes')}")
            
            messages.success(request, _('تم حفظ إعدادات الأمان بنجاح'))
        
        elif action == 'update_two_factor':
            # تحديث إعدادات المصادقة الثنائية
            set_system_setting('two_factor_enabled', 'true' if 'two_factor_enabled' in request.POST else 'false',
                              'boolean', 'security', _('تفعيل المصادقة الثنائية'))
            
            set_system_setting('two_factor_required_for_admins', 'true' if 'two_factor_required_for_admins' in request.POST else 'false',
                              'boolean', 'security', _('المصادقة الثنائية مطلوبة للمسؤولين'))
            
            messages.success(request, _('تم تحديث إعدادات المصادقة الثنائية بنجاح'))
        
        elif action == 'unlock_account':
            # فتح قفل حساب مستخدم
            from .security import unlock_account
            username = request.POST.get('username')
            
            if username:
                if unlock_account(username):
                    messages.success(request, _(f'تم فتح قفل حساب المستخدم {username} بنجاح'))
                else:
                    messages.error(request, _(f'فشل في فتح قفل حساب المستخدم {username}'))
            else:
                messages.error(request, _('لم يتم تحديد اسم المستخدم'))
        
        return redirect('superadmin_security_settings')
    
    # طباعة تشخيصية للإعدادات
    print(f"DEBUG CONTEXT: Found {security_settings.count()} security settings")
    security_settings_dict = {s.key: s for s in security_settings}
    print(f"DEBUG CONTEXT: Dictionary keys = {list(security_settings_dict.keys())}")
    print(f"DEBUG CONTEXT: account_lockout_attempts in dictionary = {'account_lockout_attempts' in security_settings_dict}")
    
    if 'account_lockout_attempts' in security_settings_dict:
        print(f"DEBUG CONTEXT: account_lockout_attempts value = {security_settings_dict['account_lockout_attempts'].value}")
    else:
        print("DEBUG CONTEXT: account_lockout_attempts not found in dictionary")
    
    # تأكد من استخدام القيم الافتراضية إذا لم تكن موجودة
    if 'account_lockout_attempts' not in security_settings_dict:
        # محاولة تهيئة الإعدادات
        print("DEBUG CONTEXT: Initializing security settings")
        init_security_tables()
        # إعادة الحصول على الإعدادات
        security_settings = SystemSetting.objects.filter(group='security').order_by('key')
        security_settings_dict = {s.key: s for s in security_settings}
        
        print("DEBUG CONTEXT: After initialization:")
        print(f"DEBUG CONTEXT: Found {security_settings.count()} security settings")
        for s in security_settings:
            print(f"DEBUG CONTEXT: {s.key} = {s.value}")
    
    # إعداد السياق
    context = {
        'security_settings': security_settings_dict,
        'two_factor_enabled': two_factor_enabled,
        'two_factor_required': two_factor_required,
        'security_stats': security_stats,
        'title': _('إعدادات الأمان'),
    }
    
    return render(request, 'superadmin/settings/security.html', context)

@login_required
def notification_settings(request):
    """إعدادات الإشعارات"""
    if not is_superadmin(request.user):
        messages.error(request, _('ليس لديك صلاحية الوصول إلى إعدادات الإشعارات'))
        return redirect('superadmin_dashboard')
    
    # الحصول على إعدادات الإشعارات الحالية
    notification_settings = SystemSetting.objects.filter(group='notifications').order_by('key')
    
    if request.method == 'POST':
        # تحديث إعدادات الإشعارات
        set_system_setting('notifications_enabled', 'true' if 'notifications_enabled' in request.POST else 'false',
                          'boolean', 'notifications', _('تفعيل الإشعارات'))
        
        set_system_setting('email_notifications_enabled', 'true' if 'email_notifications_enabled' in request.POST else 'false',
                          'boolean', 'notifications', _('تفعيل إشعارات البريد الإلكتروني'))
        
        set_system_setting('push_notifications_enabled', 'true' if 'push_notifications_enabled' in request.POST else 'false',
                          'boolean', 'notifications', _('تفعيل الإشعارات الفورية'))
        
        set_system_setting('notify_on_new_reservation', 'true' if 'notify_on_new_reservation' in request.POST else 'false',
                          'boolean', 'notifications', _('إشعار عند حجز جديد'))
        
        set_system_setting('notify_on_payment', 'true' if 'notify_on_payment' in request.POST else 'false',
                          'boolean', 'notifications', _('إشعار عند الدفع'))
        
        set_system_setting('notify_on_review', 'true' if 'notify_on_review' in request.POST else 'false',
                          'boolean', 'notifications', _('إشعار عند تقييم جديد'))
        
        set_system_setting('notify_on_error', 'true' if 'notify_on_error' in request.POST else 'false',
                          'boolean', 'notifications', _('إشعار عند حدوث خطأ'))
        
        set_system_setting('admin_email_recipients', request.POST.get('admin_email_recipients', ''),
                          'string', 'notifications', _('عناوين بريد المسؤولين للإشعارات (مفصولة بفواصل)'))
        
        messages.success(request, _('تم حفظ إعدادات الإشعارات بنجاح'))
        return redirect('superadmin_notification_settings')
    
    # إعداد السياق
    context = {
        'notification_settings': {s.key: s for s in notification_settings},
        'title': _('إعدادات الإشعارات'),
    }
    
    return render(request, 'superadmin/settings/notifications.html', context)

@login_required
def advanced_permissions(request):
    """إدارة الأذونات المتقدمة على مستوى الحقول"""
    if not is_superadmin(request.user):
        messages.error(request, _('ليس لديك صلاحية الوصول إلى إدارة الأذونات المتقدمة'))
        return redirect('superadmin_dashboard')
    
    # الحصول على الأدوار والصلاحيات
    roles = Role.objects.all()
    permissions = Permission.objects.all()
    
    # الحصول على إعدادات الأذونات المتقدمة
    advanced_perms = get_system_setting('advanced_permissions', {})    
    
    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'update_field_permissions':
            role_id = request.POST.get('role_id')
            model_name = request.POST.get('model_name')
            field_name = request.POST.get('field_name')
            
            # تهيئة مصفوفة الأذونات المتقدمة إذا لم تكن موجودة
            if not advanced_perms:
                advanced_perms = {}
            
            if role_id not in advanced_perms:
                advanced_perms[role_id] = {}
            
            if model_name not in advanced_perms[role_id]:
                advanced_perms[role_id][model_name] = {}
            
            # تعيين إذن الحقل
            field_perms = {
                'read': 'read_' + field_name in request.POST,
                'write': 'write_' + field_name in request.POST
            }
            
            advanced_perms[role_id][model_name][field_name] = field_perms
            
            # حفظ الأذونات المتقدمة
            set_system_setting('advanced_permissions', advanced_perms, 'json', 'security',
                              _('الأذونات المتقدمة على مستوى الحقول'))
            
            messages.success(request, _('تم حفظ الأذونات المتقدمة بنجاح'))
        
        return redirect('superadmin_advanced_permissions')
    
    # إعداد السياق
    context = {
        'roles': roles,
        'permissions': permissions,
        'advanced_permissions': advanced_perms,
        'available_models': [
            {'name': 'User', 'fields': ['username', 'email', 'first_name', 'last_name', 'is_active']},
            {'name': 'Customer', 'fields': ['phone', 'address', 'id_number', 'driver_license']},
            {'name': 'Reservation', 'fields': ['start_date', 'end_date', 'total_cost', 'status', 'notes']},
            {'name': 'Vehicle', 'fields': ['brand', 'model', 'year', 'color', 'daily_rate', 'is_available']},
            {'name': 'Payment', 'fields': ['amount', 'method', 'status', 'transaction_id']},
        ],
        'title': _('الأذونات المتقدمة'),
    }
    
    return render(request, 'superadmin/settings/advanced_permissions.html', context)
