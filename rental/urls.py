from django.urls import path
from . import views
from . import admin_views

urlpatterns = [
    # User-facing views
    path('', views.index, name='index'),
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('profile/', views.profile_view, name='profile'),
    path('cars/', views.car_listing, name='car_listing'),
    path('cars/<int:car_id>/', views.car_detail, name='car_detail'),
    path('cart/', views.cart_view, name='cart'),
    path('cart/remove/<int:item_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('checkout/', views.checkout, name='checkout'),
    path('confirmation/', views.confirmation, name='confirmation'),
    path('my-reservations/', views.my_reservations, name='my_reservations'),
    path('reservations/<int:reservation_id>/', views.reservation_detail, name='reservation_detail'),
    path('reservations/<int:reservation_id>/modify/', views.modify_reservation, name='modify_reservation'),
    path('reservations/<int:reservation_id>/cancel/', views.cancel_reservation, name='cancel_reservation'),
    path('review/<int:reservation_id>/', views.add_review, name='add_review'),
    path('toggle-dark-mode/', views.toggle_dark_mode, name='toggle_dark_mode'),
    
    # Static pages
    path('about-us/', views.about_us, name='about_us'),
    
    # API endpoints
    path('api/car/<int:car_id>/unavailable-dates/', views.get_unavailable_dates_api, name='get_unavailable_dates_api'),
    
    # Admin views
    path('admin-dashboard/', admin_views.admin_index, name='admin_index'),
    path('admin-dashboard/cars/', admin_views.admin_cars, name='admin_cars'),
    path('admin-dashboard/cars/add/', admin_views.add_car, name='add_car'),
    path('admin-dashboard/cars/<int:car_id>/edit/', admin_views.edit_car, name='edit_car'),
    path('admin-dashboard/cars/<int:car_id>/delete/', admin_views.delete_car, name='delete_car'),
    path('admin-dashboard/reservations/', admin_views.admin_reservations, name='admin_reservations'),
    path('admin-dashboard/reservations/<int:reservation_id>/status/<str:status>/', 
         admin_views.update_reservation_status, name='update_reservation_status'),
    path('admin-dashboard/users/', admin_views.admin_users, name='admin_users'),
    
    # Payment management
    path('admin-dashboard/payments/', admin_views.admin_payments, name='admin_payments'),
    path('admin-dashboard/payments/<str:payment_id>/', admin_views.payment_details, name='payment_details'),
    path('admin-dashboard/payments/<str:payment_id>/print/', admin_views.print_receipt, name='print_receipt'),
    path('admin-dashboard/payments/<str:payment_id>/download/', admin_views.download_receipt, name='download_receipt'),
    path('admin-dashboard/payments/<str:payment_id>/refund/', admin_views.process_refund, name='process_refund'),
    path('admin-dashboard/payments/<str:payment_id>/mark-as-paid/', admin_views.mark_as_paid, name='mark_as_paid'),
    path('admin-dashboard/payments/<str:payment_id>/cancel/', admin_views.cancel_payment, name='cancel_payment'),
]