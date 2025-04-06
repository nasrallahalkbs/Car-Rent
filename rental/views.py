from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.db.models import Q, Avg
from django.contrib import messages
from django.utils import timezone
from datetime import date, timedelta
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt, ensure_csrf_cookie

from .models import User, Car, Reservation, Review, CartItem
from .forms import (RegisterForm, LoginForm, CarSearchForm, ReservationForm, 
                   CheckoutForm, ReviewForm, ProfileForm)
from .utils import calculate_total_price, get_car_availability, get_unavailable_dates

def index(request):
    """Home page view"""
    # Get featured cars based on various criteria
    # First, try to include some luxury cars if available
    luxury_cars = Car.objects.filter(is_available=True, category='Luxury').order_by('?')[:2]
    
    # Add some economy/compact cars for balance
    economy_cars = Car.objects.filter(
        is_available=True, 
        category__in=['Economy', 'Compact']
    ).order_by('?')[:2]
    
    # Add a few more random cars to complete the selection
    remaining_count = 6 - (luxury_cars.count() + economy_cars.count())
    if remaining_count > 0:
        # Exclude cars already selected
        excluded_ids = list(luxury_cars.values_list('id', flat=True)) + list(economy_cars.values_list('id', flat=True))
        remaining_cars = Car.objects.filter(is_available=True).exclude(id__in=excluded_ids).order_by('?')[:remaining_count]
    else:
        remaining_cars = Car.objects.none()
    
    # Combine the querysets
    featured_cars = list(luxury_cars) + list(economy_cars) + list(remaining_cars)
    
    # If no cars found through this method, fall back to newest cars
    if not featured_cars:
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

@ensure_csrf_cookie
def login_view(request):
    """User login view"""
    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f'مرحباً بعودتك، {user.first_name if user.first_name else user.username}!')
                return redirect('index')
        else:
            # Print form errors to help debugging
            print(f"Form errors: {form.errors}")
            messages.error(request, 'فشل تسجيل الدخول. يرجى التحقق من اسم المستخدم وكلمة المرور.')
    else:
        form = LoginForm()
    
    return render(request, 'login_django.html', {'form': form})

def logout_view(request):
    """User logout view"""
    logout(request)
    messages.success(request, 'You have been logged out.')
    return redirect('index')

@login_required
def profile_view(request):
    """User profile view"""
    user = request.user
    if request.method == 'POST':
        form = ProfileForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('profile')
    else:
        form = ProfileForm(instance=user)
    
    # Get user's reservations for display
    reservations = Reservation.objects.filter(user=user).order_by('-created_at')[:5]
    
    return render(request, 'profile.html', {
        'form': form,
        'user': user,
        'reservations': reservations
    })

def car_listing(request):
    """Car listing page with search functionality"""
    form = CarSearchForm(request.GET or None)
    cars = Car.objects.filter(is_available=True)
    
    # Apply filters if provided
    if form.is_valid():
        # Category filter
        category = form.cleaned_data.get('category')
        if category:
            cars = cars.filter(category=category)
        
        # Transmission filter
        transmission = form.cleaned_data.get('transmission')
        if transmission:
            cars = cars.filter(transmission=transmission)
        
        # Fuel type filter
        fuel_type = form.cleaned_data.get('fuel_type')
        if fuel_type:
            cars = cars.filter(fuel_type=fuel_type)
        
        # Price range filter
        min_price = form.cleaned_data.get('min_price')
        if min_price is not None:
            cars = cars.filter(daily_rate__gte=min_price)
        
        max_price = form.cleaned_data.get('max_price')
        if max_price is not None:
            cars = cars.filter(daily_rate__lte=max_price)
    
    # Get average rating for each car
    for car in cars:
        avg_rating = Review.objects.filter(car=car).aggregate(Avg('rating'))['rating__avg']
        car.avg_rating = round(avg_rating) if avg_rating else 0
    
    return render(request, 'cars_django.html', {
        'cars': cars,
        'form': form
    })

def car_detail(request, car_id):
    """Car detail page with reservation form"""
    car = get_object_or_404(Car, id=car_id)
    
    # Get average rating
    avg_rating = Review.objects.filter(car=car).aggregate(Avg('rating'))['rating__avg']
    car.avg_rating = round(avg_rating) if avg_rating else 0
    
    # Get reviews for this car
    reviews = Review.objects.filter(car=car).order_by('-created_at')
    
    # Get rating distribution
    rating_distribution = {
        1: Review.objects.filter(car=car, rating=1).count(),
        2: Review.objects.filter(car=car, rating=2).count(),
        3: Review.objects.filter(car=car, rating=3).count(),
        4: Review.objects.filter(car=car, rating=4).count(),
        5: Review.objects.filter(car=car, rating=5).count(),
    }
    # Calculate total reviews for percentage
    total_reviews = sum(rating_distribution.values())
    if total_reviews > 0:
        for rating in rating_distribution:
            rating_distribution[rating] = (rating_distribution[rating] / total_reviews) * 100
    
    # Get similar cars (same category, different car)
    similar_cars = Car.objects.filter(
        category=car.category, 
        is_available=True
    ).exclude(id=car_id)[:3]
    
    # Calculate average rating for similar cars
    for similar_car in similar_cars:
        similar_avg_rating = Review.objects.filter(car=similar_car).aggregate(Avg('rating'))['rating__avg']
        similar_car.avg_rating = round(similar_avg_rating) if similar_avg_rating else 0
    
    if request.method == 'POST':
        # Handle reservation request
        form = ReservationForm(request.POST)
        if form.is_valid():
            # Check if user is authenticated
            if not request.user.is_authenticated:
                messages.warning(request, 'Please login to make a reservation.')
                return redirect('login')
            
            # Get form data
            start_date = form.cleaned_data['start_date']
            end_date = form.cleaned_data['end_date']
            
            # Check if car is available for the requested dates
            if get_car_availability(car_id, start_date, end_date):
                # Calculate total price
                total_price = calculate_total_price(car, start_date, end_date)
                
                # Add to cart
                cart_item = CartItem(
                    user=request.user,
                    car=car,
                    start_date=start_date,
                    end_date=end_date
                )
                cart_item.save()
                
                messages.success(request, f"{car.make} {car.model} added to cart!")
                return redirect('cart')
            else:
                messages.error(request, "Sorry, this car is not available for the selected dates.")
    else:
        form = ReservationForm(initial={'car_id': car_id})
    
    return render(request, 'car_detail_django.html', {
        'car': car,
        'form': form,
        'reviews': reviews,
        'avg_rating': car.avg_rating,
        'rating_distribution': rating_distribution,
        'similar_cars': similar_cars,
        'total_reviews': total_reviews
    })

@login_required
def cart_view(request):
    """Shopping cart view"""
    cart_items = CartItem.objects.filter(user=request.user)
    
    # Calculate total price, days, and enhance cart items with additional information
    cart_total = 0
    total_days = 0
    
    for item in cart_items:
        # Calculate days for this rental
        delta = (item.end_date - item.start_date).days
        item.days = delta
        total_days += delta
        
        # Calculate total price
        item.total = calculate_total_price(item.car, item.start_date, item.end_date)
        cart_total += item.total
    
    return render(request, 'cart_django.html', {
        'cart_items': cart_items,
        'cart_total': cart_total,
        'total_days': total_days,
        'has_discounts': False  # Set to True if you implement discounts later
    })

@login_required
def remove_from_cart(request, item_id):
    """Remove item from cart"""
    item = get_object_or_404(CartItem, id=item_id, user=request.user)
    item.delete()
    messages.success(request, "Item removed from cart.")
    return redirect('cart')

@login_required
def checkout(request):
    """Checkout and payment view"""
    cart_items = CartItem.objects.filter(user=request.user)
    
    # Redirect back to cart if empty
    if not cart_items.exists():
        messages.warning(request, "Your cart is empty.")
        return redirect('cart')
    
    # Calculate total price
    total = 0
    for item in cart_items:
        item.total_price = calculate_total_price(item.car, item.start_date, item.end_date)
        total += item.total_price
    
    if request.method == 'POST':
        form = CheckoutForm(request.POST)
        if form.is_valid():
            # Process each cart item and create reservations
            for item in cart_items:
                reservation = Reservation(
                    user=request.user,
                    car=item.car,
                    start_date=item.start_date,
                    end_date=item.end_date,
                    total_price=calculate_total_price(item.car, item.start_date, item.end_date),
                    status='confirmed',
                    payment_status='paid'
                )
                reservation.save()
                
                # Remove from cart
                item.delete()
            
            messages.success(request, "Your reservation has been confirmed! Thank you for your business.")
            return redirect('confirmation')
    else:
        form = CheckoutForm()
    
    return render(request, 'checkout.html', {
        'form': form,
        'cart_items': cart_items,
        'total': total
    })

def confirmation(request):
    """Order confirmation page"""
    # Show the latest confirmed reservation
    if request.user.is_authenticated:
        reservation = Reservation.objects.filter(
            user=request.user, 
            status='confirmed'
        ).order_by('-created_at').first()
        
        return render(request, 'confirmation.html', {
            'reservation': reservation
        })
    else:
        return redirect('index')

@login_required
def my_reservations(request):
    """User's reservations page"""
    # Get all reservations for the user
    reservations = Reservation.objects.filter(user=request.user).order_by('-created_at')
    
    # Group by status
    upcoming = reservations.filter(start_date__gte=date.today(), status__in=['confirmed', 'pending'])
    past = reservations.filter(Q(end_date__lt=date.today()) | Q(status='completed'))
    cancelled = reservations.filter(status='cancelled')
    
    return render(request, 'my_reservations.html', {
        'upcoming': upcoming,
        'past': past,
        'cancelled': cancelled
    })

@login_required
def reservation_detail(request, reservation_id):
    """Detailed view of a single reservation"""
    reservation = get_object_or_404(Reservation, id=reservation_id, user=request.user)
    
    # Check if the user has left a review for this reservation
    has_reviewed = Review.objects.filter(user=request.user, reservation=reservation).exists()
    
    # Calculate the number of days for this reservation
    days = (reservation.end_date - reservation.start_date).days
    
    return render(request, 'reservation_detail.html', {
        'reservation': reservation,
        'days': days,
        'has_reviewed': has_reviewed
    })

@login_required
def modify_reservation(request, reservation_id):
    """Modify an existing reservation"""
    reservation = get_object_or_404(Reservation, id=reservation_id, user=request.user)
    
    # Only allow modification of pending or confirmed reservations
    if reservation.status not in ['pending', 'confirmed']:
        messages.error(request, "This reservation cannot be modified.")
        return redirect('reservation_detail', reservation_id=reservation_id)
    
    # Check if the reservation start date is in the past
    if reservation.start_date < date.today():
        messages.error(request, "Reservations that have already started cannot be modified.")
        return redirect('reservation_detail', reservation_id=reservation_id)
    
    if request.method == 'POST':
        form = ReservationForm(request.POST)
        if form.is_valid():
            # Get new dates
            new_start_date = form.cleaned_data['start_date']
            new_end_date = form.cleaned_data['end_date']
            
            # Check if the dates are valid
            if new_start_date < date.today():
                messages.error(request, "Start date cannot be in the past.")
                return redirect('modify_reservation', reservation_id=reservation_id)
            
            if new_end_date <= new_start_date:
                messages.error(request, "End date must be after start date.")
                return redirect('modify_reservation', reservation_id=reservation_id)
            
            # Check if car is available for the new dates (excluding this reservation)
            if get_car_availability(reservation.car.id, new_start_date, new_end_date, exclude_reservation=reservation_id):
                # Calculate new total price
                new_total_price = calculate_total_price(reservation.car, new_start_date, new_end_date)
                
                # Update reservation
                reservation.start_date = new_start_date
                reservation.end_date = new_end_date
                reservation.total_price = new_total_price
                reservation.save()
                
                messages.success(request, "Reservation modified successfully!")
                return redirect('reservation_detail', reservation_id=reservation_id)
            else:
                messages.error(request, "Car is not available for the selected dates.")
        else:
            messages.error(request, "Invalid form submission. Please check the dates.")
    else:
        # Pre-fill form with current reservation data
        form = ReservationForm(initial={
            'car_id': reservation.car.id,
            'start_date': reservation.start_date,
            'end_date': reservation.end_date
        })
    
    return render(request, 'modify_reservation.html', {
        'form': form,
        'reservation': reservation
    })

@login_required
def cancel_reservation(request, reservation_id):
    """Cancel a reservation"""
    reservation = get_object_or_404(Reservation, id=reservation_id, user=request.user)
    
    # Only allow cancellation of pending or confirmed reservations
    if reservation.status not in ['pending', 'confirmed']:
        messages.error(request, "This reservation cannot be cancelled.")
        return redirect('reservation_detail', reservation_id=reservation_id)
    
    # Check if the reservation start date is in the past
    if reservation.start_date < date.today():
        messages.error(request, "Reservations that have already started cannot be cancelled.")
        return redirect('reservation_detail', reservation_id=reservation_id)
    
    if request.method == 'POST':
        # Update status to cancelled
        reservation.status = 'cancelled'
        reservation.payment_status = 'refunded'
        reservation.save()
        
        messages.success(request, "Reservation cancelled successfully. Any payment will be refunded.")
        return redirect('my_reservations')
    
    return render(request, 'cancel_reservation.html', {
        'reservation': reservation
    })

@login_required
def add_review(request, reservation_id):
    """Add review for a completed reservation"""
    reservation = get_object_or_404(Reservation, id=reservation_id, user=request.user)
    
    # Check if the reservation is eligible for review
    if reservation.status != 'completed':
        messages.error(request, "You can only review completed reservations.")
        return redirect('reservation_detail', reservation_id=reservation_id)
    
    # Check if a review already exists
    existing_review = Review.objects.filter(user=request.user, reservation=reservation).first()
    if existing_review:
        messages.warning(request, "You have already reviewed this reservation.")
        return redirect('reservation_detail', reservation_id=reservation_id)
    
    if request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.user = request.user
            review.car = reservation.car
            review.reservation = reservation
            review.save()
            
            messages.success(request, "Thank you for your review!")
            return redirect('reservation_detail', reservation_id=reservation_id)
    else:
        form = ReviewForm()
    
    return render(request, 'add_review.html', {
        'form': form,
        'reservation': reservation,
        'car': reservation.car
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

def about_us(request):
    """About Us page view"""
    return render(request, "about_us.html")

def get_unavailable_dates_api(request, car_id):
    """API endpoint to get unavailable dates for a car"""
    try:
        # Get the car
        car = get_object_or_404(Car, id=car_id)
        
        # Get unavailable dates
        unavailable_dates = get_unavailable_dates(car_id)
        
        # Format data for response
        data = {
            'unavailable_dates': [
                {
                    'start': start_date.strftime('%Y-%m-%d'),
                    'end': end_date.strftime('%Y-%m-%d')
                }
                for start_date, end_date in unavailable_dates
            ]
        }
        
        return JsonResponse(data)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)
