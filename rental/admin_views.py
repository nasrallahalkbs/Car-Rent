from django.shortcuts import render, redirect, get_object_or_404
from .views import get_template_by_language
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.db.models import Sum, Count, Q
from django.core.paginator import Paginator
from django.utils import timezone
from django.urls import reverse
from .models import User, Car, Reservation, CartItem, SiteSettings
from .forms import CarForm, ManualPaymentForm, RegisterForm, ProfileForm, SiteSettingsForm
from functools import wraps
from datetime import datetime, date, timedelta
import uuid
import csv
import logging

logger = logging.getLogger(__name__)

def admin_required(function):
    """
    Decorator for views that checks if the user is an admin.
    """
    @wraps(function)
    def wrapper(request, *args, **kwargs):
        # Debug output for admin_required
        print(f"Admin check for {request.user}, authenticated: {request.user.is_authenticated}")
        if not request.user.is_authenticated:
            messages.error(request, "يرجى تسجيل الدخول للوصول إلى لوحة التحكم")
            next_url = request.path
            login_url = reverse('login')
            return redirect(f"{login_url}?next={next_url}")
        elif not request.user.is_admin:
            messages.error(request, "غير مصرح لك بالوصول إلى هذه الصفحة!")
            return redirect('index')
        
        # Set a global current_user variable for admin templates
        request.current_user = request.user
        return function(request, *args, **kwargs)
    return wrapper

@login_required
@admin_required
def admin_index(request):
    """Admin dashboard home page"""
    # Get summary statistics
    total_cars = Car.objects.count()
    available_cars = Car.objects.filter(is_available=True).count()
    total_users = User.objects.filter(is_admin=False).count()
    
    # Reservation stats
    total_reservations = Reservation.objects.count()
    pending_reservations = Reservation.objects.filter(status='pending').count()
    confirmed_reservations = Reservation.objects.filter(status='confirmed').count()
    completed_reservations = Reservation.objects.filter(status='completed').count()
    cancelled_reservations = Reservation.objects.filter(status='cancelled').count()
    
    # Payment stats
    paid_total = Reservation.objects.filter(payment_status='paid').aggregate(Sum('total_price'))['total_price__sum'] or 0
    pending_payment_total = Reservation.objects.filter(payment_status='pending').aggregate(Sum('total_price'))['total_price__sum'] or 0
    
    # Recent reservations
    recent_reservations = Reservation.objects.order_by('-created_at')[:5]
    
    # Pending reservations list for display in dashboard
    pending_reservations_list = Reservation.objects.filter(status='pending').order_by('-created_at')[:5]
    
    # Data for charts
    # Monthly reservations for last 6 months
    labels = []
    reservation_data = []
    revenue_data = []
    
    now = timezone.now()
    for i in range(5, -1, -1):
        month = now.month - i
        year = now.year
        while month <= 0:
            month += 12
            year -= 1
        
        month_start = date(year, month, 1)
        if month == 12:
            next_month_start = date(year + 1, 1, 1)
        else:
            next_month_start = date(year, month + 1, 1)
        
        month_reservations = Reservation.objects.filter(
            created_at__gte=month_start,
            created_at__lt=next_month_start
        )
        
        month_count = month_reservations.count()
        month_revenue = month_reservations.filter(payment_status='paid').aggregate(Sum('total_price'))['total_price__sum'] or 0
        
        labels.append(f"{month_start.strftime('%b')} {year}")
        reservation_data.append(month_count)
        revenue_data.append(float(month_revenue))
    
    # Reservation status distribution
    status_labels = ['قيد المراجعة', 'تمت الموافقة', 'مكتمل', 'ملغي']
    status_data = [pending_reservations, confirmed_reservations, completed_reservations, cancelled_reservations]
    
    # Car category distribution
    category_data = []
    category_labels = []
    for category_choice in Car.CATEGORY_CHOICES:
        category = category_choice[0]
        count = Car.objects.filter(category=category).count()
        if count > 0:
            category_labels.append(category)
            category_data.append(count)
    
    context = {
        'total_cars': total_cars,
        'available_cars': available_cars,
        'total_users': total_users,
        'total_reservations': total_reservations,
        'pending_reservations': pending_reservations,
        'pending_reservations_list': pending_reservations_list,
        'confirmed_reservations': confirmed_reservations,
        'completed_reservations': completed_reservations,
        'cancelled_reservations': cancelled_reservations,
        'paid_total': paid_total,
        'pending_payment_total': pending_payment_total,
        'recent_reservations': recent_reservations,
        'chart_labels': labels,
        'reservation_data': reservation_data,
        'revenue_data': revenue_data,
        'status_labels': status_labels,
        'status_data': status_data,
        'category_labels': category_labels,
        'category_data': category_data,
        'current_user': request.user,  # Add current user to context
    }
    
    return render(request, 'admin/index.html', context)

@login_required
@admin_required
def admin_cars(request):
    """Admin view to manage cars"""
    # Get filter values from query parameters
    category = request.GET.get('category', '')
    availability = request.GET.get('availability', '')
    search = request.GET.get('search', '')
    
    # Start with all cars
    cars = Car.objects.all()
    
    # Apply filters
    if category:
        cars = cars.filter(category=category)
    
    if availability:
        is_available = availability == 'available'
        cars = cars.filter(is_available=is_available)
    
    if search:
        cars = cars.filter(
            Q(make__icontains=search) | 
            Q(model__icontains=search) | 
            Q(license_plate__icontains=search)
        )
    
    # Order by ID descending (newest first)
    cars = cars.order_by('-id')
    
    # Pagination
    paginator = Paginator(cars, 10)  # Show 10 cars per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Get counts for status summary
    total_count = Car.objects.count()
    available_count = Car.objects.filter(is_available=True).count()
    unavailable_count = total_count - available_count
    
    # Get category distribution
    categories = []
    for category_choice in Car.CATEGORY_CHOICES:
        category_name = category_choice[0]
        category_count = Car.objects.filter(category=category_name).count()
        categories.append({
            'name': category_name,
            'count': category_count,
        })
    
    context = {
        'cars': page_obj,
        'total_count': total_count,
        'available_count': available_count,
        'unavailable_count': unavailable_count,
        'categories': categories,
        'category_filter': category,
        'availability_filter': availability,
        'search_filter': search,
        'category_choices': Car.CATEGORY_CHOICES,
        'current_user': request.user,  # Add current user for template
    }
    
    return render(request, 'admin/cars_django.html', context)

@login_required
@admin_required
def add_car(request):
    """Admin view to add a new car"""
    if request.method == 'POST':
        form = CarForm(request.POST, request.FILES)
        if form.is_valid():
            car = form.save(commit=False)
            
            # تحديث حقل is_available بناءً على حالة السيارة
            if car.status != 'available':
                car.is_available = False
                
            car.save()
            messages.success(request, f"تمت إضافة السيارة {car.make} {car.model} بنجاح!")
            return redirect('admin_cars')
    else:
        form = CarForm(initial={'status': 'available', 'is_available': True})
    
    context = {
        'form': form,
        'action': 'add',
        'title': 'إضافة سيارة جديدة',
        'current_user': request.user,  # Add current user for template
    }
    
    return render(request, 'admin/car_form_django.html', context)

@login_required
@admin_required
def edit_car(request, car_id):
    """Admin view to edit a car"""
    car = get_object_or_404(Car, id=car_id)
    
    if request.method == 'POST':
        form = CarForm(request.POST, request.FILES, instance=car)
        if form.is_valid():
            car = form.save(commit=False)
            
            # تحديث حقل is_available بناءً على حالة السيارة
            if car.status != 'available':
                car.is_available = False
            
            car.save()
            messages.success(request, f"تم تحديث السيارة {car.make} {car.model} بنجاح!")
            return redirect('admin_cars')
    else:
        form = CarForm(instance=car)
    
    context = {
        'form': form,
        'car': car,
        'action': 'edit',
        'title': f'تعديل السيارة - {car.make} {car.model}',
        'current_user': request.user,  # Add current user for template access
    }
    
    return render(request, 'admin/car_form_django.html', context)

@login_required
@admin_required
def delete_car(request, car_id):
    """Admin view to delete a car"""
    car = get_object_or_404(Car, id=car_id)
    
    if request.method == 'POST':
        car_name = f"{car.make} {car.model}"
        car.delete()
        messages.success(request, f"تم حذف السيارة {car_name} بنجاح!")
        return redirect('admin_cars')
    
    context = {
        'car': car,
        'current_user': request.user,  # Add current user for template access
    }
    
    return render(request, 'admin/delete_car.html', context)

@login_required
@admin_required
def admin_reservations(request):
    """Admin view to manage reservations"""
    # استدعاء دالة فحص الحجوزات المنتهية من views.py
    from rental.views import check_expired_confirmations
    import logging
    
    logger = logging.getLogger(__name__)
    
    # تحقق من الحجوزات المنتهية قبل عرض الصفحة
    expired_count = check_expired_confirmations()
    if expired_count > 0:
        logger.info(f"Automatically cancelled {expired_count} expired reservations during admin_reservations view.")
        # إضافة رسالة للمسؤول
        from django.contrib import messages
        messages.info(request, f"تم إلغاء {expired_count} حجز منتهي الصلاحية تلقائيًا (بسبب عدم الدفع خلال 24 ساعة).")
    
    # Get filter values from query parameters
    status = request.GET.get('status', '')
    payment_status = request.GET.get('payment_status', '')
    search = request.GET.get('search', '')
    
    # Start with all reservations
    reservations = Reservation.objects.all()
    
    # Apply filters
    if status:
        reservations = reservations.filter(status=status)
    
    if payment_status:
        reservations = reservations.filter(payment_status=payment_status)
    
    if search:
        reservations = reservations.filter(
            Q(user__first_name__icontains=search) | 
            Q(user__last_name__icontains=search) | 
            Q(user__email__icontains=search) | 
            Q(car__make__icontains=search) | 
            Q(car__model__icontains=search)
        )
    
    # Order by creation date descending (newest first)
    reservations = reservations.order_by('-created_at')
    
    # Pagination
    paginator = Paginator(reservations, 10)  # Show 10 reservations per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Get counts for status summary
    pending_count = Reservation.objects.filter(status='pending').count()
    confirmed_count = Reservation.objects.filter(status='confirmed').count()
    completed_count = Reservation.objects.filter(status='completed').count()
    cancelled_count = Reservation.objects.filter(status='cancelled').count()
    
    context = {
        'reservations': page_obj,
        'pending_count': pending_count,
        'confirmed_count': confirmed_count,
        'completed_count': completed_count,
        'cancelled_count': cancelled_count,
        'status': status,
        'payment_status': payment_status,
        'search': search,
    }
    
    return render(request, 'admin/reservations_django.html', context)

@login_required
@admin_required
def update_reservation_status(request, reservation_id, status):
    """Admin view to update reservation status"""
    from datetime import datetime, timedelta
    
    reservation = get_object_or_404(Reservation, id=reservation_id)
    car = reservation.car
    
    valid_statuses = ['pending', 'confirmed', 'completed', 'cancelled']
    if status not in valid_statuses:
        messages.error(request, "حالة الحجز غير صالحة!")
        return redirect('admin_reservations')
    
    # Update reservation status
    reservation.status = status
    
    # Handle different status changes
    if status == 'confirmed':
        # Mark car as unavailable (reserved)
        car.is_available = False
        car.save()
        
        # Set auto-expiry time (24 hours from now)
        expiry_time = datetime.now() + timedelta(hours=24)
        reservation.confirmation_expiry = expiry_time
        
    elif status == 'cancelled':
        # Make car available again
        car.is_available = True
        car.save()
        
        # Reset payment status
        reservation.payment_status = 'pending'
        
    elif status == 'completed':
        # No need to change car availability on completion
        pass
    
    reservation.save()
    
    # Generate status messages
    status_messages = {
        'pending': "تم تعيين حالة الحجز إلى قيد المراجعة!",
        'confirmed': "تم تأكيد الحجز بنجاح! سيبقى الحجز مفعلاً لمدة 24 ساعة حتى يتم الدفع.",
        'completed': "تم إكمال الحجز بنجاح!",
        'cancelled': "تم إلغاء الحجز!"
    }
    
    messages.success(request, status_messages[status])
    return redirect('admin_reservations')

@login_required
@admin_required
def admin_users(request):
    """Admin view to manage users"""
    # Get filter values from query parameters
    user_type = request.GET.get('user_type', '')
    search = request.GET.get('search', '')
    
    # Start with all non-admin users
    users = User.objects.filter(is_admin=False)
    
    # Apply filters
    if search:
        users = users.filter(
            Q(username__icontains=search) | 
            Q(first_name__icontains=search) | 
            Q(last_name__icontains=search) | 
            Q(email__icontains=search)
        )
    
    # Order by creation date descending (newest first)
    users = users.order_by('-created_at')
    
    # For each user, get count of reservations
    for user in users:
        user.reservation_count = Reservation.objects.filter(user=user).count()
    
    # Pagination
    paginator = Paginator(users, 10)  # Show 10 users per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Get user statistics
    total_users = User.objects.filter(is_admin=False).count()
    user_with_reservations = User.objects.filter(reservation__isnull=False).distinct().count()
    new_users_last_month = User.objects.filter(
        is_admin=False,
        created_at__gte=timezone.now() - timedelta(days=30)
    ).count()
    
    context = {
        'users': page_obj,
        'total_users': total_users,
        'user_with_reservations': user_with_reservations,
        'new_users_last_month': new_users_last_month,
        'search': search,
    }
    
    return render(request, 'admin/users_django.html', context)

@login_required
@admin_required
def admin_payments(request):
    """Admin view to manage payments"""
    # Get filter values from query parameters
    payment_status = request.GET.get('payment_status', '')
    date_range = request.GET.get('date_range', '')
    search = request.GET.get('search', '')
    show_cancelled = request.GET.get('show_cancelled', '') == 'yes'
    
    # Start with all reservations that have payment information
    payments = Reservation.objects.all().select_related('user', 'car')
    
    # Exclude deleted/cancelled payments by default
    payments = payments.exclude(payment_status='deleted')  # Always exclude completely deleted payments
    
    # Exclude regular cancelled payments unless explicitly requested
    if not show_cancelled:
        payments = payments.exclude(payment_status='cancelled')
    
    # Apply filters
    if payment_status:
        payments = payments.filter(payment_status=payment_status)
    
    if date_range:
        if date_range == 'today':
            today = timezone.now().date()
            payments = payments.filter(created_at__date=today)
        elif date_range == 'week':
            week_ago = timezone.now() - timedelta(days=7)
            payments = payments.filter(created_at__gte=week_ago)
        elif date_range == 'month':
            month_ago = timezone.now() - timedelta(days=30)
            payments = payments.filter(created_at__gte=month_ago)
    
    if search:
        payments = payments.filter(
            Q(user__first_name__icontains=search) | 
            Q(user__last_name__icontains=search) | 
            Q(user__email__icontains=search) |
            Q(id__icontains=search)
        )
    
    # Order by creation date descending (newest first)
    payments = payments.order_by('-created_at')
    
    # Pagination
    paginator = Paginator(payments, 10)  # Show 10 payments per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Get payment statistics
    total_revenue = Reservation.objects.filter(payment_status='paid').aggregate(Sum('total_price'))['total_price__sum'] or 0
    pending_revenue = Reservation.objects.filter(payment_status='pending', status='confirmed').aggregate(Sum('total_price'))['total_price__sum'] or 0
    paid_count = Reservation.objects.filter(payment_status='paid').count()
    pending_count = Reservation.objects.filter(payment_status='pending').count()
    refunded_count = Reservation.objects.filter(payment_status='refunded').count()
    
    # Calculate daily and monthly revenue for statistics cards
    today = timezone.now().date()
    daily_revenue = Reservation.objects.filter(payment_status='paid', created_at__date=today).aggregate(Sum('total_price'))['total_price__sum'] or 0
    
    month_start = timezone.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    monthly_revenue = Reservation.objects.filter(payment_status='paid', created_at__gte=month_start).aggregate(Sum('total_price'))['total_price__sum'] or 0
    
    context = {
        'payments': page_obj,
        'total_revenue': total_revenue,
        'pending_revenue': pending_revenue,
        'daily_revenue': daily_revenue,
        'monthly_revenue': monthly_revenue,
        'paid_count': paid_count,
        'pending_count': pending_count,
        'refunded_count': refunded_count,
        'payment_status': payment_status,
        'date_range': date_range,
        'search': search,
        'pending_payments': pending_count,  # For the stats card
    }
    
    return render(request, 'admin/payments_django.html', context)

@login_required
@admin_required
def payment_details(request, payment_id):
    """Admin view to show payment details"""
    payment = get_object_or_404(Reservation, id=payment_id)
    
    # Calculate the number of days between start_date and end_date
    delta = (payment.end_date - payment.start_date).days + 1
    
    # Add additional payment fields needed by template
    payment.date = payment.created_at  # Use created_at for payment date
    payment.reference_number = ''  # Default empty reference number
    payment.status = payment.payment_status  # Map payment_status to status
    payment.amount = payment.total_price  # Map total_price to amount
    
    # Extract payment method and reference number from notes if available
    if payment.notes:
        notes_lines = payment.notes.split('\n')
        for line in notes_lines:
            if 'طريقة الدفع:' in line:
                payment.payment_method = line.split('طريقة الدفع:')[1].strip()
            elif 'رقم المرجع:' in line:
                payment.reference_number = line.split('رقم المرجع:')[1].strip()
    
    # Default values if not found in notes
    if not hasattr(payment, 'payment_method'):
        payment.payment_method = 'visa'  # Default payment method
    
    context = {
        'payment': payment,
        'days': delta,
        'amount': payment.total_price,
        'current_user': request.user,  # Add current user for template access
    }
    
    template_name = 'admin/payment_detail_professional.html'
    # إضافة مكون زمني لإجبار المتصفح على تحديث الصفحة وعدم استخدام النسخة المخزنة
    context['cache_buster'] = '1744903585'
    return render(request, template_name, context)

@login_required
@admin_required
def print_receipt(request, payment_id):
    """View to print a payment receipt"""
    payment = get_object_or_404(Reservation, id=payment_id)
    
    # Only allow printing receipts for paid reservations
    if payment.payment_status != 'paid':
        messages.error(request, "لا يمكن طباعة إيصال للمدفوعات غير المدفوعة!")
        return redirect('payment_details', payment_id=payment_id)
    
    # Calculate the number of days between start_date and end_date
    delta = (payment.end_date - payment.start_date).days + 1
    
    # Add additional payment fields needed by template
    payment.date = payment.created_at  # Use created_at for payment date
    payment.reference_number = ''  # Default empty reference number
    payment.status = payment.payment_status  # Map payment_status to status
    payment.amount = payment.total_price  # Map total_price to amount
    
    # Extract payment method and reference number from notes if available
    if payment.notes:
        notes_lines = payment.notes.split('\n')
        for line in notes_lines:
            if 'طريقة الدفع:' in line:
                payment.payment_method = line.split('طريقة الدفع:')[1].strip()
            elif 'رقم المرجع:' in line:
                payment.reference_number = line.split('رقم المرجع:')[1].strip()
    
    # Default values if not found in notes
    if not hasattr(payment, 'payment_method'):
        payment.payment_method = 'visa'  # Default payment method
    
    context = {
        'payment': payment,
        'receipt_id': f'R{payment.id:06d}',
        'print_date': timezone.now(),
        'days': delta,
        'amount': payment.total_price,
        'current_user': request.user,  # Add current user for template access
    }
    
    return render(request, 'admin/payment_receipt_django.html', context)

@login_required
@admin_required
def process_refund(request, payment_id):
    """Process a refund for a payment"""
    payment = get_object_or_404(Reservation, id=payment_id)
    
    # Only allow refunding paid reservations
    if payment.payment_status != 'paid':
        messages.error(request, "لا يمكن استرداد المدفوعات غير المدفوعة!")
        return redirect('payment_details', payment_id=payment_id)
    
    # Update payment status
    payment.payment_status = 'refunded'
    payment.save()
    
    messages.success(request, f"تم استرداد المبلغ {payment.total_price} دينار بنجاح!")
    return redirect('payment_details', payment_id=payment_id)

@login_required
@admin_required
def mark_as_paid(request, payment_id):
    """Mark a pending payment as paid"""
    payment = get_object_or_404(Reservation, id=payment_id)
    
    # Only allow marking pending payments as paid
    if payment.payment_status != 'pending':
        messages.error(request, "لا يمكن تعيين حالة هذا الدفع إلى مدفوع!")
        return redirect('payment_details', payment_id=payment_id)
    
    # Update payment status
    payment.payment_status = 'paid'
    payment.save()
    
    messages.success(request, f"تم تعيين حالة الدفع إلى مدفوع بنجاح!")
    return redirect('payment_details', payment_id=payment_id)

@login_required
@admin_required
def cancel_payment(request, payment_id):
    """Cancel a pending payment and completely remove it from payment records"""
    payment = get_object_or_404(Reservation, id=payment_id)
    
    # Only allow cancelling pending payments
    if payment.payment_status != 'pending':
        messages.error(request, "لا يمكن إلغاء الدفعات التي تم معالجتها بالفعل!")
        return redirect('payment_details', payment_id=payment_id)
    
    # Store payment information for confirmation message
    payment_id_str = str(payment.id)
    payment_amount = payment.total_price
    
    # الطريقة 1: حذف الدفعة نهائياً من قاعدة البيانات (الطريقة المفضلة)
    try:
        # الفعل الحقيقي: حذف السجل بشكل كامل
        payment.delete()
        messages.success(request, f"تم حذف الدفعة #{payment_id_str} بقيمة {payment_amount} د.ك نهائياً من قاعدة البيانات!")
    except Exception as e:
        # في حال فشل الحذف الكامل (مثلًا بسبب قيود العلاقات)
        # نستخدم الحذف الناعم كحل بديل
        try:
            payment.status = 'cancelled'
            payment.payment_status = 'deleted'  # استخدم حالة خاصة لن تظهر في واجهة المستخدم
            payment.save()
            messages.warning(request, f"تم إلغاء الدفعة #{payment_id_str} وإخفاءها من السجلات (لم يتم حذفها نهائياً بسبب علاقات قاعدة البيانات)")
        except Exception as inner_e:
            messages.error(request, f"حدث خطأ أثناء محاولة حذف الدفعة: {str(e)} | {str(inner_e)}")
    
    # إعادة التوجيه إلى قائمة المدفوعات
    return redirect('admin_payments')

@login_required
@admin_required
def download_receipt(request, payment_id):
    """Download a payment receipt as PDF"""
    payment = get_object_or_404(Reservation, id=payment_id)
    
    # Only allow downloading receipts for paid reservations
    if payment.payment_status != 'paid':
        messages.error(request, "لا يمكن تنزيل إيصال للمدفوعات غير المدفوعة!")
        return redirect('payment_details', payment_id=payment_id)
    
    # In a real app, you would generate a PDF here
    # For this demo, we'll generate a CSV file instead
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="receipt_{payment.id}.csv"'
    
    writer = csv.writer(response)
    writer.writerow(['Receipt ID', f'R{payment.id:06d}'])
    writer.writerow(['Date', payment.created_at.strftime('%Y-%m-%d %H:%M')])
    writer.writerow(['Customer', f'{payment.user.first_name} {payment.user.last_name}'])
    writer.writerow(['Email', payment.user.email])
    writer.writerow(['Car', f'{payment.car.make} {payment.car.model} ({payment.car.year})'])
    writer.writerow(['Rental Period', f'{payment.start_date} to {payment.end_date}'])
    writer.writerow(['Amount', f'{payment.total_price} دينار'])
    writer.writerow(['Status', 'Paid'])
    
    return response

@login_required
@admin_required
def add_manual_payment(request):
    """Add a manual payment entry"""
    # Add debugging output
    print(f"Processing add_manual_payment for user: {request.user}, authenticated: {request.user.is_authenticated}")
    print(f"Session ID: {request.session.session_key}")
    print(f"Is AJAX request: {'X-Requested-With' in request.headers}")
    print(f"Request method: {request.method}")
    print(f"POST data: {request.POST if request.method == 'POST' else 'No POST data'}")
    
    # Get all regular users (non-admin) for the dropdown - moved to top level
    all_users = User.objects.filter(is_admin=False).order_by('first_name', 'last_name')
    
    # Debug users
    print(f"Debug - Found {len(all_users)} non-admin users:")
    for user in all_users:
        print(f"  User ID: {user.id}, Username: {user.username}, Name: {user.first_name} {user.last_name}")
    
    if request.method == 'POST':
        form = ManualPaymentForm(request.POST)
        # Print form validity and data
        print(f"Form is valid: {form.is_valid()}")
        if not form.is_valid():
            print(f"Form errors: {form.errors}")
        
        if form.is_valid():
            amount = form.cleaned_data['amount']
            payment_method = form.cleaned_data['payment_method']
            reference_number = form.cleaned_data['reference_number']
            notes = form.cleaned_data['notes']
            
            # Print the form cleaned data for debugging
            print(f"Cleaned data: {form.cleaned_data}")
            print(f"Payment type: {request.POST.get('payment_type')}")
            print(f"User ID: {request.POST.get('user_id')}")
            print(f"Reservation ID: {request.POST.get('reservation_id')}")
            
            # Get the user from the form
            user_id = request.POST.get('user_id')
            if not user_id:
                messages.error(request, "يجب اختيار مستخدم!")
                # Get reservations again for the form
                incomplete_reservations = Reservation.objects.filter(
                    payment_status='pending'
                ).select_related('user', 'car')
                return render(request, 'admin/add_manual_payment_django.html', {
                    'form': form,
                    'users': all_users,
                    'all_users': all_users,  # Add all users for debugging
                    'incomplete_reservations': incomplete_reservations,
                })
            
            # Get the user object and verify that it's not an admin
            user = get_object_or_404(User, id=user_id)
            if user.is_admin:
                messages.error(request, "لا يمكن إضافة دفعة لحساب مسؤول!")
                all_users = User.objects.filter(is_admin=False).order_by('first_name', 'last_name')
                incomplete_reservations = Reservation.objects.filter(
                    payment_status='pending'
                ).select_related('user', 'car')
                return render(request, 'admin/add_manual_payment_django.html', {
                    'form': form,
                    'users': all_users,
                    'incomplete_reservations': incomplete_reservations,
                })
            
            # Get the reservation if specified
            reservation_id = request.POST.get('reservation_id')
            payment_type = request.POST.get('payment_type')
            
            # Check if we're processing a reservation payment or a manual payment
            if payment_type == 'reservation' and reservation_id and reservation_id.strip():
                # Update an existing reservation
                reservation = get_object_or_404(Reservation, id=reservation_id)
                reservation.payment_status = 'paid'
                
                # Update notes if provided
                if notes:
                    existing_notes = reservation.notes or ""
                    reservation.notes = existing_notes + f"\n\nManual Payment: {notes}"
                
                # Update status to confirmed if it was pending
                if reservation.status == 'pending':
                    reservation.status = 'confirmed'
                
                reservation.save()
                
                messages.success(request, f"تم تسجيل دفعة بقيمة {amount} دينار للحجز #{reservation.id} بنجاح!")
                return redirect('payment_details', payment_id=reservation.id)
            else:
                # Creating a payment without a reservation (e.g., deposit, refund, etc.)
                payment_reason = request.POST.get('payment_reason', 'other')
                note_text = f"سبب الدفع: {payment_reason}\n"
                if notes:
                    note_text += notes
                
                # Create a manual reservation to record the payment
                # Check if there are any cars available to use as a placeholder
                placeholder_car = None
                try:
                    placeholder_car = Car.objects.first()
                    if not placeholder_car:
                        # If no cars exist, create a placeholder dummy car for manual payments
                        placeholder_car = Car.objects.create(
                            make="Manual Payment",
                            model="System Car",
                            year=2025,
                            color="Black",
                            license_plate="MANUAL-PAY",
                            daily_rate=0,
                            category="Economy",
                            seats=4,
                            transmission="Automatic",
                            fuel_type="Gas",
                            features="For manual payments",
                            is_available=False
                        )
                except Exception as e:
                    print(f"Error creating placeholder car: {e}")
                    messages.error(request, "حدث خطأ أثناء معالجة الدفعة. الرجاء إضافة سيارة إلى النظام أولاً.")
                    return redirect('admin_payments')
                
                # Now create the reservation
                manual_reservation = Reservation(
                    user=user,
                    car=placeholder_car,
                    start_date=timezone.now().date(),
                    end_date=timezone.now().date(),
                    total_price=amount,
                    status='completed',
                    payment_status='paid',
                    notes=f"دفعة يدوية: {note_text}\nطريقة الدفع: {payment_method}\nرقم المرجع: {reference_number}"
                )
                manual_reservation.save()
                
                messages.success(request, f"تم تسجيل الدفعة بقيمة {amount} دينار بنجاح للمستخدم {user.first_name} {user.last_name}!")
                return redirect('admin_payments')
    else:
        form = ManualPaymentForm()
    
    # Get user ID from query parameter if provided
    user_id = request.GET.get('user_id')
    user = None
    if user_id:
        user = get_object_or_404(User, id=user_id)
    
    # Get reservation ID from query parameter if provided
    reservation_id = request.GET.get('reservation_id')
    reservation = None
    if reservation_id:
        reservation = get_object_or_404(Reservation, id=reservation_id)
        # Pre-fill form with reservation amount
        form.fields['amount'].initial = reservation.total_price
    
    # Get all regular users (non-admin) for the dropdown
    all_users = User.objects.filter(is_admin=False).order_by('first_name', 'last_name')
    
    # Get all incomplete reservations (pending payments)
    incomplete_reservations = Reservation.objects.filter(
        payment_status='pending'
    ).select_related('user', 'car')
    
    context = {
        'form': form,
        'selected_user': user,  # Rename to avoid conflict with request.user
        'current_user': request.user,  # Add current_user for template access
        'reservation': reservation,
        'users': all_users,
        'all_users': all_users,  # Add all_users explicitly for debugging
        'incomplete_reservations': incomplete_reservations,
    }
    
    return render(request, 'admin/add_manual_payment_django.html', context)

@login_required
@admin_required
def add_user(request):
    """Admin view to add a new user"""
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(request, f"تمت إضافة المستخدم {user.first_name} {user.last_name} بنجاح!")
            return redirect('admin_users')
    else:
        form = RegisterForm()
    
    context = {
        'form': form,
        'title': 'إضافة مستخدم جديد',
    }
    
    return render(request, 'admin/add_user_form.html', context)

@login_required
@admin_required
def user_details(request, user_id):
    """Admin view to show user details"""
    user = get_object_or_404(User, id=user_id)
    
    # Get user's reservations
    reservations = Reservation.objects.filter(user=user).order_by('-created_at')
    
    context = {
        'user_details': user,
        'current_user': request.user,  # Add current user for template access
        'reservations': reservations,
        'title': f'تفاصيل المستخدم: {user.first_name} {user.last_name}',
    }
    
    return render(request, 'admin/user_details.html', context)

@login_required
@admin_required
def edit_user(request, user_id):
    """Admin view to edit a user"""
    user = get_object_or_404(User, id=user_id)
    
    if request.method == 'POST':
        form = ProfileForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            messages.success(request, f"تم تحديث بيانات المستخدم {user.first_name} {user.last_name} بنجاح!")
            return redirect('admin_users')
    else:
        # Prefill the form with user data
        form = ProfileForm(instance=user)
    
    context = {
        'form': form,
        'user_obj': user,
        'current_user': request.user,  # Add current user for template access
        'title': f'تعديل بيانات المستخدم: {user.first_name} {user.last_name}',
    }
    
    return render(request, 'admin/edit_user_form.html', context)

@login_required
@admin_required
def get_user_reservations(request, user_id):
    """API to get reservations for a specific user"""
    # Print debugging information
    print(f"get_user_reservations called with user_id: {user_id}")
    
    try:
        user = User.objects.get(id=user_id)
        print(f"Found user: {user.username} (ID: {user.id})")
    except User.DoesNotExist:
        print(f"User with ID {user_id} not found")
        return JsonResponse({'error': 'User not found'}, status=404)
    
    # Get all incomplete reservations (pending payments) for this user
    reservations = Reservation.objects.filter(
        user=user,
        payment_status='pending'
    ).select_related('car').order_by('-created_at')
    
    print(f"Found {reservations.count()} pending reservations for user {user.username}")
    
    reservations_data = []
    for reservation in reservations:
        print(f"Processing reservation #{reservation.id}: {reservation.car.make} {reservation.car.model}, total: {reservation.total_price}")
        reservations_data.append({
            'id': reservation.id,
            'car': f"{reservation.car.make} {reservation.car.model}",
            'dates': f"{reservation.start_date} to {reservation.end_date}",
            'amount': str(reservation.total_price),
            'status': reservation.status,
            'payment_status': reservation.payment_status,
        })
    
    result = {'reservations': reservations_data}
    print(f"Returning data: {result}")
    return JsonResponse(result)
