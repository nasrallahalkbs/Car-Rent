from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.db.models import Q, Avg
from django.contrib import messages
from django.utils import timezone
from datetime import date, timedelta

from .models import User, Car, Reservation, Review, CartItem
from .forms import (RegisterForm, LoginForm, CarSearchForm, ReservationForm, 
                   CheckoutForm, ReviewForm, ProfileForm)
from .utils import calculate_total_price, get_car_availability, get_unavailable_dates

def index(request):
    """Home page view"""
    # Get featured cars (newest or by some other criteria)
    featured_cars = Car.objects.filter(is_available=True).order_by('-id')[:6]
    return render(request, 'django_index.html', {'featured_cars': featured_cars})

def register_view(request):
    """User registration view"""
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Account created successfully!')
            return redirect('index')
    else:
        form = RegisterForm()
    
    return render(request, 'register_django.html', {'form': form})

def login_view(request):
    """User login view"""
    if request.method == 'POST':
        form = LoginForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            next_url = request.GET.get('next', 'index')
            return redirect(next_url)
    else:
        form = LoginForm()
    
    return render(request, 'login_django.html', {'form': form})

def logout_view(request):
    """User logout view"""
    logout(request)
    return redirect('index')

@login_required
def profile_view(request):
    """User profile view"""
    if request.method == 'POST':
        form = ProfileForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('profile')
    else:
        form = ProfileForm(instance=request.user)
    
    return render(request, 'profile.html', {'form': form})

def car_listing(request):
    """Car listing page with search functionality"""
    # Initialize the search form
    form = CarSearchForm(request.GET)
    
    # Start with all available cars
    cars = Car.objects.filter(is_available=True)
    
    # Apply filters if form is valid
    if form.is_valid():
        category = form.cleaned_data.get('category')
        transmission = form.cleaned_data.get('transmission')
        fuel_type = form.cleaned_data.get('fuel_type')
        min_price = form.cleaned_data.get('min_price')
        max_price = form.cleaned_data.get('max_price')
        
        # Apply category filter
        if category:
            cars = cars.filter(category=category)
        
        # Apply transmission filter
        if transmission:
            cars = cars.filter(transmission=transmission)
        
        # Apply fuel type filter
        if fuel_type:
            cars = cars.filter(fuel_type=fuel_type)
        
        # Apply price range filters
        if min_price is not None:
            cars = cars.filter(daily_rate__gte=min_price)
        
        if max_price is not None:
            cars = cars.filter(daily_rate__lte=max_price)
    
    return render(request, 'cars_django.html', {'cars': cars, 'form': form})

def car_detail(request, car_id):
    """Car detail page with reservation form"""
    car = get_object_or_404(Car, id=car_id)
    reviews = Review.objects.filter(car=car).order_by('-created_at')
    
    # Calculate average rating
    avg_rating = reviews.aggregate(Avg('rating'))['rating__avg'] or 0
    
    # Initialize reservation form
    form = ReservationForm(initial={'car_id': car.id})
    
    # Get unavailable dates for this car
    unavailable_dates = get_unavailable_dates(car.id)
    
    # Get similar cars (same category, excluding current car)
    similar_cars = Car.objects.filter(
        category=car.category, 
        is_available=True
    ).exclude(id=car.id).order_by('?')[:3]  # Randomize and limit to 3
    
    # Calculate rating distribution
    rating_distribution = []
    if reviews.exists():
        for i in range(5, 0, -1):
            count = reviews.filter(rating=i).count()
            percentage = (count / reviews.count()) * 100
            rating_distribution.append({
                'rating': i,
                'count': count,
                'percentage': percentage
            })
    
    if request.method == 'POST' and request.user.is_authenticated:
        form = ReservationForm(request.POST)
        
        if form.is_valid():
            start_date = form.cleaned_data['start_date']
            end_date = form.cleaned_data['end_date']
            
            # Check if car is available for these dates
            if get_car_availability(car.id, start_date, end_date):
                # Add to cart
                cart_item = CartItem(
                    user=request.user,
                    car=car,
                    start_date=start_date,
                    end_date=end_date
                )
                cart_item.save()
                
                messages.success(request, f"{car.make} {car.model} added to your cart!")
                return redirect('cart')
            else:
                messages.error(request, "Sorry, this car is not available for the selected dates.")
    
    context = {
        'car': car,
        'reviews': reviews,
        'avg_rating': avg_rating,
        'form': form,
        'unavailable_dates': unavailable_dates,
        'similar_cars': similar_cars,
        'rating_distribution': rating_distribution,
    }
    
    return render(request, 'car_detail_django.html', context)

@login_required
def cart_view(request):
    """Shopping cart view"""
    cart_items = CartItem.objects.filter(user=request.user).select_related('car')
    
    # Calculate totals for each item
    for item in cart_items:
        item.days = (item.end_date - item.start_date).days + 1
        item.total = item.days * item.car.daily_rate
    
    # Calculate overall total
    cart_total = sum(item.total for item in cart_items)
    
    return render(request, 'cart_django.html', {
        'cart_items': cart_items,
        'cart_total': cart_total
    })

@login_required
def remove_from_cart(request, item_id):
    """Remove item from cart"""
    cart_item = get_object_or_404(CartItem, id=item_id, user=request.user)
    car_name = f"{cart_item.car.make} {cart_item.car.model}"
    cart_item.delete()
    
    messages.success(request, f"{car_name} removed from your cart.")
    return redirect('cart')

@login_required
def checkout(request):
    """Checkout and payment view"""
    # Get user's cart items
    cart_items = CartItem.objects.filter(user=request.user).select_related('car')
    
    if not cart_items:
        messages.error(request, "Your cart is empty.")
        return redirect('cart')
    
    # Calculate totals for each item
    for item in cart_items:
        item.days = (item.end_date - item.start_date).days + 1
        item.total = item.days * item.car.daily_rate
    
    # Calculate overall total
    cart_total = sum(item.total for item in cart_items)
    
    if request.method == 'POST':
        form = CheckoutForm(request.POST)
        
        if form.is_valid():
            # Process payment (this would normally involve a payment gateway)
            # For now, just create reservations and clear the cart
            
            for cart_item in cart_items:
                # Create reservation
                reservation = Reservation(
                    user=request.user,
                    car=cart_item.car,
                    start_date=cart_item.start_date,
                    end_date=cart_item.end_date,
                    total_price=cart_item.total,
                    status='confirmed',
                    payment_status='paid'
                )
                reservation.save()
                
                # Delete cart item
                cart_item.delete()
            
            messages.success(request, "Payment successful! Your reservations are confirmed.")
            return redirect('confirmation')
    else:
        form = CheckoutForm()
    
    return render(request, 'checkout.html', {
        'form': form,
        'cart_items': cart_items,
        'cart_total': cart_total
    })

@login_required
def confirmation(request):
    """Order confirmation page"""
    # Get user's recent reservations
    recent_reservations = Reservation.objects.filter(
        user=request.user
    ).order_by('-created_at')[:5]
    
    return render(request, 'confirmation.html', {
        'reservations': recent_reservations
    })

@login_required
def my_reservations(request):
    """User's reservations page"""
    reservations = Reservation.objects.filter(
        user=request.user
    ).select_related('car').order_by('-created_at')
    
    # Separate active and completed reservations
    active_reservations = [r for r in reservations if r.status in ['pending', 'confirmed']]
    completed_reservations = [r for r in reservations if r.status in ['completed', 'cancelled']]
    
    # Calculate duration in days for each reservation
    for reservation in reservations:
        reservation.days = (reservation.end_date - reservation.start_date).days + 1
    
    return render(request, 'my_reservations.html', {
        'reservations': reservations,
        'active_reservations': active_reservations,
        'completed_reservations': completed_reservations
    })

@login_required
def reservation_detail(request, reservation_id):
    """Detailed view of a single reservation"""
    reservation = get_object_or_404(
        Reservation, 
        id=reservation_id, 
        user=request.user
    )
    
    # Calculate duration in days
    reservation.days = (reservation.end_date - reservation.start_date).days + 1
    
    # Get existing review if any
    review = Review.objects.filter(
        reservation=reservation,
        user=request.user
    ).first()
    
    return render(request, 'reservation_detail.html', {
        'reservation': reservation,
        'review': review
    })

@login_required
def modify_reservation(request, reservation_id):
    """Modify an existing reservation"""
    reservation = get_object_or_404(
        Reservation, 
        id=reservation_id, 
        user=request.user
    )
    
    # Only allow modifications for pending or confirmed reservations
    if reservation.status not in ['pending', 'confirmed']:
        messages.error(request, "Sorry, you cannot modify a completed or cancelled reservation.")
        return redirect('reservation_detail', reservation_id=reservation.id)
    
    # Check if the car is still available
    car = reservation.car
    
    if request.method == 'POST':
        form = ReservationForm(request.POST)
        
        if form.is_valid():
            start_date = form.cleaned_data['start_date']
            end_date = form.cleaned_data['end_date']
            
            # Validate dates
            if start_date < date.today():
                messages.error(request, "Pick-up date cannot be in the past.")
                return redirect('modify_reservation', reservation_id=reservation.id)
            
            if end_date < start_date:
                messages.error(request, "Return date must be after the pick-up date.")
                return redirect('modify_reservation', reservation_id=reservation.id)
            
            # Check availability excluding the current reservation
            if not get_car_availability(car.id, start_date, end_date, exclude_reservation=reservation.id):
                messages.error(request, "Sorry, the car is not available for the selected dates.")
                return redirect('modify_reservation', reservation_id=reservation.id)
            
            # Calculate new total price
            new_total = calculate_total_price(car, start_date, end_date)
            
            # Update reservation
            reservation.start_date = start_date
            reservation.end_date = end_date
            reservation.total_price = new_total
            reservation.save()
            
            messages.success(request, "Your reservation has been updated successfully.")
            return redirect('reservation_detail', reservation_id=reservation.id)
    else:
        # Pre-fill the form with current reservation data
        form = ReservationForm(initial={
            'car_id': car.id,
            'start_date': reservation.start_date,
            'end_date': reservation.end_date
        })
    
    # Get unavailable dates excluding this reservation
    unavailable_dates = get_unavailable_dates(car.id, exclude_reservation=reservation.id)
    
    return render(request, 'modify_reservation.html', {
        'form': form,
        'reservation': reservation,
        'unavailable_dates': unavailable_dates
    })

@login_required
def cancel_reservation(request, reservation_id):
    """Cancel a reservation"""
    reservation = get_object_or_404(
        Reservation, 
        id=reservation_id, 
        user=request.user
    )
    
    # Only allow cancellation for pending or confirmed reservations
    if reservation.status not in ['pending', 'confirmed']:
        messages.error(request, "Sorry, you cannot cancel a completed or already cancelled reservation.")
        return redirect('reservation_detail', reservation_id=reservation.id)
    
    if request.method == 'POST':
        # Update reservation status
        reservation.status = 'cancelled'
        reservation.payment_status = 'refunded'  # In a real app, this would involve payment processing
        reservation.save()
        
        messages.success(request, "Your reservation has been cancelled successfully.")
        return redirect('my_reservations')
    
    return render(request, 'cancel_reservation.html', {
        'reservation': reservation
    })

@login_required
def add_review(request, reservation_id):
    """Add review for a completed reservation"""
    reservation = get_object_or_404(
        Reservation, 
        id=reservation_id, 
        user=request.user,
        status='completed'
    )
    
    # Check if user already reviewed this reservation
    existing_review = Review.objects.filter(
        reservation=reservation,
        user=request.user
    ).first()
    
    if existing_review:
        messages.error(request, "You have already reviewed this reservation.")
        return redirect('my_reservations')
    
    if request.method == 'POST':
        form = ReviewForm(request.POST)
        
        if form.is_valid():
            review = form.save(commit=False)
            review.user = request.user
            review.car = reservation.car
            review.reservation = reservation
            review.save()
            
            messages.success(request, "Thank you for your review!")
            return redirect('my_reservations')
    else:
        form = ReviewForm()
    
    return render(request, 'add_review.html', {
        'form': form,
        'reservation': reservation
    })

def toggle_dark_mode(request):
    """Toggle dark mode on/off"""
    dark_mode = request.session.get('dark_mode', False)
    request.session['dark_mode'] = not dark_mode
    
    # Return to previous page if available
    referer = request.META.get('HTTP_REFERER')
    if referer:
        return redirect(referer)
    else:
        return redirect('index')
        
from django.http import JsonResponse

def get_unavailable_dates_api(request, car_id):
    """API endpoint to get unavailable dates for a car"""
    try:
        # Get the car
        car = get_object_or_404(Car, id=car_id)
        
        # Get unavailable dates
        unavailable_dates = get_unavailable_dates(car_id)
        
        # Format dates for JSON response
        formatted_dates = []
        for start_date, end_date in unavailable_dates:
            formatted_dates.append([
                start_date.isoformat(),
                end_date.isoformat()
            ])
        
        return JsonResponse({
            'car_id': car_id,
            'car_name': f"{car.make} {car.model}",
            'dates': formatted_dates
        })
    except Exception as e:
        return JsonResponse({
            'error': str(e)
        }, status=400)