from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.urls import reverse
from django.utils import timezone
from django.http import JsonResponse
from django.db.models import Q, Avg, Count
from django.core.paginator import Paginator
from django.conf import settings
from django.utils.translation import gettext as _
from .forms import LoginForm, RegisterForm, CarSearchForm, ReservationForm, CheckoutForm, ReviewForm, ProfileForm
from .models import User, Car, Reservation, Review, CartItem
from .utils import calculate_total_price, get_car_availability, get_unavailable_dates
from datetime import datetime, date, timedelta
import logging
import json
import os.path

# تفعيل التسجيل لمتابعة العمليات المهمة
logger = logging.getLogger(__name__)

def check_expired_confirmations():
    """
    فحص الحجوزات المؤكدة التي انتهت صلاحيتها ولم يتم الدفع لها
    يتم استدعاء هذه الدالة عند الصفحات الرئيسية لتحديث حالات الحجوزات
    """
    # الحصول على الوقت الحالي
    now = timezone.now()

    # البحث عن الحجوزات المؤكدة التي انتهت صلاحية تأكيدها ولم يتم الدفع لها
    expired_reservations = Reservation.objects.filter(
        status='confirmed',
        payment_status='pending',
        confirmation_expiry__lt=now,  # تاريخ انتهاء الصلاحية قبل الوقت الحالي
        confirmation_expiry__isnull=False  # تأكد من وجود تاريخ انتهاء
    )

    # تسجيل عدد الحجوزات المنتهية للتتبع
    logger.info(f"Found {expired_reservations.count()} expired confirmed reservations.")

    # الإلغاء التلقائي للحجوزات المنتهية
    for reservation in expired_reservations:
        # تحديث حالة الحجز إلى "ملغي"
        reservation.status = 'cancelled'

        # تسجيل سبب الإلغاء في الملاحظات
        notes = reservation.notes or ""
        cancellation_reason = "تم الإلغاء تلقائياً بسبب عدم الدفع خلال 24 ساعة."
        if notes:
            notes += f"\n{cancellation_reason}"
        else:
            notes = cancellation_reason
        reservation.notes = notes

        # حفظ التغييرات
        reservation.save()

        # استعادة حالة السيارة إلى "متاحة"
        car = reservation.car
        car.is_available = True
        car.save()

        logger.info(f"Auto-cancelled reservation #{reservation.id} for car {car.id} due to payment timeout.")

    # إرجاع عدد الحجوزات التي تم إلغاؤها
    return expired_reservations.count()

def get_template_by_language(request, base_template):
    """
    Helper function to choose the appropriate template based on language setting

    الدالة المساعدة لاختيار القالب المناسب بناء على إعداد اللغة.
    تسهل هذه الدالة استخدام نظام Django i18n الأصلي من خلال توحيد نظام القوالب.
    """
    # تأكد من قراءة اللغة الحالية مباشرة من django كل مرة
    from django.utils.translation import get_language

    # الحصول على اللغة الحالية (ar أو en)
    current_language = get_language()

    # طباعة للتصحيح
    print(f"Current language: {current_language}")
    print(f"Cookie language: {request.COOKIES.get('django_language', 'none')}")

    # قاموس لتحويل القوالب الأساسية إلى نسخها المدعومة بنظام i18n
    template_mappings = {
        # قوالب التنقل الرئيسية
        'index.html': 'index_django.html',
        'cars.html': 'cars_django.html',
        'profile.html': 'profile_django.html',
        'car_detail.html': 'car_detail_django.html',
        'about_us.html': 'about_us_django.html',
        'cart.html': 'cart_django.html',
        'confirmation.html': 'confirmation_django.html',
        'checkout.html': 'checkout_django.html',
        'login.html': 'login_django.html',
        'register.html': 'register_django.html',
        'my_reservations.html': 'my_reservations_django.html',
        'booking.html': 'booking_django.html',
        'reservation_detail.html': 'reservation_detail_django.html',
        'error.html': 'error_django.html',
        'admin_dashboard.html': 'admin_dashboard_django.html',
    }

    # حالة خاصة للقالب index_arabic.html - توجيه إلى index_django.html
    if base_template == 'index_arabic.html':
        return 'index_django.html'

    # إذا كان لدينا تعيين مباشر، استخدمه
    if base_template in template_mappings:
        return template_mappings[base_template]

    # للقوالب التي قد تنتهي بالفعل بـ _django.html
    if base_template.endswith('.html') and not base_template.endswith('_django.html'):
        base_name = base_template[:-5]
        django_template = f"{base_name}_django.html"
        return django_template

    # التعامل الافتراضي
    return base_template

def index(request):
    """Home page view"""
    # قبل عرض الصفحة، تحقق من الحجوزات المنتهية وقم بإلغائها تلقائيًا
    expired_count = check_expired_confirmations()
    if expired_count > 0:
        logger.info(f"Auto-cancelled {expired_count} expired reservations during index view.")

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
        'category_choices': Car.CATEGORY_CHOICES,  # Add category choices for translations
    }

    # Use our helper function to select the appropriate template
    template = get_template_by_language(request, 'index.html')

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

    template = get_template_by_language(request, 'register.html')
    return render(request, template, {'form': form})

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

    template = get_template_by_language(request, 'login.html')
    return render(request, template, {'form': form})

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
    template = get_template_by_language(request, 'profile.html')
    return render(request, template, context)

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

    # الحصول على اللغة الحالية مباشرة من django i18n
    from django.utils.translation import get_language
    current_language = get_language()
    is_arabic = (current_language == 'ar')

    # تعيين فئات الهوامش بناءً على اتجاه اللغة
    margin_right_class = 'ms-2' if is_arabic else 'me-2'
    margin_left_class = 'me-1' if is_arabic else 'ms-1'

    context = {
        'form': form,
        'cars': page_obj,
        'today': date.today(),
        'is_arabic': is_arabic,
        'margin_right_class': margin_right_class,
        'margin_left_class': margin_left_class,
    }

    template = get_template_by_language(request, 'cars.html')
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

    template = get_template_by_language(request, 'car_detail.html')
    return render(request, template, context)

@login_required
def cart_view(request):
    """Shopping cart view"""
    cart_items = CartItem.objects.filter(user=request.user)

    # Calculate total for each item and the grand total
    grand_total = 0
    total_days = 0
    for item in cart_items:
        # Use the computed property days instead of setting it directly
        days = item.days  # This will call the @property
        total_days += days
        # Use the computed property total instead of setting it
        grand_total += item.total  # This will call the @property

    context = {
        'cart_items': cart_items,
        'cart_total': grand_total,  # Make sure the key matches what's in the template
        'total_days': total_days,   # Add total days to the context
    }

    template = get_template_by_language(request, 'cart.html')
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
def checkout_old(request):
    """Original checkout function that will be replaced"""
    return redirect('checkout_new')

@login_required
def checkout_new(request):
    """New simplified checkout function without complex templates"""
    # Check if coming from a specific reservation
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

        # Handle POST request (payment processing)
        if request.method == 'POST':
            # Process payment (simplified)
            reservation.payment_status = 'paid'

            # Update status to completed if it was confirmed
            if reservation.status == 'confirmed':
                reservation.status = 'completed'

            reservation.save()

            messages.success(request, "Payment completed successfully!")
            request.session['last_paid_reservation_id'] = reservation.id
            return redirect('confirmation')

        context = {
            'reservation': reservation,
            'total_amount': reservation.total_price
        }
    else:
        # User is checking out items from cart
        cart_items = CartItem.objects.filter(user=request.user)

        if not cart_items:
            messages.warning(request, "Your cart is empty!")
            return redirect('cart')

        # Calculate totals
        grand_total = 0
        for item in cart_items:
            # Use the computed properties instead of setting them directly
            grand_total += item.total  # This will use the @property

        # Handle POST request (create reservations)
        if request.method == 'POST':
            # Create reservations for all cart items
            for item in cart_items:
                # Check car availability
                if get_car_availability(item.car.id, item.start_date, item.end_date):
                    total_price = calculate_total_price(item.car, item.start_date, item.end_date)

                    # Create reservation with pending status
                    Reservation.objects.create(
                        user=request.user,
                        car=item.car,
                        start_date=item.start_date,
                        end_date=item.end_date,
                        total_price=total_price,
                        status='pending',
                        payment_status='pending'
                    )
                else:
                    messages.error(
                        request, 
                        f"Sorry, the car {item.car.make} {item.car.model} is no longer available."
                    )
                    return redirect('cart')

            # Clear the cart
            cart_items.delete()

            messages.success(request, "Booking request submitted successfully!")
            return redirect('confirmation')

        context = {
            'cart_items': cart_items,
            'total_amount': grand_total
        }

    # Use a simple template that doesn't have URL references
    return render(request, 'checkout_minimal.html', context)

def checkout(request):
    """Checkout and payment view - redirects to the new unified payment gateway"""
    from django.utils.translation import get_language
    from django.contrib import messages

    current_language = get_language()
    is_english = current_language == 'en'

    # Get reservation ID from request parameters
    reservation_id = request.GET.get('reservation_id')

    if reservation_id:
        # Check if reservation exists and belongs to current user
        try:
            reservation = Reservation.objects.get(
                id=reservation_id,
                user=request.user
            )

            # Check if reservation is confirmed (payment is only allowed for confirmed reservations)
            if reservation.status == 'confirmed' and reservation.payment_status == 'pending':
                # Redirect to our new unified payment gateway
                return redirect(f'/payment/gateway/?reservation_id={reservation_id}')
            elif reservation.status == 'pending':
                # Cannot pay for pending reservations
                if is_english:
                    message = "This reservation is still pending administrator approval. Payment can only be made after approval."
                else:
                    message = "هذا الحجز لا يزال في انتظار موافقة المسؤول. يمكن إجراء الدفع فقط بعد الموافقة."

                messages.warning(request, message)
                return redirect('my_reservations')
            elif reservation.payment_status == 'paid':
                # Already paid
                if is_english:
                    message = "This reservation has already been paid."
                else:
                    message = "تم الدفع لهذا الحجز بالفعل."

                messages.info(request, message)
                return redirect('reservation_detail', reservation_id=reservation_id)
            else:
                # Other status (e.g., cancelled)
                if is_english:
                    message = "Cannot process payment for this reservation."
                else:
                    message = "لا يمكن معالجة الدفع لهذا الحجز."

                messages.error(request, message)
                return redirect('my_reservations')

        except Reservation.DoesNotExist:
            # Reservation not found
            if is_english:
                message = "Reservation not found."
            else:
                message = "الحجز غير موجود."

            messages.error(request, message)
            return redirect('my_reservations')
    else:
        # Redirect to our new unified payment gateway for cart items
        return redirect('/payment/gateway/')
@login_required
def my_reservations(request):
    """User's reservations page with search capability"""
    # تحقق من الحجوزات المنتهية قبل عرض الصفحة
    expired_count = check_expired_confirmations()
    if expired_count > 0:
        logger.info(f"Auto-cancelled {expired_count} expired reservations during my_reservations view.")

    # الحصول على الوقت الحالي (مطلوب للعداد التنازلي)
    now = timezone.now()

    # الحصول على كافة حجوزات المستخدم الحالي
    reservations_query = Reservation.objects.filter(user=request.user)

    # استخراج معايير البحث من الاستعلام
    search_query = request.GET.get('search', '')
    status_filter = request.GET.get('status', '')
    date_from = request.GET.get('date_from', '')
    date_to = request.GET.get('date_to', '')

    # تطبيق عوامل التصفية المختلفة إذا توفرت
    if search_query:
        # البحث في حقول متعددة
        reservations_query = reservations_query.filter(
            Q(car__make__icontains=search_query) | 
            Q(car__model__icontains=search_query) |
            Q(car__license_plate__icontains=search_query) |
            Q(id__icontains=search_query)
        )

    if status_filter:
        reservations_query = reservations_query.filter(status=status_filter)

    if date_from:
        try:
            date_from_obj = datetime.strptime(date_from, '%Y-%m-%d').date()
            reservations_query = reservations_query.filter(start_date__gte=date_from_obj)
        except ValueError:
            pass

    if date_to:
        try:
            date_to_obj = datetime.strptime(date_to, '%Y-%m-%d').date()
            reservations_query = reservations_query.filter(end_date__lte=date_to_obj)
        except ValueError:
            pass

    # ترتيب النتائج حسب تاريخ الإنشاء (الأحدث أولاً)
    reservations = reservations_query.order_by('-created_at')

    context = {
        'reservations': reservations,
        'search_query': search_query,
        'status_filter': status_filter,
        'date_from': date_from,
        'date_to': date_to,
        'status_choices': Reservation.STATUS_CHOICES,
        'today': date.today(),
        'now': now,  # إضافة الوقت الحالي للقالب (مطلوب للعداد التنازلي)
    }

    # استخدام القالب الأصلي مع التصميم السابق وإضافة العد التنازلي
    # استخدام القالب مباشرة لتجنب تحويله بواسطة get_template_by_language
    return render(request, 'my_reservations_original.html', context)

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
        messages.warning(request, _("لم يتم العثور على أي حجوزات!"))
        return redirect('index')

    context = {
        'reservation': reservation,
    }

    template = get_template_by_language(request, 'confirmation.html')
    return render(request, template, context)

@login_required
def reservation_detail(request, reservation_id):
    """Detailed view of a single reservation"""
    try:
        reservation = get_object_or_404(Reservation, id=reservation_id, user=request.user)

        # Check if user has already reviewed this reservation
        has_review = Review.objects.filter(reservation=reservation, user=request.user).exists()

        context = {
            'reservation': reservation,
            'has_review': has_review,
        }

        template = get_template_by_language(request, 'reservation_detail.html')
        return render(request, template, context)
    except:
        messages.error(request, _("الحجز غير موجود أو لا يمكنك الوصول إليه"))
        return redirect('my_reservations')

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

    template = get_template_by_language(request, 'modify_reservation.html')
    return render(request, template, context)

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

    template = get_template_by_language(request, 'cancel_reservation.html')
    return render(request, template, context)

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

    template = get_template_by_language(request, 'add_review.html')
    return render(request, template, context)

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
    """
    تبديل إعدادات اللغة بين العربية والإنجليزية بشكل مباشر
    """
    from django.utils import translation
    from django.utils.translation import get_language
    from django.conf import settings
    import logging

    logger = logging.getLogger(__name__)

    # الحصول على اللغة الحالية
    current_language = get_language() or 'ar'
    logger.debug(f"Current language before toggle: {current_language}")

    # تبديل بين العربية والإنجليزية
    new_language = 'en' if current_language == 'ar' else 'ar'

    # تنشيط اللغة الجديدة
    translation.activate(new_language)

    # حفظ تفضيل اللغة في جلسة المستخدم
    request.session[settings.LANGUAGE_COOKIE_NAME] = new_language
    request.session.modified = True

    # طباعة معلومات التصحيح
    print(f"Language session updated: {new_language}")

    # إعادة توجيه بشكل مباشر إلى المسار المناسب مع بادئة اللغة الجديدة
    response = redirect(f'/{new_language}/')

    # ضبط ملف تعريف الارتباط
    response.set_cookie(
        settings.LANGUAGE_COOKIE_NAME, 
        new_language,
        max_age=settings.LANGUAGE_COOKIE_AGE,
        path=settings.LANGUAGE_COOKIE_PATH,
        domain=settings.LANGUAGE_COOKIE_DOMAIN,
        secure=settings.LANGUAGE_COOKIE_SECURE,
        httponly=settings.LANGUAGE_COOKIE_HTTPONLY,
        samesite=settings.LANGUAGE_COOKIE_SAMESITE,
    )

    logger.debug(f"Language switched to: {new_language}, redirecting to home page in {new_language}")
    return response



def about_us(request):
    """About Us page view"""
    template = get_template_by_language(request, 'about_us.html')
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

    template = get_template_by_language(request, 'booking.html')
    return render(request, template, context)

@login_required
def process_booking(request):
    """Process the booking form submission"""
    if request.method != 'POST':
        return redirect('cars')

    car_id = request.POST.get('car_id')
    car = get_object_or_404(Car, id=car_id, is_available=True)

    # استخراج المعلومات الأساسية للحجز
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

    # استخراج معلومات العميل
    full_name = request.POST.get('full_name', '')
    national_id = request.POST.get('national_id', '')

    # استخراج تفاصيل الحجز الإضافية
    rental_type = request.POST.get('rental_type', '')
    payment_method = request.POST.get('payment_method', '')
    guarantee_type = request.POST.get('guarantee_type', '')
    guarantee_details = request.POST.get('guarantee_details', '')

    # معالجة الوديعة (إذا كانت موجودة)
    deposit_amount = request.POST.get('deposit_amount', '')
    if deposit_amount and deposit_amount.strip():
        try:
            deposit_amount = float(deposit_amount)
        except ValueError:
            deposit_amount = None
    else:
        deposit_amount = None  # تحديد قيمة None بدلاً من النص الفارغ

    # Create reservation with pending status - admin must approve before payment
    reservation = Reservation.objects.create(
        user=request.user,
        car=car,
        start_date=start_date,
        end_date=end_date,
        total_price=total_price,
        status='pending',  # Set as pending - admin must confirm before payment
        payment_status='pending',
        notes=notes,
        # معلومات العميل الإضافية
        full_name=full_name,
        national_id=national_id,
        # معلومات الحجز الإضافية
        rental_type=rental_type,
        payment_method=payment_method,
        guarantee_type=guarantee_type,
        guarantee_details=guarantee_details,
        deposit_amount=deposit_amount
    )

    # معالجة ملف صورة الهوية
    if 'id_card_image' in request.FILES:
        reservation.id_card_image = request.FILES['id_card_image']
        reservation.save()

    # Remove the item from cart if it exists
    CartItem.objects.filter(
        user=request.user,
        car=car,
        start_date=start_date,
        end_date=end_date
    ).delete()

    # Save reservation ID in session for the confirmation page
    request.session['last_paid_reservation_id'] = reservation.id

    # Redirect to confirmation page to show pending status
    return redirect('confirmation')

def get_unavailable_dates_api(request, car_id):
    """API endpoint to get unavailable dates for a car"""
    unavailable_dates_list = get_unavailable_dates(car_id)

    # Format the data for API response
    formatted_dates = []
    for date_obj in unavailable_dates_list:
        formatted_dates.append(date_obj.strftime('%Y-%m-%d'))

    return JsonResponse({'unavailable_dates': formatted_dates})

def bank_transfer_info(request):
    # Get user language
    from django.utils.translation import get_language
    current_language = get_language()
    is_english = current_language == 'en'
    is_rtl = current_language == 'ar'

    context = {
        'is_english': is_english,
        'is_rtl': is_rtl
    }

    return render(request, 'bank_transfer_info.html', context)