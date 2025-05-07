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
            # استخدام مسار التوجيه الكامل مع الحفاظ على بادئة اللغة
            language_code = request.LANGUAGE_CODE
            return redirect(f'/{language_code}/superadmin/settings/security/')
            
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
                language_code = request.LANGUAGE_CODE
                return redirect(f'/{language_code}/superadmin/settings/security/')

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
            language_code = request.LANGUAGE_CODE
            return redirect(f'/{language_code}/superadmin/settings/security/')
        
        elif action == 'update_two_factor':
            # تحديث إعدادات المصادقة الثنائية
            set_system_setting('two_factor_enabled', 'true' if 'two_factor_enabled' in request.POST else 'false',
                              'boolean', 'security', _('تفعيل المصادقة الثنائية'))
            
            set_system_setting('two_factor_required_for_admins', 'true' if 'two_factor_required_for_admins' in request.POST else 'false',
                              'boolean', 'security', _('المصادقة الثنائية مطلوبة للمسؤولين'))
            
            messages.success(request, _('تم تحديث إعدادات المصادقة الثنائية بنجاح'))
            language_code = request.LANGUAGE_CODE
            return redirect(f'/{language_code}/superadmin/settings/security/')
        
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
        
        language_code = request.LANGUAGE_CODE
        return redirect(f'/{language_code}/superadmin/settings/security/')
    
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
        language_code = request.LANGUAGE_CODE
        return redirect(f'/{language_code}/superadmin/settings/notifications/')
    
    # إعداد السياق
    context = {
        'notification_settings': {s.key: s for s in notification_settings},
        'title': _('إعدادات الإشعارات'),
    }
    
    return render(request, 'superadmin/settings/notifications.html', context)

@login_required
def advanced_permissions(request):
    """إدارة الصلاحيات المتقدمة بواجهة حديثة"""
    if not is_superadmin(request.user):
        messages.error(request, _('ليس لديك صلاحية الوصول إلى إدارة الصلاحيات المتقدمة'))
        return redirect('superadmin_dashboard')
    
    # الحصول على الأدوار والصلاحيات
    roles = Role.objects.all()
    permissions = Permission.objects.all()
    
    # الحصول على إعدادات الأذونات المتقدمة
    advanced_perms = get_system_setting('advanced_permissions', {})    
    
    if request.method == 'POST':
        action = request.POST.get('action')
        
        # إنشاء دور جديد
        if action == 'create_role':
            role_name = request.POST.get('role_name')
            role_description = request.POST.get('role_description')
            role_type = request.POST.get('role_type')
            copy_from_role = request.POST.get('copy_from_role')
            
            # التحقق من تكرار اسم الدور
            if Role.objects.filter(name=role_name).exists():
                messages.error(request, _('الدور بهذا الاسم موجود بالفعل'))
                return redirect('superadmin_advanced_permissions')
            
            # تحديد ما إذا كان الدور للمسؤول الأعلى
            is_superadmin_role = (role_type == 'superadmin')
            
            # إنشاء دور جديد
            new_role = Role.objects.create(
                name=role_name,
                description=role_description,
                is_superadmin_role=is_superadmin_role
            )
            
            # نسخ الصلاحيات من دور موجود
            if copy_from_role:
                try:
                    source_role = Role.objects.get(id=copy_from_role)
                    
                    # نسخ الصلاحيات الأساسية
                    for permission in source_role.permissions.all():
                        new_role.permissions.add(permission)
                    
                    # نسخ الصلاحيات المتقدمة
                    if advanced_perms and copy_from_role in advanced_perms:
                        if not advanced_perms.get(str(new_role.id)):
                            advanced_perms[str(new_role.id)] = {}
                        
                        advanced_perms[str(new_role.id)] = advanced_perms[copy_from_role].copy()
                        
                        # حفظ الصلاحيات المتقدمة المنسوخة
                        set_system_setting('advanced_permissions', advanced_perms, 'json', 'security',
                                         _('الصلاحيات المتقدمة'))
                except Role.DoesNotExist:
                    pass
                
            messages.success(request, _('تم إنشاء الدور الجديد بنجاح'))
            return redirect('superadmin_advanced_permissions')
            
        # تعديل دور موجود
        elif action == 'edit_role':
            role_id = request.POST.get('role_id')
            role_name = request.POST.get('role_name')
            role_description = request.POST.get('role_description')
            is_superadmin_role = request.POST.get('is_superadmin_role') == 'on'
            
            try:
                role = Role.objects.get(id=role_id)
                
                # التحقق من تكرار اسم الدور
                if role.name != role_name and Role.objects.filter(name=role_name).exists():
                    messages.error(request, _('الدور بهذا الاسم موجود بالفعل'))
                    return redirect('superadmin_advanced_permissions')
                
                # تحديث الدور
                role.name = role_name
                role.description = role_description
                role.is_superadmin_role = is_superadmin_role
                role.save()
                
                messages.success(request, _('تم تحديث الدور بنجاح'))
            except Role.DoesNotExist:
                messages.error(request, _('الدور غير موجود'))
                
            return redirect('superadmin_advanced_permissions')
            
        # حذف دور
        elif action == 'delete_role':
            role_id = request.POST.get('role_id')
            
            try:
                role = Role.objects.get(id=role_id)
                
                # التحقق مما إذا كان هناك مستخدمون مرتبطون بهذا الدور
                users_count = role.adminuser_set.count()
                if users_count > 0:
                    messages.error(request, _('لا يمكن حذف الدور لأنه مرتبط بـ {} مستخدم').format(users_count))
                    return redirect('superadmin_advanced_permissions')
                
                # حذف الصلاحيات المتقدمة المرتبطة بالدور
                if advanced_perms and role_id in advanced_perms:
                    del advanced_perms[role_id]
                    set_system_setting('advanced_permissions', advanced_perms, 'json', 'security',
                                     _('الصلاحيات المتقدمة'))
                
                # حذف الدور
                role_name = role.name
                role.delete()
                
                messages.success(request, _('تم حذف الدور {} بنجاح').format(role_name))
            except Role.DoesNotExist:
                messages.error(request, _('الدور غير موجود'))
                
            return redirect('superadmin_advanced_permissions')
        
        # تحديث صلاحيات الحقول
        elif action == 'update_field_permissions':
            role_id = request.POST.get('role_id')
            
            # تهيئة مصفوفة الأذونات المتقدمة إذا لم تكن موجودة
            if not advanced_perms:
                advanced_perms = {}
            
            if role_id not in advanced_perms:
                advanced_perms[role_id] = {}
            
            # إعادة تعيين الصلاحيات الموجودة للدور (لإزالة الصلاحيات غير المحددة)
            for model_name in list(advanced_perms[role_id].keys()):
                advanced_perms[role_id][model_name] = {
                    k: v for k, v in advanced_perms[role_id][model_name].items()
                    if isinstance(v, dict)  # الاحتفاظ فقط بالحقول (التي تكون قاموس)
                }
            
            # معالجة صلاحيات جميع النماذج والحقول
            for key, value in request.POST.items():
                # معالجة صلاحيات العمليات العامة
                if key.startswith('permission_') and not key.startswith('permission_field_'):
                    parts = key.split('_')
                    if len(parts) >= 3:
                        model_name = parts[1]
                        permission_name = parts[2]
                        
                        if model_name not in advanced_perms[role_id]:
                            advanced_perms[role_id][model_name] = {}
                        
                        advanced_perms[role_id][model_name][permission_name] = True
                
                # معالجة صلاحيات الحقول
                elif key.startswith('permission_') and '_field_' in key:
                    parts = key.split('_field_')
                    if len(parts) == 2:
                        model_part = parts[0].replace('permission_', '')
                        field_part = parts[1]
                        
                        field_parts = field_part.split('_')
                        if len(field_parts) >= 2:
                            field_name = '_'.join(field_parts[:-1])
                            permission_type = field_parts[-1]  # read or write
                            
                            if model_part not in advanced_perms[role_id]:
                                advanced_perms[role_id][model_part] = {}
                            
                            if field_name not in advanced_perms[role_id][model_part]:
                                advanced_perms[role_id][model_part][field_name] = {}
                            
                            if isinstance(advanced_perms[role_id][model_part][field_name], dict):
                                advanced_perms[role_id][model_part][field_name][permission_type] = True
                            else:
                                advanced_perms[role_id][model_part][field_name] = {permission_type: True}
            
            # حفظ الأذونات المتقدمة
            set_system_setting('advanced_permissions', advanced_perms, 'json', 'security',
                              _('الصلاحيات المتقدمة'))
            
            messages.success(request, _('تم حفظ الصلاحيات المتقدمة بنجاح'))
        
        return redirect('superadmin_advanced_permissions')
    
    # إعداد السياق
    context = {
        'roles': roles,
        'permissions': permissions,
        'advanced_permissions': advanced_perms,
        'available_models': [
            # وحدات المستخدمين والأدوار
            {
                'name': 'User', 
                'fields': ['username', 'email', 'first_name', 'last_name', 'is_active', 'phone', 'address', 'last_login', 'date_joined'],
                'special_permissions': [
                    {'key': 'reset_password', 'name': _('إعادة تعيين كلمة المرور'), 'type': 'admin'},
                    {'key': 'activate_account', 'name': _('تفعيل/تعطيل الحساب'), 'type': 'admin'},
                    {'key': 'two_factor_auth', 'name': _('إدارة المصادقة الثنائية'), 'type': 'admin'},
                    {'key': 'manage_api_tokens', 'name': _('إدارة رموز API'), 'type': 'admin'},
                    {'key': 'view_activity_logs', 'name': _('عرض سجلات النشاط'), 'type': 'read'}
                ]
            },
            {
                'name': 'Admin', 
                'fields': ['username', 'email', 'first_name', 'last_name', 'is_active', 'role', 'is_superadmin', 'phone', 'last_login'],
                'special_permissions': [
                    {'key': 'reset_password', 'name': _('إعادة تعيين كلمة المرور'), 'type': 'admin'},
                    {'key': 'create_admin', 'name': _('إنشاء مسؤول جديد'), 'type': 'admin'},
                    {'key': 'assign_roles', 'name': _('تعيين الأدوار للمسؤولين'), 'type': 'admin'},
                    {'key': 'deactivate_admin', 'name': _('تعطيل حساب مسؤول'), 'type': 'admin'},
                ]
            },
            {
                'name': 'Role', 
                'fields': ['name', 'description', 'is_superadmin_role', 'created_at', 'updated_at'],
                'special_permissions': [
                    {'key': 'create_role', 'name': _('إنشاء دور جديد'), 'type': 'admin'},
                    {'key': 'edit_role', 'name': _('تعديل دور موجود'), 'type': 'admin'},
                    {'key': 'delete_role', 'name': _('حذف دور'), 'type': 'delete'},
                    {'key': 'assign_permissions', 'name': _('تعيين الصلاحيات'), 'type': 'admin'},
                ]
            },
            {
                'name': 'Permission', 
                'fields': ['name', 'codename', 'description', 'module'],
                'special_permissions': [
                    {'key': 'create_permission', 'name': _('إنشاء صلاحية جديدة'), 'type': 'admin'},
                    {'key': 'edit_permission', 'name': _('تعديل صلاحية موجودة'), 'type': 'admin'},
                ]
            },
            
            # وحدات المحتوى الرئيسية
            {
                'name': 'Customer', 
                'fields': ['phone', 'address', 'id_number', 'driver_license', 'email', 'name', 'nationality', 'dob', 'created_at', 'status'],
                'special_permissions': [
                    {'key': 'view_sensitive', 'name': _('عرض المعلومات الحساسة'), 'type': 'admin'},
                    {'key': 'manage_identity', 'name': _('إدارة وثائق الهوية'), 'type': 'admin'},
                    {'key': 'block_customer', 'name': _('حظر عميل'), 'type': 'admin'},
                    {'key': 'export_customers', 'name': _('تصدير بيانات العملاء'), 'type': 'admin'},
                ]
            },
            {
                'name': 'CustomerGuarantee', 
                'fields': ['customer', 'guarantee_type', 'value', 'document', 'expiry_date', 'status', 'notes', 'created_at'],
                'special_permissions': [
                    {'key': 'verify_guarantee', 'name': _('التحقق من الضمان'), 'type': 'admin'},
                    {'key': 'renew_guarantee', 'name': _('تجديد الضمان'), 'type': 'write'},
                ]
            },
            {
                'name': 'Vehicle', 
                'fields': ['brand', 'model', 'year', 'color', 'daily_rate', 'is_available', 'license_plate', 'maintenance_status', 'mileage', 'features', 'category', 'insurance_expiry'],
                'special_permissions': [
                    {'key': 'maintenance', 'name': _('تسجيل صيانة'), 'type': 'write'},
                    {'key': 'update_pricing', 'name': _('تحديث الأسعار'), 'type': 'admin'},
                    {'key': 'mark_unavailable', 'name': _('تعليم كغير متاح'), 'type': 'write'},
                    {'key': 'manage_images', 'name': _('إدارة صور المركبة'), 'type': 'write'},
                    {'key': 'manage_documents', 'name': _('إدارة وثائق المركبة'), 'type': 'admin'},
                ]
            },
            {
                'name': 'VehicleCategory', 
                'fields': ['name', 'description', 'base_price', 'image', 'created_at'],
                'special_permissions': [
                    {'key': 'create_category', 'name': _('إنشاء فئة جديدة'), 'type': 'admin'},
                    {'key': 'manage_inventory', 'name': _('إدارة المخزون'), 'type': 'admin'},
                ]
            },
            {
                'name': 'VehicleFeature', 
                'fields': ['name', 'icon', 'description', 'category', 'is_highlighted'],
                'special_permissions': [
                    {'key': 'create_feature', 'name': _('إنشاء ميزة جديدة'), 'type': 'write'},
                ]
            },
            {
                'name': 'VehicleMaintenance', 
                'fields': ['vehicle', 'maintenance_type', 'description', 'cost', 'date', 'mileage', 'notes', 'status'],
                'special_permissions': [
                    {'key': 'schedule_maintenance', 'name': _('جدولة صيانة'), 'type': 'write'},
                    {'key': 'approve_costs', 'name': _('الموافقة على التكاليف'), 'type': 'admin'},
                ]
            },
            
            # وحدات الحجوزات والمدفوعات
            {
                'name': 'Reservation', 
                'fields': ['start_date', 'end_date', 'total_cost', 'status', 'notes', 'customer', 'vehicle', 'payment_status', 'pickup_location', 'return_location', 'additional_services', 'discount'],
                'special_permissions': [
                    {'key': 'cancel', 'name': _('إلغاء الحجز'), 'type': 'delete'},
                    {'key': 'extend', 'name': _('تمديد الحجز'), 'type': 'write'},
                    {'key': 'discount', 'name': _('تطبيق خصم'), 'type': 'admin'},
                    {'key': 'expedite', 'name': _('تسريع الموافقة'), 'type': 'admin'},
                    {'key': 'override_conflict', 'name': _('تجاوز تعارض الحجز'), 'type': 'admin'},
                    {'key': 'manage_addons', 'name': _('إدارة الإضافات'), 'type': 'write'},
                ]
            },
            {
                'name': 'Payment', 
                'fields': ['amount', 'method', 'status', 'transaction_id', 'customer', 'reservation', 'date', 'notes', 'payment_gateway', 'currency', 'fees'],
                'special_permissions': [
                    {'key': 'refund', 'name': _('إجراء استرداد'), 'type': 'admin'},
                    {'key': 'manual_payment', 'name': _('تسجيل دفعة يدوية'), 'type': 'write'},
                    {'key': 'approve_payment', 'name': _('الموافقة على الدفع'), 'type': 'admin'},
                    {'key': 'view_financial', 'name': _('عرض التقارير المالية'), 'type': 'admin'},
                    {'key': 'manage_bank_transfers', 'name': _('إدارة التحويلات البنكية'), 'type': 'admin'},
                ]
            },
            {
                'name': 'Invoice', 
                'fields': ['number', 'reservation', 'customer', 'total', 'tax', 'discount', 'issue_date', 'due_date', 'status', 'notes'],
                'special_permissions': [
                    {'key': 'generate_invoice', 'name': _('إنشاء فاتورة'), 'type': 'write'},
                    {'key': 'send_reminders', 'name': _('إرسال تذكيرات'), 'type': 'write'},
                    {'key': 'mark_as_paid', 'name': _('تعليم كمدفوع'), 'type': 'admin'},
                ]
            },
            {
                'name': 'Discount', 
                'fields': ['code', 'amount', 'type', 'start_date', 'end_date', 'max_uses', 'current_uses', 'applicable_categories', 'min_days', 'status'],
                'special_permissions': [
                    {'key': 'create_discount', 'name': _('إنشاء خصم'), 'type': 'admin'},
                    {'key': 'apply_manual_discount', 'name': _('تطبيق خصم يدوي'), 'type': 'admin'},
                ]
            },
            {
                'name': 'AdditionalService', 
                'fields': ['name', 'price', 'description', 'is_active', 'icon', 'category'],
                'special_permissions': [
                    {'key': 'create_service', 'name': _('إنشاء خدمة'), 'type': 'admin'},
                    {'key': 'update_pricing', 'name': _('تحديث الأسعار'), 'type': 'admin'},
                ]
            },
            
            # فحص المركبات والتسليم والاستلام
            {
                'name': 'VehicleInspection', 
                'fields': ['reservation', 'vehicle', 'inspection_type', 'inspection_date', 'inspector', 'status', 'notes', 'images', 'damage_reported'],
                'special_permissions': [
                    {'key': 'conduct_inspection', 'name': _('إجراء فحص'), 'type': 'write'},
                    {'key': 'approve_inspection', 'name': _('الموافقة على الفحص'), 'type': 'admin'},
                    {'key': 'report_damage', 'name': _('الإبلاغ عن ضرر'), 'type': 'write'},
                ]
            },
            {
                'name': 'InspectionItem', 
                'fields': ['inspection', 'item_name', 'category', 'status', 'notes', 'images'],
                'special_permissions': [
                    {'key': 'customize_checklist', 'name': _('تخصيص قائمة التحقق'), 'type': 'admin'},
                ]
            },
            {
                'name': 'DamageReport', 
                'fields': ['inspection', 'description', 'severity', 'repair_cost', 'responsible_party', 'status', 'resolution_date', 'images'],
                'special_permissions': [
                    {'key': 'assess_damages', 'name': _('تقييم الأضرار'), 'type': 'admin'},
                    {'key': 'approve_repair', 'name': _('الموافقة على الإصلاح'), 'type': 'admin'},
                    {'key': 'bill_customer', 'name': _('محاسبة العميل'), 'type': 'admin'},
                ]
            },
            
            # إدارة الأرشيف والوثائق
            {
                'name': 'ArchiveFolder', 
                'fields': ['name', 'parent', 'description', 'created_at', 'created_by', 'path', 'is_system_folder'],
                'special_permissions': [
                    {'key': 'create_folder', 'name': _('إنشاء مجلد'), 'type': 'write'},
                    {'key': 'delete_folder', 'name': _('حذف مجلد'), 'type': 'delete'},
                    {'key': 'move_folder', 'name': _('نقل مجلد'), 'type': 'write'},
                    {'key': 'manage_system_folders', 'name': _('إدارة المجلدات النظامية'), 'type': 'admin'},
                ]
            },
            {
                'name': 'Document', 
                'fields': ['name', 'file', 'folder', 'description', 'created_at', 'created_by', 'size', 'mime_type', 'is_auto_generated'],
                'special_permissions': [
                    {'key': 'download', 'name': _('تنزيل الملفات'), 'type': 'read'},
                    {'key': 'upload', 'name': _('رفع ملفات'), 'type': 'write'},
                    {'key': 'delete_document', 'name': _('حذف مستند'), 'type': 'delete'},
                    {'key': 'move_document', 'name': _('نقل مستند'), 'type': 'write'},
                    {'key': 'generate_document', 'name': _('إنشاء مستند تلقائي'), 'type': 'admin'},
                ]
            },
            {
                'name': 'DocumentTemplate', 
                'fields': ['name', 'type', 'content', 'variables', 'created_at', 'updated_at', 'is_active'],
                'special_permissions': [
                    {'key': 'create_template', 'name': _('إنشاء قالب'), 'type': 'admin'},
                    {'key': 'edit_template', 'name': _('تعديل قالب'), 'type': 'admin'},
                ]
            },
            
            # إدارة النظام والتقارير
            {
                'name': 'SystemSetting', 
                'fields': ['key', 'value', 'value_type', 'group', 'description', 'is_public', 'created_at', 'updated_at'],
                'special_permissions': [
                    {'key': 'edit_settings', 'name': _('تعديل الإعدادات'), 'type': 'admin'},
                    {'key': 'manage_security', 'name': _('إدارة إعدادات الأمان'), 'type': 'admin'},
                    {'key': 'manage_backups', 'name': _('إدارة النسخ الاحتياطية'), 'type': 'admin'},
                ]
            },
            {
                'name': 'ScheduledTask', 
                'fields': ['name', 'task_function', 'cron_expression', 'args', 'kwargs', 'is_active', 'last_run', 'next_run', 'description'],
                'special_permissions': [
                    {'key': 'create_task', 'name': _('إنشاء مهمة مجدولة'), 'type': 'admin'},
                    {'key': 'run_task', 'name': _('تشغيل مهمة'), 'type': 'admin'},
                    {'key': 'pause_task', 'name': _('إيقاف مهمة مؤقتًا'), 'type': 'admin'},
                ]
            },
            {
                'name': 'SystemLog', 
                'fields': ['log_type', 'severity', 'timestamp', 'source', 'message', 'details', 'user'],
                'special_permissions': [
                    {'key': 'view_logs', 'name': _('عرض السجلات'), 'type': 'admin'},
                    {'key': 'clear_logs', 'name': _('مسح السجلات'), 'type': 'admin'},
                    {'key': 'export_logs', 'name': _('تصدير السجلات'), 'type': 'admin'},
                ]
            },
            {
                'name': 'Notification', 
                'fields': ['user', 'title', 'message', 'created_at', 'read_at', 'type', 'link', 'source'],
                'special_permissions': [
                    {'key': 'send_notification', 'name': _('إرسال إشعار'), 'type': 'admin'},
                    {'key': 'manage_templates', 'name': _('إدارة قوالب الإشعارات'), 'type': 'admin'},
                ]
            },
            {
                'name': 'Report', 
                'fields': ['title', 'type', 'date_range', 'created_by', 'created_at', 'description', 'is_scheduled', 'schedule', 'parameters', 'output_format'],
                'special_permissions': [
                    {'key': 'generate', 'name': _('إنشاء تقرير'), 'type': 'write'},
                    {'key': 'export', 'name': _('تصدير تقرير'), 'type': 'read'},
                    {'key': 'schedule_report', 'name': _('جدولة تقرير'), 'type': 'admin'},
                    {'key': 'access_financial', 'name': _('الوصول للتقارير المالية'), 'type': 'admin'},
                ]
            },
            
            # أجزاء موقع الويب
            {
                'name': 'WebsiteContent', 
                'fields': ['key', 'title', 'content', 'language', 'page', 'updated_at', 'updated_by'],
                'special_permissions': [
                    {'key': 'edit_content', 'name': _('تعديل المحتوى'), 'type': 'admin'},
                    {'key': 'publish', 'name': _('نشر التغييرات'), 'type': 'admin'},
                ]
            },
            {
                'name': 'Review', 
                'fields': ['customer', 'rating', 'comment', 'status', 'created_at', 'service_type', 'reservation'],
                'special_permissions': [
                    {'key': 'approve_review', 'name': _('الموافقة على المراجعة'), 'type': 'admin'},
                    {'key': 'feature_review', 'name': _('تمييز المراجعة'), 'type': 'admin'},
                    {'key': 'respond', 'name': _('الرد على المراجعة'), 'type': 'write'},
                ]
            },
            {
                'name': 'ContactMessage', 
                'fields': ['name', 'email', 'phone', 'message', 'created_at', 'status', 'assigned_to', 'response'],
                'special_permissions': [
                    {'key': 'respond_message', 'name': _('الرد على الرسالة'), 'type': 'write'},
                    {'key': 'assign_message', 'name': _('تعيين الرسالة'), 'type': 'admin'},
                ]
            },
            
            # أقسام لوحة التحكم
            {
                'name': 'AdminDashboard', 
                'special_permissions': [
                    {'key': 'view_dashboard', 'name': _('عرض لوحة التحكم'), 'type': 'read'},
                    {'key': 'customize_widgets', 'name': _('تخصيص الويدجات'), 'type': 'admin'},
                ]
            },
            {
                'name': 'SuperAdminDashboard', 
                'special_permissions': [
                    {'key': 'view_dashboard', 'name': _('عرض لوحة التحكم'), 'type': 'admin'},
                    {'key': 'system_overview', 'name': _('نظرة عامة على النظام'), 'type': 'admin'},
                    {'key': 'performance_metrics', 'name': _('قياسات الأداء'), 'type': 'admin'},
                ]
            },
            {
                'name': 'Analytics', 
                'special_permissions': [
                    {'key': 'view_basic_stats', 'name': _('عرض الإحصائيات الأساسية'), 'type': 'read'},
                    {'key': 'view_detailed_stats', 'name': _('عرض الإحصائيات المفصلة'), 'type': 'admin'},
                    {'key': 'generate_custom_reports', 'name': _('إنشاء تقارير مخصصة'), 'type': 'admin'},
                    {'key': 'export_analytics', 'name': _('تصدير التحليلات'), 'type': 'admin'},
                ]
            },
            {
                'name': 'Settings', 
                'special_permissions': [
                    {'key': 'view_settings', 'name': _('عرض الإعدادات'), 'type': 'read'},
                    {'key': 'edit_general_settings', 'name': _('تعديل الإعدادات العامة'), 'type': 'admin'},
                    {'key': 'manage_security_settings', 'name': _('إدارة إعدادات الأمان'), 'type': 'admin'},
                    {'key': 'manage_notifications', 'name': _('إدارة إعدادات الإشعارات'), 'type': 'admin'},
                    {'key': 'manage_api_settings', 'name': _('إدارة إعدادات API'), 'type': 'admin'},
                ]
            },
        ],
        'title': _('إدارة الصلاحيات المتقدمة'),
    }
    
    return render(request, 'superadmin/settings/advanced_permissions_modern.html', context)
