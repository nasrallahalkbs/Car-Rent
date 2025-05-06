from django.urls import path
from django.contrib.auth.decorators import login_required
from django.views.generic.base import RedirectView

from . import superadmin_views
from . import superadmin_export_views
from . import superadmin_backup_views
from . import superadmin_scheduler_views
from . import superadmin_settings_views
from . import superadmin_diagnostics_views

urlpatterns = [
    # صفحات تسجيل الدخول والخروج
    path('login/', superadmin_views.superadmin_login, name='superadmin_login'),
    path('logout/', superadmin_views.superadmin_logout, name='superadmin_logout'),
    
    # لوحة التحكم الرئيسية
    path('', superadmin_views.superadmin_dashboard, name='superadmin_dashboard'),
    
    # إدارة المسؤولين
    path('admins/', superadmin_views.manage_admins, name='superadmin_manage_admins'),
    path('admins/add/', superadmin_views.add_admin, name='superadmin_add_admin'),
    path('admins/<int:admin_id>/', superadmin_views.admin_details, name='superadmin_admin_details'),
    path('admins/<int:admin_id>/edit/', superadmin_views.edit_admin, name='superadmin_edit_admin'),
    path('admins/<int:admin_id>/toggle/', superadmin_views.toggle_admin_status, name='superadmin_toggle_admin_status'),
    
    # إدارة الأدوار - تعليق مؤقت
    path('roles/', superadmin_views.superadmin_dashboard, name='superadmin_manage_roles'),
    # path('roles/add/', superadmin_views.add_role, name='superadmin_add_role'),
    # path('roles/<int:role_id>/', superadmin_views.role_details, name='superadmin_role_details'),
    # path('roles/<int:role_id>/edit/', superadmin_views.edit_role, name='superadmin_edit_role'),
    # path('roles/<int:role_id>/delete/', superadmin_views.delete_role, name='superadmin_delete_role'),
    
    # إدارة الأذونات - تعليق مؤقت
    path('permissions/', superadmin_views.superadmin_dashboard, name='superadmin_manage_permissions'),
    # path('permissions/add/', superadmin_views.add_permission, name='superadmin_add_permission'),
    # path('permissions/<int:permission_id>/edit/', superadmin_views.edit_permission, name='superadmin_edit_permission'),
    # path('permissions/<int:permission_id>/delete/', superadmin_views.delete_permission, name='superadmin_delete_permission'),
    
    # الإحصائيات والتحليلات - تعليق مؤقت
    path('analytics/', superadmin_views.superadmin_dashboard, name='superadmin_analytics'),
    # path('analytics/users/', superadmin_views.users_analytics, name='superadmin_users_analytics'),
    # path('analytics/reservations/', superadmin_views.reservations_analytics, name='superadmin_reservations_analytics'),
    # path('analytics/reviews/', superadmin_views.reviews_analytics, name='superadmin_reviews_analytics'),
    # path('analytics/revenue/', superadmin_views.revenue_analytics, name='superadmin_revenue_analytics'),
    
    # سجلات النظام
    path('logs/', superadmin_views.system_logs, name='superadmin_system_logs'),
    path('logs/admin-activity/', superadmin_views.system_logs, name='superadmin_admin_activity_logs'),
    # path('logs/user-activity/', superadmin_views.user_activity_logs, name='superadmin_user_activity_logs'),
    # path('logs/error-logs/', superadmin_views.error_logs, name='superadmin_error_logs'),
    
    # إدارة التقييمات
    path('reviews/', superadmin_views.manage_reviews, name='superadmin_manage_reviews'),
    path('reviews/<int:review_id>/', superadmin_views.review_details, name='superadmin_review_details'),
    path('reviews/<int:review_id>/approve/', superadmin_views.approve_review, name='superadmin_approve_review'),
    path('reviews/<int:review_id>/reject/', superadmin_views.reject_review, name='superadmin_reject_review'),
    
    # تصدير التقارير
    path('export/pdf/<str:report_type>/', superadmin_export_views.export_pdf_report, name='superadmin_export_pdf'),
    path('export/excel/<str:report_type>/', superadmin_export_views.export_excel_report, name='superadmin_export_excel'),
    
    # النسخ الاحتياطي واستعادة النظام
    path('backup/', superadmin_backup_views.backup_system, name='superadmin_backup'),
    path('backup/create/', superadmin_backup_views.create_backup, name='superadmin_create_backup'),
    path('backup/<int:backup_id>/restore/', superadmin_backup_views.restore_backup, name='superadmin_restore_backup'),
    path('backup/<int:backup_id>/download/', superadmin_backup_views.download_backup, name='superadmin_download_backup'),
    path('backup/<int:backup_id>/delete/', superadmin_backup_views.delete_backup, name='superadmin_delete_backup'),
    
    # جدولة المهام
    path('scheduler/', superadmin_scheduler_views.scheduler_dashboard, name='superadmin_scheduler'),
    path('scheduler/add/', superadmin_scheduler_views.add_scheduled_job, name='superadmin_add_scheduled_job'),
    path('scheduler/<int:job_id>/edit/', superadmin_scheduler_views.edit_scheduled_job, name='superadmin_edit_scheduled_job'),
    path('scheduler/<int:job_id>/delete/', superadmin_scheduler_views.delete_scheduled_job, name='superadmin_delete_scheduled_job'),
    path('scheduler/<int:job_id>/toggle/', superadmin_scheduler_views.toggle_scheduled_job, name='superadmin_toggle_scheduled_job'),
    
    # إعدادات النظام
    path('settings/', superadmin_settings_views.system_settings, name='superadmin_settings'),
    path('settings/security/', superadmin_settings_views.security_settings, name='superadmin_security_settings'),
    path('settings/notifications/', superadmin_settings_views.notification_settings, name='superadmin_notification_settings'),
    path('settings/advanced-permissions/', superadmin_settings_views.advanced_permissions, name='superadmin_advanced_permissions'),
    
    # تشخيص وإصلاح النظام
    path('diagnostics/', superadmin_diagnostics_views.system_diagnostics, name='superadmin_diagnostics'),
    path('diagnostics/run/<str:diagnostic_type>/', superadmin_diagnostics_views.run_diagnostic, name='superadmin_run_diagnostic'),
    path('diagnostics/fix/<int:issue_id>/', superadmin_diagnostics_views.fix_system_issue, name='superadmin_fix_issue'),
]