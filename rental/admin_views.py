from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Count, Avg, Sum
from django.utils import timezone
from datetime import timedelta, date
from decimal import Decimal

from .models import User, Car, Reservation, Review
from .forms import CarForm, ManualPaymentForm

def admin_required(function):
    """
    Decorator for views that checks if the user is an admin.
    """
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated or not request.user.is_admin:
            messages.error(request, "You don't have permission to access this page.")
            return redirect('index')
        return function(request, *args, **kwargs)
    return wrapper

@login_required
@admin_required
def admin_index(request):
    """Admin dashboard home page"""
    # Get statistics for the dashboard
    total_users = User.objects.count()
    total_cars = Car.objects.count()
    available_cars = Car.objects.filter(is_available=True).count()
    total_reservations = Reservation.objects.count()
    
    # Get pending reservations that need attention
    pending_reservations = Reservation.objects.filter(status='pending').select_related('user', 'car')
    
    # Get recent reservations
    recent_reservations = Reservation.objects.all().order_by('-created_at')[:5]
    
    # Get revenue data
    # Today's revenue
    today = timezone.now().date()
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
    
    context = {
        'total_users': total_users,
        'total_cars': total_cars,
        'available_cars': available_cars,
        'total_reservations': total_reservations,
        'pending_reservations': pending_reservations,
        'recent_reservations': recent_reservations,
        'daily_revenue': daily_revenue,
        'weekly_revenue': weekly_revenue,
        'monthly_revenue': monthly_revenue,
    }
    
    return render(request, 'admin/index.html', context)

@login_required
@admin_required
def admin_cars(request):
    """Admin view to manage cars"""
    cars = Car.objects.all().order_by('-id')
    return render(request, 'admin/cars_django.html', {'cars': cars})

@login_required
@admin_required
def add_car(request):
    """Admin view to add a new car"""
    if request.method == 'POST':
        form = CarForm(request.POST)
        if form.is_valid():
            car = form.save()
            messages.success(request, f"{car.make} {car.model} added successfully!")
            return redirect('admin_cars')
    else:
        form = CarForm()
    
    return render(request, 'car_form.html', {'form': form, 'title': 'Add New Car'})

@login_required
@admin_required
def edit_car(request, car_id):
    """Admin view to edit a car"""
    car = get_object_or_404(Car, id=car_id)
    
    if request.method == 'POST':
        form = CarForm(request.POST, instance=car)
        if form.is_valid():
            car = form.save()
            messages.success(request, f"{car.make} {car.model} updated successfully!")
            return redirect('admin_cars')
    else:
        form = CarForm(instance=car)
    
    return render(request, 'car_form.html', {
        'form': form,
        'title': f'Edit Car: {car.make} {car.model}',
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
            messages.error(request, f"Cannot delete {car_name} as it has reservations.")
        else:
            car.delete()
            messages.success(request, f"{car_name} deleted successfully!")
        return redirect('admin_cars')
    
    return render(request, 'delete_car.html', {
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
    
    # Create a list of dictionaries with reservation, user, and car data
    reservation_data = []
    for reservation in reservations:
        reservation_data.append({
            'reservation': reservation,
            'user': reservation.user,
            'car': reservation.car
        })
    
    return render(request, 'admin/reservations_django.html', {
        'reservations': reservation_data
    })

@login_required
@admin_required
def update_reservation_status(request, reservation_id, status):
    """Admin view to update reservation status"""
    valid_statuses = ['pending', 'confirmed', 'completed', 'cancelled']
    
    if status not in valid_statuses:
        messages.error(request, "Invalid status")
        return redirect('admin_reservations')
    
    reservation = get_object_or_404(Reservation, id=reservation_id)
    old_status = reservation.status
    reservation.status = status
    
    # Update payment status if needed
    if status == 'cancelled' and reservation.payment_status == 'paid':
        reservation.payment_status = 'refunded'
    
    reservation.save()
    
    messages.success(request, f"Reservation #{reservation_id} updated from {old_status} to {status}")
    return redirect('admin_reservations')

@login_required
@admin_required
def admin_users(request):
    """Admin view to manage users"""
    users = User.objects.all().order_by('-id')
    
    return render(request, 'admin/users_django.html', {'users': users})

@login_required
@admin_required
def admin_payments(request):
    """Admin view to manage payments"""
    # Get all reservations with payment status of 'paid' or 'refunded'
    reservations = Reservation.objects.filter(
        payment_status__in=['paid', 'refunded', 'pending']
    ).select_related('user', 'car').order_by('-created_at')
    
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
    
    # Total refunds
    refunded_amount = Reservation.objects.filter(
        payment_status='refunded'
    ).aggregate(Sum('total_price'))['total_price__sum'] or 0
    
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
            'payment_method': 'credit_card',  # Default method
            'card_last4': '1234',  # Placeholder
        }
        
        # Add different payment methods randomly for demonstration
        if reservation.id % 4 == 0:
            payment['payment_method'] = 'visa'
        elif reservation.id % 4 == 1:
            payment['payment_method'] = 'mastercard'
        elif reservation.id % 4 == 2:
            payment['payment_method'] = 'amex'
        else:
            payment['payment_method'] = 'discover'
            
        payments.append(payment)
    
    context = {
        'payments': payments,
        'daily_revenue': daily_revenue,
        'weekly_revenue': weekly_revenue,
        'monthly_revenue': monthly_revenue,
        'total_revenue': total_revenue,
        'refunded_amount': refunded_amount,
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
        'card_last4': '1234',
        'card_holder_name': f"{reservation.user.first_name} {reservation.user.last_name}",
        'card_expiry_month': '12',
        'card_expiry_year': '2025',
    }
    
    # Add refund details if applicable
    if payment['status'] == 'refunded':
        payment['refund_date'] = reservation.created_at + timedelta(days=2)  # Placeholder
        payment['refund_amount'] = payment['amount']
        payment['refund_transaction_id'] = f"R{reservation.id:06d}"
        payment['refund_reason'] = "Customer requested cancellation"
        payment['final_amount'] = 0
    
    # Add error details if applicable
    if payment['status'] == 'failed':
        payment['error_date'] = reservation.created_at
        payment['error_code'] = "CARD_DECLINED"
        payment['error_message'] = "The card was declined by the issuer."
    
    # Calculate reservation duration in days
    start_date = reservation.start_date
    end_date = reservation.end_date
    days = (end_date - start_date).days
    
    # Add reservation details
    payment['reservation'].days = days
    payment['reservation'].subtotal = reservation.car.daily_rate * days
    
    # Add tax calculation (for demo purposes)
    tax_rate = 8.5  # Example tax rate
    payment['reservation'].tax_rate = tax_rate
    # Convert to Decimal for proper calculation with Decimal subtotal
    from decimal import Decimal
    payment['reservation'].tax_amount = payment['reservation'].subtotal * (Decimal(str(tax_rate)) / Decimal('100'))
    
    # Get reservation user's stats
    user_reservations_count = Reservation.objects.filter(user=reservation.user).count()
    payment['user'].total_reservations = user_reservations_count
    
    # Add current datetime for the receipt
    current_datetime = timezone.now()
    
    context = {
        'payment': payment,
        'current_datetime': current_datetime,
    }
    
    return render(request, 'admin/payment_detail_django.html', context)

@login_required
@admin_required
def print_receipt(request, payment_id):
    """View to print a payment receipt"""
    # Reuse the payment_details view but render a different template
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
        'card_last4': '1234',
    }
    
    # Add refund details if applicable
    if payment['status'] == 'refunded':
        payment['refund_date'] = reservation.created_at + timedelta(days=2)
        payment['refund_amount'] = payment['amount']
        payment['final_amount'] = 0
    
    # Calculate reservation duration in days
    days = (reservation.end_date - reservation.start_date).days
    payment['reservation'].days = days
    payment['reservation'].subtotal = reservation.car.daily_rate * days
    
    # Add tax calculation
    tax_rate = 8.5
    payment['reservation'].tax_rate = tax_rate
    # Convert to Decimal for proper calculation with Decimal subtotal
    from decimal import Decimal
    payment['reservation'].tax_amount = payment['reservation'].subtotal * (Decimal(str(tax_rate)) / Decimal('100'))
    
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
        messages.error(request, "Only paid reservations can be refunded.")
        return redirect('payment_details', payment_id=payment_id)
    
    # Process the refund
    reservation.payment_status = 'refunded'
    reservation.status = 'cancelled'
    reservation.save()
    
    messages.success(request, f"Payment #{payment_id} has been refunded successfully.")
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
        messages.error(request, "Only pending payments can be marked as paid.")
        return redirect('payment_details', payment_id=payment_id)
    
    # Mark as paid
    reservation.payment_status = 'paid'
    if reservation.status == 'pending':
        reservation.status = 'confirmed'
    reservation.save()
    
    messages.success(request, f"Payment #{payment_id} has been marked as paid.")
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
        messages.error(request, "Only pending payments can be cancelled.")
        return redirect('payment_details', payment_id=payment_id)
    
    # Cancel the payment and reservation
    reservation.payment_status = 'cancelled'
    reservation.status = 'cancelled'
    reservation.save()
    
    messages.success(request, f"Payment #{payment_id} has been cancelled.")
    return redirect('payment_details', payment_id=payment_id)

@login_required
@admin_required
def download_receipt(request, payment_id):
    """Download a payment receipt as PDF"""
    # This would generate a PDF in a real application
    # For this demo, we'll just redirect to the print view
    messages.info(request, "PDF download functionality would be implemented here.")
    return redirect('print_receipt', payment_id=payment_id)

@login_required
@admin_required
def add_manual_payment(request):
    """Add a manual payment entry"""
    # Get all users for the select dropdown
    users = User.objects.all().order_by('first_name', 'last_name')
    reservations = None
    selected_user = None
    
    if request.method == 'POST':
        # Get the form data
        form = ManualPaymentForm(request.POST)
        user_id = request.POST.get('user_id')
        reservation_id = request.POST.get('reservation_id')
        
        if user_id:
            selected_user = get_object_or_404(User, id=user_id)
            # Get all pending reservations for this user
            reservations = Reservation.objects.filter(
                user=selected_user,
                payment_status='pending'
            ).order_by('-created_at')
        
        # If form is valid and a reservation was selected
        if form.is_valid() and reservation_id:
            reservation = get_object_or_404(Reservation, id=reservation_id)
            
            # Update reservation payment status
            reservation.payment_status = 'paid'
            if reservation.status == 'pending':
                reservation.status = 'confirmed'
            
            # If the amount is different than the reservation total, update it
            amount = form.cleaned_data['amount']
            if amount != reservation.total_price:
                reservation.total_price = amount
            
            reservation.save()
            
            # Add a success message
            payment_id = f"P{reservation.id:06d}"
            messages.success(
                request, 
                f"Manual payment of ${amount} has been recorded for reservation #{reservation.id}"
            )
            
            # Redirect to payment details
            return redirect('payment_details', payment_id=payment_id)
            
    else:
        form = ManualPaymentForm()
        
    return render(request, 'admin/add_payment_django.html', {
        'form': form,
        'users': users,
        'reservations': reservations,
        'selected_user': selected_user
    })