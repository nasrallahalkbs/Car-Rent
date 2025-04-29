from direct_upload_implementation import direct_sql_upload_document
from simple_upload_fix import very_simple_upload
from super_upload_without_signal import super_upload
from .fixed_upload import super_reliable_upload
from ultimate_upload_solution import ultimate_upload
from .upload_direct import upload_direct_view
from working_upload_solution import guaranteed_upload_view
from direct_sql_solution import direct_sql_upload
from final_direct_upload import final_direct_upload
from .direct_archive_upload import super_direct_upload


from django.urls import path
from django.shortcuts import render
from . import views, admin_views, payment_views, analytics_views
from .admin_views_windows import admin_archive_windows_explorer
from .windows_explorer_view import admin_archive_windows
from .csrf_debug import csrf_debug_view, csrf_debug_page

urlpatterns = [
    path('ar/dashboard/archive/direct_upload/', direct_sql_upload_document, name='direct_sql_upload_document'),
    path('ar/dashboard/archive/simple_upload/', very_simple_upload, name='very_simple_upload'),
    path('ar/dashboard/archive/super_upload/', super_upload, name='super_upload'),
    # إضافة مسار الرفع للغة العربية
    path('ar/dashboard/archive/upload/', admin_views.admin_archive_upload, name='admin_archive_upload_ar'),
    # User-facing views
    path('', views.index, name='index'),
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('profile/', views.profile_view, name='profile'),
    path('cars/', views.car_listing, name='cars'),
    path('car/<int:car_id>/', views.car_detail, name='car_detail'),
    path('car/<int:car_id>/reviews/', views.car_reviews, name='car_reviews'),
    path('car/<int:car_id>/book/', views.book_car, name='book_car'),
    path('car/<int:car_id>/review/', views.add_direct_review, name='add_direct_review'),
    path('booking/process/', views.process_booking, name='process_booking'),
    path('cart/', views.cart_view, name='cart'),
    path('cart/add/', views.add_to_cart, name='add_to_cart'),
    path('cart/remove/<int:item_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('checkout/', views.checkout, name='checkout'),
    path('checkout-new/', views.checkout_new, name='checkout_new'),
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
    # Admin views
    path('dashboard/', admin_views.admin_index, name='admin_index'),
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
    path('dashboard/users/', admin_views.admin_users, name='admin_users'),
    path('dashboard/users/add/', admin_views.add_user, name='add_user'),
    path('dashboard/users/<int:user_id>/', admin_views.user_details, name='user_details'),
    path('dashboard/users/<int:user_id>/edit/', admin_views.edit_user, name='edit_user'),
    path('dashboard/payments/', admin_views.admin_payments, name='admin_payments'),
    path('dashboard/payments/add-manual/', admin_views.add_manual_payment, name='add_manual_payment'),
    path('dashboard/payments/<str:payment_id>/', admin_views.payment_details, name='payment_details'),
    path('dashboard/payments/<str:payment_id>/print/', admin_views.print_receipt, name='print_receipt'),
    path('dashboard/payments/<str:payment_id>/receipt/', admin_views.download_receipt, name='download_receipt'),
    path('dashboard/payments/<str:payment_id>/refund/', admin_views.process_refund, name='process_refund'),
    path('dashboard/payments/<str:payment_id>/mark-paid/', admin_views.mark_as_paid, name='mark_as_paid'),
    path('dashboard/payments/<str:payment_id>/cancel/', admin_views.cancel_payment, name='cancel_payment'),
    path('api/users/<int:user_id>/reservations/', admin_views.get_user_reservations, name='get_user_reservations'),
    # Analytics Routes
    path('dashboard/analytics/', analytics_views.admin_dashboard_analytics, name='admin_dashboard_analytics'),
    path('dashboard/analytics/reports/', analytics_views.admin_payment_analytics, name='admin_payment_analytics'),

    # مسار الأرشيف الإلكتروني - الصفحة الرئيسية فقط
    path('dashboard/archive/', admin_archive_windows, name='admin_archive'),
    # إضافة مسارات جديدة لمعالجة معاملات المجلد والإجراء
    path('dashboard/archive/<int:folder_id>/', admin_archive_windows, name='admin_archive_folder'),
    path('dashboard/archive/<int:folder_id>/<str:action>/', admin_archive_windows, name='admin_archive_action'),
    path('dashboard/archive/<str:action>/', admin_archive_windows, name='admin_archive_action_only'),
    path('dashboard/archive/add/', admin_views.admin_archive_add, name='admin_archive_add'),
    # استخدام دالة الرفع المباشر الجديدة التي تتجاوز أي حماية
    path('dashboard/archive/upload/', super_direct_upload, name='admin_archive_upload'),

    # استدعاء دالة الرفع المباشر المطورة من ملف upload_direct.py
    path('dashboard/archive/upload-reliable/', upload_direct_view, name='admin_archive_upload_reliable'),
    # إضافة مسار دالة الرفع فائقة الموثوقية 
    path('dashboard/archive/reliable-upload/', super_reliable_upload, name='admin_reliable_upload'),
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

    # Diagnostic routes
    path('csrf-debug/', csrf_debug_view, name='csrf_debug'),
    path('csrf-debug-page/', csrf_debug_page, name='csrf_debug_page'),

    # إضافة الإصلاح البسيط كخيار إضافي
    path('dashboard/archive/simple-upload/', admin_views.simple_upload_form, name='simple_upload_form'),
    path('dashboard/archive/simple-upload/process/', admin_views.simple_upload, name='simple_upload'),

    # تم تعليق هذا المسار لتجنب التضارب - هناك تعريف آخر له في السطر 108
    # path('dashboard/archive/direct-sql-upload/', admin_views.direct_sql_upload, name='direct_sql_upload'),
]