from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.utils.translation import gettext_lazy as _
from django.urls import reverse
from django.db.models import Q, Count
from django.http import JsonResponse
from django.utils import timezone
from functools import wraps
from django.db import transaction
from django.contrib.auth.hashers import make_password

from .models import User, Review
from .models_superadmin import Permission, Role, AdminUser, AdminActivity, ReviewManagement
from .forms_superadmin import PermissionForm, RoleForm, AdminUserForm, ReviewManagementForm, SuperAdminLoginForm
# دوال التحليلات
from .analytics_superadmin import *

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

def superadmin_login(request):
    """Super Admin login view"""
    if request.user.is_authenticated:
        try:
            # Check if user has superadmin profile
            admin_profile = AdminUser.objects.get(user=request.user)
            if admin_profile.is_superadmin:
                return redirect('superadmin_dashboard')
            else:
                # If user is not superadmin, logout and show error
                logout(request)
                messages.error(request, _("ليس لديك صلاحيات المسؤول الأعلى"))
        except AdminUser.DoesNotExist:
            logout(request)
            messages.error(request, _("ليس لديك حساب مسؤول أعلى"))
        return redirect('superadmin_login')

    if request.method == 'POST':
        form = SuperAdminLoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(username=username, password=password)

            if user is not None:
                try:
                    admin_profile = AdminUser.objects.get(user=user)
                    if admin_profile.is_superadmin:
                        login(request, user)
                        # Log superadmin login activity
                        log_admin_activity(
                            admin_profile,
                            _("تسجيل دخول"),
                            _("تم تسجيل الدخول للوحة تحكم المسؤول الأعلى"),
                            request
                        )
                        return redirect('superadmin_dashboard')
                    else:
                        messages.error(request, _("ليس لديك صلاحيات المسؤول الأعلى"))
                except AdminUser.DoesNotExist:
                    messages.error(request, _("ليس لديك حساب مسؤول أعلى"))
            else:
                messages.error(request, _("اسم المستخدم أو كلمة المرور غير صحيحة"))
            
            if user is not None:
                try:
                    admin_profile = AdminUser.objects.get(user=user)
                    if admin_profile.is_superadmin:
                        login(request, user)
                        
                        # تحديث معلومات الدخول
                        admin_profile.last_login_ip = get_client_ip(request)
                        admin_profile.save()
                        
                        # تسجيل نشاط الدخول
                        log_admin_activity(
                            admin_profile,
                            _("تسجيل دخول"),
                            _("تم تسجيل الدخول إلى لوحة تحكم المسؤول الأعلى"),
                            request
                        )
                        
                        messages.success(request, _("تم تسجيل الدخول بنجاح"))
                        return redirect('superadmin_dashboard')
                    else:
                        messages.error(request, _("ليس لديك صلاحيات المسؤول الأعلى"))
                except AdminUser.DoesNotExist:
                    messages.error(request, _("ليس لديك صلاحيات المسؤول الأعلى"))
            else:
                messages.error(request, _("اسم المستخدم أو كلمة المرور غير صحيحة"))
    else:
        form = SuperAdminLoginForm()
    
    return render(request, 'superadmin/login.html', {'form': form})

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
    
    context = {
        'admin_user': admin_user,
        'recent_activities': recent_activities,
        'managed_reviews': managed_reviews,
    }
    
    return render(request, 'superadmin/admin_details.html', context)

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
    
    return render(request, 'superadmin/permission_form.html', {'form': form, 'title': _('إضافة صلاحية جديدة')})

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
    
    return render(request, 'superadmin/permission_form.html', {'form': form, 'permission': permission, 'title': _('تعديل الصلاحية')})

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
