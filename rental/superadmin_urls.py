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
    
    # تصدير التقارير
    path('export/pdf/<str:report_type>/', superadmin_views.export_pdf_report, name='superadmin_export_pdf'),
    path('export/excel/<str:report_type>/', superadmin_views.export_excel_report, name='superadmin_export_excel'),
    
    # نظام النسخ الاحتياطي واستعادة النظام
    path('backup/', superadmin_views.backup_system, name='superadmin_backup'),
    path('backup/create/', superadmin_views.create_backup, name='superadmin_create_backup'),
    path('backup/restore/<str:backup_id>/', superadmin_views.restore_backup, name='superadmin_restore_backup'),
    path('backup/download/<str:backup_id>/', superadmin_views.download_backup, name='superadmin_download_backup'),
    path('backup/delete/<str:backup_id>/', superadmin_views.delete_backup, name='superadmin_delete_backup'),
    
    # جدولة النسخ الاحتياطي والوظائف
    path('scheduler/', superadmin_views.scheduler_dashboard, name='superadmin_scheduler'),
    path('scheduler/job/add/', superadmin_views.add_scheduled_job, name='superadmin_add_scheduled_job'),
    path('scheduler/job/<int:job_id>/edit/', superadmin_views.edit_scheduled_job, name='superadmin_edit_scheduled_job'),
    path('scheduler/job/<int:job_id>/delete/', superadmin_views.delete_scheduled_job, name='superadmin_delete_scheduled_job'),
    path('scheduler/job/<int:job_id>/toggle/', superadmin_views.toggle_scheduled_job, name='superadmin_toggle_scheduled_job'),
    
    # إعدادات النظام
    path('settings/', superadmin_views.system_settings, name='superadmin_settings'),
    path('settings/security/', superadmin_views.security_settings, name='superadmin_security_settings'),
    path('settings/notifications/', superadmin_views.notification_settings, name='superadmin_notification_settings'),
    path('settings/advanced-permissions/', superadmin_views.advanced_permissions, name='superadmin_advanced_permissions'),
    
    # أدوات تشخيص وإصلاح النظام
    path('diagnostics/', superadmin_views.system_diagnostics, name='superadmin_diagnostics'),
    path('diagnostics/run/<str:diagnostic_type>/', superadmin_views.run_diagnostic, name='superadmin_run_diagnostic'),
    path('diagnostics/fix/<str:issue_id>/', superadmin_views.fix_system_issue, name='superadmin_fix_issue'),
]