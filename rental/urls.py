from direct_upload_implementation import direct_sql_upload_document
from simple_upload_fix import very_simple_upload
from super_upload_without_signal import super_upload
from .fixed_upload import fixed_direct_upload
from ultimate_upload_solution import ultimate_upload
from .upload_direct import upload_direct_view
from working_upload_solution import guaranteed_upload_view
from direct_sql_solution import direct_sql_upload
from final_direct_upload import final_direct_upload
from .direct_archive_upload import super_direct_upload
from direct_upload_page import direct_upload_page
from fixed_direct_upload_page import fixed_direct_upload_page
from .fixed_analytics_view import direct_payment_analytics


from django.urls import path
from django.shortcuts import render
from . import views, admin_views, payment_views, analytics_views
from .superadmin_diagnostics_views import system_diagnostics, run_diagnostic, fix_issue
from .superadmin_settings_views import superadmin_generate_2fa_qr, superadmin_enable_2fa
from .admin_views_windows import admin_archive_windows_explorer
from .windows_explorer_view import admin_archive_windows
# CSRF Debug وظائف - تم إزالة الوظائف المفقودة
# from .csrf_debug import csrf_debug_view, csrf_debug_page
from . import car_condition_views
from . import views_custody

urlpatterns = [
    path('ar/dashboard/archive/direct_upload/', direct_sql_upload_document, name='direct_sql_upload_document'),
    path('ar/dashboard/archive/simple_upload/', very_simple_upload, name='very_simple_upload'),
    path('ar/dashboard/archive/super_upload/', super_upload, name='super_upload'),
    # إضافة مسار الرفع للغة العربية باستخدام دالة الرفع الموثوقة الجديدة
    path('ar/dashboard/archive/upload/', fixed_direct_upload, name='admin_archive_upload_ar'),
    # إضافة مسار صفحة الإضافة باللغة العربية
    path('ar/dashboard/archive/add/', admin_views.admin_archive_add, name='admin_archive_add_ar'),
    # User-facing views
    path('', views.index, name='index'),
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('profile/', views.profile_view, name='profile'),
    path('profile/2fa-setup/', views.user_2fa_setup, name='user_2fa_setup'),
    path('ar/profile/2fa-setup/', views.user_2fa_setup, name='user_2fa_setup_ar'),
    path('cars/', views.car_listing, name='cars'),
    path('ar/cars/', views.car_listing, name='cars_ar'),
    path('car/<int:car_id>/', views.car_detail, name='car_detail'),
    path('car/<int:car_id>/reviews/', views.car_reviews, name='car_reviews'),
    path('car/<int:car_id>/book/', views.book_car, name='book_car'),
    path('car/<int:car_id>/review/', views.add_direct_review, name='add_direct_review'),
    # إضافة مسارات باللغة العربية للسيارات
    path('ar/car/<int:car_id>/', views.car_detail, name='car_detail_ar'),
    path('ar/car/<int:car_id>/reviews/', views.car_reviews, name='car_reviews_ar'),
    path('ar/car/<int:car_id>/book/', views.book_car, name='book_car_ar'),
    path('ar/car/<int:car_id>/review/', views.add_direct_review, name='add_direct_review_ar'),
    path('booking/process/', views.process_booking, name='process_booking'),
    path('cart/', views.cart_view, name='cart'),
    path('cart/add/', views.add_to_cart, name='add_to_cart'),
    path('cart/remove/<int:item_id>/', views.remove_from_cart, name='remove_from_cart'),
    # إضافة مسارات باللغة العربية للحجز والسلة
    path('ar/booking/process/', views.process_booking, name='process_booking_ar'),
    path('ar/cart/', views.cart_view, name='cart_ar'),
    path('ar/cart/add/', views.add_to_cart, name='add_to_cart_ar'),
    path('ar/cart/remove/<int:item_id>/', views.remove_from_cart, name='remove_from_cart_ar'),
    path('book-from-cart/', views.book_from_cart, name='book_from_cart'),
    path('ar/book-from-cart/', views.book_from_cart, name='book_from_cart_ar'),
    path('checkout/', views.checkout, name='checkout'),
    path('checkout-new/', views.checkout_new, name='checkout_new'),
    path('ar/checkout-new/', views.checkout_new, name='checkout_new_ar'),
    path('confirmation/', views.confirmation, name='confirmation'),
    path('reservations/', views.my_reservations, name='my_reservations'),
    path('payment/', payment_views.professional_payment, name='professional_payment'),
    path('payment/gateway/', payment_views.payment_gateway_backup, name='payment_gateway'),
    path('payment/international/', payment_views.international_payment, name='international_payment'),
    path('payment/paypal/', payment_views.paypal_payment, name='paypal_payment'),
    path('payment/bank-transfer/', payment_views.bank_transfer_payment, name='bank_transfer_payment'),
    path('reservation/<int:reservation_id>/', views.reservation_detail, name='reservation_detail'),
    path('reservation/<int:reservation_id>/modify/', views.modify_reservation, name='modify_reservation'),
    path('reservation/<int:reservation_id>/cancel/', views.cancel_reservation, name='cancel_reservation'),
    path('reservation/<int:reservation_id>/review/', views.add_review, name='add_review'),
    path('reservation/<int:reservation_id>/receipt/', views.payment_receipt, name='payment_receipt'),
    path('toggle-dark-mode/', views.toggle_dark_mode, name='toggle_dark_mode'),
    path('toggle-language/', views.toggle_language, name='toggle_language'),
    path('about-us/', views.about_us, name='about_us'),
    path('bank-transfer-info/', views.bank_transfer_info, name='bank_transfer_info'),
    path('payment-test/', lambda request: render(request, 'payment_test.html'), name='payment_test'),
    path('favorites/', views.favorite_cars, name='favorite_cars'),
    path('favorites/toggle/<int:car_id>/', views.toggle_favorite, name='toggle_favorite'),

    # API endpoints
    path('api/car/<int:car_id>/unavailable-dates/', views.get_unavailable_dates_api, name='get_unavailable_dates_api'),
    path('api/superadmin/generate-2fa-qr/', superadmin_generate_2fa_qr, name='superadmin_generate_2fa_qr'),
    path('api/superadmin/enable-2fa/', superadmin_enable_2fa, name='superadmin_enable_2fa'),
    path('ar/api/superadmin/generate-2fa-qr/', superadmin_generate_2fa_qr, name='superadmin_generate_2fa_qr_ar'),
    path('ar/api/superadmin/enable-2fa/', superadmin_enable_2fa, name='superadmin_enable_2fa_ar'),
    # Admin views
    path('dashboard/', admin_views.admin_index, name='admin_index'),
    path('dashboard/profile/', admin_views.admin_profile, name='admin_profile'),
    path('dashboard/profile/2fa-setup/', admin_views.admin_2fa_setup, name='admin_2fa_setup'),
    path('ar/dashboard/profile/2fa-setup/', admin_views.admin_2fa_setup, name='admin_2fa_setup_ar'),
    path('dashboard/cars/', admin_views.admin_cars, name='admin_cars'),
    path('dashboard/cars/add/', admin_views.add_car, name='add_car'),
    path('dashboard/cars/<int:car_id>/edit/', admin_views.edit_car, name='edit_car'),
    path('dashboard/cars/<int:car_id>/delete/', admin_views.delete_car, name='delete_car'),
    path('dashboard/reservations/', admin_views.admin_reservations, name='admin_reservations'),
    path('dashboard/reservations/<int:reservation_id>/<str:status>/', admin_views.update_reservation_status, name='update_reservation_status'),
    # إضافة مسارات مباشرة لكل حالة لتجاوز مشكلة المعلمات
    path('dashboard/reservations/<int:reservation_id>/confirm/', admin_views.confirm_reservation, name='confirm_reservation'),
    path('dashboard/reservations/<int:reservation_id>/cancel/', admin_views.cancel_reservation_admin, name='cancel_reservation_admin'),
    path('dashboard/reservations/<int:reservation_id>/complete/', admin_views.complete_reservation, name='complete_reservation'),
    path('dashboard/reservations/<int:reservation_id>/delete/', admin_views.delete_reservation, name='delete_reservation'),
    path('dashboard/reservations/<int:reservation_id>/details/', admin_views.admin_reservation_detail, name='admin_reservation_detail'),
    # مسار بديل ومكافئ للسماح باستخدام /view/ أيضًا
    path('dashboard/reservations/<int:reservation_id>/view/', admin_views.admin_reservation_detail, name='admin_reservation_view'),
    path('dashboard/reservations/<int:reservation_id>/print/', admin_views.print_reservation_contract, name='print_reservation_contract'),
    path('dashboard/reservations/<int:reservation_id>/print/enhanced/', lambda request, reservation_id: admin_views.print_reservation_contract(request, reservation_id, 'enhanced'), name='print_enhanced_reservation_contract'),
    path('dashboard/users/', admin_views.admin_users, name='admin_users'),
    path('dashboard/users/add/', admin_views.add_user, name='add_user'),
    path('dashboard/users/<int:user_id>/', admin_views.user_details, name='user_details'),
    path('dashboard/users/<int:user_id>/edit/', admin_views.edit_user, name='edit_user'),
    path('dashboard/payments/', admin_views.admin_payments, name='admin_payments'),
    path('dashboard/payments/add-manual/', admin_views.add_manual_payment, name='add_manual_payment'),
    path('dashboard/payments/<str:payment_id>/', admin_views.payment_details, name='payment_details'),
    path('dashboard/reports/', admin_views.admin_reports, name='admin_reports'),
    path('ar/dashboard/reports/', admin_views.admin_reports, name='admin_reports_ar'),
    path('dashboard/payments/<str:payment_id>/print/', admin_views.print_receipt, name='print_receipt'),
    path('dashboard/payments/<str:payment_id>/print/details/', admin_views.print_payment_details, name='print_payment_details'),
    path('dashboard/payments/<str:payment_id>/receipt/', admin_views.download_receipt, name='download_receipt'),
    path('dashboard/payments/<str:payment_id>/refund/', admin_views.process_refund, name='process_refund'),
    path('dashboard/payments/<str:payment_id>/mark-paid/', admin_views.mark_as_paid, name='mark_as_paid'),
    path('dashboard/payments/<str:payment_id>/cancel/', admin_views.cancel_payment, name='cancel_payment'),
    path('api/users/<int:user_id>/reservations/', admin_views.get_user_reservations, name='get_user_reservations'),
    # Analytics Routes
    path('dashboard/analytics/', analytics_views.admin_dashboard_analytics, name='admin_dashboard_analytics'),
    path('dashboard/analytics/reports/', analytics_views.admin_payment_analytics, name='admin_payment_analytics'),
    # مسار تقارير جديد يستخدم دالة مخصصة لتجاوز مشكلة القوالب
    path('dashboard/analytics/fixed-reports/', direct_payment_analytics, name='direct_payment_analytics'),
    path('ar/dashboard/analytics/fixed-reports/', direct_payment_analytics, name='direct_payment_analytics_ar'),

    # مسار الأرشيف الإلكتروني - الصفحة الرئيسية فقط
    path('dashboard/archive/', admin_archive_windows, name='admin_archive'),
    # إضافة مسارات جديدة لمعالجة معاملات المجلد والإجراء
    path('dashboard/archive/<int:folder_id>/', admin_archive_windows, name='admin_archive_folder'),
    path('dashboard/archive/<int:folder_id>/<str:action>/', admin_archive_windows, name='admin_archive_action'),
    path('dashboard/archive/<str:action>/', admin_archive_windows, name='admin_archive_action_only'),
    path('dashboard/archive/add/', admin_views.admin_archive_add, name='admin_archive_add'),
    # استخدام دالة الرفع الموثوقة الجديدة المطورة
    path('dashboard/archive/upload/', fixed_direct_upload, name='admin_archive_upload'),

    # استدعاء دالة الرفع المباشر المطورة من ملف upload_direct.py
    path('dashboard/archive/upload-reliable/', upload_direct_view, name='admin_archive_upload_reliable'),
    # إضافة مسار دالة الرفع فائقة الموثوقية 
    path('dashboard/archive/reliable-upload/', fixed_direct_upload, name='admin_reliable_upload'),
    path('dashboard/archive/guaranteed-upload/', guaranteed_upload_view, name='guaranteed_upload'),
    path('dashboard/archive/direct-sql-upload/', direct_sql_upload, name='direct_sql_upload'),
    path('dashboard/archive/ultimate-upload/', ultimate_upload, name='ultimate_upload'),
    path('dashboard/archive/final-upload/', final_direct_upload, name='final_direct_upload'),
    # إضافة نسخة للغة العربية
    path('ar/dashboard/archive/final-upload/', final_direct_upload, name='final_direct_upload_ar'),
    path('dashboard/archive/upload-form/', admin_views.admin_archive_upload_form, name='admin_archive_upload_form'),
    path('dashboard/archive/folder/add/', admin_views.admin_archive_folder_add, name='admin_archive_folder_add'),
    path('dashboard/archive/folder/<int:folder_id>/edit/', admin_views.edit_folder, name='admin_archive_folder_edit'),
    path('dashboard/archive/folder/<int:folder_id>/delete/', admin_views.delete_folder, name='admin_archive_folder_delete'),
    path('dashboard/archive/folder/<int:folder_id>/documents/', admin_views.folder_documents, name='admin_archive_folder_documents'),
    path('dashboard/archive/folder/<int:folder_id>/add-document/', admin_views.add_document_to_folder, name='admin_archive_folder_add_document'),
    path('dashboard/archive/windows/', admin_archive_windows_explorer, name='admin_archive_windows'),
    path('dashboard/archive/document/<int:document_id>/download/', admin_views.download_document, name='download_document'),
    path('dashboard/archive/download/<int:document_id>/', admin_views.download_document, name='admin_archive_download'),
    path('dashboard/archive/document/<int:document_id>/view/', admin_views.view_document, name='view_document'),
    path('dashboard/archive/view/<int:document_id>/', admin_views.view_document, name='admin_archive_view'),
    path('dashboard/archive/document/<int:document_id>/', admin_views.document_detail, name='admin_archive_detail'),
    path('dashboard/archive/document/<int:document_id>/detail/', admin_views.document_detail, name='admin_document_detail'),
    # استخدام الوظائف الحالية للتعديل والحذف 
    path('dashboard/archive/edit/<int:document_id>/', admin_views.edit_document, name='edit_document'),
    path('dashboard/archive/document/<int:document_id>/edit/', admin_views.admin_archive_edit, name='admin_archive_edit'),
    path('dashboard/archive/delete/<int:document_id>/', admin_views.delete_document, name='delete_document'),
    path('dashboard/archive/upload-direct/', admin_views.admin_archive_upload_direct, name='admin_archive_upload_direct'),

    # Diagnostic routes - مسارات صفحات التشخيص
    path('superadmin/diagnostics/', system_diagnostics, name='superadmin_diagnostics'),
    path('superadmin/diagnostics/run/<str:diagnostic_type>/', run_diagnostic, name='superadmin_run_diagnostic'),
    path('superadmin/diagnostics/fix/<int:issue_id>/', fix_issue, name='superadmin_fix_issue'),
    # path('csrf-debug/', csrf_debug_view, name='csrf_debug'),
    # path('csrf-debug-page/', csrf_debug_page, name='csrf_debug_page'),

    # إضافة الإصلاح البسيط كخيار إضافي
    path('dashboard/archive/simple-upload/', admin_views.simple_upload_form, name='simple_upload_form'),
    
    # إضافة الحل الجديد لمشكلة رفع الملفات
    path('dashboard/archive/fixed-upload/', fixed_direct_upload, name='fixed_direct_upload'),
    path('dashboard/archive/new-upload/', fixed_direct_upload_page, name='fixed_direct_upload_page'),
    path('ar/dashboard/archive/new-upload/', fixed_direct_upload_page, name='fixed_direct_upload_page_ar'),
    path('dashboard/archive/simple-upload/process/', admin_views.simple_upload, name='simple_upload'),

    # تم تعليق هذا المسار لتجنب التضارب - هناك تعريف آخر له في السطر 108
    # path('dashboard/archive/direct-sql-upload/', admin_views.direct_sql_upload, name='direct_sql_upload'),
    
    # مسارات تقارير حالة السيارة
    path('dashboard/car-condition/', car_condition_views.car_condition_list, name='car_condition_list'),
    path('dashboard/car-condition/create/', car_condition_views.car_condition_create, name='car_condition_create'),
    path('dashboard/car-condition/<int:report_id>/', car_condition_views.car_condition_detail, name='car_condition_detail'),
    path('dashboard/car-condition/<int:report_id>/edit/', car_condition_views.car_condition_edit, name='car_condition_edit'),
    path('dashboard/car-condition/<int:report_id>/delete/', car_condition_views.car_condition_delete, name='car_condition_delete'),
    path('dashboard/car-condition/car/<int:car_id>/history/', car_condition_views.car_history_reports, name='car_history_reports'),
    path('dashboard/car-condition/statistics/', car_condition_views.car_condition_statistics, name='car_condition_statistics'),
    path('dashboard/car-condition/reservation/<int:reservation_id>/comparison/', car_condition_views.car_condition_comparison, name='car_condition_comparison'),
    path('api/get-car-by-reservation/', car_condition_views.get_car_by_reservation, name='get_car_by_reservation'),
    path('ar/api/get-car-by-reservation/', car_condition_views.get_car_by_reservation, name='get_car_by_reservation_ar'),
    
    # مسارات تقارير حالة السيارة باللغة العربية
    path('ar/dashboard/car-condition/', car_condition_views.car_condition_list, name='car_condition_list_ar'),
    path('ar/dashboard/car-condition/create/', car_condition_views.car_condition_create, name='car_condition_create_ar'),
    path('ar/dashboard/car-condition/<int:report_id>/', car_condition_views.car_condition_detail, name='car_condition_detail_ar'),
    path('ar/dashboard/car-condition/<int:report_id>/edit/', car_condition_views.car_condition_edit, name='car_condition_edit_ar'),
    path('ar/dashboard/car-condition/<int:report_id>/delete/', car_condition_views.car_condition_delete, name='car_condition_delete_ar'),
    path('ar/dashboard/car-condition/car/<int:car_id>/history/', car_condition_views.car_history_reports, name='car_history_reports_ar'),
    path('ar/dashboard/car-condition/statistics/', car_condition_views.car_condition_statistics, name='car_condition_statistics_ar'),
    path('ar/dashboard/car-condition/reservation/<int:reservation_id>/comparison/', car_condition_views.car_condition_comparison, name='car_condition_comparison_ar'),
    
    # مسارات إدارة العهدة
    path('dashboard/custody/', views_custody.custody_dashboard, name='custody_dashboard'),
    path('dashboard/custody/dashboard/', views_custody.custody_dashboard, name='custody_dashboard2'),
    path('dashboard/custody/list/', views_custody.custody_list, name='custody_list'),
    path('dashboard/custody/create/', views_custody.custody_create, name='custody_create'),
    path('dashboard/custody/<int:guarantee_id>/', views_custody.custody_detail, name='custody_detail'),
    path('dashboard/custody/<int:guarantee_id>/edit/', views_custody.custody_edit, name='custody_edit'),
    path('dashboard/custody/<int:guarantee_id>/return/', views_custody.custody_return, name='custody_return'),
    path('dashboard/custody/<int:guarantee_id>/print/', views_custody.custody_print, name='custody_print'),
    path('dashboard/custody/export/', views_custody.custody_export, name='custody_export'),
    
    # مسارات إدارة العهدة باللغة العربية
    path('ar/dashboard/custody/', views_custody.custody_dashboard, name='custody_dashboard_ar'),
    path('ar/dashboard/custody/dashboard/', views_custody.custody_dashboard, name='custody_dashboard_ar2'),
    path('ar/dashboard/custody/list/', views_custody.custody_list, name='custody_list_ar'),
    path('ar/dashboard/custody/create/', views_custody.custody_create, name='custody_create_ar'),
    path('ar/dashboard/custody/<int:guarantee_id>/', views_custody.custody_detail, name='custody_detail_ar'),
    path('ar/dashboard/custody/<int:guarantee_id>/edit/', views_custody.custody_edit, name='custody_edit_ar'),
    path('ar/dashboard/custody/<int:guarantee_id>/return/', views_custody.custody_return, name='custody_return_ar'),
    path('ar/dashboard/custody/<int:guarantee_id>/print/', views_custody.custody_print, name='custody_print_ar'),
    path('ar/dashboard/custody/export/', views_custody.custody_export, name='custody_export_ar'),
    
    # مسارات نظام توثيق حالة السيارة المتقدم
    # إدارة فئات وعناصر الفحص
    path('dashboard/car-condition/categories/', car_condition_views.inspection_category_list, name='inspection_category_list'),
    path('dashboard/car-condition/categories/<int:category_id>/edit/', car_condition_views.inspection_category_edit, name='inspection_category_edit'),
    path('dashboard/car-condition/categories/<int:category_id>/delete/', car_condition_views.inspection_category_delete, name='inspection_category_delete'),
    path('dashboard/car-condition/items/', car_condition_views.inspection_item_list, name='inspection_item_list'),
    path('dashboard/car-condition/items/<int:item_id>/edit/', car_condition_views.inspection_item_edit, name='inspection_item_edit'),
    path('dashboard/car-condition/items/<int:item_id>/delete/', car_condition_views.inspection_item_delete, name='inspection_item_delete'),
    
    # إنشاء تقرير فحص تفصيلي
    path('dashboard/car-condition/inspection/create/', car_condition_views.complete_car_inspection_create, name='complete_car_inspection_create'),
    path('dashboard/car-condition/inspection/<int:report_id>/', car_condition_views.car_inspection_detail, name='car_inspection_detail'),
    
    # إدارة الصور والتوقيعات
    path('dashboard/car-condition/inspection/<int:report_id>/images/', car_condition_views.add_inspection_images, name='add_inspection_images'),
    path('dashboard/car-condition/inspection/images/<int:image_id>/delete/', car_condition_views.delete_inspection_image, name='delete_inspection_image'),
    path('dashboard/car-condition/inspection/<int:report_id>/customer-signature/', car_condition_views.add_customer_signature, name='add_customer_signature'),
    path('dashboard/car-condition/inspection/<int:report_id>/staff-signature/', car_condition_views.add_staff_signature, name='add_staff_signature'),
    path('dashboard/car-condition/inspection/<int:report_id>/pdf/', car_condition_views.download_inspection_report_pdf, name='download_inspection_report_pdf'),
    path('dashboard/car-condition/inspection/<int:report_id>/print-delivery/', car_condition_views.print_car_delivery_report, name='print_car_delivery_report'),
    
    # إدارة الإصلاحات
    path('dashboard/car-condition/repairs/', car_condition_views.car_repair_list, name='car_repair_list'),
    path('dashboard/car-condition/repairs/report/', car_condition_views.car_repair_report, name='car_repair_report'),
    path('dashboard/car-condition/repairs/report/<int:car_id>/', car_condition_views.car_repair_report, name='car_repair_report_by_car'),
    path('dashboard/car-condition/repair/<int:detail_id>/', car_condition_views.car_repair_detail, name='car_repair_detail'),
]