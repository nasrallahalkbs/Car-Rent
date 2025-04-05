from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Count, Avg, Sum
from django.utils import timezone
from datetime import timedelta

from .models import User, Car, Reservation, Review
from .forms import CarForm

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
    return render(request, 'admin/cars.html', {'cars': cars})

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
    
    return render(request, 'admin/car_form.html', {'form': form, 'title': 'Add New Car'})

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
    
    return render(request, 'admin/car_form.html', {
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
    
    # Create a list of dictionaries with reservation, user, and car data
    reservation_data = []
    for reservation in reservations:
        reservation_data.append({
            'reservation': reservation,
            'user': reservation.user,
            'car': reservation.car
        })
    
    return render(request, 'admin/reservations.html', {
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
    
    return render(request, 'admin/users.html', {'users': users})