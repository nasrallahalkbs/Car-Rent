from django.urls import path
from . import superadmin_views
from django.views.generic.base import RedirectView

# مسارات URL للوحة تحكم المسؤول الأعلى
urlpatterns = [
    # تسجيل الدخول والخروج
    path('login/', superadmin_views.superadmin_login, name='superadmin_login'),
    path('logout/', superadmin_views.superadmin_logout, name='superadmin_logout'),
    
    # مسار تسجيل الدخول الموحد
    path('unified-login/', superadmin_views.unified_login, name='unified_login'),
    
    # لوحة المعلومات الرئيسية
    path('', superadmin_views.superadmin_dashboard, name='superadmin_dashboard'),
    
    # إدارة المسؤولين
    path('admins/', superadmin_views.manage_admins, name='superadmin_manage_admins'),
    path('admins/<int:admin_id>/', superadmin_views.admin_details, name='superadmin_admin_details'),
    path('admins/add/', superadmin_views.add_admin, name='superadmin_add_admin'),
    path('admins/<int:admin_id>/edit/', superadmin_views.edit_admin, name='superadmin_edit_admin'),
    path('admins/<int:admin_id>/toggle-status/', superadmin_views.toggle_admin_status, name='superadmin_toggle_admin_status'),
    
    # إدارة الأدوار
    path('roles/', superadmin_views.manage_roles, name='superadmin_manage_roles'),
    path('roles/<int:role_id>/', superadmin_views.role_details, name='superadmin_role_details'),
    path('roles/add/', superadmin_views.add_role, name='superadmin_add_role'),
    path('roles/<int:role_id>/edit/', superadmin_views.edit_role, name='superadmin_edit_role'),
    path('roles/<int:role_id>/delete/', superadmin_views.delete_role, name='superadmin_delete_role'),
    
    # إدارة الصلاحيات
    path('permissions/', superadmin_views.manage_permissions, name='superadmin_manage_permissions'),
    path('permissions/add/', superadmin_views.add_permission, name='superadmin_add_permission'),
    path('permissions/<int:permission_id>/edit/', superadmin_views.edit_permission, name='superadmin_edit_permission'),
    path('permissions/<int:permission_id>/delete/', superadmin_views.delete_permission, name='superadmin_delete_permission'),
    
    # إدارة التقييمات
    path('reviews/', superadmin_views.manage_reviews, name='superadmin_manage_reviews'),
    path('reviews/<int:review_id>/', superadmin_views.review_details, name='superadmin_review_details'),
    
    # سجلات النظام
    path('logs/', superadmin_views.system_logs, name='superadmin_system_logs'),
    
    # التحليلات والإحصائيات
    path('analytics/', superadmin_views.superadmin_analytics, name='superadmin_analytics'),
]