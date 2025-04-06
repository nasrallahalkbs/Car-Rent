from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Count, Avg, Sum
from django.utils import timezone
from datetime import timedelta, date
from decimal import Decimal
from django.http import HttpResponse
import json

from .models import User, Car, Reservation, Review
from .forms import CarForm, ManualPaymentForm

def admin_required(function):
    """
    Decorator for views that checks if the user is an admin.
    """
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated or not request.user.is_admin:
            messages.error(request, "لا تملك صلاحية الوصول لهذه الصفحة.")
            return redirect('index')
        return function(request, *args, **kwargs)
    return wrapper

@login_required
@admin_required
def admin_index(request):
    """Admin dashboard home page"""
    # Get today's date for context
    today = timezone.now().date()
    
    # Get statistics for the dashboard
    total_users = User.objects.count()
    total_cars = Car.objects.count()
    available_cars = Car.objects.filter(is_available=True).count()
    total_reservations = Reservation.objects.count()
    
    # Get user stats
    month_ago = today - timedelta(days=30)
    new_users = User.objects.filter(created_at__gte=month_ago).count()
    active_users = User.objects.filter(reservation__status__in=['confirmed', 'pending']).distinct().count()
    
    # Get pending reservations that need attention
    pending_reservations = Reservation.objects.filter(status='pending').select_related('user', 'car')
    
    # Get recent payments
    recent_payments = Reservation.objects.filter(
        payment_status='paid'
    ).select_related('user', 'car').order_by('-created_at')[:5]
    
    # Get revenue data
    # Today's revenue
    daily_revenue = Reservation.objects.filter(
        created_at__date=today,
        payment_status='paid'
    ).aggregate(Sum('total_price'))['total_price__sum'] or 0
    
    # Weekly revenue
    week_ago = today - timedelta(days=7)
    weekly_revenue = Reservation.objects.filter(
        created_at__date__gte=week_ago,
        payment_status='paid'
    ).aggregate(Sum('total_price'))['total_price__sum'] or 0
    
    # Monthly revenue
    monthly_revenue = Reservation.objects.filter(
        created_at__date__gte=month_ago,
        payment_status='paid'
    ).aggregate(Sum('total_price'))['total_price__sum'] or 0
    
    # Total revenue
    total_revenue = Reservation.objects.filter(
        payment_status='paid'
    ).aggregate(Sum('total_price'))['total_price__sum'] or 0
    
    # Calculate monthly change percentage
    two_months_ago = today - timedelta(days=60)
    prev_month_revenue = Reservation.objects.filter(
        created_at__date__gte=two_months_ago,
        created_at__date__lt=month_ago,
        payment_status='paid'
    ).aggregate(Sum('total_price'))['total_price__sum'] or 0
    
    if prev_month_revenue > 0:
        monthly_revenue_change = ((monthly_revenue - prev_month_revenue) / prev_month_revenue) * 100
        monthly_revenue_change = round(monthly_revenue_change)
    else:
        monthly_revenue_change = 100  # If there was no revenue in the previous month
    
    context = {
        'today': today,
        'total_users': total_users,
        'total_cars': total_cars,
        'available_cars': available_cars,
        'total_reservations': total_reservations,
        'pending_reservations': pending_reservations,
        'recent_payments': recent_payments,
        'daily_revenue': daily_revenue,
        'weekly_revenue': weekly_revenue,
        'monthly_revenue': monthly_revenue,
        'total_revenue': total_revenue,
        'new_users': new_users,
        'active_users': active_users,
        'monthly_revenue_change': monthly_revenue_change,
    }
    
    return render(request, 'admin/index.html', context)

@login_required
@admin_required
def admin_cars(request):
    """Admin view to manage cars"""
    # Apply filters if provided in request
    cars = Car.objects.all()
    
    # Filter by category if provided
    category = request.GET.get('category')
    if category:
        cars = cars.filter(category=category)
    
    # Filter by transmission if provided
    transmission = request.GET.get('transmission')
    if transmission:
        cars = cars.filter(transmission=transmission)
    
    # Filter by fuel type if provided
    fuel_type = request.GET.get('fuel_type')
    if fuel_type:
        cars = cars.filter(fuel_type=fuel_type)
    
    # Filter by availability if provided
    availability = request.GET.get('availability')
    if availability == 'available':
        cars = cars.filter(is_available=True)
    elif availability == 'unavailable':
        cars = cars.filter(is_available=False)
    
    # Search by make, model, or license plate if provided
    search = request.GET.get('search')
    if search:
        cars = cars.filter(
            Q(make__icontains=search) | 
            Q(model__icontains=search) | 
            Q(license_plate__icontains=search)
        )
    
    # Count available cars
    available_cars = Car.objects.filter(is_available=True).count()
    
    # Calculate average daily rate
    avg_daily_rate = Car.objects.aggregate(Avg('daily_rate'))['daily_rate__avg'] or 0
    
    # Count reservations
    reservations_count = Reservation.objects.count()
    
    # Order by id descending for newest first
    cars = cars.order_by('-id')
    
    context = {
        'cars': cars,
        'available_cars': available_cars,
        'avg_daily_rate': avg_daily_rate,
        'reservations_count': reservations_count,
    }
    
    return render(request, 'admin/cars_django.html', context)

@login_required
@admin_required
def add_car(request):
    """Admin view to add a new car"""
    if request.method == 'POST':
        form = CarForm(request.POST)
        if form.is_valid():
            car = form.save()
            messages.success(request, f"تمت إضافة {car.make} {car.model} بنجاح!")
            return redirect('admin_cars')
    else:
        form = CarForm()
    
    return render(request, 'admin/car_form.html', {'form': form, 'title': 'إضافة سيارة جديدة'})

@login_required
@admin_required
def edit_car(request, car_id):
    """Admin view to edit a car"""
    car = get_object_or_404(Car, id=car_id)
    
    if request.method == 'POST':
        form = CarForm(request.POST, instance=car)
        if form.is_valid():
            car = form.save()
            messages.success(request, f"تم تحديث {car.make} {car.model} بنجاح!")
            return redirect('admin_cars')
    else:
        form = CarForm(instance=car)
    
    return render(request, 'admin/car_form.html', {
        'form': form,
        'title': f'تعديل: {car.make} {car.model}',
        'car': car
    })

@login_required
@admin_required
def delete_car(request, car_id):
    """Admin view to delete a car"""
    car = get_object_or_404(Car, id=car_id)
    car_name = f"{car.make} {car.model}"
    
    # Check if car has any reservations
    has_reservations = Reservation.objects.filter(car=car).exists()
    
    if request.method == 'POST':
        if has_reservations and request.POST.get('confirm') != 'yes':
            messages.error(request, f"لا يمكن حذف {car_name} لأنها مرتبطة بحجوزات.")
        else:
            car.delete()
            messages.success(request, f"تم حذف {car_name} بنجاح!")
        return redirect('admin_cars')
    
    return render(request, 'admin/delete_car.html', {
        'car': car,
        'has_reservations': has_reservations
    })

@login_required
@admin_required
def admin_reservations(request):
    """Admin view to manage reservations"""
    # Get all reservations with related user and car data
    reservations = Reservation.objects.all().select_related(
        'user', 'car'
    ).order_by('-created_at')
    
    # Apply filters if provided
    status = request.GET.get('status')
    if status:
        reservations = reservations.filter(status=status)
    
    payment_status = request.GET.get('payment_status')
    if payment_status:
        reservations = reservations.filter(payment_status=payment_status)
    
    date_from = request.GET.get('date_from')
    if date_from:
        try:
            date_from = timezone.datetime.strptime(date_from, '%Y-%m-%d').date()
            reservations = reservations.filter(start_date__gte=date_from)
        except ValueError:
            pass
    
    date_to = request.GET.get('date_to')
    if date_to:
        try:
            date_to = timezone.datetime.strptime(date_to, '%Y-%m-%d').date()
            reservations = reservations.filter(end_date__lte=date_to)
        except ValueError:
            pass
    
    search = request.GET.get('search')
    if search:
        reservations = reservations.filter(
            Q(user__username__icontains=search) |
            Q(user__first_name__icontains=search) |
            Q(user__last_name__icontains=search) |
            Q(car__make__icontains=search) |
            Q(car__model__icontains=search)
        )
    
    # Count reservations by status
    total_reservations = Reservation.objects.count()
    pending_count = Reservation.objects.filter(status='pending').count()
    active_count = Reservation.objects.filter(status__in=['confirmed', 'pending']).count()
    cancelled_count = Reservation.objects.filter(status='cancelled').count()
    
    context = {
        'reservations': reservations,
        'total_reservations': total_reservations,
        'pending_count': pending_count,
        'active_count': active_count,
        'cancelled_count': cancelled_count,
    }
    
    return render(request, 'admin/reservations_django.html', context)

@login_required
@admin_required
def update_reservation_status(request, reservation_id, status):
    """Admin view to update reservation status"""
    valid_statuses = ['pending', 'confirmed', 'completed', 'cancelled']
    
    if status not in valid_statuses:
        messages.error(request, "الحالة غير صالحة")
        return redirect('admin_reservations')
    
    reservation = get_object_or_404(Reservation, id=reservation_id)
    old_status = reservation.status
    reservation.status = status
    
    # Update payment status if needed
    if status == 'cancelled' and reservation.payment_status == 'paid':
        reservation.payment_status = 'refunded'
    
    reservation.save()
    
    messages.success(request, f"تم تحديث الحجز #{reservation_id} من '{old_status}' إلى '{status}'")
    return redirect('admin_reservations')

@login_required
@admin_required
def admin_users(request):
    """Admin view to manage users"""
    users = User.objects.all()
    
    # Apply filters if provided
    role = request.GET.get('role')
    if role == 'admin':
        users = users.filter(is_admin=True)
    elif role == 'user':
        users = users.filter(is_admin=False)
    
    date_joined = request.GET.get('date_joined')
    today = timezone.now().date()
    if date_joined == 'today':
        users = users.filter(created_at__date=today)
    elif date_joined == 'this_week':
        week_ago = today - timedelta(days=7)
        users = users.filter(created_at__date__gte=week_ago)
    elif date_joined == 'this_month':
        month_ago = today - timedelta(days=30)
        users = users.filter(created_at__date__gte=month_ago)
    elif date_joined == 'this_year':
        year_ago = today - timedelta(days=365)
        users = users.filter(created_at__date__gte=year_ago)
    
    has_reservations = request.GET.get('has_reservations')
    if has_reservations == 'yes':
        users = users.filter(reservation__isnull=False).distinct()
    elif has_reservations == 'no':
        users = users.exclude(reservation__isnull=False)
    
    search = request.GET.get('search')
    if search:
        users = users.filter(
            Q(username__icontains=search) |
            Q(first_name__icontains=search) |
            Q(last_name__icontains=search) |
            Q(email__icontains=search) |
            Q(phone__icontains=search)
        )
    
    # Add reservation count to each user
    for user in users:
        user.reservation_count = Reservation.objects.filter(user=user).count()
    
    # Get user stats
    admin_count = User.objects.filter(is_admin=True).count()
    month_ago = today - timedelta(days=30)
    new_users = User.objects.filter(created_at__gte=month_ago).count()
    active_users = User.objects.filter(reservation__status__in=['confirmed', 'pending']).distinct().count()
    
    context = {
        'users': users,
        'admin_count': admin_count,
        'new_users': new_users,
        'active_users': active_users,
    }
    
    return render(request, 'admin/users_django.html', context)

@login_required
@admin_required
def admin_payments(request):
    """Admin view to manage payments"""
    # Get all reservations with payment status of 'paid' or 'refunded'
    reservations = Reservation.objects.filter(
        payment_status__in=['paid', 'refunded', 'pending']
    ).select_related('user', 'car').order_by('-created_at')
    
    # Apply filters if provided
    payment_status = request.GET.get('payment_status')
    if payment_status:
        reservations = reservations.filter(payment_status=payment_status)
    
    payment_method = request.GET.get('payment_method')
    if payment_method:
        # This would require a payment method field in the model
        # Filter by notes field containing payment method as a workaround
        reservations = reservations.filter(notes__icontains=payment_method)
    
    date_from = request.GET.get('date_from')
    if date_from:
        try:
            date_from = timezone.datetime.strptime(date_from, '%Y-%m-%d').date()
            reservations = reservations.filter(created_at__date__gte=date_from)
        except ValueError:
            pass
    
    date_to = request.GET.get('date_to')
    if date_to:
        try:
            date_to = timezone.datetime.strptime(date_to, '%Y-%m-%d').date()
            reservations = reservations.filter(created_at__date__lte=date_to)
        except ValueError:
            pass
    
    search = request.GET.get('search')
    if search:
        reservations = reservations.filter(
            Q(user__username__icontains=search) |
            Q(user__first_name__icontains=search) |
            Q(user__last_name__icontains=search) |
            Q(notes__icontains=search)
        )
    
    # Get revenue statistics
    today = timezone.now().date()
    
    # Daily revenue
    daily_revenue = Reservation.objects.filter(
        created_at__date=today,
        payment_status='paid'
    ).aggregate(Sum('total_price'))['total_price__sum'] or 0
    
    # Weekly revenue
    week_ago = today - timedelta(days=7)
    weekly_revenue = Reservation.objects.filter(
        created_at__date__gte=week_ago,
        payment_status='paid'
    ).aggregate(Sum('total_price'))['total_price__sum'] or 0
    
    # Monthly revenue
    month_ago = today - timedelta(days=30)
    monthly_revenue = Reservation.objects.filter(
        created_at__date__gte=month_ago,
        payment_status='paid'
    ).aggregate(Sum('total_price'))['total_price__sum'] or 0
    
    # Total revenue (all time)
    total_revenue = Reservation.objects.filter(
        payment_status='paid'
    ).aggregate(Sum('total_price'))['total_price__sum'] or 0
    
    # Pending payments count
    pending_payments = Reservation.objects.filter(payment_status='pending').count()
    
    # Create a list of payment data for the template
    payments = []
    for reservation in reservations:
        # Convert reservation to payment object for the template
        payment = {
            'id': f"P{reservation.id:06d}",  # Format as P000001, P000002, etc.
            'reservation': reservation,
            'user': reservation.user,
            'car': reservation.car,
            'date': reservation.created_at,
            'amount': reservation.total_price,
            'status': reservation.payment_status,
            'payment_method': 'visa',  # Default method
            'reference_number': f"REF-{reservation.id}-{reservation.created_at.strftime('%Y%m%d')}",
        }
        
        # Add different payment methods based on reservation id remainder
        methods = ['visa', 'mastercard', 'amex', 'cash', 'bank_transfer']
        payment['payment_method'] = methods[reservation.id % len(methods)]
            
        payments.append(payment)
    
    context = {
        'payments': payments,
        'daily_revenue': daily_revenue,
        'weekly_revenue': weekly_revenue,
        'monthly_revenue': monthly_revenue,
        'total_revenue': total_revenue,
        'pending_payments': pending_payments,
    }
    
    return render(request, 'admin/payments_django.html', context)

@login_required
@admin_required
def payment_details(request, payment_id):
    """Admin view to show payment details"""
    # Extract the numeric part from payment_id (remove the 'P' prefix)
    if payment_id.startswith('P'):
        reservation_id = int(payment_id[1:])
    else:
        reservation_id = int(payment_id)
    
    # Get the reservation
    reservation = get_object_or_404(Reservation, id=reservation_id)
    
    # Create a payment object with additional details
    payment = {
        'id': f"P{reservation.id:06d}",
        'reservation': reservation,
        'user': reservation.user,
        'car': reservation.car,
        'date': reservation.created_at,
        'amount': reservation.total_price,
        'status': reservation.payment_status,
        'payment_method': 'visa',  # Default method
        'masked_card_number': '•••• •••• •••• 1234',
        'card_name': f"{reservation.user.first_name} {reservation.user.last_name}",
        'expiry_date': '12/2025',
        'reference_number': f"REF-{reservation.id}-{reservation.created_at.strftime('%Y%m%d')}",
        'notes': reservation.notes or '',
    }
    
    # Add different payment methods based on reservation id remainder
    methods = ['visa', 'mastercard', 'amex', 'cash', 'bank_transfer']
    payment['payment_method'] = methods[reservation.id % len(methods)]
    
    # Add refund details if applicable
    if payment['status'] == 'refunded':
        payment['refund_date'] = reservation.created_at + timedelta(days=2)  # Placeholder
        payment['refund_amount'] = payment['amount']
        payment['refund_transaction_id'] = f"R{reservation.id:06d}"
        payment['refund_reason'] = "طلب العميل الإلغاء"
    
    # Calculate reservation duration in days
    days = (reservation.end_date - reservation.start_date).days
    payment['days'] = days
    
    # Add tax calculation (for demo purposes)
    # Convert to Decimal for proper calculation with Decimal subtotal
    days_decimal = Decimal(str(days))
    payment['subtotal'] = reservation.car.daily_rate * days_decimal
    tax_rate = Decimal('5')  # Tax rate as Decimal
    payment['tax_rate'] = tax_rate
    payment['tax_amount'] = payment['subtotal'] * (tax_rate / Decimal('100'))
    
    context = {
        'payment': payment,
    }
    
    return render(request, 'admin/payment_details_django.html', context)

@login_required
@admin_required
def print_receipt(request, payment_id):
    """View to print a payment receipt"""
    # Reuse the payment_details logic but render a different template
    if payment_id.startswith('P'):
        reservation_id = int(payment_id[1:])
    else:
        reservation_id = int(payment_id)
    
    reservation = get_object_or_404(Reservation, id=reservation_id)
    
    # Create payment object (same as in payment_details)
    payment = {
        'id': f"P{reservation.id:06d}",
        'reservation': reservation,
        'user': reservation.user,
        'car': reservation.car,
        'date': reservation.created_at,
        'amount': reservation.total_price,
        'status': reservation.payment_status,
        'payment_method': 'visa',
        'masked_card_number': '•••• •••• •••• 1234',
        'reference_number': f"REF-{reservation.id}-{reservation.created_at.strftime('%Y%m%d')}",
    }
    
    # Add different payment methods based on reservation id remainder
    methods = ['visa', 'mastercard', 'amex', 'cash', 'bank_transfer']
    payment['payment_method'] = methods[reservation.id % len(methods)]
    
    # Add refund details if applicable
    if payment['status'] == 'refunded':
        payment['refund_date'] = reservation.created_at + timedelta(days=2)
        payment['refund_amount'] = payment['amount']
    
    # Calculate reservation duration in days
    days = (reservation.end_date - reservation.start_date).days
    payment['days'] = days
    
    # Add tax calculation
    days_decimal = Decimal(str(days))
    payment['subtotal'] = reservation.car.daily_rate * days_decimal
    tax_rate = Decimal('5')  # Tax rate as Decimal
    payment['tax_rate'] = tax_rate
    payment['tax_amount'] = payment['subtotal'] * (tax_rate / Decimal('100'))
    
    current_datetime = timezone.now()
    
    context = {
        'payment': payment,
        'current_datetime': current_datetime,
    }
    
    return render(request, 'admin/payment_receipt_django.html', context)

@login_required
@admin_required
def process_refund(request, payment_id):
    """Process a refund for a payment"""
    if payment_id.startswith('P'):
        reservation_id = int(payment_id[1:])
    else:
        reservation_id = int(payment_id)
    
    reservation = get_object_or_404(Reservation, id=reservation_id)
    
    if reservation.payment_status != 'paid':
        messages.error(request, "يمكن رد المبلغ فقط للمدفوعات المكتملة.")
        return redirect('payment_details', payment_id=payment_id)
    
    # Process the refund
    reservation.payment_status = 'refunded'
    reservation.status = 'cancelled'
    reservation.save()
    
    messages.success(request, f"تم رد مبلغ الدفعة رقم {payment_id} بنجاح.")
    return redirect('payment_details', payment_id=payment_id)

@login_required
@admin_required
def mark_as_paid(request, payment_id):
    """Mark a pending payment as paid"""
    if payment_id.startswith('P'):
        reservation_id = int(payment_id[1:])
    else:
        reservation_id = int(payment_id)
    
    reservation = get_object_or_404(Reservation, id=reservation_id)
    
    if reservation.payment_status != 'pending':
        messages.error(request, "يمكن تحديث حالة المدفوعات المعلقة فقط.")
        return redirect('payment_details', payment_id=payment_id)
    
    # Mark as paid
    reservation.payment_status = 'paid'
    if reservation.status == 'pending':
        reservation.status = 'confirmed'
    reservation.save()
    
    messages.success(request, f"تم تحديث حالة الدفعة رقم {payment_id} إلى 'مدفوع' بنجاح.")
    return redirect('payment_details', payment_id=payment_id)

@login_required
@admin_required
def cancel_payment(request, payment_id):
    """Cancel a pending payment"""
    if payment_id.startswith('P'):
        reservation_id = int(payment_id[1:])
    else:
        reservation_id = int(payment_id)
    
    reservation = get_object_or_404(Reservation, id=reservation_id)
    
    if reservation.payment_status != 'pending':
        messages.error(request, "يمكن إلغاء المدفوعات المعلقة فقط.")
        return redirect('payment_details', payment_id=payment_id)
    
    # Cancel payment and reservation
    reservation.payment_status = 'cancelled'
    reservation.status = 'cancelled'
    reservation.save()
    
    messages.success(request, f"تم إلغاء الدفعة {payment_id} بنجاح.")
    return redirect('payment_details', payment_id=payment_id)

@login_required
@admin_required
def download_receipt(request, payment_id):
    """Download a payment receipt as PDF"""
    # For now, just render the receipt view
    # In a real implementation, this would generate a PDF
    return redirect('print_receipt', payment_id=payment_id)

@login_required
@admin_required
def add_manual_payment(request):
    """Add a manual payment entry"""
    # Get all users for selection
    users = User.objects.all().order_by('first_name', 'last_name')
    
    # Get incomplete reservations for selection
    incomplete_reservations = Reservation.objects.filter(
        payment_status='pending'
    ).select_related('user', 'car').order_by('-created_at')
    
    # Process form submission
    if request.method == 'POST':
        form = ManualPaymentForm(request.POST)
        
        # Get selected user and reservation
        selected_user_id = request.POST.get('user_id')
        selected_user = None
        if selected_user_id:
            selected_user = get_object_or_404(User, id=selected_user_id)
        
        reservation_id = request.POST.get('reservation_id')
        no_reservation = request.POST.get('no_reservation') == 'on'
        payment_reason = request.POST.get('payment_reason')
        
        # Get existing reservations for this user
        user_reservations = []
        if selected_user:
            user_reservations = Reservation.objects.filter(
                user=selected_user,
                payment_status='pending'
            ).order_by('-created_at')
        
        # If form is valid
        if form.is_valid():
            # Handle payment with reservation
            if reservation_id and not no_reservation:
                reservation = get_object_or_404(Reservation, id=reservation_id)
                
                # Update reservation payment status
                reservation.payment_status = 'paid'
                if reservation.status == 'pending':
                    reservation.status = 'confirmed'
                
                # If the amount is different than the reservation total, update it
                amount = form.cleaned_data['amount']
                if amount != reservation.total_price:
                    reservation.total_price = amount
                
                # Save notes
                notes = form.cleaned_data['notes']
                if notes:
                    reservation.notes = notes
                
                reservation.save()
                
                # Add a success message
                payment_id = f"P{reservation.id:06d}"
                messages.success(
                    request, 
                    f"تم تسجيل دفعة يدوية بقيمة {amount} د.ك للحجز رقم {reservation.id}"
                )
                
                # Redirect to payment details
                return redirect('payment_details', payment_id=payment_id)
            
            # Handle payment without reservation
            elif no_reservation and selected_user:
                amount = form.cleaned_data['amount']
                payment_method = form.cleaned_data['payment_method']
                reference_number = form.cleaned_data['reference_number']
                notes = form.cleaned_data['notes']
                
                # For payments without reservations, we create a placeholder reservation
                today = date.today()
                yesterday = today - timedelta(days=1)
                
                # Create a description based on payment reason
                reason_display = {
                    'deposit': 'وديعة',
                    'prepayment': 'دفعة مقدمة',
                    'credit': 'رصيد حساب',
                    'other': 'دفعة أخرى'
                }
                
                description = reason_display.get(payment_reason, 'دفعة يدوية')
                if notes:
                    description += f" - {notes}"
                
                # Get the first available car just as a placeholder
                placeholder_car = Car.objects.first()
                if not placeholder_car:
                    messages.error(request, "لا يمكن إنشاء دفعة: لا توجد سيارات في النظام")
                    return redirect('admin_payments')
                
                # Create a special reservation
                reservation = Reservation.objects.create(
                    user=selected_user,
                    car=placeholder_car,
                    start_date=yesterday,
                    end_date=today,
                    total_price=Decimal(str(amount)),
                    status='completed',
                    payment_status='paid',
                    notes=description
                )
                
                # Add a success message
                payment_id = f"P{reservation.id:06d}"
                messages.success(
                    request, 
                    f"تم تسجيل دفعة يدوية بقيمة {amount} د.ك للمستخدم {selected_user.first_name} {selected_user.last_name} ({description})"
                )
                
                # Redirect to payment details
                return redirect('payment_details', payment_id=payment_id)
            
            else:
                messages.error(request, "يرجى تحديد مستخدم أو حجز للدفعة.")
    else:
        form = ManualPaymentForm()
        
    return render(request, 'admin/add_manual_payment_django.html', {
        'form': form,
        'users': users,
        'incomplete_reservations': incomplete_reservations,
    })

@login_required
@admin_required
def get_user_reservations(request):
    """API to get reservations for a specific user"""
    user_id = request.GET.get('user_id')
    if not user_id:
        return HttpResponse(json.dumps({'error': 'User ID is required'}), content_type='application/json')
    
    user = get_object_or_404(User, id=user_id)
    reservations = Reservation.objects.filter(
        user=user,
        payment_status='pending'
    ).select_related('car').order_by('-created_at')
    
    reservation_data = []
    for res in reservations:
        reservation_data.append({
            'id': res.id,
            'car': f"{res.car.make} {res.car.model}",
            'start_date': res.start_date.strftime('%Y-%m-%d'),
            'end_date': res.end_date.strftime('%Y-%m-%d'),
            'total_price': float(res.total_price),
        })
    
    return HttpResponse(json.dumps({'reservations': reservation_data}), content_type='application/json')
