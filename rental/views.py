from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.urls import reverse
from django.utils import timezone
from django.http import JsonResponse
from django.db.models import Q, Avg, Count
from django.core.paginator import Paginator
from .forms import LoginForm, RegisterForm, CarSearchForm, ReservationForm, CheckoutForm, ReviewForm, ProfileForm
from .models import User, Car, Reservation, Review, CartItem
from .utils import calculate_total_price, get_car_availability, get_unavailable_dates
from datetime import datetime, date, timedelta
import logging
import json

logger = logging.getLogger(__name__)

def index(request):
    """Home page view"""
    # Get featured cars (newest 6 cars)
    featured_cars = Car.objects.filter(is_available=True).order_by('-id')[:6]
    
    # Get cars by category
    categories = Car.CATEGORY_CHOICES
    category_cars = {}
    for category_tuple in categories:
        category = category_tuple[0]
        category_cars[category] = Car.objects.filter(category=category, is_available=True)[:4]
    
    context = {
        'featured_cars': featured_cars,
        'category_cars': category_cars,
    }
    
    # Choose template based on language setting
    language = request.session.get('language', 'ar')
    template = 'index.html' if language == 'en' else 'index_django.html'
    
    return render(request, template, context)

def register_view(request):
    """User registration view"""
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "تم التسجيل بنجاح!")
            return redirect('index')
    else:
        form = RegisterForm()
    
    return render(request, 'register_django.html', {'form': form})

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
                messages.success(request, "تم تسجيل الدخول بنجاح!")
                return redirect('index')
        else:
            messages.error(request, "خطأ في اسم المستخدم أو كلمة المرور!")
    else:
        form = LoginForm()
        
    return render(request, 'login_django.html', {'form': form})

def logout_view(request):
    """User logout view"""
    logout(request)
    messages.info(request, "تم تسجيل الخروج!")
    return redirect('index')

@login_required
def profile_view(request):
    """User profile view"""
    if request.method == 'POST':
        form = ProfileForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "تم تحديث الملف الشخصي بنجاح!")
            return redirect('profile')
    else:
        form = ProfileForm(instance=request.user)
    
    # Get reservation history
    reservations = Reservation.objects.filter(user=request.user).order_by('-created_at')[:5]
    
    context = {
        'form': form,
        'user': request.user,
        'reservations': reservations,
        'current_date': timezone.now(),
    }
    return render(request, 'profile.html', context)

def car_listing(request):
    """Car listing page with search functionality"""
    # Initialize search form
    form = CarSearchForm(request.GET)
    
    # Get all available cars by default, ordered by id for consistent pagination
    cars = Car.objects.filter(is_available=True).order_by('id')
    
    # Filter based on search criteria if form is valid
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
        max_price = form.cleaned_data.get('max_price')
        
        if min_price is not None:
            cars = cars.filter(daily_rate__gte=min_price)
        
        if max_price is not None:
            cars = cars.filter(daily_rate__lte=max_price)
    
    # Pagination
    paginator = Paginator(cars, 9)  # Show 9 cars per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'form': form,
        'cars': page_obj,
        'today': date.today(),
    }
    
    # Choose template based on language setting
    language = request.session.get('language', 'ar')
    template = 'cars.html' if language == 'en' else 'cars_django.html'
    
    return render(request, template, context)

def car_detail(request, car_id):
    """Car detail page with reservation form"""
    car = get_object_or_404(Car, id=car_id)
    
    # Get reviews for this car
    reviews = Review.objects.filter(car=car).order_by('-created_at')
    
    # Calculate average rating
    avg_rating = reviews.aggregate(Avg('rating'))['rating__avg'] or 0
    avg_rating = round(avg_rating, 1)
    
    # Calculate rating distribution (percentage for each star level)
    total_reviews = reviews.count()
    rating_distribution = {}
    
    if total_reviews > 0:
        for i in range(1, 6):
            count = reviews.filter(rating=i).count()
            percentage = (count / total_reviews) * 100
            rating_distribution[i] = percentage
    else:
        for i in range(1, 6):
            rating_distribution[i] = 0
    
    # Get similar cars (same category, exclude current car)
    similar_cars = Car.objects.filter(category=car.category).exclude(id=car.id)[:3]
    
    context = {
        'car': car,
        'reviews': reviews,
        'avg_rating': avg_rating,
        'total_reviews': total_reviews,
        'rating_distribution': rating_distribution,
        'similar_cars': similar_cars,
        'today': date.today(),
    }
    
    # Choose template based on language setting
    language = request.session.get('language', 'ar')
    template = 'car_detail.html' if language == 'en' else 'car_detail_django.html'
    
    return render(request, template, context)

@login_required
def cart_view(request):
    """Shopping cart view"""
    cart_items = CartItem.objects.filter(user=request.user)
    
    # Calculate total for each item and the grand total
    grand_total = 0
    total_days = 0
    for item in cart_items:
        # Calculate days (inclusive)
        delta = (item.end_date - item.start_date).days + 1
        item.days = delta
        total_days += delta
        item.total = item.car.daily_rate * delta
        grand_total += item.total
    
    context = {
        'cart_items': cart_items,
        'cart_total': grand_total,  # Make sure the key matches what's in the template
        'total_days': total_days,   # Add total days to the context
    }
    
    # Choose template based on language setting
    language = request.session.get('language', 'ar')
    template = 'cart.html' if language == 'en' else 'cart_django.html'
    
    return render(request, template, context)

@login_required
def add_to_cart(request):
    """Add a car to shopping cart"""
    if request.method != 'POST':
        return redirect('cars')
    
    car_id = request.POST.get('car_id')
    car = get_object_or_404(Car, id=car_id, is_available=True)
    
    start_date_str = request.POST.get('start_date')
    end_date_str = request.POST.get('end_date')
    
    try:
        start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
        end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
    except ValueError:
        messages.error(request, "تنسيق التاريخ غير صحيح. يرجى المحاولة مرة أخرى.")
        return redirect('car_detail', car_id=car_id)
    
    # Validate dates
    if start_date < date.today():
        messages.error(request, "لا يمكن حجز تاريخ في الماضي.")
        return redirect('car_detail', car_id=car_id)
    
    if end_date < start_date:
        messages.error(request, "يجب أن يكون تاريخ التسليم بعد تاريخ الاستلام.")
        return redirect('car_detail', car_id=car_id)
    
    # Check car availability
    if not get_car_availability(car_id, start_date, end_date):
        messages.error(request, "السيارة غير متاحة في التواريخ المحددة.")
        return redirect('car_detail', car_id=car_id)
    
    # Check if the same car with the same dates is already in cart
    existing_item = CartItem.objects.filter(
        user=request.user,
        car=car,
        start_date=start_date,
        end_date=end_date
    ).first()
    
    if existing_item:
        messages.info(request, "هذه السيارة موجودة بالفعل في سلة التسوق للتواريخ المحددة.")
    else:
        # Add to cart
        CartItem.objects.create(
            user=request.user,
            car=car,
            start_date=start_date,
            end_date=end_date
        )
        messages.success(request, "تمت إضافة السيارة إلى سلة التسوق!")
    
    return redirect('book_car', car_id=car_id)

@login_required
def remove_from_cart(request, item_id):
    """Remove item from cart"""
    item = get_object_or_404(CartItem, id=item_id, user=request.user)
    item.delete()
    messages.success(request, "تمت إزالة العنصر من السلة!")
    return redirect('cart')

@login_required
def checkout(request):
    """Checkout and payment view"""
    # Check if coming from a specific reservation (direct payment)
    reservation_id = request.GET.get('reservation_id')
    
    if reservation_id:
        # User is paying for a specific reservation
        reservation = get_object_or_404(
            Reservation, 
            id=reservation_id, 
            user=request.user, 
            status='confirmed', 
            payment_status='pending'
        )
        
        # Create form for the payment
        if request.method == 'POST':
            form = CheckoutForm(request.POST)
            if form.is_valid():
                # Process payment (in a real app, this would integrate with a payment gateway)
                # For now, just mark the reservation as paid and set status to completed
                reservation.payment_status = 'paid'
                
                # Once paid, update status to completed if it was confirmed
                if reservation.status == 'confirmed':
                    reservation.status = 'completed'
                
                reservation.save()
                
                messages.success(request, "تم إتمام عملية الدفع بنجاح!")
                
                # Store reservation ID in session for confirmation page
                request.session['last_paid_reservation_id'] = reservation.id
                
                return redirect('confirmation')
        else:
            form = CheckoutForm()
        
        context = {
            'form': form,
            'reservation': reservation,
        }
        
        return render(request, 'checkout.html', context)
    else:
        # User is checking out items from cart
        cart_items = CartItem.objects.filter(user=request.user)
        
        if not cart_items:
            messages.warning(request, "السلة فارغة!")
            return redirect('cart')
        
        # Calculate totals
        grand_total = 0
        for item in cart_items:
            delta = (item.end_date - item.start_date).days + 1
            item.days = delta
            item.total = item.car.daily_rate * delta
            grand_total += item.total
        
        if request.method == 'POST':
            form = CheckoutForm(request.POST)
            if form.is_valid():
                # Create reservations for all cart items
                for item in cart_items:
                    # Check again if car is available (in case someone else booked it)
                    if get_car_availability(item.car.id, item.start_date, item.end_date):
                        total_price = calculate_total_price(item.car, item.start_date, item.end_date)
                        
                        # Create reservation with pending status initially
                        reservation = Reservation.objects.create(
                            user=request.user,
                            car=item.car,
                            start_date=item.start_date,
                            end_date=item.end_date,
                            total_price=total_price,
                            status='pending',  # All reservations start as pending
                            payment_status='pending'
                        )
                    else:
                        messages.error(
                            request, 
                            f"عذرًا، السيارة {item.car.make} {item.car.model} لم تعد متاحة في التواريخ المحددة."
                        )
                        return redirect('cart')
                
                # Clear the cart
                cart_items.delete()
                
                messages.success(request, "تم إرسال طلب الحجز بنجاح! يرجى انتظار موافقة المسؤول.")
                return redirect('confirmation')
        else:
            form = CheckoutForm()
        
        context = {
            'form': form,
            'cart_items': cart_items,
            'cart_total': grand_total,
            'total_days': sum(item.days for item in cart_items),
        }
        
        return render(request, 'checkout.html', context)

@login_required
def confirmation(request):
    """Order confirmation page"""
    # Check if there's a specific reservation ID in the session (for payments)
    paid_reservation_id = request.session.get('last_paid_reservation_id')
    
    if paid_reservation_id:
        # Get the specific reservation that was just paid for
        reservation = get_object_or_404(Reservation, id=paid_reservation_id, user=request.user)
        # Clear the session variable
        del request.session['last_paid_reservation_id']
    else:
        # Otherwise get the most recent reservation for this user
        reservation = Reservation.objects.filter(user=request.user).order_by('-created_at').first()
    
    if not reservation:
        messages.warning(request, "لم يتم العثور على أي حجوزات!")
        return redirect('index')
    
    context = {
        'reservation': reservation,
    }
    
    # Choose template based on language setting
    language = request.session.get('language', 'ar')
    template = 'confirmation.html' if language == 'en' else 'confirmation_django.html'
    
    return render(request, template, context)

@login_required
def my_reservations(request):
    """User's reservations page"""
    reservations = Reservation.objects.filter(user=request.user).order_by('-created_at')
    
    context = {
        'reservations': reservations,
    }
    
    # Choose template based on language setting
    language = request.session.get('language', 'ar')
    template = 'my_reservations.html' if language == 'en' else 'my_reservations_django.html'
    
    return render(request, template, context)

@login_required
def reservation_detail(request, reservation_id):
    """Detailed view of a single reservation"""
    reservation = get_object_or_404(Reservation, id=reservation_id, user=request.user)
    
    # Check if user has already reviewed this reservation
    has_review = Review.objects.filter(reservation=reservation, user=request.user).exists()
    
    context = {
        'reservation': reservation,
        'has_review': has_review,
    }
    
    return render(request, 'reservation_detail.html', context)

@login_required
def modify_reservation(request, reservation_id):
    """Modify an existing reservation"""
    reservation = get_object_or_404(
        Reservation, 
        id=reservation_id, 
        user=request.user, 
        status='pending'  # Only pending reservations can be modified
    )
    
    if request.method == 'POST':
        form = ReservationForm(request.POST)
        if form.is_valid():
            start_date = form.cleaned_data['start_date']
            end_date = form.cleaned_data['end_date']
            
            # Check if the new dates are available
            if get_car_availability(reservation.car.id, start_date, end_date, exclude_reservation=reservation.id):
                # Update reservation
                reservation.start_date = start_date
                reservation.end_date = end_date
                reservation.total_price = calculate_total_price(reservation.car, start_date, end_date)
                reservation.save()
                
                messages.success(request, "تم تعديل الحجز بنجاح!")
                return redirect('reservation_detail', reservation_id=reservation.id)
            else:
                messages.error(request, "السيارة غير متاحة في التواريخ المحددة!")
    else:
        # Pre-fill form with current reservation data
        initial_data = {
            'car_id': reservation.car.id,
            'start_date': reservation.start_date,
            'end_date': reservation.end_date,
        }
        form = ReservationForm(initial=initial_data)
    
    context = {
        'form': form,
        'reservation': reservation,
        'today': date.today(),
    }
    
    return render(request, 'modify_reservation.html', context)

@login_required
def cancel_reservation(request, reservation_id):
    """Cancel a reservation"""
    reservation = get_object_or_404(
        Reservation, 
        id=reservation_id, 
        user=request.user, 
        status__in=['pending', 'confirmed']  # Only pending or confirmed reservations can be cancelled
    )
    
    if request.method == 'POST':
        reservation.status = 'cancelled'
        reservation.save()
        
        messages.success(request, "تم إلغاء الحجز بنجاح!")
        return redirect('my_reservations')
    
    context = {
        'reservation': reservation,
    }
    
    return render(request, 'cancel_reservation.html', context)

@login_required
def add_review(request, reservation_id):
    """Add review for a completed reservation"""
    reservation = get_object_or_404(
        Reservation, 
        id=reservation_id, 
        user=request.user, 
        status='completed',
        payment_status='paid'
    )
    
    # Check if user has already reviewed this reservation
    existing_review = Review.objects.filter(reservation=reservation, user=request.user).first()
    if existing_review:
        messages.warning(request, "لقد قمت بتقييم هذه الرحلة بالفعل!")
        return redirect('reservation_detail', reservation_id=reservation.id)
    
    if request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.user = request.user
            review.car = reservation.car
            review.reservation = reservation
            review.save()
            
            messages.success(request, "شكراً لتقييمك!")
            return redirect('car_detail', car_id=reservation.car.id)
    else:
        form = ReviewForm()
    
    context = {
        'form': form,
        'reservation': reservation,
    }
    
    return render(request, 'add_review.html', context)

def toggle_dark_mode(request):
    """Toggle dark mode on/off"""
    current_mode = request.session.get('dark_mode', False)
    request.session['dark_mode'] = not current_mode
    
    # Go back to the previous page
    referer = request.META.get('HTTP_REFERER')
    if referer:
        return redirect(referer)
    return redirect('index')

def toggle_language(request):
    """Toggle between Arabic and English languages"""
    current_language = request.session.get('language', 'ar')  # Default to Arabic if not set
    print(f"Current language: {current_language}")  # Debug log
    
    # Toggle between 'ar' and 'en'
    new_language = 'en' if current_language == 'ar' else 'ar'
    request.session['language'] = new_language
    
    # Force save session to ensure changes are persisted
    request.session.modified = True
    print(f"New language set to: {new_language}")  # Debug log
    
    # Add success message
    if new_language == 'ar':
        messages.success(request, "تم تغيير اللغة إلى العربية")
    else:
        messages.success(request, "Language changed to English successfully")
    
    # Go back to the previous page
    referer = request.META.get('HTTP_REFERER')
    print(f"Referer: {referer}")  # Debug log
    if referer:
        return redirect(referer)
    return redirect('index')

def about_us(request):
    """About Us page view"""
    # Choose template based on language setting
    language = request.session.get('language', 'ar')
    template = 'about_us.html' if language == 'en' else 'about_us_django.html'
    
    return render(request, template)

@login_required
def book_car(request, car_id):
    """View for booking a car directly from car detail page"""
    car = get_object_or_404(Car, id=car_id, is_available=True)
    
    # First check if there's a cart item for this car
    cart_item = CartItem.objects.filter(user=request.user, car=car).order_by('-created_at').first()
    
    start_date = None
    end_date = None
    
    # If we have a cart item, use its dates
    if cart_item:
        start_date = cart_item.start_date
        end_date = cart_item.end_date
    else:
        # Otherwise look for dates in GET parameters
        start_date_str = request.GET.get('start_date')
        end_date_str = request.GET.get('end_date')
        
        if start_date_str:
            try:
                start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
            except ValueError:
                pass
        
        if end_date_str:
            try:
                end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
            except ValueError:
                pass
    
    context = {
        'car': car,
        'start_date': start_date,
        'end_date': end_date,
        'today': date.today(),
        'cart_item': cart_item,  # Pass the cart item to the template
    }
    
    return render(request, 'booking.html', context)

@login_required
def process_booking(request):
    """Process the booking form submission"""
    if request.method != 'POST':
        return redirect('cars')
    
    car_id = request.POST.get('car_id')
    car = get_object_or_404(Car, id=car_id, is_available=True)
    
    start_date_str = request.POST.get('start_date')
    end_date_str = request.POST.get('end_date')
    notes = request.POST.get('notes', '')
    
    try:
        start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
        end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
    except ValueError:
        messages.error(request, "تنسيق التاريخ غير صحيح. يرجى المحاولة مرة أخرى.")
        return redirect('book_car', car_id=car_id)
    
    # Validate dates
    if start_date < date.today():
        messages.error(request, "لا يمكن حجز تاريخ في الماضي.")
        return redirect('book_car', car_id=car_id)
    
    if end_date < start_date:
        messages.error(request, "يجب أن يكون تاريخ التسليم بعد تاريخ الاستلام.")
        return redirect('book_car', car_id=car_id)
    
    # Check car availability
    if not get_car_availability(car_id, start_date, end_date):
        messages.error(request, "السيارة غير متاحة في التواريخ المحددة.")
        return redirect('book_car', car_id=car_id)
    
    # Calculate total price
    total_price = calculate_total_price(car, start_date, end_date)
    
    # Create reservation with pending status (awaiting admin approval)
    reservation = Reservation.objects.create(
        user=request.user,
        car=car,
        start_date=start_date,
        end_date=end_date,
        total_price=total_price,
        status='pending',
        payment_status='pending',
        notes=notes
    )
    
    # Remove the item from cart if it exists
    CartItem.objects.filter(
        user=request.user,
        car=car,
        start_date=start_date,
        end_date=end_date
    ).delete()
    
    messages.success(request, "تم إرسال طلب الحجز بنجاح! سيتم إشعارك عند مراجعة طلبك.")
    return redirect('confirmation')

def get_unavailable_dates_api(request, car_id):
    """API endpoint to get unavailable dates for a car"""
    unavailable_ranges = get_unavailable_dates(car_id)
    
    # Format the data for API response
    unavailable_dates = []
    for start_date, end_date in unavailable_ranges:
        unavailable_dates.append({
            'start': start_date.strftime('%Y-%m-%d'),
            'end': end_date.strftime('%Y-%m-%d')
        })
    
    return JsonResponse({'unavailable_dates': unavailable_dates})
