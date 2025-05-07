from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout, get_user_model
from django.contrib.auth.decorators import login_required
from django.utils.translation import gettext_lazy as _
from django.urls import reverse
from django.db.models import Q, Count
from django.http import HttpResponse, JsonResponse, FileResponse
from django.utils import timezone
from functools import wraps
from django.db import transaction
from django.contrib.auth.hashers import make_password

from .models import User, Review
from .models_superadmin import Permission, Role, AdminUser, AdminActivity, ReviewManagement
from .models_system import SystemBackup, ScheduledJob, SystemSetting, SystemIssue, SystemNotification
from .forms_superadmin import PermissionForm, RoleForm, AdminUserForm, ReviewManagementForm, SuperAdminLoginForm
from .security_models import UserSecurity, LoginAttempt
from .security import setup_2fa_for_user, generate_qr_code_image, unlock_account as security_unlock_account

# دوال التحليلات
from .analytics_superadmin import *

# دوال تصدير التقارير
from .superadmin_export_views import export_pdf_report, export_excel_report

# دوال النسخ الاحتياطي والاستعادة
from .superadmin_backup_views import backup_system, create_backup, restore_backup, download_backup, delete_backup

# دوال جدولة المهام
from .superadmin_scheduler_views import scheduler_dashboard, add_scheduled_job, edit_scheduled_job, delete_scheduled_job, toggle_scheduled_job

# دوال إعدادات النظام
from .superadmin_settings_views import system_settings, security_settings, notification_settings, advanced_permissions

# دوال تشخيص وإصلاح النظام
from .superadmin_diagnostics_views import system_diagnostics, run_diagnostic, fix_system_issue

# استيراد وظائف أمان إضافية
from .security import (
    disable_2fa_for_user, 
    enable_2fa_for_user, 
    reset_failed_login_attempts, 
    generate_backup_codes,
    verify_2fa_token,
    setup_2fa_for_user,
    generate_qr_code_image,
    unlock_account as security_unlock_account
)

def get_client_ip(request):
    """Get the client IP address"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip

def log_admin_activity(admin_user, action, details, request):
    """Log admin activity"""
    ip_address = get_client_ip(request)
    AdminActivity.objects.create(
        admin=admin_user,
        action=action,
        details=details,
        ip_address=ip_address
    )

def superadmin_required(function):
    """Decorator to require superadmin access"""
    @wraps(function)
    def wrapper(request, *args, **kwargs):
        # التحقق من تسجيل الدخول
        if not request.user.is_authenticated:
            messages.error(request, _("يجب تسجيل الدخول للوصول إلى لوحة تحكم المسؤول الأعلى"))
            return redirect('superadmin_login')
        
        # التحقق من وجود بروفايل مسؤول
        try:
            admin_profile = request.user.admin_profile
        except:
            messages.error(request, _("ليس لديك صلاحيات الوصول إلى لوحة تحكم المسؤول الأعلى"))
            return redirect('index')
        
        # التحقق من صلاحيات المسؤول الأعلى
        if not admin_profile.is_superadmin:
            messages.error(request, _("ليس لديك صلاحيات المسؤول الأعلى"))
            return redirect('index')
            
        request.admin_profile = admin_profile
        return function(request, *args, **kwargs)
    return wrapper

def unified_login(request):
    """صفحة تسجيل الدخول الموحدة للجميع (المستخدمين، المسؤولين، والمسؤولين الأعلى)"""
    
    # إذا كان المستخدم مسجل الدخول بالفعل، نوجهه للصفحة المناسبة
    if request.user.is_authenticated:
        # التحقق إذا كان المستخدم سوبر أدمن
        try:
            admin_profile = AdminUser.objects.get(user=request.user)
            if admin_profile.is_superadmin:
                return redirect('superadmin_dashboard')
            elif request.user.is_staff or request.user.is_admin:
                return redirect('admin_index')  # توجيه للوحة تحكم المسؤول العادي
        except AdminUser.DoesNotExist:
            # المستخدم ليس لديه ملف مسؤول
            if request.user.is_staff:
                return redirect('admin_index')  # توجيه للوحة تحكم المسؤول العادي
            else:
                return redirect('profile')  # توجيه لصفحة الملف الشخصي للمستخدم العادي
    
    # معالجة تسجيل الدخول
    if request.method == 'POST':
        form = SuperAdminLoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            
            # محاولة المصادقة
            user = authenticate(username=username, password=password)

            if user is not None:
                # تسجيل دخول المستخدم
                login(request, user)
                
                # التحقق من نوع المستخدم وتوجيهه للصفحة المناسبة
                try:
                    admin_profile = AdminUser.objects.get(user=user)
                    if admin_profile.is_superadmin:
                        # تحديث معلومات آخر تسجيل دخول
                        admin_profile.last_login_ip = get_client_ip(request)
                        admin_profile.save()
                        
                        # تسجيل النشاط
                        log_admin_activity(
                            admin_profile,
                            _("تسجيل دخول"),
                            _("تم تسجيل الدخول إلى لوحة تحكم المسؤول الأعلى"),
                            request
                        )
                        
                        messages.success(request, _("تم تسجيل الدخول بنجاح كمسؤول أعلى"))
                        return redirect('superadmin_dashboard')
                except AdminUser.DoesNotExist:
                    # المستخدم ليس لديه ملف مسؤول أعلى
                    pass
                
                # التحقق إذا كان مسؤول عادي
                if user.is_staff or getattr(user, 'is_admin', False):
                    messages.success(request, _("تم تسجيل الدخول بنجاح كمسؤول"))
                    return redirect('admin_index')
                
                # المستخدم العادي
                messages.success(request, _("تم تسجيل الدخول بنجاح"))
                return redirect('profile')
            else:
                messages.error(request, _("اسم المستخدم أو كلمة المرور غير صحيحة"))
    else:
        form = SuperAdminLoginForm()
    
    # عند عرض صفحة تسجيل الدخول
    context = {
        'form': form,
        'hide_layout': True,  # لمنع عرض شريط التنقل الجانبي قبل تسجيل الدخول
        'unified_login': True  # إضافة علامة لتوضيح أنها صفحة تسجيل دخول موحدة
    }
    return render(request, 'superadmin/login.html', context)

def superadmin_login(request):
    """توجيه لصفحة تسجيل الدخول الموحدة"""
    return unified_login(request)

def superadmin_logout(request):
    """Super Admin logout view"""
    if request.user.is_authenticated:
        try:
            admin_profile = request.user.admin_profile
            # تسجيل نشاط تسجيل الخروج
            log_admin_activity(
                admin_profile,
                _("تسجيل خروج"),
                _("تم تسجيل الخروج من لوحة تحكم المسؤول الأعلى"),
                request
            )
        except:
            pass
    
    logout(request)
    messages.success(request, _("تم تسجيل الخروج بنجاح"))
    return redirect('superadmin_login')

@superadmin_required
def superadmin_dashboard(request):
    """Super Admin dashboard"""
    # طباعة معلومات تصحيحية لتتبع المشكلة
    print(f"Admin check for superadmin, authenticated: {request.user.is_authenticated}")
    
    # إحصائيات للوحة المعلومات
    total_admins = AdminUser.objects.count()
    total_roles = Role.objects.count()
    active_admins = AdminUser.objects.filter(user__is_active=True).count()
    superadmins = AdminUser.objects.filter(is_superadmin=True).count()
    
    # آخر الأنشطة
    recent_activities = AdminActivity.objects.all().order_by('-created_at')[:10]
    
    # إحصائيات التقييمات
    reviews_stats = {
        'total': Review.objects.count(),
        'pending_moderation': ReviewManagement.objects.filter(status='pending').count(),
        'approved': ReviewManagement.objects.filter(status='approved').count(),
        'rejected': ReviewManagement.objects.filter(status='rejected').count(),
    }
    
    # آخر تسجيلات الدخول
    recent_logins = AdminActivity.objects.filter(action=_("تسجيل دخول")).order_by('-created_at')[:5]
    
    context = {
        'total_admins': total_admins,
        'total_roles': total_roles,
        'active_admins': active_admins,
        'superadmins': superadmins,
        'recent_activities': recent_activities,
        'reviews_stats': reviews_stats,
        'recent_logins': recent_logins,
    }
    
    return render(request, 'superadmin/dashboard.html', context)

# إدارة المسؤولين
@superadmin_required
def manage_admins(request):
    """Manage administrators"""
    admins = AdminUser.objects.select_related('user', 'role').all()
    
    # البحث والتصفية
    search_query = request.GET.get('q', '')
    role_filter = request.GET.get('role', '')
    status_filter = request.GET.get('status', '')
    
    if search_query:
        admins = admins.filter(
            Q(user__username__icontains=search_query) |
            Q(user__first_name__icontains=search_query) |
            Q(user__last_name__icontains=search_query) |
            Q(user__email__icontains=search_query)
        )
    
    if role_filter:
        admins = admins.filter(role_id=role_filter)
    
    if status_filter:
        is_active = status_filter == 'active'
        admins = admins.filter(user__is_active=is_active)
    
    # الأدوار للتصفية
    roles = Role.objects.all()
    
    context = {
        'admins': admins,
        'roles': roles,
        'search_query': search_query,
        'role_filter': role_filter,
        'status_filter': status_filter,
    }
    
    return render(request, 'superadmin/manage_admins.html', context)

@superadmin_required
def admin_details(request, admin_id):
    """View admin details"""
    admin_user = get_object_or_404(AdminUser, id=admin_id)
    
    # الأنشطة الأخيرة لهذا المسؤول
    recent_activities = AdminActivity.objects.filter(admin=admin_user).order_by('-created_at')[:20]
    
    # التقييمات التي قام بإدارتها
    managed_reviews = ReviewManagement.objects.filter(admin=admin_user).order_by('-action_date')[:10]
    
    # الحصول على معلومات المصادقة الثنائية للمستخدم
    try:
        security = UserSecurity.objects.get(user=admin_user.user)
        two_factor_enabled = security.two_factor_enabled
    except UserSecurity.DoesNotExist:
        security = None
        two_factor_enabled = False
    
    context = {
        'admin_user': admin_user,
        'recent_activities': recent_activities,
        'managed_reviews': managed_reviews,
        'two_factor_enabled': two_factor_enabled,
    }
    
    # محاولة تحميل القالب من المسار الصريح
    try:
        return render(request, 'superadmin/admin_details.html', context)
    except Exception as e:
        print(f"خطأ في تحميل القالب: {e}")
        # محاولة تحميل القالب بشكل مباشر
        return render(request, 'templates/superadmin/admin_details.html', context)

@login_required
@superadmin_required
def admin_advanced_permissions(request, admin_id):
    """إدارة الصلاحيات المتقدمة للمسؤول"""
    try:
        admin = get_object_or_404(AdminUser, id=admin_id)
    except AdminUser.DoesNotExist:
        messages.error(request, _('المسؤول غير موجود'))
        return redirect('superadmin_manage_admins')
    
    # الحصول على الصلاحيات الحالية للمسؤول من قاعدة البيانات
    # استخدام SQLite مباشرة للتجنب مشاكل ORM
    admin_permissions = {}
    
    # محاولة الحصول على الصلاحيات المخصصة إذا كانت موجودة
    try:
        import sqlite3
        import json
        
        # الاتصال بقاعدة البيانات مباشرة
        conn = sqlite3.connect('db.sqlite3')
        c = conn.cursor()
        
        # التحقق من جدول rental_adminpermission
        c.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='rental_adminpermission'")
        if not c.fetchone():
            print("جدول rental_adminpermission غير موجود، سيتم إنشاؤه...")
            c.execute('''
            CREATE TABLE rental_adminpermission (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                admin_id INTEGER NOT NULL,
                permissions TEXT NOT NULL,
                UNIQUE(admin_id)
            )
            ''')
            conn.commit()
            print("تم إنشاء جدول rental_adminpermission")
        
        # استعلام عن صلاحيات المسؤول
        c.execute("SELECT permissions FROM rental_adminpermission WHERE admin_id = ?", (admin_id,))
        result = c.fetchone()
        
        if result and result[0]:
            try:
                admin_permissions = json.loads(result[0])
                print(f"تم تحميل صلاحيات المسؤول {admin_id}:", admin_permissions)
            except json.JSONDecodeError as json_error:
                print(f"خطأ في تحليل JSON للصلاحيات: {json_error}")
        else:
            print(f"لا توجد صلاحيات مخزنة للمسؤول {admin_id}")
        
        # إغلاق الاتصال
        conn.close()
        
    except Exception as e:
        print(f"خطأ في قراءة الصلاحيات: {e}")
        admin_permissions = {}
    
    # قائمة بجميع الصلاحيات مقسمة حسب الأقسام
    all_permissions = {
        'dashboard': ['view_dashboard', 'view_calendar', 'view_notifications', 'customize_dashboard'],
        'reservations': ['view_reservations', 'view_reservation_details', 'edit_reservations', 'create_reservations', 'cancel_reservations', 'extend_reservations'],
        'confirmation': ['view_pending_reservations', 'approve_reservations', 'reject_reservations', 'view_confirmation_history', 'add_confirmation_notes'],
        'customers': ['view_customers', 'view_customer_details', 'edit_customers', 'create_customers', 'delete_customers'],
        'vehicles': ['view_vehicles', 'view_vehicle_details', 'edit_vehicles', 'create_vehicles', 'delete_vehicles', 'maintenance_records'],
        'custody': ['view_custody_items', 'add_custody_items', 'edit_custody_items', 'complete_custody', 'print_custody_document'],
        'payments': ['view_payments', 'view_payment_details', 'create_manual_payments', 'edit_payments', 'delete_payments'],
        'archive': ['view_archive', 'view_documents', 'search_archive', 'download_documents', 'archive_settings'],
        'archive_folders': ['view_folders', 'create_folders', 'edit_folders', 'delete_folders'],
        'archive_upload': ['upload_documents', 'edit_document_metadata', 'replace_document'],
        'archive_quick_upload': ['batch_upload', 'view_upload_history'],
        'condition': ['view_condition_reports', 'create_inspection_reports', 'edit_inspection_reports', 'manage_vehicle_images', 'export_condition_reports'],
        'repairs': ['view_repairs', 'add_repairs', 'edit_repairs', 'manage_repair_costs', 'delete_repairs'],
        'analytics': ['view_analytics_dashboard', 'view_sales_analytics', 'view_customer_analytics', 'export_analytics'],
        'reports': ['view_reports', 'export_reports', 'customize_reports', 'schedule_reports'],
        'dashboard_analytics': ['view_dashboard_analytics', 'customize_analytics_view', 'export_dashboard_analytics'],
        'payment_analytics': ['view_payment_reports', 'filter_payment_data', 'export_payment_reports'],
        'profile': ['view_profile', 'edit_profile', 'change_password', 'manage_2fa', 'view_activity_logs'],
        'settings': ['view_settings', 'edit_general_settings', 'edit_user_settings', 'edit_advanced_settings'],
        'reviews': ['view_reviews', 'approve_reviews', 'edit_reviews', 'delete_reviews'],
        'system_logs': ['view_logs', 'filter_search_logs', 'export_logs'],
        'backup': ['view_backups', 'create_backup', 'download_backup', 'restore_backup'],
        'diagnostics': ['view_system_status', 'view_technical_reports', 'clean_system_data', 'repair_system_issues']
    }
    
    # معالجة طلب POST لحفظ الصلاحيات - آلية محسنة وشاملة
    if request.method == 'POST':
        # طباعة معلومات للتصحيح
        print(f"### بدء معالجة طلب حفظ الصلاحيات")
        print(f"### معرف المسؤول: {admin_id}")
        
        # طباعة جميع المفاتيح المرسلة للتحقق من وصول البيانات
        print("Keys received in POST:", list(request.POST.keys()))
        
        # تغيير استراتيجية المعالجة - نستخدم طريقة واحدة موحدة لجمع الصلاحيات
        # نتخلى عن التمييز بين save_changes_only وغيره لأنه سبب مشاكل
        save_changes_only = False
        
        # إنشاء كائن لتتبع الصلاحيات - آلية جديدة تتجاوز كل المشاكل السابقة
        selected_permissions = {}
        
        if save_changes_only and changes_json:
            # حفظ التغييرات فقط
            import json
            try:
                # تحليل JSON التغييرات
                changes = json.loads(changes_json)
                print("Changes JSON received:", changes)
                
                # استرجاع الصلاحيات الحالية قبل تحديثها
                selected_permissions = dict(admin_permissions) if admin_permissions else {}
                
                # حفظ نسخة من الصلاحيات الأصلية للمقارنة لاحقاً
                original_permissions = {k: list(v) for k, v in selected_permissions.items()}
                
                # طباعة الصلاحيات قبل التغيير
                print("Original permissions before changes:", original_permissions)
                
                # معالجة التغييرات
                for section, perms in changes.items():
                    # التأكد من وجود المصفوفة
                    if section not in selected_permissions:
                        selected_permissions[section] = []
                    
                    # إذا كان القسم فارغاً وموجود في التغييرات، نتحقق من إلغاء جميع الصلاحيات
                    section_has_changes = False
                    section_has_active = False
                    
                    for perm in perms:
                        # تحديد الحالة الجديدة (نشطة أم لا)
                        is_active = request.POST.get(f"{section}_{perm}") == 'on'
                        print(f"Processing change: {section}_{perm} = {is_active}")
                        section_has_changes = True
                        
                        if is_active:
                            section_has_active = True
                            # إذا كانت نشطة وغير موجودة، أضفها
                            if perm not in selected_permissions[section]:
                                selected_permissions[section].append(perm)
                                print(f"Added permission: {section}_{perm}")
                        else:
                            # إذا كانت غير نشطة وموجودة، احذفها
                            if perm in selected_permissions[section]:
                                selected_permissions[section].remove(perm)
                                print(f"Removed permission: {section}_{perm}")
                    
                    # إذا كان هناك تغييرات ولكن لا توجد صلاحيات نشطة، نفرغ القسم
                    if section_has_changes and not section_has_active:
                        selected_permissions[section] = []
                        print(f"Section {section} has changes but no active permissions, emptying it")
                
                # فحص أقسام محددة للتأكد من عدم وجود صلاحيات نشطة
                # من أجل قسم الحجوزات تحديداً
                
                # التحقق من وجود علامة إلغاء جميع صلاحيات الحجوزات (من JavaScript)
                if request.POST.get('reservations_empty') == 'true':
                    selected_permissions['reservations'] = []
                    print("✅ تم إفراغ قسم الحجوزات باستخدام علامة reservations_empty")
                # أو البحث عن التغييرات المرسلة في JSON
                elif 'reservations' in changes and len(changes['reservations']) > 0:
                    # التحقق إذا كانت هناك طلبات POST صريحة لإلغاء الصلاحيات
                    all_deactivated = True
                    for perm in all_permissions.get('reservations', []):
                        # إذا كان هناك أي صلاحية نشطة، نضع المتغير كـ False
                        if request.POST.get(f"reservations_{perm}") == 'on':
                            all_deactivated = False
                            break
                    
                    # إذا تم إلغاء جميع الصلاحيات، نتأكد من أن المصفوفة فارغة
                    if all_deactivated:
                        selected_permissions['reservations'] = []
                        print("All reservations permissions were deactivated, setting to empty list")
                
                # فحص جميع الأقسام الأخرى لاكتشاف الأقسام الفارغة
                for section in all_permissions.keys():
                    # إذا كان القسم موجود في selected_permissions
                    if section in selected_permissions:
                        # إذا كان هناك علامة بإفراغ هذا القسم
                        if request.POST.get(f"{section}_empty") == 'true':
                            selected_permissions[section] = []
                            print(f"✅ تم إفراغ قسم {section} باستخدام علامة {section}_empty")
                
                print("Updated permissions after changes:", selected_permissions)
            except json.JSONDecodeError as e:
                print(f"Error parsing changes JSON: {e}")
                # استخدام الطريقة التقليدية كحل بديل
                save_changes_only = False
        
        # تجميع الصلاحيات من النموذج (الطريقة المحسنة يدويًا لكافة الحالات)
        if not save_changes_only:
            # جمع جميع الصلاحيات المحددة من النموذج (الطريقة المحسنة)
            # أولاً نقوم بإنشاء قائمة فارغة لكل قسم للتأكد من تطبيق الإلغاء بشكل صحيح
            selected_permissions = {}
            for section in all_permissions.keys():
                selected_permissions[section] = []
                
            # الآن نبحث عن الصلاحيات المحددة فقط
            # فحص جميع مفاتيح POST
            for key in request.POST.keys():
                # البحث عن أنماط أسماء الصلاحيات
                for section in all_permissions.keys():
                    # فحص نمط section_permission (مثل dashboard_view_dashboard)
                    if key.startswith(f"{section}_") and request.POST.get(key) == 'on':
                        # استخراج اسم الصلاحية من المفتاح
                        permission = key.replace(f"{section}_", "")
                        
                        # التأكد من أن الصلاحية موجودة في قائمة الصلاحيات المتاحة للقسم
                        if permission in all_permissions.get(section, []):
                            if permission not in selected_permissions[section]:
                                selected_permissions[section].append(permission)
                                print(f"✅ تمت إضافة الصلاحية: {section}_{permission}")
            
            # طباعة تقرير عن الأقسام
            for section in list(selected_permissions.keys()):
                if not selected_permissions[section]:
                    print(f"🔍 القسم {section} فارغ")
                else:
                    print(f"🔍 القسم {section} يحتوي على {len(selected_permissions[section])} صلاحية")
        
        # طباعة الصلاحيات المحددة للتشخيص
        print("Final Permissions Object:", selected_permissions)
        
        # حفظ الصلاحيات بواسطة SQLite مباشرة (تجنب استخدام connection والـ ORM)
        try:
            # استخدام SQLite مباشرة
            import json
            import sqlite3
            
            permissions_json = json.dumps(selected_permissions)
            print("Permissions JSON:", permissions_json)
            
            # الاتصال بقاعدة البيانات مباشرة
            conn = sqlite3.connect('db.sqlite3')
            c = conn.cursor()
            
            # حذف السجل الموجود للمسؤول إن وجد
            c.execute("DELETE FROM rental_adminpermission WHERE admin_id = ?", (admin_id,))
            
            # إضافة السجل الجديد
            c.execute("INSERT INTO rental_adminpermission (admin_id, permissions) VALUES (?, ?)", 
                    (admin_id, permissions_json))
            
            # التأكد من الإضافة
            c.execute("SELECT permissions FROM rental_adminpermission WHERE admin_id = ?", (admin_id,))
            result = c.fetchone()
            if result:
                print(f"✅ تم حفظ الصلاحيات للمسؤول رقم {admin_id}")
            else:
                print(f"❌ فشل حفظ الصلاحيات للمسؤول رقم {admin_id}")
            
            # حفظ التغييرات وإغلاق الاتصال
            conn.commit()
            conn.close()
            print("تم حفظ الصلاحيات بنجاح في قاعدة البيانات")
            
            # تسجيل نشاط تحديث الصلاحيات
            log_admin_activity(
                request.admin_profile,
                _("تحديث الصلاحيات المتقدمة"),
                _("تم تحديث الصلاحيات المتقدمة للمسؤول: %(username)s") % {'username': admin.user.username},
                request
            )
            
            messages.success(request, _("تم حفظ الصلاحيات بنجاح"))
            admin_permissions = selected_permissions  # تحديث الصلاحيات المعروضة
            
            # إعادة توجيه مع معلمة نجاح للإشارة إلى الحفظ الناجح
            return redirect(f"{request.path}?saved=true")
            
        except Exception as e:
            print(f"خطأ في حفظ الصلاحيات: {e}")
            messages.error(request, _("حدث خطأ أثناء حفظ الصلاحيات"))
    
    # تحويل قائمة الصلاحيات ليتم عرضها في القالب
    context_permissions = {}
    for section, permissions in all_permissions.items():
        context_permissions[section] = []
        for perm in permissions:
            is_active = False
            if section in admin_permissions and perm in admin_permissions[section]:
                is_active = True
            context_permissions[section].append({
                'name': perm,
                'active': is_active
            })
    
    # تسجيل نشاط الوصول إلى الصلاحيات المتقدمة (فقط للطلبات GET)
    if request.method == 'GET':
        log_admin_activity(
            request.admin_profile,
            _("عرض الصلاحيات المتقدمة"),
            _("تم عرض الصلاحيات المتقدمة للمسؤول: %(username)s") % {'username': admin.user.username},
            request
        )
    
    # استخدام user.get_full_name بدلاً من admin.get_full_name
    context = {
        'admin': admin,
        'title': _('إدارة الصلاحيات المتقدمة - ') + admin.user.get_full_name(),
        'permissions': context_permissions
    }
    
    return render(request, 'superadmin/admin_advanced_permissions_redesign.html', context)

@superadmin_required
def add_admin(request):
    """Add new administrator"""
    if request.method == 'POST':
        form = AdminUserForm(request.POST, new_user=True)
        if form.is_valid():
            with transaction.atomic():
                # إنشاء الحساب
                admin_user = form.save(commit=False)
                
                # التأكد من تعيين حقل is_admin للمستخدم أيضاً
                user = admin_user.user
                user.is_admin = True
                
                # تعيين كلمة المرور إذا تم تقديمها
                password = form.cleaned_data.get('password')
                if password:
                    user.password = make_password(password)
                
                user.save()
                admin_user.save()
                
                # تسجيل النشاط
                log_admin_activity(
                    request.admin_profile,
                    _("إضافة مسؤول"),
                    _("تمت إضافة مسؤول جديد: %(username)s") % {'username': user.username},
                    request
                )
                
                messages.success(request, _("تمت إضافة المسؤول بنجاح"))
                return redirect('superadmin_manage_admins')
    else:
        form = AdminUserForm(new_user=True)
    
    return render(request, 'superadmin/admin_form.html', {'form': form, 'title': _('إضافة مسؤول جديد')})

@superadmin_required
def edit_admin(request, admin_id):
    """Edit administrator"""
    admin_user = get_object_or_404(AdminUser, id=admin_id)
    
    if request.method == 'POST':
        form = AdminUserForm(request.POST, instance=admin_user)
        if form.is_valid():
            with transaction.atomic():
                admin_user = form.save(commit=False)
                
                # تحديث معلومات المستخدم
                user = admin_user.user
                user.is_admin = True
                
                # تحديث كلمة المرور إذا تم تقديمها
                password = form.cleaned_data.get('password')
                if password:
                    user.password = make_password(password)
                
                user.save()
                admin_user.save()
                
                # تسجيل النشاط
                log_admin_activity(
                    request.admin_profile,
                    _("تعديل مسؤول"),
                    _("تم تعديل معلومات المسؤول: %(username)s") % {'username': user.username},
                    request
                )
                
                messages.success(request, _("تم تحديث معلومات المسؤول بنجاح"))
                return redirect('superadmin_admin_details', admin_id=admin_user.id)
    else:
        form = AdminUserForm(instance=admin_user)
    
    return render(request, 'superadmin/admin_form.html', {'form': form, 'admin_user': admin_user, 'title': _('تعديل معلومات المسؤول')})

@superadmin_required
def toggle_admin_status(request, admin_id):
    """Toggle admin active status"""
    admin_user = get_object_or_404(AdminUser, id=admin_id)
    user = admin_user.user
    
    # تغيير حالة المستخدم
    user.is_active = not user.is_active
    user.save()
    
    # تسجيل النشاط
    status_text = _("تفعيل") if user.is_active else _("تعطيل")
    log_admin_activity(
        request.admin_profile,
        _("تغيير حالة مسؤول"),
        _("تم %(status)s حساب المسؤول: %(username)s") % {'status': status_text, 'username': user.username},
        request
    )
    
    # رسالة نجاح
    if user.is_active:
        messages.success(request, _("تم تفعيل حساب المسؤول بنجاح"))
    else:
        messages.success(request, _("تم تعطيل حساب المسؤول بنجاح"))
    
    return redirect('superadmin_admin_details', admin_id=admin_user.id)

# إدارة الأدوار والصلاحيات
@superadmin_required
def manage_roles(request):
    """Manage roles"""
    roles = Role.objects.annotate(admin_count=Count('adminuser'))
    return render(request, 'superadmin/manage_roles.html', {'roles': roles})

@superadmin_required
def role_details(request, role_id):
    """View role details"""
    role = get_object_or_404(Role, id=role_id)
    
    # المسؤولين الذين لديهم هذا الدور
    admins = AdminUser.objects.filter(role=role).select_related('user')
    
    # الصلاحيات المرتبطة بهذا الدور
    permissions = role.permissions.all()
    
    context = {
        'role': role,
        'admins': admins,
        'permissions': permissions,
    }
    
    return render(request, 'superadmin/role_details.html', context)

@superadmin_required
def add_role(request):
    """Add new role"""
    if request.method == 'POST':
        form = RoleForm(request.POST)
        if form.is_valid():
            role = form.save()
            
            # تسجيل النشاط
            log_admin_activity(
                request.admin_profile,
                _("إضافة دور"),
                _("تمت إضافة دور جديد: %(name)s") % {'name': role.name},
                request
            )
            
            messages.success(request, _("تمت إضافة الدور بنجاح"))
            return redirect('superadmin_manage_roles')
    else:
        form = RoleForm()
    
    return render(request, 'superadmin/role_form.html', {'form': form, 'title': _('إضافة دور جديد')})

@superadmin_required
def edit_role(request, role_id):
    """Edit role"""
    role = get_object_or_404(Role, id=role_id)
    
    if request.method == 'POST':
        form = RoleForm(request.POST, instance=role)
        if form.is_valid():
            role = form.save()
            
            # تسجيل النشاط
            log_admin_activity(
                request.admin_profile,
                _("تعديل دور"),
                _("تم تعديل الدور: %(name)s") % {'name': role.name},
                request
            )
            
            messages.success(request, _("تم تحديث الدور بنجاح"))
            return redirect('superadmin_role_details', role_id=role.id)
    else:
        form = RoleForm(instance=role)
    
    return render(request, 'superadmin/role_form.html', {'form': form, 'role': role, 'title': _('تعديل الدور')})

@superadmin_required
def delete_role(request, role_id):
    """Delete role"""
    role = get_object_or_404(Role, id=role_id)
    
    # التحقق مما إذا كان هناك مسؤولون يستخدمون هذا الدور
    if AdminUser.objects.filter(role=role).exists():
        messages.error(request, _("لا يمكن حذف الدور لأنه مستخدم من قبل مسؤولين حاليين"))
        return redirect('superadmin_role_details', role_id=role.id)
    
    if request.method == 'POST':
        # تسجيل النشاط قبل الحذف
        log_admin_activity(
            request.admin_profile,
            _("حذف دور"),
            _("تم حذف الدور: %(name)s") % {'name': role.name},
            request
        )
        
        role.delete()
        messages.success(request, _("تم حذف الدور بنجاح"))
        return redirect('superadmin_manage_roles')
    
    return render(request, 'superadmin/delete_role.html', {'role': role})

@superadmin_required
def manage_permissions(request):
    """Manage permissions"""
    permissions = Permission.objects.all()
    return render(request, 'superadmin/manage_permissions.html', {'permissions': permissions})

@superadmin_required
def add_permission(request):
    """Add new permission"""
    if request.method == 'POST':
        form = PermissionForm(request.POST)
        if form.is_valid():
            permission = form.save()
            
            # تسجيل النشاط
            log_admin_activity(
                request.admin_profile,
                _("إضافة صلاحية"),
                _("تمت إضافة صلاحية جديدة: %(name)s") % {'name': permission.name},
                request
            )
            
            messages.success(request, _("تمت إضافة الصلاحية بنجاح"))
            return redirect('superadmin_manage_permissions')
    else:
        form = PermissionForm()
    
    return render(request, 'superadmin/permission_form_new.html', {'form': form, 'title': _('إضافة صلاحية جديدة')})

@superadmin_required
def edit_permission(request, permission_id):
    """Edit permission"""
    permission = get_object_or_404(Permission, id=permission_id)
    
    if request.method == 'POST':
        form = PermissionForm(request.POST, instance=permission)
        if form.is_valid():
            permission = form.save()
            
            # تسجيل النشاط
            log_admin_activity(
                request.admin_profile,
                _("تعديل صلاحية"),
                _("تم تعديل الصلاحية: %(name)s") % {'name': permission.name},
                request
            )
            
            messages.success(request, _("تم تحديث الصلاحية بنجاح"))
            return redirect('superadmin_manage_permissions')
    else:
        form = PermissionForm(instance=permission)
    
    return render(request, 'superadmin/permission_form_new.html', {'form': form, 'permission': permission, 'title': _('تعديل الصلاحية')})

@superadmin_required
def delete_permission(request, permission_id):
    """Delete permission"""
    permission = get_object_or_404(Permission, id=permission_id)
    
    # التحقق مما إذا كانت الصلاحية مستخدمة من قبل أي دور
    if Role.objects.filter(permissions=permission).exists():
        messages.error(request, _("لا يمكن حذف الصلاحية لأنها مستخدمة من قبل أدوار حالية"))
        return redirect('superadmin_manage_permissions')
    
    if request.method == 'POST':
        # تسجيل النشاط قبل الحذف
        log_admin_activity(
            request.admin_profile,
            _("حذف صلاحية"),
            _("تم حذف الصلاحية: %(name)s") % {'name': permission.name},
            request
        )
        
        permission.delete()
        messages.success(request, _("تم حذف الصلاحية بنجاح"))
        return redirect('superadmin_manage_permissions')
    
    return render(request, 'superadmin/delete_permission.html', {'permission': permission})

# إدارة المصادقة الثنائية للمستخدمين
# تم حذف النسخة المكررة من الدالة هنا من أجل تجنب الإزدواجية

# إدارة التقييمات
@superadmin_required
def manage_reviews(request):
    """Manage reviews"""
    # استرجاع جميع التقييمات
    reviews = Review.objects.select_related('user', 'car').all()
    
    # التصفية والبحث
    status_filter = request.GET.get('status', '')
    rating_filter = request.GET.get('rating', '')
    search_query = request.GET.get('q', '')
    
    if status_filter:
        # التصفية حسب حالة التقييم (معلق، معتمد، مرفوض)
        reviewed_ids = ReviewManagement.objects.filter(status=status_filter).values_list('review_id', flat=True)
        reviews = reviews.filter(id__in=reviewed_ids)
    
    if rating_filter:
        # التصفية حسب التقييم (1-5 نجوم)
        try:
            rating = int(rating_filter)
            reviews = reviews.filter(rating=rating)
        except ValueError:
            pass
    
    if search_query:
        # البحث في التعليقات واسم المستخدم والسيارة
        reviews = reviews.filter(
            Q(comment__icontains=search_query) |
            Q(user__username__icontains=search_query) |
            Q(user__first_name__icontains=search_query) |
            Q(user__last_name__icontains=search_query) |
            Q(car__make__icontains=search_query) |
            Q(car__model__icontains=search_query)
        )
    
    # إحصائيات التقييمات
    stats = {
        'total': Review.objects.count(),
        'pending': ReviewManagement.objects.filter(status='pending').count(),
        'approved': ReviewManagement.objects.filter(status='approved').count(),
        'rejected': ReviewManagement.objects.filter(status='rejected').count(),
    }
    
    context = {
        'reviews': reviews,
        'stats': stats,
        'status_filter': status_filter,
        'rating_filter': rating_filter,
        'search_query': search_query,
    }
    
    return render(request, 'superadmin/manage_reviews.html', context)

@superadmin_required
def review_details(request, review_id):
    """View review details and moderate"""
    review = get_object_or_404(Review, id=review_id)
    
    # محاولة الحصول على سجل إدارة التقييم إذا كان موجوداً
    try:
        review_management = ReviewManagement.objects.get(review_id=review.id)
    except ReviewManagement.DoesNotExist:
        review_management = None
    
    if request.method == 'POST':
        form = ReviewManagementForm(request.POST, instance=review_management)
        if form.is_valid():
            management = form.save(commit=False)
            management.review_id = review.id
            management.admin = request.admin_profile
            management.save()
            
            # تسجيل النشاط
            log_admin_activity(
                request.admin_profile,
                _("إدارة تقييم"),
                _("تم تحديث حالة التقييم #%(id)s إلى %(status)s") % {
                    'id': review.id,
                    'status': management.get_status_display()
                },
                request
            )
            
            messages.success(request, _("تم تحديث حالة التقييم بنجاح"))
            return redirect('superadmin_review_details', review_id=review.id)
    else:
        if review_management:
            form = ReviewManagementForm(instance=review_management)
        else:
            # إنشاء سجل إدارة جديد بحالة افتراضية 'pending'
            form = ReviewManagementForm(initial={'status': 'pending'})
    
    context = {
        'review': review,
        'form': form,
        'review_management': review_management,
    }
    
    return render(request, 'superadmin/review_details.html', context)

@superadmin_required
def approve_review(request, review_id):
    """الموافقة على تقييم"""
    review = get_object_or_404(Review, id=review_id)
    
    # محاولة الحصول على سجل إدارة التقييم أو إنشائه إذا لم يكن موجوداً
    review_management, created = ReviewManagement.objects.get_or_create(
        review=review,
        defaults={
            'status': 'pending',
            'admin': request.admin_profile,
            'notes': ''
        }
    )
    
    # تحديث الحالة إلى موافق عليه
    review_management.status = 'approved'
    review_management.admin = request.admin_profile
    review_management.action_date = timezone.now()
    review_management.save()
    
    # تسجيل النشاط
    log_admin_activity(
        request.admin_profile,
        _("الموافقة على تقييم"),
        _("تمت الموافقة على تقييم المستخدم: %(username)s") % {'username': review.user.username},
        request
    )
    
    messages.success(request, _("تمت الموافقة على التقييم بنجاح"))
    return redirect('superadmin_manage_reviews')

@superadmin_required
def reject_review(request, review_id):
    """رفض تقييم"""
    review = get_object_or_404(Review, id=review_id)
    
    # محاولة الحصول على سجل إدارة التقييم أو إنشائه إذا لم يكن موجوداً
    review_management, created = ReviewManagement.objects.get_or_create(
        review=review,
        defaults={
            'status': 'pending',
            'admin': request.admin_profile,
            'notes': ''
        }
    )
    
    # تحديث الحالة إلى مرفوض
    review_management.status = 'rejected'
    review_management.admin = request.admin_profile
    review_management.action_date = timezone.now()
    review_management.save()
    
    # تسجيل النشاط
    log_admin_activity(
        request.admin_profile,
        _("رفض تقييم"),
        _("تم رفض تقييم المستخدم: %(username)s") % {'username': review.user.username},
        request
    )
    
    messages.success(request, _("تم رفض التقييم بنجاح"))
    return redirect('superadmin_manage_reviews')

@superadmin_required
def system_logs(request):
    """View system logs"""
    # استرجاع جميع سجلات النشاط
    logs = AdminActivity.objects.select_related('admin', 'admin__user').all().order_by('-created_at')
    
    # التصفية والبحث
    admin_filter = request.GET.get('admin', '')
    action_filter = request.GET.get('action', '')
    date_filter = request.GET.get('date', '')
    search_query = request.GET.get('q', '')
    
    if admin_filter:
        logs = logs.filter(admin_id=admin_filter)
    
    if action_filter:
        logs = logs.filter(action=action_filter)
    
    if date_filter:
        try:
            date = timezone.datetime.strptime(date_filter, '%Y-%m-%d').date()
            logs = logs.filter(created_at__date=date)
        except ValueError:
            pass
    
    if search_query:
        logs = logs.filter(
            Q(details__icontains=search_query) |
            Q(admin__user__username__icontains=search_query) |
            Q(action__icontains=search_query)
        )
    
    # المسؤولين للتصفية
    admins = AdminUser.objects.select_related('user').all()
    
    # الإجراءات الفريدة للتصفية
    actions = AdminActivity.objects.values_list('action', flat=True).distinct()
    
    context = {
        'logs': logs,
        'admins': admins,
        'actions': actions,
        'admin_filter': admin_filter,
        'action_filter': action_filter,
        'date_filter': date_filter,
        'search_query': search_query,
    }
    
    return render(request, 'superadmin/system_logs.html', context)


# إدارة المصادقة الثنائية للمستخدمين
@superadmin_required
def user_2fa(request, user_id):
    """إدارة المصادقة الثنائية للمستخدم"""
    User = get_user_model()
    user = get_object_or_404(User, id=user_id)
    
    # التحقق من وجود معلومات أمان المستخدم أو إنشائها
    user_security, created = UserSecurity.objects.get_or_create(user=user)
    
    # الحصول على بيانات QR ورموز النسخ الاحتياطية
    qr_code = None
    backup_codes = None
    
    # جلب سجل محاولات تسجيل الدخول
    login_attempts = LoginAttempt.objects.filter(user=user).order_by('-timestamp')[:20]
    
    # معالجة الإجراءات
    if request.method == 'POST':
        action = request.POST.get('action')
        
        # إعداد المصادقة الثنائية
        if action == 'setup_2fa':
            security = setup_2fa_for_user(user)
            qr_code = generate_qr_code_image(user)
            backup_codes = security.backup_codes
            
            # تفعيل المصادقة الثنائية مباشرة
            security.two_factor_enabled = True
            security.save(update_fields=['two_factor_enabled'])
            
            messages.success(request, _("تم إعداد وتفعيل المصادقة الثنائية بنجاح. يرجى مسح رمز QR بتطبيق المصادقة."))
            
            # تسجيل النشاط
            log_admin_activity(
                request.admin_profile,
                _("إعداد المصادقة الثنائية"),
                _("تم إعداد وتفعيل المصادقة الثنائية للمستخدم {}").format(user.username),
                request
            )
        
        # تعطيل المصادقة الثنائية
        elif action == 'disable_2fa':
            result = disable_2fa_for_user(user, force=True)
            if result:
                messages.success(request, _("تم تعطيل المصادقة الثنائية بنجاح."))
                
                # تسجيل النشاط
                log_admin_activity(
                    request.admin_profile,
                    _("تعطيل المصادقة الثنائية"),
                    _("تم تعطيل المصادقة الثنائية للمستخدم {}").format(user.username),
                    request
                )
            else:
                messages.error(request, _("حدث خطأ أثناء تعطيل المصادقة الثنائية."))
        
        # إعادة توليد رموز النسخ الاحتياطية
        elif action == 'regenerate_backup_codes':
            backup_codes = generate_backup_codes(user, force_regenerate=True)
            messages.success(request, _("تم إعادة توليد رموز النسخ الاحتياطية بنجاح."))
            
            # تسجيل النشاط
            log_admin_activity(
                request.admin_profile,
                _("إعادة توليد رموز النسخ الاحتياطية"),
                _("تم إعادة توليد رموز النسخ الاحتياطية للمستخدم {}").format(user.username),
                request
            )
        
        # فتح قفل الحساب
        elif action == 'unlock_account':
            result = security_unlock_account(user)
            if result:
                messages.success(request, _("تم فتح قفل الحساب بنجاح."))
                
                # تسجيل النشاط
                log_admin_activity(
                    request.admin_profile,
                    _("فتح قفل الحساب"),
                    _("تم فتح قفل حساب المستخدم {}").format(user.username),
                    request
                )
            else:
                messages.error(request, _("حدث خطأ أثناء فتح قفل الحساب."))
        
        # إعادة تعيين محاولات تسجيل الدخول
        elif action == 'reset_login_attempts':
            result = reset_failed_login_attempts(user)
            if result:
                messages.success(request, _("تم إعادة تعيين محاولات تسجيل الدخول بنجاح."))
                
                # تسجيل النشاط
                log_admin_activity(
                    request.admin_profile,
                    _("إعادة تعيين محاولات تسجيل الدخول"),
                    _("تم إعادة تعيين محاولات تسجيل الدخول للمستخدم {}").format(user.username),
                    request
                )
            else:
                messages.error(request, _("حدث خطأ أثناء إعادة تعيين محاولات تسجيل الدخول."))
        
        # تفعيل الحساب
        elif action == 'activate_account':
            user.is_active = True
            user.save()
            messages.success(request, _("تم تفعيل الحساب بنجاح."))
            
            # تسجيل النشاط
            log_admin_activity(
                request.admin_profile,
                _("تفعيل الحساب"),
                _("تم تفعيل حساب المستخدم {}").format(user.username),
                request
            )
        
        # تعطيل الحساب
        elif action == 'deactivate_account':
            user.is_active = False
            user.save()
            messages.success(request, _("تم تعطيل الحساب بنجاح."))
            
            # تسجيل النشاط
            log_admin_activity(
                request.admin_profile,
                _("تعطيل الحساب"),
                _("تم تعطيل حساب المستخدم {}").format(user.username),
                request
            )
    
    # التحقق من وجود رموز احتياطية
    if user_security.two_factor_enabled and not backup_codes:
        backup_codes = user_security.backup_codes
    
    # التحقق من وجود مسؤول أعلى
    is_superadmin = False
    try:
        admin_user = AdminUser.objects.get(user=user)
        is_superadmin = admin_user.is_superadmin
    except AdminUser.DoesNotExist:
        pass
    
    # رمز QR إذا كانت المصادقة الثنائية مفعلة ولم يتم تحميل الرمز بعد
    if user_security.two_factor_enabled and not qr_code:
        qr_code = generate_qr_code_image(user)
    
    context = {
        'user': user,
        'user_security': user_security,
        'login_attempts': login_attempts,
        'qr_code': qr_code,
        'backup_codes': backup_codes,
        'is_superadmin': is_superadmin,
        'totp_secret': user_security.totp_secret,
    }
    
    return render(request, 'superadmin/user_2fa.html', context)
