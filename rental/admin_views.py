from django.shortcuts import render, redirect, get_object_or_404
from .views import get_template_by_language
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse, HttpResponse, FileResponse
from django.db.models import Sum, Count, Q
from django.core.paginator import Paginator
from django.utils import timezone
from django.urls import reverse
from django.utils.translation import get_language
from .models import User, Car, Reservation, CartItem, SiteSettings, Document
from .forms import CarForm, ManualPaymentForm, RegisterForm, ProfileForm, SiteSettingsForm
from functools import wraps
from datetime import datetime, date, timedelta
import uuid
import csv
import logging
import os
import mimetypes
from django.db.models import Q
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.core.files.storage import default_storage
from django.utils.text import slugify

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
    # الحصول على معلمات التصفية
    status = request.GET.get('status', '')
    payment_status = request.GET.get('payment_status', '')
    start_date_str = request.GET.get('start_date', '')
    end_date_str = request.GET.get('end_date', '')
    search = request.GET.get('search', '')
    
    # تصفية الحجوزات
    reservations = Reservation.objects.all().order_by('-created_at')
    
    # تطبيق التصفية حسب الحالة
    if status:
        reservations = reservations.filter(status=status)
    
    # تطبيق التصفية حسب حالة الدفع
    if payment_status:
        reservations = reservations.filter(payment_status=payment_status)
    
    # تطبيق التصفية حسب التاريخ
    if start_date_str:
        try:
            start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
            reservations = reservations.filter(pickup_date__gte=start_date)
        except ValueError:
            pass
    
    if end_date_str:
        try:
            end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
            reservations = reservations.filter(return_date__lte=end_date)
        except ValueError:
            pass
    
    # تطبيق البحث
    if search:
        reservations = reservations.filter(
            Q(reservation_number__icontains=search) |
            Q(user__first_name__icontains=search) |
            Q(user__last_name__icontains=search) |
            Q(user__email__icontains=search) |
            Q(car__make__icontains=search) |
            Q(car__model__icontains=search)
        )
    
    # إحصائيات عدد الحجوزات حسب الحالة
    pending_count = Reservation.objects.filter(status='pending').count()
    confirmed_count = Reservation.objects.filter(status='confirmed').count()
    cancelled_count = Reservation.objects.filter(status='cancelled').count()
    completed_count = Reservation.objects.filter(status='completed').count()
    
    # ترقيم الصفحات
    paginator = Paginator(reservations, 10)  # 10 حجوزات في كل صفحة
    page_number = request.GET.get('page', 1)
    
    try:
        reservations = paginator.page(page_number)
    except (PageNotAnInteger, EmptyPage):
        reservations = paginator.page(1)
    
    # تحديد لغة المستخدم
    current_language = get_language()
    is_english = current_language == 'en'
    
    context = {
        'reservations': reservations,
        'pending_count': pending_count,
        'confirmed_count': confirmed_count,
        'cancelled_count': cancelled_count,
        'completed_count': completed_count,
        'status': status,
        'payment_status': payment_status,
        'start_date': start_date_str,
        'end_date': end_date_str,
        'search': search,
        'is_english': is_english,
        'is_rtl': current_language == 'ar'
    }
    
    return render(request, 'admin/enhanced/reservations_with_sidebar_fixed.html', context)

def admin_analytics(request):
    # Get all reservations count by status
    pending_count = Reservation.objects.filter(status='pending').count()
    confirmed_count = Reservation.objects.filter(status='confirmed').count()
    completed_count = Reservation.objects.filter(status='completed').count()
    cancelled_count = Reservation.objects.filter(status='cancelled').count()
    
    # Get all reservations
    reservations = Reservation.objects.all().order_by('-created_at')
    
    # تحديد لغة المستخدم
    current_language = get_language()
    is_english = current_language == 'en'
    is_rtl = current_language == 'ar'
    
    context = {
        'reservations': reservations,
        'pending_count': pending_count,
        'confirmed_count': confirmed_count,
        'completed_count': completed_count,
        'cancelled_count': cancelled_count,
        'is_english': is_english,
        'is_rtl': is_rtl,
    }

    # استخدام القالب الاحترافي المحسن مع قائمة لوحة التحكم
    return render(request, 'admin/enhanced/reservations_with_sidebar_fixed.html', context)

@login_required
@admin_required
def update_reservation_status(request, reservation_id, status):
    """Admin view to update reservation status"""
    # استخدام timezone لضمان استخدام الوقت المناسب مع مراعاة المنطقة الزمنية
    from django.utils import timezone

    reservation = get_object_or_404(Reservation, id=reservation_id)
    car = reservation.car

    # تشخيص الأخطاء
    print(f"DIAGNOSTIC: Request received for reservation {reservation_id} with status {status}")
    
    valid_statuses = ['pending', 'confirmed', 'completed', 'cancelled', 'view', 'details', 'delete']
    if status not in valid_statuses:
        print(f"ERROR: Invalid status '{status}' received for reservation {reservation_id}")
        messages.error(request, f"حالة الحجز غير صالحة: {status}")
        return redirect('admin_reservations')
        
    # معالجة حالة 'view' أو 'details' الخاصة
    if status in ['view', 'details']:
        # عرض التفاصيل بدلاً من تحديث الحالة
        return admin_reservation_detail(request, reservation_id)
        
    # معالجة حالة 'delete' الخاصة
    if status == 'delete':
        # توجيه الطلب مباشرة إلى دالة حذف الحجز
        print(f"DIAGNOSTIC: Redirecting delete request for reservation {reservation_id} to delete_reservation")
        return delete_reservation(request, reservation_id)

    # Update reservation status
    reservation.status = status

    # Handle different status changes
    if status == 'confirmed':
        # Mark car as unavailable (reserved)
        car.is_available = False
        car.save()

        # Set auto-expiry time (24 hours from now)
        # استخدام timezone.now() بدلاً من datetime.now() للحصول على التاريخ المناسب مع المنطقة الزمنية
        expiry_time = timezone.now() + timezone.timedelta(hours=24)
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
def confirm_reservation(request, reservation_id):
    """Admin view to confirm a reservation - simplified URL pattern"""
    reservation = get_object_or_404(Reservation, id=reservation_id)
    
    # حفظ الحالة الجديدة
    reservation.status = 'confirmed'
    
    # تعديل حالة توفر السيارة
    car = reservation.car
    car.is_available = False
    car.save()
    
    # تعيين تاريخ انتهاء مهلة الدفع (24 ساعة من الآن)
    # استخدام confirmation_expiry الذي يتم استخدامه في النموذج بدلاً من expiry_date
    reservation.confirmation_expiry = timezone.now() + timezone.timedelta(hours=24)
    
    reservation.save()
    
    # رسالة تأكيد
    messages.success(request, "تم تأكيد الحجز بنجاح! سيبقى الحجز مفعلاً لمدة 24 ساعة حتى يتم الدفع.")
    return redirect('admin_reservations')

@login_required
@admin_required
def cancel_reservation_admin(request, reservation_id):
    """Admin view to cancel a reservation - simplified URL pattern"""
    reservation = get_object_or_404(Reservation, id=reservation_id)
    
    # حفظ الحالة الجديدة
    reservation.status = 'cancelled'
    
    # إعادة السيارة إلى حالة متاحة
    car = reservation.car
    car.is_available = True
    car.save()
    
    # إعادة تعيين حالة الدفع
    reservation.payment_status = 'pending'
    
    reservation.save()
    
    # رسالة تأكيد
    messages.success(request, "تم إلغاء الحجز!")
    return redirect('admin_reservations')

@login_required
@admin_required
def complete_reservation(request, reservation_id):
    """Admin view to mark a reservation as completed - simplified URL pattern"""
    reservation = get_object_or_404(Reservation, id=reservation_id)
    
    # حفظ الحالة الجديدة
    reservation.status = 'completed'
    reservation.save()
    
    # رسالة تأكيد
    messages.success(request, "تم إكمال الحجز بنجاح!")
    return redirect('admin_reservations')
    
@login_required
@admin_required
def admin_reservation_detail(request, reservation_id):
    """Admin view to show reservation details"""
    try:
        # إضافة تسجيل للمتابعة
        logger.info(f"Accessing reservation details for ID: {reservation_id}")
        print(f"DIAGNOSTIC: Accessing reservation details for ID: {reservation_id}")
        
        # محاولة العثور على الحجز
        reservation = get_object_or_404(Reservation, id=reservation_id)
        print(f"DIAGNOSTIC: Found reservation: {reservation.id}, car: {reservation.car.make}")
        print(f"DIAGNOSTIC: full_name: {reservation.full_name if hasattr(reservation, 'full_name') else 'Not available'}")
        print(f"DIAGNOSTIC: hasattr(reservation, 'full_name'): {hasattr(reservation, 'full_name')}")
        
        # حساب عدد الأيام بين تاريخ البداية وتاريخ النهاية
        delta = (reservation.end_date - reservation.start_date).days + 1
        
        # تحديد لغة المستخدم
        from django.utils.translation import get_language
        current_language = get_language()
        is_english = current_language == 'en'
        is_rtl = current_language == 'ar'
        print(f"DIAGNOSTIC: Language: {current_language}, is_rtl: {is_rtl}")
        
        # إضافة معلومات عن المستخدم وعدد الحجوزات
        user = reservation.user
        user.reservation_count = Reservation.objects.filter(user=user).count()
        
        # إعداد سياق القالب بجميع المعلومات المطلوبة
        context = {
            'reservation': reservation,
            'days': delta,
            'is_english': is_english,
            'is_rtl': is_rtl,
            'current_user': request.user,
        }
        
        # إضافة معلومات الدفع إذا كانت متوفرة
        if hasattr(reservation, 'payment_method') or (reservation.notes and ('طريقة الدفع:' in reservation.notes)):
            if hasattr(reservation, 'payment_method'):
                # استخدام القيمة المخزنة مباشرة إذا كانت موجودة
                context['payment_method'] = reservation.payment_method
            else:
                # استخراج طريقة الدفع من الملاحظات
                notes_lines = reservation.notes.split('\n')
                for line in notes_lines:
                    if 'طريقة الدفع:' in line:
                        context['payment_method'] = line.split('طريقة الدفع:')[1].strip()
                        break
            
            # استخراج رقم المرجع من الملاحظات
            notes_lines = reservation.notes.split('\n') if reservation.notes else []
            for line in notes_lines:
                if 'رقم المرجع:' in line:
                    context['payment_reference'] = line.split('رقم المرجع:')[1].strip()
                    break
        
        # استخدام قالب التصميم الاحترافي المصحح
        print(f"DIAGNOSTIC: Rendering fixed professional template")
        return render(request, 'admin/reservation_detail_fix.html', context)
    
    except Exception as e:
        # تسجيل أي أخطاء واظهارها للمستخدم بشكل مفصل
        error_message = f"Error showing reservation details: {str(e)}"
        logger.error(error_message)
        print(f"ERROR in admin_reservation_detail: {error_message}")
        import traceback
        traceback.print_exc()
        messages.error(request, f"حدث خطأ أثناء محاولة عرض تفاصيل الحجز: {str(e)}")
        return redirect('admin_reservations')

@login_required
@admin_required
def delete_reservation(request, reservation_id):
    """Admin view to permanently delete a reservation"""
    try:
        reservation = get_object_or_404(Reservation, id=reservation_id)
        
        # اسمح بالحذف عبر طلبات GET (بعد تأكيد جافا سكريبت) أو طلبات POST
        if request.method == 'GET' or request.method == 'POST':
            # تخزين المعلومات قبل الحذف
            reservation_id_str = str(reservation_id)
            car_info = f"{reservation.car.make} {reservation.car.model}"
            user_info = f"{reservation.user.get_full_name() or reservation.user.username}"
            
            # جعل السيارة متاحة إذا كانت محجوزة
            if reservation.status in ['confirmed', 'pending'] and not reservation.car.is_available:
                car = reservation.car
                car.is_available = True
                car.save()
            
            # حذف الحجز
            reservation.delete()
            
            messages.success(
                request, 
                f"تم حذف الحجز #{reservation_id_str} نهائياً. (السيارة: {car_info}, المستخدم: {user_info})"
            )
            return redirect('admin_reservations')
        
        # في حالة طلبات أخرى، إعادة توجيه للصفحة الرئيسية للحجوزات
        return redirect('admin_reservations')
        
    except Exception as e:
        logger.error(f"Error deleting reservation: {str(e)}")
        messages.error(request, f"حدث خطأ أثناء محاولة حذف الحجز: {str(e)}")
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

    # Get basic payment counts for filtering
    pending_count = Reservation.objects.filter(payment_status='pending').count()

    context = {
        'payments': page_obj,
        'payment_status': payment_status,
        'date_range': date_range,
        'search': search,
        'pending_count': pending_count
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

    # تحديد لغة المستخدم
    from django.utils.translation import get_language
    current_language = get_language()
    is_english = current_language == 'en'
    is_rtl = current_language == 'ar'

    context = {
        'payment': payment,
        'days': delta,
        'amount': payment.total_price,
        'current_user': request.user,
        'is_english': is_english,
        'is_rtl': is_rtl,
    }

    # تحديث ملف CSS منفصل
    import time
    context['cache_buster'] = str(int(time.time()))

    # استخدام قالب المتجر الالكتروني الاحترافي
    template_name = 'admin/payment_detail_ecommerce.html'

    return render(request, template_name, context)

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
def print_receipt(request, payment_id):
    """Show a printable receipt"""
    from django.utils.translation import get_language
    
    payment = get_object_or_404(Reservation, id=payment_id)

    # Only allow viewing receipts for paid reservations
    if payment.payment_status != 'paid':
        messages.error(request, "لا يمكن طباعة إيصال للمدفوعات غير المدفوعة!")
        return redirect('payment_details', payment_id=payment_id)

    # Calculate the number of days between start_date and end_date
    delta = (payment.end_date - payment.start_date).days + 1

    # Add additional payment fields needed by template
    payment.date = payment.created_at  # Use created_at for payment date
    payment.reference_number = ''  # Default empty reference number

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

    # تحديد لغة المستخدم
    current_language = get_language()
    is_english = current_language == 'en'
    is_rtl = current_language == 'ar'

    context = {
        'payment': payment,
        'days': delta,
        'amount': payment.total_price,
        'is_english': is_english,
        'is_rtl': is_rtl,
    }

    return render(request, 'admin/payment_receipt_printable.html', context)

@login_required
@admin_required
def download_receipt(request, payment_id):
    """Generate a PDF receipt for download"""
    import io
    import tempfile
    from django.utils.translation import get_language
    
    # تجربة استخدام weasyprint
    try:
        from weasyprint import HTML
        from django.template.loader import render_to_string
        
        payment = get_object_or_404(Reservation, id=payment_id)

        # Only allow downloading receipts for paid reservations
        if payment.payment_status != 'paid':
            messages.error(request, "لا يمكن تنزيل إيصال للمدفوعات غير المدفوعة!")
            return redirect('payment_details', payment_id=payment_id)

        # Calculate the number of days between start_date and end_date
        delta = (payment.end_date - payment.start_date).days + 1

        # Add additional payment fields needed by template
        payment.date = payment.created_at  # Use created_at for payment date
        payment.reference_number = ''  # Default empty reference number

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

        # تحديد لغة المستخدم
        current_language = get_language()
        is_english = current_language == 'en'
        is_rtl = current_language == 'ar'

        context = {
            'payment': payment,
            'days': delta,
            'amount': payment.total_price,
            'is_english': is_english,
            'is_rtl': is_rtl,
        }

        # هنا نستخدم نفس القالب الذي نستخدمه للطباعة لكن نحذف منه أزرار الطباعة
        html_string = render_to_string('admin/payment_receipt_printable.html', context)
        
        # نحاول إنشاء ملف PDF
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="إيصال_دفع_{payment.id}.pdf"'
        
        # استخدام ملف مؤقت لتجنب مشاكل الذاكرة مع ملفات PDF الكبيرة
        with tempfile.NamedTemporaryFile(suffix='.html') as temp:
            temp.write(html_string.encode('utf-8'))
            temp.flush()
            
            # إنشاء PDF من HTML
            HTML(filename=temp.name).write_pdf(response)
        
        return response
        
    # إذا فشلت عملية إنشاء PDF، نعود لإنشاء ملف CSV
    except Exception as e:
        print(f"Error generating PDF: {e}")
        
        # Fall back to CSV
        import csv
        
        payment = get_object_or_404(Reservation, id=payment_id)

        # Only allow downloading receipts for paid reservations
        if payment.payment_status != 'paid':
            messages.error(request, "لا يمكن تنزيل إيصال للمدفوعات غير المدفوعة!")
            return redirect('payment_details', payment_id=payment_id)

        # Calculate the number of days between start_date and end_date
        delta = (payment.end_date - payment.start_date).days + 1
        total_price = payment.total_price
        daily_rate = payment.car.daily_rate
        
        # Extract payment method from notes if available
        payment_method = 'غير معروف'
        reference_number = ''
        if payment.notes:
            notes_lines = payment.notes.split('\n')
            for line in notes_lines:
                if 'طريقة الدفع:' in line:
                    payment_method = line.split('طريقة الدفع:')[1].strip()
                elif 'رقم المرجع:' in line:
                    reference_number = line.split('رقم المرجع:')[1].strip()

        # Create a CSV file with better formatting and UTF-8 BOM for Arabic support
        response = HttpResponse(content_type='text/csv; charset=utf-8-sig')
        response['Content-Disposition'] = f'attachment; filename="إيصال_دفع_{payment.id}.csv"'
        
        writer = csv.writer(response)
        
        # إضافة عنوان الإيصال
        writer.writerow(['شركة تأجير السيارات الحديثة'])
        writer.writerow(['الكويت - شارع الخليج - مجمع الأفنيوز - الطابق الثاني'])
        writer.writerow(['هاتف: 9999-9999-965+ | البريد الإلكتروني: info@modern-rental.com'])
        writer.writerow([''])
        
        # معلومات الإيصال
        writer.writerow([f'رقم الإيصال', f'#{payment.id:06d}'])
        writer.writerow(['تاريخ الإيصال', payment.created_at.strftime('%Y-%m-%d %H:%M')])
        writer.writerow(['حالة الدفع', 'مدفوع بالكامل'])
        writer.writerow([''])
        
        # معلومات العميل
        writer.writerow(['معلومات العميل', ''])
        writer.writerow(['الاسم', f'{payment.user.first_name} {payment.user.last_name}'])
        writer.writerow(['البريد الإلكتروني', payment.user.email])
        writer.writerow(['اسم المستخدم', payment.user.username])
        writer.writerow([''])
        
        # تفاصيل السيارة
        writer.writerow(['تفاصيل السيارة', ''])
        writer.writerow(['السيارة', f'{payment.car.make} {payment.car.model} ({payment.car.year})'])
        writer.writerow(['الفئة', payment.car.category])
        writer.writerow(['اللون', payment.car.color])
        writer.writerow(['فترة الإيجار', f'من {payment.start_date} إلى {payment.end_date}'])
        writer.writerow([''])
        
        # تفاصيل الدفع
        writer.writerow(['تفاصيل الدفع', ''])
        writer.writerow(['طريقة الدفع', payment_method])
        if reference_number:
            writer.writerow(['رقم المرجع', reference_number])
        writer.writerow([''])
        
        # معلومات التكلفة
        writer.writerow(['ملخص التكلفة', ''])
        writer.writerow(['سعر الإيجار اليومي', f'{daily_rate} د.ك'])
        writer.writerow(['عدد الأيام', f'{delta} يوم'])
        writer.writerow(['المجموع الفرعي', f'{daily_rate} × {delta}'])
        writer.writerow(['المجموع', f'{total_price} د.ك'])
        writer.writerow([''])
        
        # ملاحظة ختامية
        writer.writerow(['شكراً لاختيارك شركة تأجير السيارات الحديثة'])
        writer.writerow(['هذا الإيصال صدر إلكترونياً وهو دليل على إتمام الدفع'])
        writer.writerow(['يرجى الاحتفاظ بنسخة من هذا الإيصال للرجوع إليه في المستقبل'])
        
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


@login_required
@admin_required
def admin_archive(request):
    """صفحة إدارة الأرشيف الإلكتروني للمستندات"""
    # الحصول على معلمات التصفية
    document_type = request.GET.get('document_type', '')
    related_to = request.GET.get('related_to', '')
    start_date_str = request.GET.get('start_date', '')
    end_date_str = request.GET.get('end_date', '')
    search = request.GET.get('search', '')
    
    # تصفية المستندات
    documents = Document.objects.all().order_by('-created_at')
    
    # تطبيق التصفية حسب نوع المستند
    if document_type:
        documents = documents.filter(document_type=document_type)
    
    # تطبيق التصفية حسب الارتباط
    if related_to:
        documents = documents.filter(related_to=related_to)
    
    # تطبيق التصفية حسب التاريخ
    if start_date_str:
        try:
            start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
            documents = documents.filter(document_date__gte=start_date)
        except ValueError:
            pass
    
    if end_date_str:
        try:
            end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
            documents = documents.filter(document_date__lte=end_date)
        except ValueError:
            pass
    
    # تطبيق البحث
    if search:
        documents = documents.filter(
            Q(title__icontains=search) | 
            Q(description__icontains=search) | 
            Q(reference_number__icontains=search) |
            Q(tags__icontains=search)
        )
    
    # تقسيم الصفحات
    paginator = Paginator(documents, 12)  # عرض 12 مستند في الصفحة
    page_number = request.GET.get('page')
    documents_page = paginator.get_page(page_number)
    
    # إحصائيات المستندات
    total_documents = Document.objects.count()
    contracts_count = Document.objects.filter(document_type='contract').count()
    receipts_count = Document.objects.filter(document_type='receipt').count()
    custody_count = Document.objects.filter(document_type='custody').count()
    custody_release_count = Document.objects.filter(document_type='custody_release').count()
    other_count = Document.objects.filter(document_type='other').count()
    
    # العدد حسب الارتباط
    reservation_docs = Document.objects.filter(related_to='reservation').count()
    car_docs = Document.objects.filter(related_to='car').count()
    user_docs = Document.objects.filter(related_to='user').count()
    
    context = {
        'documents': documents_page,
        'total_documents': total_documents,
        'contracts_count': contracts_count,
        'receipts_count': receipts_count,
        'custody_count': custody_count,
        'custody_release_count': custody_release_count,
        'other_count': other_count,
        'reservation_docs': reservation_docs,
        'car_docs': car_docs,
        'user_docs': user_docs,
        'document_type_filter': document_type,
        'related_to_filter': related_to,
        'start_date': start_date_str,
        'end_date': end_date_str,
        'search': search,
        'document_types': Document.DOCUMENT_TYPE_CHOICES,
        'related_to_types': Document.RELATED_TO_CHOICES,
        'current_user': request.user,
    }
    
    return render(request, 'admin/archive/documents.html', context)

@login_required
@admin_required
def admin_archive_add(request):
    """صفحة إضافة مستند جديد للأرشيف"""
    if request.method == 'POST':
        # الحصول على بيانات النموذج
        title = request.POST.get('title')
        document_type = request.POST.get('document_type')
        description = request.POST.get('description', '')
        document_date_str = request.POST.get('document_date')
        expiry_date_str = request.POST.get('expiry_date', '')
        related_to = request.POST.get('related_to')
        related_id = request.POST.get('related_id', '')
        tags = request.POST.get('tags', '')
        
        # التحقق من الحقول الإلزامية
        if not title or not document_type or not document_date_str or not related_to:
            messages.error(request, "يرجى ملء جميع الحقول الإلزامية")
            return redirect('admin_archive_add')
        
        # التحقق من وجود ملف مرفق
        if 'file' not in request.FILES:
            messages.error(request, "يرجى تحميل ملف المستند")
            return redirect('admin_archive_add')
        
        # تحويل التواريخ
        try:
            document_date = datetime.strptime(document_date_str, '%Y-%m-%d').date()
        except ValueError:
            messages.error(request, "تنسيق تاريخ المستند غير صحيح")
            return redirect('admin_archive_add')
        
        expiry_date = None
        if expiry_date_str:
            try:
                expiry_date = datetime.strptime(expiry_date_str, '%Y-%m-%d').date()
            except ValueError:
                messages.error(request, "تنسيق تاريخ انتهاء الصلاحية غير صحيح")
                return redirect('admin_archive_add')
        
        # إنشاء المستند
        document = Document(
            title=title,
            document_type=document_type,
            description=description,
            document_date=document_date,
            expiry_date=expiry_date,
            related_to=related_to,
            file=request.FILES['file'],
            tags=tags,
            added_by=request.user
        )
        
        # تعيين العلاقات حسب نوع الارتباط
        if related_to == 'reservation' and related_id:
            try:
                reservation = Reservation.objects.get(id=related_id)
                document.reservation = reservation
            except Reservation.DoesNotExist:
                pass
        elif related_to == 'car' and related_id:
            try:
                car = Car.objects.get(id=related_id)
                document.car = car
            except Car.DoesNotExist:
                pass
        elif related_to == 'user' and related_id:
            try:
                user = User.objects.get(id=related_id)
                document.user = user
            except User.DoesNotExist:
                pass
        
        # حفظ المستند
        document.save()
        
        messages.success(request, f"تم إضافة المستند '{title}' بنجاح")
        return redirect('admin_archive')
    
    # الحصول على قوائم للعلاقات
    reservations = Reservation.objects.order_by('-created_at')[:50]
    cars = Car.objects.order_by('-id')[:50]
    users = User.objects.order_by('-date_joined')[:50]
    
    context = {
        'document_types': Document.DOCUMENT_TYPE_CHOICES,
        'related_to_types': Document.RELATED_TO_CHOICES,
        'reservations': reservations,
        'cars': cars,
        'users': users,
        'current_user': request.user,
        'today': timezone.now().date().strftime('%Y-%m-%d'),
    }
    
    return render(request, 'admin/archive/add_document.html', context)

@login_required
@admin_required
def admin_archive_detail(request, document_id):
    """عرض تفاصيل مستند في الأرشيف"""
    document = get_object_or_404(Document, id=document_id)
    
    # التحقق إذا كان المستند مرتبط بأي كيانات
    related_entity = None
    related_entity_type = None
    
    if document.reservation:
        related_entity = document.reservation
        related_entity_type = 'reservation'
    elif document.car:
        related_entity = document.car
        related_entity_type = 'car'
    elif document.user:
        related_entity = document.user
        related_entity_type = 'user'
    
    context = {
        'document': document,
        'related_entity': related_entity,
        'related_entity_type': related_entity_type,
        'current_user': request.user,
    }
    
    return render(request, 'admin/archive/document_detail.html', context)

@login_required
@admin_required
def admin_archive_edit(request, document_id):
    """تعديل مستند في الأرشيف"""
    document = get_object_or_404(Document, id=document_id)
    
    if request.method == 'POST':
        # الحصول على بيانات النموذج
        title = request.POST.get('title')
        document_type = request.POST.get('document_type')
        description = request.POST.get('description', '')
        document_date_str = request.POST.get('document_date')
        expiry_date_str = request.POST.get('expiry_date', '')
        related_to = request.POST.get('related_to')
        related_id = request.POST.get('related_id', '')
        tags = request.POST.get('tags', '')
        
        # التحقق من الحقول الإلزامية
        if not title or not document_type or not document_date_str or not related_to:
            messages.error(request, "يرجى ملء جميع الحقول الإلزامية")
            return redirect('admin_archive_edit', document_id=document_id)
        
        # تحويل التواريخ
        try:
            document_date = datetime.strptime(document_date_str, '%Y-%m-%d').date()
        except ValueError:
            messages.error(request, "تنسيق تاريخ المستند غير صحيح")
            return redirect('admin_archive_edit', document_id=document_id)
        
        expiry_date = None
        if expiry_date_str:
            try:
                expiry_date = datetime.strptime(expiry_date_str, '%Y-%m-%d').date()
            except ValueError:
                messages.error(request, "تنسيق تاريخ انتهاء الصلاحية غير صحيح")
                return redirect('admin_archive_edit', document_id=document_id)
        
        # تحديث بيانات المستند
        document.title = title
        document.document_type = document_type
        document.description = description
        document.document_date = document_date
        document.expiry_date = expiry_date
        document.related_to = related_to
        document.tags = tags
        
        # تحديث الملف إذا تم تقديم ملف جديد
        if 'file' in request.FILES:
            # حذف الملف القديم
            if document.file:
                try:
                    default_storage.delete(document.file.path)
                except:
                    pass  # تجاهل الأخطاء إذا لم يمكن حذف الملف
            
            document.file = request.FILES['file']
        
        # تعيين العلاقات حسب نوع الارتباط
        # إعادة تعيين العلاقات
        document.reservation = None
        document.car = None
        document.user = None
        
        if related_to == 'reservation' and related_id:
            try:
                reservation = Reservation.objects.get(id=related_id)
                document.reservation = reservation
            except Reservation.DoesNotExist:
                pass
        elif related_to == 'car' and related_id:
            try:
                car = Car.objects.get(id=related_id)
                document.car = car
            except Car.DoesNotExist:
                pass
        elif related_to == 'user' and related_id:
            try:
                user = User.objects.get(id=related_id)
                document.user = user
            except User.DoesNotExist:
                pass
        
        # حفظ المستند
        document.save()
        
        messages.success(request, f"تم تحديث المستند '{title}' بنجاح")
        return redirect('admin_archive_detail', document_id=document_id)
    
    # الحصول على قوائم للعلاقات
    reservations = Reservation.objects.order_by('-created_at')[:50]
    cars = Car.objects.order_by('-id')[:50]
    users = User.objects.order_by('-date_joined')[:50]
    
    # تحديد الكيان المرتبط الحالي
    current_related_id = None
    if document.related_to == 'reservation' and document.reservation:
        current_related_id = document.reservation.id
    elif document.related_to == 'car' and document.car:
        current_related_id = document.car.id
    elif document.related_to == 'user' and document.user:
        current_related_id = document.user.id
    
    context = {
        'document': document,
        'document_types': Document.DOCUMENT_TYPE_CHOICES,
        'related_to_types': Document.RELATED_TO_CHOICES,
        'reservations': reservations,
        'cars': cars,
        'users': users,
        'current_related_id': current_related_id,
        'current_user': request.user,
    }
    
    return render(request, 'admin/archive/edit_document.html', context)

@login_required
@admin_required
def admin_archive_delete(request, document_id):
    """حذف مستند من الأرشيف"""
    document = get_object_or_404(Document, id=document_id)
    
    if request.method == 'POST':
        # حذف الملف من نظام الملفات
        if document.file:
            try:
                default_storage.delete(document.file.path)
            except:
                pass  # تجاهل الأخطاء إذا لم يمكن حذف الملف
        
        # حذف المستند من قاعدة البيانات
        document_title = document.title
        document.delete()
        
        messages.success(request, f"تم حذف المستند '{document_title}' بنجاح")
        return redirect('admin_archive')
    
    context = {
        'document': document,
        'current_user': request.user,
    }
    
    return render(request, 'admin/archive/delete_document.html', context)

@login_required
@admin_required
def admin_archive_download(request, document_id):
    """تنزيل ملف مستند من الأرشيف"""
    document = get_object_or_404(Document, id=document_id)
    
    if not document.file:
        messages.error(request, "الملف غير موجود")
        return redirect('admin_archive_detail', document_id=document_id)
    
    try:
        file_path = document.file.path
        
        # التحقق من وجود الملف
        if not os.path.exists(file_path):
            messages.error(request, "الملف غير موجود على الخادم")
            return redirect('admin_archive_detail', document_id=document_id)
        
        # تحديد نوع MIME للملف
        content_type, encoding = mimetypes.guess_type(file_path)
        if content_type is None:
            content_type = 'application/octet-stream'
        
        # إنشاء اسم الملف للتنزيل
        filename = os.path.basename(file_path)
        
        # إرجاع استجابة FileResponse
        response = FileResponse(open(file_path, 'rb'), content_type=content_type)
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        return response
    
    except Exception as e:
        messages.error(request, f"حدث خطأ أثناء تنزيل الملف: {str(e)}")
        return redirect('admin_archive_detail', document_id=document_id)

@login_required
@admin_required
def admin_archive_view(request, document_id):
    """عرض ملف مستند مباشرة في المتصفح"""
    document = get_object_or_404(Document, id=document_id)
    
    if not document.file:
        messages.error(request, "الملف غير موجود")
        return redirect('admin_archive_detail', document_id=document_id)
    
    try:
        file_path = document.file.path
        
        # التحقق من وجود الملف
        if not os.path.exists(file_path):
            messages.error(request, "الملف غير موجود على الخادم")
            return redirect('admin_archive_detail', document_id=document_id)
        
        # تحديد نوع MIME للملف
        content_type, encoding = mimetypes.guess_type(file_path)
        if content_type is None:
            content_type = 'application/octet-stream'
        
        # إرجاع استجابة FileResponse
        response = FileResponse(open(file_path, 'rb'), content_type=content_type)
        response['Content-Disposition'] = 'inline'
        return response
    
    except Exception as e:
        messages.error(request, f"حدث خطأ أثناء عرض الملف: {str(e)}")
        return redirect('admin_archive_detail', document_id=document_id)