from django.shortcuts import render, redirect, get_object_or_404
from .views import get_template_by_language
from django.contrib.auth.decorators import login_required
from django.contrib import messages
# استيراد وظيفة الرفع المباشر
from .direct_sql_upload import direct_sql_upload
from django.http import JsonResponse, HttpResponse, FileResponse
from django.db.models import Sum, Count, Q, Avg, F
from django.core.paginator import Paginator
from django.utils import timezone
from django.urls import reverse
from django.db import transaction, connection
from django.utils.translation import get_language, gettext as _
from django.conf import settings
from .models import User, Car, Reservation, CartItem, SiteSettings, Document, ArchiveFolder
from .security import setup_2fa_for_user, disable_2fa_for_user, generate_qr_code_image
from .security_models import UserSecurity
from .forms import CarForm, RegisterForm, ManualPaymentForm, ProfileForm
from functools import wraps
from datetime import datetime, date, timedelta
import uuid
import csv
# استيراد نموذج AdminUser من models_superadmin
from .models_superadmin import AdminUser, Role, AdminActivity
import logging
import os
import json
import mimetypes
from django.db.models import Q
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.core.files.storage import default_storage
from django.utils.text import slugify

logger = logging.getLogger(__name__)


# دالة تنظيف المستندات الوهمية من قائمة المستندات
def clean_document_list(documents):
    """تنظيف المستندات الوهمية من قائمة المستندات المعروضة"""
    if documents:
        return documents.filter(title__isnull=False).exclude(title__in=["بدون عنوان", "", " ", "نموذج_استعلام_الارشيف"])
    return documents

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
def simple_upload_form(request):
    """عرض نموذج الرفع البسيط"""
    folders = ArchiveFolder.objects.all().order_by('name')
    context = {
        'folders': folders,
        'document_types': Document.DOCUMENT_TYPE_CHOICES,
        'related_to_types': Document.RELATED_TO_CHOICES,
    }
    return render(request, 'admin/archive/simple_upload_form.html', context)

@login_required
@admin_required
def simple_upload(request):
    """معالجة رفع المستندات بطريقة بسيطة"""
    if request.method != 'POST':
        return redirect('simple_upload_form')
    
    try:
        # الحصول على البيانات من النموذج
        title = request.POST.get('title', '')
        description = request.POST.get('description', '')
        document_type = request.POST.get('document_type', 'OTHER')
        related_to = request.POST.get('related_to', 'NONE')
        folder_id = request.POST.get('folder', None)
        
        if folder_id == '':
            folder_id = None
            
        expiry_date = request.POST.get('expiry_date', None)
        expiry_date_value = None
        
        if expiry_date:
            try:
                expiry_date_value = datetime.strptime(expiry_date, '%Y-%m-%d').date()
            except ValueError:
                pass
        
        # التأكد من وجود ملف
        if 'file' not in request.FILES:
            messages.error(request, "لم يتم تحديد ملف للرفع")
            return redirect('simple_upload_form')
            
        uploaded_file = request.FILES['file']
        file_name = uploaded_file.name
        file_size = uploaded_file.size
        file_type = uploaded_file.content_type
        
        # تخزين الملف على القرص
        timestamp = int(datetime.now().timestamp())
        random_part = str(timestamp)[-4:]
        safe_filename = f"direct_{timestamp}_{random_part}_{file_name}"
        
        # مسار الملف
        upload_dir = os.path.join(settings.MEDIA_ROOT, 'uploads')
        os.makedirs(upload_dir, exist_ok=True)
        file_path = os.path.join('uploads', safe_filename)
        full_path = os.path.join(settings.MEDIA_ROOT, file_path)
        
        # نسخ محتوى الملف
        with open(full_path, 'wb+') as destination:
            for chunk in uploaded_file.chunks():
                destination.write(chunk)
        
        # إدخال السجل في قاعدة البيانات باستخدام SQL مباشر
        with connection.cursor() as cursor:
            now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            expiry_date_str = expiry_date_value.strftime('%Y-%m-%d') if expiry_date_value else None
            
            # استعلام SQL
            query = """
            INSERT INTO rental_document 
            (title, description, document_type, related_to, folder_id, 
            file, file_name, file_type, file_size, 
            is_archived, is_auto_created, document_date, expiry_date, 
            created_at, added_by_id)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING id;
            """
            
            # تنفيذ الاستعلام
            cursor.execute(query, [
                title, description, document_type, related_to, folder_id, 
                file_path, file_name, file_type, file_size,
                True, False, datetime.now().date().isoformat(), expiry_date_str,
                now, request.user.id
            ])
            
            # الحصول على معرف المستند الجديد
            row = cursor.fetchone()
            if row:
                document_id = row[0]
                messages.success(request, f"تم رفع المستند '{title}' بنجاح")
            else:
                messages.error(request, "حدث خطأ أثناء محاولة رفع المستند")
        
        # إعادة التوجيه
        if folder_id:
            return redirect('admin_archive_folder', folder_id=folder_id)
        else:
            return redirect('admin_archive')
            
    except Exception as e:
        # عرض رسالة خطأ للمستخدم
        messages.error(request, f"حدث خطأ أثناء رفع المستند: {str(e)[:100]}")
        return redirect('admin_archive')


# دالة تنظيف المستندات الوهمية من قائمة المستندات
def clean_document_list(documents):
    """تنظيف المستندات الوهمية من قائمة المستندات المعروضة"""
    if documents:
        return documents.filter(title__isnull=False).exclude(title__in=["بدون عنوان", "", " ", "نموذج_استعلام_الارشيف"])
    return documents


@login_required
@admin_required
def admin_index(request):
    """Admin dashboard home page"""
    # Import Review model at the top of the function to ensure it's available
    from .models import Review
    from django.db.models import Count, Avg
    
    # Get summary statistics
    total_cars = Car.objects.count()
    available_cars = Car.objects.filter(is_available=True).count()
    total_customers = User.objects.filter(is_staff=False).count()
    new_customers = User.objects.filter(is_staff=False, date_joined__gte=timezone.now() - timedelta(days=30)).count()

    # Reservation stats
    total_reservations = Reservation.objects.count()
    active_reservations = Reservation.objects.filter(status__in=['pending', 'confirmed']).count()
    pending_reservations = Reservation.objects.filter(status='pending').count()
    confirmed_reservations = Reservation.objects.filter(status='confirmed').count()
    completed_reservations = Reservation.objects.filter(status='completed').count()
    cancelled_reservations = Reservation.objects.filter(status='cancelled').count()

    # Payment stats
    paid_total = Reservation.objects.filter(payment_status='paid').aggregate(Sum('total_price'))['total_price__sum'] or 0
    pending_payment_total = Reservation.objects.filter(payment_status='pending').aggregate(Sum('total_price'))['total_price__sum'] or 0
    
    # Recent reservations
    recent_reservations = Reservation.objects.order_by('-created_at')[:10]

    # Pending reservations list for display in dashboard
    pending_reservations_list = Reservation.objects.filter(status='pending').order_by('-created_at')[:5]
    
    # Review stats - استخدام قيم افتراضية بسبب عدم وجود حقول is_approved و is_rejected في نموذج Review
    total_reviews = Review.objects.count()
    
    # تحليل تقسيم التقييمات حسب عدد النجوم
    five_star_count = Review.objects.filter(rating=5).count()
    four_star_count = Review.objects.filter(rating=4).count()
    three_star_count = Review.objects.filter(rating=3).count()
    two_star_count = Review.objects.filter(rating=2).count()
    one_star_count = Review.objects.filter(rating=1).count()
    
    # حساب النسب المئوية
    five_star_percentage = (five_star_count / total_reviews * 100) if total_reviews > 0 else 0
    four_star_percentage = (four_star_count / total_reviews * 100) if total_reviews > 0 else 0
    three_star_percentage = (three_star_count / total_reviews * 100) if total_reviews > 0 else 0
    
    # استخدام قيم افتراضية للتقييمات المعلقة والموافق عليها والمرفوضة
    pending_reviews = 0
    approved_reviews = total_reviews
    rejected_reviews = 0
    
    # Generate recent activities (sample data)
    # در واقع، باید این داده ها از یک مدل فعالیت سیستم گرفته شوند
    recent_activities = []
    for i, reservation in enumerate(recent_reservations[:5]):
        activity = {
            'user': reservation.user,
            'timestamp': reservation.created_at,
            'action_text': f"قام بحجز {reservation.car.make} {reservation.car.model}",
            'description': f"من {reservation.start_date.strftime('%Y-%m-%d')} إلى {reservation.end_date.strftime('%Y-%m-%d')}"
        }
        recent_activities.append(activity)

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

    # هذا الاستيراد سيتم تجاهله لأننا قمنا بالاستيراد بالفعل في الأعلى
    
    context = {
        'total_cars': total_cars,
        'available_cars': available_cars,
        'total_customers': total_customers,
        'new_customers': new_customers,
        'total_reservations': total_reservations,
        'active_reservations': active_reservations,
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
        
        # Review stats
        'total_reviews': total_reviews,
        'pending_reviews': pending_reviews,
        'approved_reviews': approved_reviews,
        'rejected_reviews': rejected_reviews,
        'five_star_percentage': five_star_percentage,
        'four_star_percentage': four_star_percentage,
        'three_star_percentage': three_star_percentage,
        
        # Recent activities
        'recent_activities': recent_activities,
        
        # Occupancy data (sample data)
        'occupancy_data': '65, 75, 82, 78, 80, 70, 68',
        
        'current_user': request.user,  # Add current user to context
    }

    return render(request, 'admin/enhanced/index.html', context)

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

from .decorators import permission_required, check_permission

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
    
    # إضافة عدد أيام الحجز لكل حجز
    for reservation in reservations:
        if hasattr(reservation, 'pickup_date') and hasattr(reservation, 'return_date'):
            reservation.days = (reservation.return_date - reservation.pickup_date).days + 1
    
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
    
    # إضافة متغير timestamps للتأكد من عدم تخزين الملفات في ذاكرة التخزين المؤقت
    from datetime import datetime
    timestamp = datetime.now().timestamp()
    
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
        'is_rtl': current_language == 'ar',
        'timestamp': timestamp  # إضافة الختم الزمني للسياق
    }
    
    # استخدام قالب مباشر عوضاً عن استخدام دالة get_template_by_language
    return render(request, 'admin/reservations_compact.html', context)

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

    # استخدام قالب التحليلات الاحترافي
    return render(request, 'admin/analytics_dashboard.html', context)

@login_required
@permission_required("reservations", "edit_reservations")
def update_reservation_status(request, reservation_id, status):
    """Admin view to update reservation status"""
    # استخدام timezone لضمان استخدام الوقت المناسب مع مراعاة المنطقة الزمنية
    from django.utils import timezone

    reservation = get_object_or_404(Reservation, id=reservation_id)
    car = reservation.car

    # تشخيص الأخطاء
    print(f"DIAGNOSTIC: Request received for reservation {reservation_id} with status {status}")
    
    # تصحيح الحالات المتقاربة لفظياً
    if status == 'confirm':
        status = 'confirmed'
        print(f"STATUS NORMALIZED: 'confirm' changed to 'confirmed' for reservation {reservation_id}")
    
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
@permission_required("reservations", "approve_reservations")
def confirm_reservation(request, reservation_id):
    """Admin view to confirm a reservation - simplified URL pattern"""
    # تسجيل تشخيصي
    print(f"DIAGNOSTIC: Processing confirmation for reservation {reservation_id}")
    
    try:
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
        print(f"DIAGNOSTIC: Reservation {reservation_id} confirmed successfully")
    except Exception as e:
        # التقاط أي أخطاء وتسجيلها
        print(f"ERROR: Failed to confirm reservation {reservation_id}. Error: {str(e)}")
        messages.error(request, f"حدث خطأ أثناء تأكيد الحجز: {str(e)}")
    
    return redirect('admin_reservations')

@login_required
@permission_required("reservations", "edit_reservations")
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
@permission_required("reservations", "edit_reservations")
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
@permission_required("reservations", "view_reservations")
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
        
        # تسجيل تشخيصي للتحقق من بيانات العميل
        has_customer_details = any([
            reservation.full_name, 
            reservation.national_id, 
            reservation.rental_type,
            reservation.guarantee_type,
            reservation.guarantee_details,
            reservation.deposit_amount
        ])
        print(f"DIAGNOSTIC: reservation has customer details: {has_customer_details}")
        print(f"DIAGNOSTIC: full_name: {reservation.full_name}")
        print(f"DIAGNOSTIC: national_id: {reservation.national_id}")
        print(f"DIAGNOSTIC: rental_type: {reservation.rental_type}")
        print(f"DIAGNOSTIC: guarantee_type: {reservation.guarantee_type}")
        print(f"DIAGNOSTIC: guarantee_details: {reservation.guarantee_details}")
        print(f"DIAGNOSTIC: deposit_amount: {reservation.deposit_amount}")
        
        # إضافة timestamp لمنع استخدام الكاش
        import time
        cache_buster = int(time.time())
        
        # إعداد سياق القالب بجميع المعلومات المطلوبة
        context = {
            'reservation': reservation,
            'days': delta,
            'is_english': is_english,
            'is_rtl': is_rtl,
            'current_user': request.user,
            'has_customer_details': has_customer_details,
            'cache_buster': cache_buster,
            # إضافة البيانات المهمة للتأكد من وصولها للقالب
            'full_name': reservation.full_name,
            'national_id': reservation.national_id,
            'rental_type': reservation.rental_type,
            'guarantee_type': reservation.guarantee_type,
            'guarantee_details': reservation.guarantee_details,
            'deposit_amount': reservation.deposit_amount,
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
        
        
def print_payment_details(request, payment_id):
    """عرض نموذج تفاصيل الدفع بتنسيق قابل للطباعة"""
    # التحقق من الصلاحيات
    if not check_permission(request, 'payments', 'view_payments'):
        messages.error(request, "ليس لديك صلاحية لعرض هذه الصفحة")
        return redirect('login')
    
    try:
        # محاولة العثور على الحجز
        payment = get_object_or_404(Reservation, id=payment_id)
        
        # حساب عدد الأيام بين تاريخ البداية وتاريخ النهاية
        delta = (payment.end_date - payment.start_date).days + 1
        
        # تحديد حالة الدفع
        payment.status = payment.payment_status
        payment.amount = payment.total_price
        payment.date = payment.created_at
        
        # تحديد لغة المستخدم
        from django.utils.translation import get_language
        current_language = get_language()
        is_english = current_language == 'en'
        is_rtl = current_language == 'ar'
        
        # استخراج معلومات الدفع من الملاحظات إذا كانت متوفرة
        payment_method = None
        payment_reference = None
        
        if hasattr(payment, 'payment_method') and payment.payment_method:
            payment_method = payment.payment_method
        elif payment.notes and ('طريقة الدفع:' in payment.notes):
            notes_lines = payment.notes.split('\n')
            for line in notes_lines:
                if 'طريقة الدفع:' in line:
                    payment_method = line.split('طريقة الدفع:')[1].strip()
                    break
        
        # استخراج رقم المرجع من الملاحظات
        if payment.notes and ('رقم المرجع:' in payment.notes):
            notes_lines = payment.notes.split('\n')
            for line in notes_lines:
                if 'رقم المرجع:' in line:
                    payment_reference = line.split('رقم المرجع:')[1].strip()
                    break
        
        # تعيين معلومات الدفع إلى كائن الدفع
        payment.payment_method = payment_method or 'visa'  # قيمة افتراضية
        payment.reference_number = payment_reference or ''
        
        context = {
            'payment': payment,
            'days': delta,
            'now': timezone.now(),
            'current_user': request.user,
            'is_english': is_english,
            'is_rtl': is_rtl,
        }
        
        return render(request, 'admin/payment_details_printable.html', context)
    
    except Exception as e:
        # تسجيل أي أخطاء واظهارها للمستخدم
        error_message = f"خطأ في عرض تفاصيل الدفع: {str(e)}"
        messages.error(request, error_message)
        logger.error(error_message)
        return redirect('payment_details', payment_id=payment_id)

def print_reservation_contract(request, reservation_id, template_type='standard'):
    """طباعة عقد إيجار السيارة"""
    # التحقق من الصلاحيات
    if not check_permission(request, 'reservations', 'view_reservation_details'):
        messages.error(request, "ليس لديك صلاحية لعرض هذه الصفحة")
        return redirect('login')
    
    try:
        # محاولة العثور على الحجز
        reservation = get_object_or_404(Reservation, id=reservation_id)
        
        # حساب عدد الأيام بين تاريخ البداية وتاريخ النهاية
        delta = (reservation.end_date - reservation.start_date).days + 1
        
        # تحديد لغة المستخدم
        from django.utils.translation import get_language
        
        current_language = get_language()
        is_rtl = current_language == 'ar'
        
        # إضافة timestamp لمنع استخدام الكاش
        import time
        cache_buster = int(time.time())
        
        # استخراج معلومات الدفع من الملاحظات إذا كانت متوفرة
        payment_method = None
        payment_reference = None
        
        if hasattr(reservation, 'payment_method') and reservation.payment_method:
            payment_method = reservation.payment_method
        elif reservation.notes and ('طريقة الدفع:' in reservation.notes):
            notes_lines = reservation.notes.split('\n')
            for line in notes_lines:
                if 'طريقة الدفع:' in line:
                    payment_method = line.split('طريقة الدفع:')[1].strip()
                    break
        
        # استخراج رقم المرجع من الملاحظات
        if reservation.notes and ('رقم المرجع:' in reservation.notes):
            notes_lines = reservation.notes.split('\n')
            for line in notes_lines:
                if 'رقم المرجع:' in line:
                    payment_reference = line.split('رقم المرجع:')[1].strip()
                    break
        
        # إعداد سياق القالب بجميع المعلومات المطلوبة
        context = {
            'reservation': reservation,
            'days': delta,
            'is_rtl': is_rtl,
            'cache_buster': cache_buster,
            # إضافة البيانات المهمة للتأكد من وصولها للقالب
            'full_name': reservation.full_name,
            'national_id': reservation.national_id,
            'rental_type': reservation.rental_type,
            'guarantee_type': reservation.guarantee_type,
            'guarantee_details': reservation.guarantee_details,
            'deposit_amount': reservation.deposit_amount,
            'payment_method': payment_method,
            'payment_reference': payment_reference,
        }
        
        # تحديد القالب المناسب
        template = 'admin/enhanced_reservation_contract.html' if template_type == 'enhanced' else 'admin/print_reservation_contract.html'
        
        return render(request, template, context)
    
    except Exception as e:
        # تسجيل أي أخطاء واظهارها للمستخدم
        error_message = f"خطأ في عرض عقد الحجز: {str(e)}"
        messages.error(request, error_message)
        logger.error(error_message)
        return redirect('admin_reservation_detail', reservation_id=reservation_id)
        import traceback
        traceback.print_exc()
        messages.error(request, f"حدث خطأ أثناء محاولة عرض تفاصيل الحجز: {str(e)}")
        return redirect('admin_reservations')

# وظائف الأرشيف الإلكتروني
@login_required
def archive_list(request):
    """عرض قائمة الوثائق المؤرشفة"""
    # التحقق من أن المستخدم مسؤول
    if not request.user.is_admin:
        messages.error(request, "ليس لديك صلاحية للوصول إلى هذه الصفحة")
        return redirect('index')
    
    # البحث والتصفية
    search_query = request.GET.get('search', '')
    document_type = request.GET.get('document_type', '')
    date_from = request.GET.get('date_from', '')
    date_to = request.GET.get('date_to', '')
    
    # استعلام قاعدة البيانات
    documents = Document.objects.all().order_by('-created_at')
    
    # تطبيق عوامل التصفية
    if search_query:
        documents = documents.filter(
            Q(title__icontains=search_query) |
            Q(reference_number__icontains=search_query) |
            Q(description__icontains=search_query) |
            Q(tags__icontains=search_query)
        )
    
    if document_type:
        documents = documents.filter(document_type=document_type)
    
    if date_from:
        try:
            date_from_obj = datetime.strptime(date_from, '%Y-%m-%d').date()
            documents = documents.filter(document_date__gte=date_from_obj)
        except ValueError:
            pass
    
    if date_to:
        try:
            date_to_obj = datetime.strptime(date_to, '%Y-%m-%d').date()
            documents = documents.filter(document_date__lte=date_to_obj)
        except ValueError:
            pass
    
    # الحصول على إحصائيات الأرشيف
    stats = {
        'total_documents': Document.objects.count(),
        'contracts': Document.objects.filter(document_type='contract').count(),
        'receipts': Document.objects.filter(document_type='receipt').count(),
        'custody': Document.objects.filter(document_type='custody').count(),
        'custody_release': Document.objects.filter(document_type='custody_release').count(),
        'official_documents': Document.objects.filter(document_type='official_document').count(),
        'other': Document.objects.filter(document_type='other').count(),
    }
    
    context = {
        'documents': documents,
        'stats': stats,
        'search_query': search_query,
        'document_type': document_type,
        'date_from': date_from,
        'date_to': date_to,
        'document_type_choices': Document.DOCUMENT_TYPE_CHOICES,
        'related_to_choices': Document.RELATED_TO_CHOICES,
    }
    
    # عرض القالب
    return render(request, 'admin/archive/documents.html', context)

@login_required
def add_document(request):
    """إضافة وثيقة جديدة إلى الأرشيف"""
    # التحقق من أن المستخدم مسؤول
    if not request.user.is_admin:
        messages.error(request, "ليس لديك صلاحية للوصول إلى هذه الصفحة")
        return redirect('index')
    
    if request.method == 'POST':
        # معالجة نموذج إضافة وثيقة
        title = request.POST.get('title')
        document_type = request.POST.get('document_type')
        description = request.POST.get('description')
        related_to = request.POST.get('related_to')
        document_date = request.POST.get('document_date')
        expiry_date = request.POST.get('expiry_date')
        tags = request.POST.get('tags')
        
        # استخراج المعرفات المرتبطة
        reservation_id = request.POST.get('reservation_id')
        car_id = request.POST.get('car_id')
        user_id = request.POST.get('user_id')
        reference_number = request.POST.get('reference_number')
        
        # إنشاء كائن الوثيقة
        document = Document(
            title=title,
            document_type=document_type,
            description=description,
            related_to=related_to,
            tags=tags,
            reference_number=reference_number,
            added_by=request.user
        )
        
        # ضبط التواريخ
        if document_date:
            try:
                document.document_date = datetime.strptime(document_date, '%Y-%m-%d').date()
            except ValueError:
                pass
        
        if expiry_date:
            try:
                document.expiry_date = datetime.strptime(expiry_date, '%Y-%m-%d').date()
            except ValueError:
                pass
        
        # ضبط العلاقات
        if reservation_id:
            document.reservation_id = reservation_id
        
        if car_id:
            document.car_id = car_id
        
        if user_id:
            document.user_id = user_id
        
        # حفظ ملف الوثيقة في قاعدة البيانات
        if 'file' in request.FILES:
            uploaded_file = request.FILES['file']
            file_name = uploaded_file.name
            file_type = uploaded_file.content_type
            file_size = uploaded_file.size
            file_content = uploaded_file.read()
            
            # تخزين معلومات الملف في قاعدة البيانات
            document.file_name = file_name
            document.file_type = file_type
            document.file_size = file_size
            document.file_content = file_content
            
            # إلغاء الملف في نظام الملفات
            document.file = None
        
        # حفظ الوثيقة
        document.save()
        
        messages.success(request, "تمت إضافة الوثيقة بنجاح")
        return redirect('admin_archive')
    
    # نموذج إضافة وثيقة جديدة
    context = {
        'document_type_choices': Document.DOCUMENT_TYPE_CHOICES,
        'related_to_choices': Document.RELATED_TO_CHOICES,
        'reservations': Reservation.objects.filter(status__in=['confirmed', 'completed']).order_by('-created_at')[:50],
        'cars': Car.objects.all().order_by('make'),
        'users': User.objects.all().order_by('username'),
    }
    
    return render(request, 'admin/archive/add_document.html', context)

@login_required
def document_detail(request, document_id):
    """عرض تفاصيل وثيقة"""
    # التحقق من أن المستخدم مسؤول
    if not request.user.is_admin:
        messages.error(request, "ليس لديك صلاحية للوصول إلى هذه الصفحة")
        return redirect('index')
    
    document = get_object_or_404(Document, id=document_id)
    
    context = {
        'document': document
    }
    
    return render(request, 'admin/archive/document_detail.html', context)

@login_required
@admin_required
def edit_document(request, document_id):
    """وظيفة تعديل وثيقة للحفاظ على التوافق مع الروابط القديمة. 
    تم توحيد الوظيفة مع admin_archive_edit."""
    
    # توجيه الطلب إلى الوظيفة المحسنة
    print(f"DEBUG: تم استدعاء edit_document، سيتم توجيه الطلب إلى admin_archive_edit")
    return admin_archive_edit(request, document_id)

@login_required
@admin_required
def delete_document(request, document_id):
    """حذف وثيقة"""
    
    document = get_object_or_404(Document, id=document_id)
    
    if request.method == 'POST':
        # حذف الوثيقة
        document.delete()
        messages.success(request, "تم حذف الوثيقة بنجاح")
        return redirect('admin_archive')
    
    context = {
        'document': document
    }
    
    return render(request, 'admin/archive/delete_document.html', context)

@login_required
@permission_required("reservations", "edit_reservations")
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
    # التعامل مع طلب حذف المستخدم
    delete_user_id = request.GET.get('delete_user')
    if delete_user_id:
        try:
            user = get_object_or_404(User, id=delete_user_id, is_admin=False)
            username = user.username
            
            # حذف المستخدم
            user.delete()
            
            messages.success(request, f"تم حذف المستخدم '{username}' بنجاح")
            return redirect('admin_users')
        except Exception as e:
            messages.error(request, f"حدث خطأ أثناء محاولة حذف المستخدم: {str(e)}")
            return redirect('admin_users')
    
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

    return render(request, 'admin/users_enhanced.html', context)

@login_required
@permission_required("payments", "view_payments")
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

    return render(request, 'admin/payments_dropdown.html', context)

@login_required
@permission_required("payments", "view_payments")
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
@permission_required("payments", "edit_payments")
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

    messages.success(request, f"تم استرداد المبلغ {payment.total_price} ريال يمني بنجاح!")
    return redirect('payment_details', payment_id=payment_id)

@login_required
@permission_required("payments", "edit_payments")
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
@permission_required("payments", "delete_payments")
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
@permission_required("payments", "view_payments")
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
@permission_required("payments", "view_payments")
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
# @permission_required("payments", "create_payments") - تم تعطيل التحقق من الصلاحيات مؤقتاً
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

                messages.success(request, f"تم تسجيل دفعة بقيمة {amount} ريال يمني للحجز #{reservation.id} بنجاح!")
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

                messages.success(request, f"تم تسجيل الدفعة بقيمة {amount} ريال يمني بنجاح للمستخدم {user.first_name} {user.last_name}!")
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
@permission_required("payments", "view_payments")
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
    """عرض الأرشيف الإلكتروني بالتصميم المحدث"""
    from django.utils.translation import get_language
    from django.shortcuts import redirect
    current_language = get_language()
    is_english = current_language == 'en'
    is_rtl = current_language == 'ar'
    
    # الحصول على معلمات URL
    folder_param = request.GET.get('folder', None)
    document_param = request.GET.get('document', None)
    action_param = request.GET.get('action', None)
    
    print(f"DEBUG - معلمة المجلد: {folder_param}")
    print(f"DEBUG - معلمة المستند: {document_param}")
    print(f"DEBUG - معلمة الإجراء: {action_param}")
    
    # معالجة طلبات POST من النماذج
    if request.method == 'POST':
        action = request.POST.get('action', None)
        
        # معالجة تحرير المجلد
        if action == 'edit_folder':
            folder_id = request.POST.get('folder_id', None)
            folder_name = request.POST.get('folder_name', '')
            
            if folder_id and folder_name:
                try:
                    folder = ArchiveFolder.objects.get(id=folder_id)
                    folder.name = folder_name
                    folder.save()
                    
                    # إعادة التوجيه إلى نفس المجلد
                    if folder.parent:
                        return redirect(f"{reverse('admin_archive')}?folder={folder.parent.id}")
                    else:
                        return redirect('admin_archive')
                except ArchiveFolder.DoesNotExist:
                    messages.error(request, _("المجلد غير موجود"))
                    return redirect('admin_archive')
        
        # معالجة حذف المجلد
        elif action == 'delete_folder':
            folder_id = request.POST.get('folder_id', None)
            
            if folder_id:
                try:
                    folder = ArchiveFolder.objects.get(id=folder_id)
                    parent_id = None
                    if folder.parent:
                        parent_id = folder.parent.id
                    
                    # حذف المجلد وكل محتوياته
                    folder.delete()
                    
                    # إعادة التوجيه إلى المجلد الأب أو الرئيسية
                    if parent_id:
                        return redirect(f"{reverse('admin_archive')}?folder={parent_id}")
                    else:
                        return redirect('admin_archive')
                except ArchiveFolder.DoesNotExist:
                    messages.error(request, _("المجلد غير موجود"))
                    return redirect('admin_archive')
        
        # معالجة تحرير المستند
        elif action == 'edit_document':
            document_id = request.POST.get('document_id', None)
            document_title = request.POST.get('document_title', '')
            
            if document_id and document_title:
                try:
                    document = Document.objects.get(id=document_id)
                    document.title = document_title
                    document.save()
                    
                    # إعادة التوجيه إلى نفس المجلد
                    if document.folder:
                        return redirect(f"{reverse('admin_archive')}?folder={document.folder.id}")
                    else:
                        return redirect('admin_archive')
                except Document.DoesNotExist:
                    messages.error(request, _("المستند غير موجود"))
                    return redirect('admin_archive')
        
        # معالجة حذف المستند
        elif action == 'delete_document':
            document_id = request.POST.get('document_id', None)
            
            if document_id:
                try:
                    document = Document.objects.get(id=document_id)
                    folder_id = None
                    if document.folder:
                        folder_id = document.folder.id
                    
                    # حذف المستند
                    document.delete()
                    
                    # إعادة التوجيه إلى نفس المجلد
                    if folder_id:
                        return redirect(f"{reverse('admin_archive')}?folder={folder_id}")
                    else:
                        return redirect('admin_archive')
                except Document.DoesNotExist:
                    messages.error(request, _("المستند غير موجود"))
                    return redirect('admin_archive')
    
    # معالجة إضافة مجلد جديد عبر GET (من القالب القديم)
    if action_param == 'add_folder' and request.method == 'POST':
        name = request.POST.get('name', '')
        description = request.POST.get('description', '')
        parent_id = request.POST.get('parent', None)
        
        if name:
            try:
                # البحث عن المجلد الأب إذا تم تحديده
                parent = None
                if parent_id:
                    try:
                        parent = ArchiveFolder.objects.get(id=parent_id)
                    except ArchiveFolder.DoesNotExist:
                        pass
                
                # إنشاء المجلد بطريقة آمنة تماماً تمنع إنشاء المستندات التلقائية
                # استخدام SQL المباشر لتجاوز آليات النظام
                from django.db import connection, transaction
                
                try:
                    with transaction.atomic():
                        cursor = connection.cursor()
                        
                        # تعطيل المحفزات (triggers) أثناء عملية الإنشاء
                        cursor.execute("SET session_replication_role = 'replica';")
                        
                        # الحصول على معرف المستخدم المنشئ إذا وجد
                        created_by_id = None
                        if request.user.is_authenticated:
                            created_by_id = request.user.id
                        
                        # تحضير قيمة parent_id
                        parent_id = None
                        if parent:
                            parent_id = parent.id
                        
                        # إنشاء المجلد مباشرة في قاعدة البيانات
                        sql = """
                        INSERT INTO rental_archivefolder 
                        (name, parent_id, created_at, updated_at, description, created_by_id, is_system_folder, folder_type) 
                        VALUES (%s, %s, NOW(), NOW(), %s, %s, %s, %s)
                        RETURNING id;
                        """
                        
                        cursor.execute(sql, [
                            name, 
                            parent_id, 
                            description, 
                            created_by_id,
                            False,  # is_system_folder
                            None    # folder_type
                        ])
                        
                        folder_id = cursor.fetchone()[0]
                        
                        # إعادة تفعيل المحفزات
                        cursor.execute("SET session_replication_role = 'origin';")
                        
                        # الحصول على كائن المجلد من قاعدة البيانات
                        folder = ArchiveFolder.objects.get(id=folder_id)
                        
                        # للتأكد - حذف أي مستندات قد تكون أنشئت بعد استعادة المحفزات
                        Document.objects.filter(folder=folder, title__in=['', 'بدون عنوان', None]).delete()
                        
                        print(f"DEBUG - تم إنشاء مجلد جديد: {folder.name} بأسلوب SQL المباشر الآمن ومنع أي مستندات تلقائية")
                except Exception as e:
                    print(f"ERROR - حدث خطأ أثناء إنشاء المجلد باستخدام SQL المباشر: {str(e)}")
                    # في حالة حدوث خطأ، ننشئ المجلد بالطريقة العادية المحسنة
                    folder = ArchiveFolder(name=name, description=description, parent=parent)
                    folder._skip_auto_document_creation = True  # منع المستندات التلقائية
                    # تعطيل المستندات التلقائية تماماً
                    folder.disable_auto_documents = True
                    folder._skip_auto_document_creation = True
                    folder._prevent_auto_docs = True
                    folder.save()
                    
                    # التنظيف الفوري بعد الحفظ
                    Document.objects.filter(folder=folder, title__in=['', 'بدون عنوان', None]).delete()
                    print(f"DEBUG - تم إنشاء المجلد باستخدام الطريقة البديلة: {folder.name}")
                messages.success(request, f"تم إنشاء المجلد '{name}' بنجاح")
                
                # إعادة توجيه إلى المجلد الجديد
                return redirect(f"{request.path}?folder={folder.id}")
            except Exception as e:
                # لوج أي استثناءات للمساعدة في عملية التصحيح
                print(f"ERROR - فشل في إنشاء المجلد: {str(e)}")
                messages.error(request, f"حدث خطأ أثناء إنشاء المجلد: {str(e)}")
        else:
            messages.error(request, "يرجى إدخال اسم المجلد")
    
    # معالجة إضافة ملف جديد
    if action_param == 'add_file' and request.method == 'POST':
        title = request.POST.get('title', '')
        description = request.POST.get('description', '')
        folder_id = request.POST.get('folder', None)
        uploaded_file = request.FILES.get('file', None)
        
        if title and uploaded_file:
            # البحث عن المجلد المستهدف إذا تم تحديده
            folder = None
            if folder_id:
                try:
                    folder = ArchiveFolder.objects.get(id=folder_id)
                except:
                    pass
            
            # حساب حجم الملف بوحدة البايت
            file_size = uploaded_file.size
            
            # تأكد من أن المستند ليس تلقائياً
            if not title or title.strip() == '' or title == 'بدون عنوان':
                print(f"DEBUG - محاولة إنشاء مستند تلقائي مرفوضة!")
                messages.error(request, "لا يمكن إنشاء مستند بدون عنوان")
                return redirect(request.path)
            
            # إنشاء مستند جديد (ملف) بطريقة آمنة
            try:
                # إضافة علامة واضحة لمنع إنشاء مستندات بشكل تلقائي فقط إذا كان هناك مجلد
                if folder is not None:
                    if not hasattr(folder, '_skip_auto_document_creation'):
                        setattr(folder, '_skip_auto_document_creation', True)
                    
                # قراءة معلومات الملف لتخزينه في قاعدة البيانات
                file_name = uploaded_file.name
                file_type = uploaded_file.content_type
                file_content = uploaded_file.read()
                
                # إنشاء المستند مع تخزين الملف في قاعدة البيانات
                document = Document.objects.create(
                    title=title,
                    description=description,
                    document_type='other',  # استخدام القيمة الافتراضية 'other'
                    # تخزين معلومات الملف في قاعدة البيانات
                    file_name=file_name,
                    file_type=file_type,
                    file_size=file_size,
                    file_content=file_content,
                    document_date=timezone.now().date(),
                    related_to='other',  # استخدام القيمة الافتراضية 'other'
                    added_by=request.user if request.user.is_authenticated else None,
                    folder=folder
                )
                
                print(f"🟢 تم إنشاء مستند جديد بنجاح: {document.title}")
                print(f"🟢 معرف المستند: {document.id}, في المجلد: {folder.name if folder else 'المجلد الرئيسي'}")
                print(f"🟢 حجم المستند: {file_size}, نوع الملف: {file_type}")
                # التحقق من أن المستند موجود في قاعدة البيانات
                verify_doc = Document.objects.filter(id=document.id).first()
                if verify_doc:
                    print(f"🟢 تم التحقق من وجود المستند في قاعدة البيانات، معرف: {verify_doc.id}, العنوان: {verify_doc.title}")
            except Exception as e:
                print(f"ERROR - فشل في إنشاء المستند: {str(e)}")
                messages.error(request, f"حدث خطأ أثناء إنشاء المستند: {str(e)}")
                return redirect(request.path)
            messages.success(request, f"تم إضافة الملف '{title}' بنجاح")
            
            # إعادة توجيه
            if folder:
                return redirect(f"{request.path}?folder={folder.id}")
            else:
                return redirect(request.path)
        else:
            if not title:
                messages.error(request, "يرجى إدخال عنوان الملف")
            if not uploaded_file:
                messages.error(request, "يرجى اختيار ملف للرفع")
    
    # الحصول على مجلدات الجذر وتجاهل المجلدات بدون اسم
    try:
        # استبعاد المجلدات بدون اسم أو باسم "بدون اسم"
        root_folders = ArchiveFolder.objects.filter(
            parent=None,
            name__isnull=False
        ).exclude(
            name__in=['بدون اسم', '', ' ']
        ).order_by('name')
        
        # الحصول على جميع المجلدات مع استبعاد المجلدات التلقائية
        all_folders = ArchiveFolder.objects.filter(
            name__isnull=False
        ).exclude(
            name__in=['بدون اسم', '', ' ']
        ).order_by('name')
        
        print(f"DEBUG - عدد المجلدات الرئيسية المفلترة: {root_folders.count()}")
        
        # حذف أي مجلدات غير صالحة تلقائيًا
        invalid_folders = ArchiveFolder.objects.filter(
            name__in=['بدون اسم', '', ' ']
        )
        if invalid_folders.exists():
            print(f"DEBUG - حذف {invalid_folders.count()} مجلد غير صالح تلقائيًا")
            invalid_folders.delete()
    except Exception as e:
        print(f"ERROR - حدثت مشكلة في استرجاع المجلدات: {str(e)}")
        # تعيين قوائم فارغة في حالة حدوث خطأ
        root_folders = ArchiveFolder.objects.none()
        all_folders = ArchiveFolder.objects.none()
    
    # معالجة إضافة مجلد جديد (ملحوظة: تم استبدال هذا بالتعليمات أعلاه)
    # لا حاجة لهذا الكود، تم تعريفه بالفعل في السطور الأولى من الدالة
    
    # ملاحظة: تم حذف كود إضافة الملف المكرر هنا لأنه تم تعريفه بالفعل في الأعلى
    
    # الحصول على المستندات والمجلدات الفرعية
    documents = []
    subfolders = []
    current_folder = None
    folder_path = []
    
    if folder_param:
        try:
            # تحقق إذا كان معرف المجلد عدداً صحيحاً
            try:
                folder_id = int(folder_param)
                # محاولة العثور على المجلد
                current_folder = ArchiveFolder.objects.get(id=folder_id)
                # الحصول على المجلدات الفرعية والمستندات
                subfolders = ArchiveFolder.objects.filter(parent=current_folder).order_by('name')
                
                # استعلام محسّن للمستندات: يشمل كل المستندات الصالحة وفلترة المستندات بشكل كامل
                try:
                    # الاستعلام الأساسي - بدون أي فلترة
                    base_documents = Document.objects.filter(folder=current_folder)
                    print(f"🔍 عدد المستندات الأولي في المجلد {current_folder.id}: {base_documents.count()}")
                    
                    # فلترة المستندات غير الصالحة
                    documents = base_documents.filter(
                        title__isnull=False
                    ).exclude(
                        title__in=["بدون عنوان", "", " ", "نموذج_استعلام_الارشيف", None]
                    ).order_by('-created_at')
                    
                    # التحقق من كل المستندات
                    all_docs = []
                    for doc in documents:
                        # جلب معلومات حول حالة المستند
                        has_file = hasattr(doc, 'file') and bool(doc.file)
                        has_content = hasattr(doc, 'file_content') and bool(doc.file_content)
                        
                        # طباعة معلومات عن المستند
                        print(f"🔍 مستند: {doc.id} | {doc.title} | file: {has_file} | file_content: {has_content}")
                        
                        # إضافة المستند إلى القائمة
                        all_docs.append(doc)
                    
                    # تحويل قائمة المستندات الصالحة إلى queryset جديد - الخطوة الحاسمة!
                    if all_docs:
                        documents = Document.objects.filter(id__in=[doc.id for doc in all_docs]).order_by('-created_at')
                    else:
                        documents = Document.objects.none()
                except Exception as e:
                    print(f"❌ خطأ في استرجاع المستندات: {str(e)}")
                    documents = Document.objects.none()
                
                # التحقق من المستندات وطباعة معلومات تصحيح
                print(f"🔍 المستندات في المجلد {current_folder.name} (ID: {current_folder.id}):")
                for doc in documents:
                    print(f"📄 مستند: {doc.id} | {doc.title} | {doc.file_name if hasattr(doc, 'file_name') else 'لا يوجد اسم ملف'}")
                    print(f"   - نوع التخزين: {'file_content' if doc.file_content else 'file' if doc.file else 'غير معروف'}")
                
                # بناء مسار المجلد
                folder_path = []
                temp_folder = current_folder
                while temp_folder:
                    folder_path.insert(0, temp_folder)
                    temp_folder = temp_folder.parent
                
                print(f"DEBUG - المجلد الحالي: {current_folder.name}")
                print(f"DEBUG - عدد المجلدات الفرعية: {subfolders.count()}")
                print(f"DEBUG - عدد المستندات: {documents.count()}")
            except ValueError:
                # إذا كان معرف المجلد ليس عدداً صحيحاً، نستخدم العرض الافتراضي
                print(f"DEBUG - استخدام العرض الافتراضي للمجلد: {folder_param}")
        except ArchiveFolder.DoesNotExist:
            print(f"DEBUG - المجلد غير موجود: {folder_param}")
    else:
        # عرض المستندات في المجلد الرئيسي (بدون مجلد) مع استبعاد المستندات التلقائية
        try:
            # الاستعلام الأساسي - بدون أي فلترة
            base_documents = Document.objects.filter(folder__isnull=True)
            print(f"🔍 عدد المستندات الأولي في المجلد الرئيسي: {base_documents.count()}")
            
            # فلترة المستندات غير الصالحة
            documents = base_documents.filter(
                title__isnull=False
            ).exclude(
                title__in=['بدون عنوان', '', ' ', 'نموذج_استعلام_الارشيف', None]
            ).order_by('-created_at')
            
            # طباعة معلومات المستندات في المجلد الرئيسي للتصحيح
            print(f"🔍 المستندات المفلترة في المجلد الرئيسي: {documents.count()}")
            
            # التحقق من كل المستندات
            all_docs = []
            for doc in documents:
                # جلب معلومات حول حالة المستند
                has_file = hasattr(doc, 'file') and bool(doc.file)
                has_content = hasattr(doc, 'file_content') and bool(doc.file_content)
                
                # طباعة معلومات عن المستند
                print(f"📄 مستند: {doc.id} | {doc.title} | file: {has_file} | file_content: {has_content}")
                print(f"   - نوع التخزين: {'file_content' if has_content else 'file' if has_file else 'غير معروف'}")
                
                # إضافة المستند إلى القائمة
                all_docs.append(doc)
            
            # تحويل قائمة المستندات الصالحة إلى queryset جديد
            if all_docs:
                documents = Document.objects.filter(id__in=[doc.id for doc in all_docs]).order_by('-created_at')
            else:
                documents = Document.objects.none()
                
        except Exception as e:
            print(f"❌ خطأ في استرجاع المستندات في المجلد الرئيسي: {str(e)}")
            documents = Document.objects.none()
    
    # إعداد سياق البيانات
    # إضافة وقت حالي لمنع التخزين المؤقت
    from datetime import datetime
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")
    
    context = {
        'root_folders': root_folders,
        'subfolders': subfolders,
        'documents': documents,
        'files': documents,  # إضافة المستندات كـ files للتوافق مع القالب
        'current_folder': current_folder,
        'folder_path': folder_path,
        'folder_param': folder_param,
        'document_param': document_param,
        'all_folders': all_folders,  # إضافة قائمة كاملة بجميع المجلدات
        'is_english': is_english,
        'is_rtl': is_rtl,
        'active_section': 'archive',
        'current_date_time': current_time  # إضافة وقت حالي لمنع التخزين المؤقت
    }
    
    # طباعة معلومات تصحيح إضافية عن كل مستند يتم تمريره للقالب
    print(f"🔄 تمرير {len(documents)} مستند للقالب:")
    for idx, doc in enumerate(documents):
        has_file_content = hasattr(doc, 'file_content') and doc.file_content is not None
        has_file = hasattr(doc, 'file') and doc.file is not None
        print(f"   {idx+1}. معرف: {doc.id}, العنوان: {doc.title}")
        print(f"      - file_content: {'موجود' if has_file_content else 'غير موجود'}")
        print(f"      - file: {'موجود' if has_file else 'غير موجود'}")
        print(f"      - file_name: {doc.file_name if hasattr(doc, 'file_name') else 'غير موجود'}")
        print(f"      - file_type: {doc.file_type if hasattr(doc, 'file_type') else 'غير موجود'}")
        
    # استخدام القالب المحدث
    return render(request, 'admin/archive/direct_fix_v2.html', context)

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
        
        # إنشاء المستند مع تخزين الملف في قاعدة البيانات
        uploaded_file = request.FILES['file']
        file_name = uploaded_file.name
        file_type = uploaded_file.content_type
        file_size = uploaded_file.size
        
        # قراءة محتوى الملف
        file_content = uploaded_file.read()
        
        document = Document(
            title=title,
            document_type=document_type,
            description=description,
            document_date=document_date,
            expiry_date=expiry_date,
            related_to=related_to,
            # تخزين معلومات الملف
            file_name=file_name,
            file_type=file_type,
            file_size=file_size,
            file_content=file_content,
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
    
    # تحديد لغة المستخدم
    from django.utils.translation import get_language
    current_language = get_language()
    is_english = current_language == 'en'
    is_rtl = current_language == 'ar'
    
    context = {
        'document_types': Document.DOCUMENT_TYPE_CHOICES,
        'related_to_types': Document.RELATED_TO_CHOICES,
        'reservations': reservations,
        'cars': cars,
        'users': users,
        'current_user': request.user,
        'today': timezone.now().date().strftime('%Y-%m-%d'),
        'is_english': is_english,
        'is_rtl': is_rtl,
        'active_section': 'archive'
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
    
    # تحديد لغة المستخدم
    from django.utils.translation import get_language
    current_language = get_language()
    is_english = current_language == 'en'
    is_rtl = current_language == 'ar'
    
    context = {
        'document': document,
        'related_entity': related_entity,
        'related_entity_type': related_entity_type,
        'current_user': request.user,
        'is_english': is_english,
        'is_rtl': is_rtl,
        'active_section': 'archive'
    }
    
    return render(request, 'admin/archive/document_detail.html', context)

@login_required
@admin_required
def admin_archive_edit(request, document_id):
    """تعديل مستند في الأرشيف"""
    document = get_object_or_404(Document, id=document_id)
    
    if request.method == 'POST':
        # طباعة البيانات المستلمة للتصحيح
        print(f"DEBUG: استلام بيانات POST لتعديل المستند {document_id}")
        print(f"DEBUG: محتويات POST: {request.POST}")
        
        # الحصول على بيانات النموذج
        title = request.POST.get('title')
        document_type = request.POST.get('document_type')
        description = request.POST.get('description', '')
        document_date_str = request.POST.get('document_date')
        expiry_date_str = request.POST.get('expiry_date', '')
        related_to = request.POST.get('related_to')
        related_id = request.POST.get('related_id', '')
        tags = request.POST.get('tags', '')
        
        print(f"DEBUG: القيم المستخرجة - العنوان: {title}, النوع: {document_type}, التاريخ: {document_date_str}, الارتباط: {related_to}")
        
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
            print(f"DEBUG: تم استلام ملف جديد لتحديث المستند {document_id}")
            
            # تعيين الملف مباشرة باستخدام حقل FileField - هذا يقوم تلقائياً بحذف الملف القديم
            document.file = request.FILES['file']
            
            # تحديث بيانات الملف (إذا كانت هذه الحقول موجودة في النموذج)
            if hasattr(document, 'file_name'):
                document.file_name = request.FILES['file'].name
                print(f"DEBUG: تم تحديث اسم الملف إلى {document.file_name}")
                
            if hasattr(document, 'file_type'):
                document.file_type = request.FILES['file'].content_type
                print(f"DEBUG: تم تحديث نوع الملف إلى {document.file_type}")
                
            if hasattr(document, 'file_size'):
                document.file_size = request.FILES['file'].size
                print(f"DEBUG: تم تحديث حجم الملف إلى {document.file_size}")
        
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
        
        # حفظ المستند - مع إضافة تسجيل تصحيح إضافي
        print(f"DEBUG: جاري حفظ المستند بالمعلومات المحدثة - العنوان: {document.title}, النوع: {document.document_type}")
        
        # حفظ بيانات المستند الحالية قبل الحفظ
        old_title = Document.objects.get(id=document_id).title
        old_type = Document.objects.get(id=document_id).document_type
        
        # تعيين علامة تجاوز منع المستندات التلقائية
        # هذه هي المشكلة الرئيسية - نحتاج إلى تعيين هذه العلامة لتجاوز إشارة pre_save
        setattr(document, '_ignore_auto_document_signal', True)
        print(f"DEBUG: تم تعيين علامة تجاوز منع المستندات التلقائية: {getattr(document, '_ignore_auto_document_signal', False)}")
        
        # استخدام المعاملات لضمان نجاح الحفظ
        with transaction.atomic():
            document.save()
        
        # التحقق من نجاح الحفظ
        updated_doc = Document.objects.get(id=document_id)
        print(f"DEBUG: تم حفظ المستند - البيانات القديمة: العنوان: {old_title}, النوع: {old_type}")
        print(f"DEBUG: تم حفظ المستند - البيانات الجديدة: العنوان: {updated_doc.title}, النوع: {updated_doc.document_type}")
        
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
    
    # تحديد لغة المستخدم
    from django.utils.translation import get_language
    current_language = get_language()
    is_english = current_language == 'en'
    is_rtl = current_language == 'ar'
    
    context = {
        'document': document,
        'document_types': Document.DOCUMENT_TYPE_CHOICES,
        'related_to_types': Document.RELATED_TO_CHOICES,
        'document_type_choices': Document.DOCUMENT_TYPE_CHOICES,  # Adding this for compatibility
        'related_to_choices': Document.RELATED_TO_CHOICES,  # Adding this for compatibility
        'reservations': reservations,
        'cars': cars,
        'users': users,
        'current_related_id': current_related_id,
        'current_user': request.user,
        'is_english': is_english,
        'is_rtl': is_rtl,
        'active_section': 'archive'
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
    
    # تحديد لغة المستخدم
    from django.utils.translation import get_language
    current_language = get_language()
    is_english = current_language == 'en'
    is_rtl = current_language == 'ar'
    
    context = {
        'document': document,
        'current_user': request.user,
        'is_english': is_english,
        'is_rtl': is_rtl,
        'active_section': 'archive'
    }
    
    return render(request, 'admin/archive/delete_document.html', context)

@login_required
@admin_required
def admin_archive_download(request, document_id):
    """تنزيل ملف مستند من الأرشيف - يدعم الملفات المخزنة في قاعدة البيانات"""
    document = get_object_or_404(Document, id=document_id)
    
    # فحص إذا كان الملف مخزن في قاعدة البيانات
    if document.file_content:
        try:
            # تحديد نوع MIME للملف
            content_type = document.file_type or 'application/octet-stream'
            
            # تحديد اسم الملف
            filename = document.file_name or f"document_{document.id}.bin"
            
            # إنشاء استجابة HttpResponse مع المحتوى الثنائي
            response = HttpResponse(document.file_content, content_type=content_type)
            response['Content-Disposition'] = f'attachment; filename="{filename}"'
            return response
            
        except Exception as e:
            print(f"خطأ في تنزيل المستند من قاعدة البيانات: {str(e)}")
            messages.error(request, f"حدث خطأ أثناء تنزيل الملف: {str(e)}")
            return redirect('admin_archive_detail', document_id=document_id)
    
    # إذا كان الملف غير مخزن في قاعدة البيانات، استخدم الطريقة القديمة
    elif document.file:
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
    else:
        messages.error(request, "الملف غير موجود")
        return redirect('admin_archive_detail', document_id=document_id)

@login_required
@admin_required
def admin_archive_view(request, document_id):
    """عرض ملف مستند مباشرة في المتصفح - يدعم الملفات المخزنة في قاعدة البيانات"""
    document = get_object_or_404(Document, id=document_id)
    
    print(f"🔍 محاولة عرض المستند: {document.id} | {document.title}")
    print(f"🔍 معلومات المستند: file_content: {'موجود' if document.file_content else 'غير موجود'}, file: {'موجود' if hasattr(document, 'file') and document.file else 'غير موجود'}")
    
    # التحقق من حجم ملف المستند
    if hasattr(document, 'file_size'):
        print(f"🔍 حجم الملف المسجل: {document.file_size} بايت")
    
    # فحص إذا كان الملف مخزن في قاعدة البيانات
    if document.file_content:
        try:
            print(f"📄 استخدام file_content للمستند {document.id} - حجم البيانات: {len(document.file_content)} بايت")
            
            # تحديد نوع MIME للملف
            content_type = document.file_type or 'application/octet-stream'
            print(f"📄 نوع المحتوى: {content_type}")
            
            # للصور والملفات النصية والـ PDF، استخدم العرض المباشر
            if (content_type.startswith('image/') or
                content_type.startswith('text/') or
                content_type == 'application/pdf'):
                disposition = 'inline'
            else:
                # للملفات الأخرى، استخدم التنزيل
                disposition = 'attachment'
            
            # إنشاء استجابة HttpResponse بدلاً من FileResponse
            response = HttpResponse(document.file_content, content_type=content_type)
            
            # تعيين اسم الملف إذا كان متوفرًا
            if document.file_name:
                response['Content-Disposition'] = f'{disposition}; filename="{document.file_name}"'
            else:
                response['Content-Disposition'] = disposition
            
            # إضافة رأس التخزين المؤقت
            response['Cache-Control'] = 'no-cache, no-store, must-revalidate'
            response['Pragma'] = 'no-cache'
            response['Expires'] = '0'
            
            print(f"✅ تم إنشاء استجابة صحيحة للمستند {document.id}")
            return response
        except Exception as e:
            print(f"❌ خطأ في عرض المستند من قاعدة البيانات: {str(e)}")
            import traceback
            print(f"التفاصيل: {traceback.format_exc()}")
            messages.error(request, f"حدث خطأ أثناء عرض الملف: {str(e)}")
            return redirect('admin_archive_detail', document_id=document_id)
    
    # إذا كان الملف غير مخزن في قاعدة البيانات، استخدم الطريقة القديمة
    elif document.file:
        try:
            print(f"📄 استخدام file.url للمستند {document.id}: {document.file.url}")
            file_path = document.file.path
            
            # التحقق من وجود الملف
            if not os.path.exists(file_path):
                print(f"❌ الملف غير موجود على المسار: {file_path}")
                messages.error(request, "الملف غير موجود على الخادم")
                return redirect('admin_archive_detail', document_id=document_id)
            
            # تسجيل معلومات إضافية
            file_size = os.path.getsize(file_path)
            print(f"📄 جاري فتح الملف: {file_path} | الحجم: {file_size} بايت")
            
            # تحديد نوع MIME للملف
            content_type, encoding = mimetypes.guess_type(file_path)
            if content_type is None:
                content_type = 'application/octet-stream'
            
            print(f"📄 نوع المحتوى: {content_type}")
            
            # للصور والملفات النصية والـ PDF، استخدم العرض المباشر
            if (content_type.startswith('image/') or
                content_type.startswith('text/') or
                content_type == 'application/pdf'):
                disposition = 'inline'
            else:
                # للملفات الأخرى، استخدم التنزيل
                disposition = 'attachment'
            
            # إرجاع استجابة FileResponse
            response = FileResponse(open(file_path, 'rb'), content_type=content_type)
            response['Content-Disposition'] = f'{disposition}; filename="{os.path.basename(file_path)}"'
            
            # إضافة رأس التخزين المؤقت
            response['Cache-Control'] = 'no-cache, no-store, must-revalidate'
            response['Pragma'] = 'no-cache'
            response['Expires'] = '0'
            
            print(f"✅ تم إنشاء استجابة FileResponse للمستند {document.id}")
            return response
        
        except Exception as e:
            print(f"❌ خطأ في عرض المستند من الملف: {str(e)}")
            import traceback
            print(f"التفاصيل: {traceback.format_exc()}")
            messages.error(request, f"حدث خطأ أثناء عرض الملف: {str(e)}")
            return redirect('admin_archive_detail', document_id=document_id)
    else:
        print(f"❌ لا يوجد ملف مرتبط بالمستند {document.id}")
        messages.error(request, "الملف غير موجود")
        return redirect('admin_archive_detail', document_id=document_id)

# دوال إدارة المجلدات في نظام الأرشيف

@login_required
@admin_required
def admin_archive_folders(request):
    """صفحة إدارة مجلدات الأرشيف"""
    # تحديد لغة العرض
    from django.utils.translation import get_language
    current_language = get_language()
    is_english = current_language == 'en'
    is_rtl = current_language == 'ar'
    
    # الحصول على جميع المجلدات الجذرية (بدون أب)
    root_folders = ArchiveFolder.get_root_folders()
    
    # إحصائيات المجلدات
    total_folders = ArchiveFolder.objects.count()
    system_folders_count = ArchiveFolder.objects.filter(is_system_folder=True).count()
    custom_folders_count = total_folders - system_folders_count
    total_documents = Document.objects.count()
    
    # الحصول على عدد المستندات في كل مجلد جذري
    for folder in root_folders:
        folder.documents_count = folder.all_document_count
    
    context = {
        'folders': root_folders,
        'total_folders': total_folders,
        'system_folders_count': system_folders_count,
        'custom_folders_count': custom_folders_count,
        'total_documents': total_documents,
        'is_english': is_english,
        'is_rtl': is_rtl,
        'current_user': request.user,
        'active_section': 'archive'
    }
    
    return render(request, 'admin/archive/folders.html', context)

@login_required
@admin_required
def admin_archive_folder_add(request):
    """إضافة مجلد جديد للأرشيف"""
    # تحديد لغة العرض
    from django.utils.translation import get_language
    current_language = get_language()
    is_english = current_language == 'en'
    is_rtl = current_language == 'ar'
    
    if request.method == 'POST':
        folder_name = request.POST.get('name')
        description = request.POST.get('description', '')
        parent_id = request.POST.get('parent_id')
        folder_type = request.POST.get('folder_type', '')
        
        # التحقق من البيانات
        if not folder_name:
            messages.error(request, "يرجى إدخال اسم المجلد")
            return redirect('admin_archive_folder_add')
        
        # إنشاء مجلد جديد - منع إنشاء المستندات التلقائية تماماً
        try:
            print("🔴 بدء عملية إنشاء مجلد جديد...")
            
            # البحث عن المجلد الأب إذا كان موجودًا
            parent_folder = None
            if parent_id:
                try:
                    parent_folder = ArchiveFolder.objects.get(id=parent_id)
                except ArchiveFolder.DoesNotExist:
                    messages.warning(request, "لم يتم العثور على المجلد الأب المحدد")
            
            # الحل: استخدام إنشاء SQL مباشر لتجاوز signals و triggers
            from django.db import transaction, connection
            
            # إنشاء المجلد مباشرة للتأكد من تجاوز أي سلوك تلقائي
            with transaction.atomic():
                try:
                    # محاولة تنفيذ استعلام SQL مباشر أولاً
                    cursor = connection.cursor()
                    
                    # تحضير البيانات
                    created_by_id = request.user.id if request.user.is_authenticated else None
                    parent_id_value = parent_folder.id if parent_folder else None
                    is_system_folder = False
                    
                    # استخدم اسم جدول المجلد + المستند من قاعدة البيانات الفعلية
                    folder_table_name = ArchiveFolder._meta.db_table
                    document_table_name = Document._meta.db_table
                    
                    # طباعة تشخيصية
                    print(f"🔴 اسم جدول المجلد الفعلي في قاعدة البيانات: {folder_table_name}")
                    print(f"🔴 اسم جدول المستند الفعلي في قاعدة البيانات: {document_table_name}")
                    
                    # إيقاف المحفز (trigger) المسؤول عن إنشاء المستندات التلقائية
                    try:
                        cursor.execute("SET session_replication_role = 'replica';")
                        print("🔴 تم تعطيل المحفزات مؤقتًا")
                    except Exception as e:
                        print(f"🔴 عدم القدرة على تعطيل المحفزات: {str(e)}")
                    
                    # الاستعلام SQL
                    sql = f"""
                    INSERT INTO {folder_table_name} 
                    (name, parent_id, created_at, updated_at, description, created_by_id, is_system_folder, folder_type) 
                    VALUES (%s, %s, NOW(), NOW(), %s, %s, %s, %s)
                    RETURNING id;
                    """
                    
                    cursor.execute(sql, [folder_name, parent_id_value, description, created_by_id, is_system_folder, folder_type])
                    folder_id = cursor.fetchone()[0]
                    
                    # إعادة تفعيل المحفزات
                    try:
                        cursor.execute("SET session_replication_role = 'origin';")
                        print("🔴 تم إعادة تفعيل المحفزات")
                    except Exception as e:
                        print(f"🔴 عدم القدرة على إعادة تفعيل المحفزات: {str(e)}")
                    
                    # الحصول على كائن المجلد المنشأ حديثاً
                    folder = ArchiveFolder.objects.get(id=folder_id)
                    print(f"🔴 تم إنشاء المجلد مباشرة عبر SQL: {folder.name} (ID: {folder.id})")
                    
                    # حذف أي مستندات تلقائية قد تكون أنشئت
                    docs = Document.objects.filter(folder=folder)
                    if docs.exists():
                        doc_count = docs.count()
                        docs.delete()
                        print(f"🔴 تم حذف {doc_count} مستند تلقائي")
                    
                except Exception as e:
                    print(f"🔴 حدث خطأ في إنشاء المجلد عبر SQL: {str(e)}")
                    print("🔴 الانتقال إلى الخطة البديلة باستخدام ORM...")
                    
                    # خطة بديلة: استخدام داله ORM مع منع المستندات
                    folder = ArchiveFolder(
                        name=folder_name,
                        description=description,
                        folder_type=folder_type,
                        parent=parent_folder,
                        created_by=request.user,
                        is_system_folder=False
                    )
                    
                    # وضع علامة على المجلد لمنع إنشاء المستندات
                    folder._skip_auto_document_creation = True
                    print("🔴 تم تعيين _skip_auto_document_creation = True على المجلد")
                    
                    # حفظ المجلد
                    # تعطيل المستندات التلقائية تماماً
                    folder.disable_auto_documents = True
                    folder._skip_auto_document_creation = True
                    folder._prevent_auto_docs = True
                    folder.save()
                    
                    # التنظيف الفوري بعد الحفظ
                    Document.objects.filter(folder=folder, title__in=['', 'بدون عنوان', None]).delete()
                    print(f"🔴 تم حفظ المجلد باستخدام ORM: {folder.name} (ID: {folder.id})")
                
                # تنظيف أي مستندات تم إنشاؤها
                doc_count = Document.objects.filter(folder=folder).count()
                if doc_count > 0:
                    print(f"🔴 تم العثور على {doc_count} مستند تلقائي رغم المحاولات - حذف نهائي")
                    # فقط حذف المستندات التلقائية (التي بدون عنوان) - الحل النهائي
                    Document.objects.filter(folder=folder, title__in=['', 'بدون عنوان', None]).delete()
            
            # تأكد من عدم وجود مستندات تلقائية خارج نطاق المعاملة
            doc_count = Document.objects.filter(folder=folder, title__in=['', 'بدون عنوان', None]).count()
            if doc_count > 0:
                print(f"🔴 مازال هناك {doc_count} مستند! محاولة حذف أخيرة")
                Document.objects.filter(folder=folder, title__in=['', 'بدون عنوان', None]).delete()
            
            # رسالة تأكيد وتوجيه المستخدم
            print(f"🔴 اكتملت عملية إنشاء المجلد {folder.name} بمعرف {folder.id} بنجاح")
            messages.success(request, f"تم إنشاء المجلد '{folder_name}' بنجاح")
            return redirect('admin_archive')
        except Exception as e:
            print(f"🔴 حدث خطأ غير متوقع أثناء إنشاء المجلد: {str(e)}")
            messages.error(request, f"حدث خطأ أثناء إنشاء المجلد: {str(e)}")
    
    # الحصول على قائمة المجلدات الموجودة للاختيار من بينها
    all_folders = ArchiveFolder.objects.all().order_by('name')
    folder_types = ['حجوزات', 'سيارات', 'عقود', 'إيصالات', 'مستندات رسمية', 'أخرى']
    
    context = {
        'all_folders': all_folders,
        'folder_types': folder_types,
        'is_english': is_english,
        'is_rtl': is_rtl,
        'current_user': request.user,
        'active_section': 'archive'
    }
    
    return render(request, 'admin/archive/add_folder.html', context)

@login_required
@admin_required
def admin_archive_folder_view(request, folder_id):
    """عرض محتويات مجلد معين - النظام الشجري الجديد"""
    folder = get_object_or_404(ArchiveFolder, id=folder_id)
    # تنظيف تلقائي للمستندات التلقائية عند فتح المجلد
    title_conditions = Q(title__isnull=True) | Q(title='') | Q(title='بدون عنوان')
    auto_docs = Document.objects.filter(folder=folder).filter(title_conditions)
    if auto_docs.exists():
        deleted_count = auto_docs.count()
        print(f"🧹 تم حذف {deleted_count} مستند تلقائي من المجلد {folder.name} (ID: {folder.id})")
        auto_docs.delete()
    
    
    # تحديد لغة العرض
    from django.utils.translation import get_language
    current_language = get_language()
    is_english = current_language == 'en'
    is_rtl = current_language == 'ar'
    
    # البحث والتصفية
    search = request.GET.get('search', '')
    
    # الحصول على المجلدات الفرعية
    subfolders = folder.children.all().order_by('name')
    
    # الحصول على المستندات في هذا المجلد مع تطبيق البحث إذا وجد
    files = folder.documents.filter(title__isnull=False).exclude(title__in=["بدون عنوان", "", " ", "نموذج_استعلام_الارشيف"]).order_by('-created_at')
    if search:
        files = files.filter(
            Q(title__icontains=search) | 
            Q(description__icontains=search) | 
            Q(reference_number__icontains=search) |
            Q(tags__icontains=search)
        )
    
    # بناء شجرة المجلدات للجافاسكريبت
    def build_tree(folder_obj):
        result = {
            'id': folder_obj.id,
            'text': folder_obj.name,
            'icon': 'fas fa-folder',
            'state': {
                'opened': folder_obj.id == folder.id or any(p.id == folder_obj.id for p in folder_path)
            },
            'children': []
        }
        
        # إضافة المجلدات الفرعية
        for child in folder_obj.children.all().order_by('name'):
            result['children'].append(build_tree(child))
        
        return result
    
    # الحصول على مسار المجلد الكامل (من الجذر إلى هذا المجلد)
    folder_path = []
    current = folder
    while current:
        folder_path.insert(0, current)
        current = current.parent
    
    # بناء شجرة كاملة من الجذر
    root_folders = ArchiveFolder.get_root_folders()
    folder_tree = []
    
    # إضافة نقطة الجذر (الرئيسية)
    folder_tree.append({
        'id': '#',
        'text': _('الرئيسية'),
        'icon': 'fas fa-hdd',
        'state': {
            'opened': True
        }
    })
    
    # إضافة المجلدات الرئيسية
    for root_folder in root_folders:
        folder_tree.append(build_tree(root_folder))
    
    context = {
        'folder': folder,
        'folder_path': folder_path,
        'subfolders': subfolders,
        'files': files,
        'total_folders': subfolders.count(),
        'total_files': files.count(),
        'folder_tree': json.dumps(folder_tree),
        'search': search,
        'today': timezone.now().date().strftime('%Y-%m-%d'),
        'current_folder': folder,
        'is_english': is_english,
        'is_rtl': is_rtl,
        'current_user': request.user,
        'active_section': 'archive'
    }
    
    return render(request, 'admin/archive/archive_main.html', context)

@login_required
@admin_required
def admin_archive_folder_edit(request, folder_id):
    """تعديل مجلد في الأرشيف"""
    folder = get_object_or_404(ArchiveFolder, id=folder_id)
    
    # تحديد لغة العرض
    from django.utils.translation import get_language
    current_language = get_language()
    is_english = current_language == 'en'
    is_rtl = current_language == 'ar'
    
    if request.method == 'POST':
        folder_name = request.POST.get('name')
        description = request.POST.get('description', '')
        parent_id = request.POST.get('parent_id')
        folder_type = request.POST.get('folder_type', '')
        
        # التحقق من البيانات
        if not folder_name:
            messages.error(request, "يرجى إدخال اسم المجلد")
            return redirect('admin_archive_folder_edit', folder_id=folder_id)
        
        # منع وضع المجلد كأب لنفسه أو أحد أبنائه (لتجنب الدورة)
        if parent_id and int(parent_id) == folder.id:
            messages.error(request, "لا يمكن جعل المجلد أباً لنفسه")
            return redirect('admin_archive_folder_edit', folder_id=folder_id)
        
        # تحديث بيانات المجلد
        folder.name = folder_name
        folder.description = description
        folder.folder_type = folder_type
        
        # تحديث المجلد الأب إذا تم تغييره
        if parent_id:
            try:
                # التحقق من أن المجلد الجديد ليس من الأبناء لتجنب التداخل
                new_parent = ArchiveFolder.objects.get(id=parent_id)
                # فحص ما إذا كان المجلد الجديد هو ابن للمجلد الحالي
                temp_parent = new_parent
                while temp_parent:
                    if temp_parent.id == folder.id:
                        messages.error(request, "لا يمكن اختيار مجلد فرعي كأب")
                        return redirect('admin_archive_folder_edit', folder_id=folder_id)
                    temp_parent = temp_parent.parent
                
                folder.parent = new_parent
            except ArchiveFolder.DoesNotExist:
                folder.parent = None
        else:
            folder.parent = None
        
        # حفظ التغييرات
        try:
            # تعطيل المستندات التلقائية تماماً
            folder.disable_auto_documents = True
            folder._skip_auto_document_creation = True
            folder._prevent_auto_docs = True
            folder.save()
            
            # التنظيف الفوري بعد الحفظ
            Document.objects.filter(folder=folder, title__in=['', 'بدون عنوان', None]).delete()
            
            messages.success(request, f"تم تحديث المجلد '{folder_name}' بنجاح")
            return redirect('admin_archive_folder', folder_id=folder.id)
        except Exception as e:
            messages.error(request, f"حدث خطأ أثناء تحديث المجلد: {str(e)}")
    
    # الحصول على قائمة المجلدات الموجودة للاختيار من بينها (باستثناء هذا المجلد وأبنائه)
    excluded_ids = [folder.id]
    # الحصول على معرفات جميع الأبناء بشكل عودي
    def get_child_ids(folder_obj):
        child_ids = list(folder_obj.children.values_list('id', flat=True))
        for child_id in list(child_ids):  # استخدام نسخة من القائمة لتجنب مشاكل التكرار
            child = ArchiveFolder.objects.get(id=child_id)
            child_ids.extend(get_child_ids(child))
        return child_ids
    
    excluded_ids.extend(get_child_ids(folder))
    selectable_folders = ArchiveFolder.objects.exclude(id__in=excluded_ids).order_by('name')
    
    folder_types = ['حجوزات', 'سيارات', 'عقود', 'إيصالات', 'مستندات رسمية', 'أخرى']
    
    context = {
        'folder': folder,
        'selectable_folders': selectable_folders,
        'folder_types': folder_types,
        'is_english': is_english,
        'is_rtl': is_rtl,
        'current_user': request.user,
        'active_section': 'archive'
    }
    
    return render(request, 'admin/archive/edit_folder.html', context)

@login_required
@admin_required
def admin_archive_folder_delete(request, folder_id):
    """حذف مجلد من الأرشيف"""
    folder = get_object_or_404(ArchiveFolder, id=folder_id)
    
    # تحديد لغة العرض
    from django.utils.translation import get_language
    current_language = get_language()
    is_english = current_language == 'en'
    is_rtl = current_language == 'ar'
    
    # منع حذف المجلدات النظامية
    if folder.is_system_folder:
        messages.error(request, "لا يمكن حذف مجلدات النظام")
        return redirect('admin_archive_folder', folder_id=folder_id)
    
    if request.method == 'POST':
        parent_id = folder.parent.id if folder.parent else None
        
        # تحديد كيفية التعامل مع المحتويات
        documents_action = request.POST.get('documents_action')
        subfolders_action = request.POST.get('subfolders_action')
        
        # تحريك المستندات إلى المجلد الأب أو حذفها
        if documents_action == 'move' and folder.parent:
            Document.objects.filter(folder=folder).update(folder=folder.parent)
        
        # تحريك المجلدات الفرعية إلى المجلد الأب أو حذفها
        if subfolders_action == 'move' and folder.parent:
            ArchiveFolder.objects.filter(parent=folder).update(parent=folder.parent)
        
        # حذف المجلد
        folder_name = folder.name
        folder.delete()
        
        messages.success(request, f"تم حذف المجلد '{folder_name}' بنجاح")
        if parent_id:
            return redirect('admin_archive_folder', folder_id=parent_id)
        else:
            return redirect('admin_archive_folders')
    
    # حساب عدد المستندات والمجلدات الفرعية
    documents_count = folder.documents.count()
    subfolders_count = folder.children.count()
    
    context = {
        'folder': folder,
        'documents_count': documents_count,
        'subfolders_count': subfolders_count,
        'has_parent': folder.parent is not None,
        'is_english': is_english,
        'is_rtl': is_rtl,
        'current_user': request.user,
        'active_section': 'archive'
    }
    
    return render(request, 'admin/archive/delete_folder.html', context)

@login_required
@admin_required
def admin_archive_folder_documents(request, folder_id):
    """عرض مستندات مجلد معين (مع تصفية وبحث)"""
    folder = get_object_or_404(ArchiveFolder, id=folder_id)
    
    # تحديد لغة العرض
    from django.utils.translation import get_language
    current_language = get_language()
    is_english = current_language == 'en'
    is_rtl = current_language == 'ar'
    
    # الحصول على معلمات التصفية
    document_type = request.GET.get('document_type', '')
    related_to = request.GET.get('related_to', '')
    start_date_str = request.GET.get('start_date', '')
    end_date_str = request.GET.get('end_date', '')
    search = request.GET.get('search', '')
    
    # تصفية المستندات
    documents = folder.documents.filter(title__isnull=False).exclude(title__in=["بدون عنوان", "", " ", "نموذج_استعلام_الارشيف"]).order_by('-created_at')
    
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
    
    # الحصول على مسار المجلد الكامل
    folder_path = []
    current = folder
    while current:
        folder_path.insert(0, current)
        current = current.parent
    
    context = {
        'folder': folder,
        'folder_path': folder_path,
        'documents': documents_page,
        'total_documents': documents.count(),
        'document_type_filter': document_type,
        'related_to_filter': related_to,
        'start_date': start_date_str,
        'end_date': end_date_str,
        'search': search,
        'document_types': Document.DOCUMENT_TYPE_CHOICES,
        'related_to_types': Document.RELATED_TO_CHOICES,
        'is_english': is_english,
        'is_rtl': is_rtl,
        'current_user': request.user,
        'active_section': 'archive'
    }
    
    return render(request, 'admin/archive/folder_documents.html', context)

@login_required
@admin_required
def admin_archive_folder_add_document(request, folder_id):
    """إضافة مستند جديد إلى مجلد محدد"""
    folder = get_object_or_404(ArchiveFolder, id=folder_id)
    
    # تحديد لغة العرض
    from django.utils.translation import get_language
    current_language = get_language()
    is_english = current_language == 'en'
    is_rtl = current_language == 'ar'
    
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
            return redirect('admin_archive_folder_add_document', folder_id=folder_id)
        
        # التحقق من وجود ملف مرفق
        if 'file' not in request.FILES:
            messages.error(request, "يرجى تحميل ملف المستند")
            return redirect('admin_archive_folder_add_document', folder_id=folder_id)
        
        # تحويل التواريخ
        try:
            document_date = datetime.strptime(document_date_str, '%Y-%m-%d').date()
        except ValueError:
            messages.error(request, "تنسيق تاريخ المستند غير صحيح")
            return redirect('admin_archive_folder_add_document', folder_id=folder_id)
        
        expiry_date = None
        if expiry_date_str:
            try:
                expiry_date = datetime.strptime(expiry_date_str, '%Y-%m-%d').date()
            except ValueError:
                messages.error(request, "تنسيق تاريخ انتهاء الصلاحية غير صحيح")
                return redirect('admin_archive_folder_add_document', folder_id=folder_id)
        
        # إنشاء المستند مع تخزين الملف في قاعدة البيانات
        uploaded_file = request.FILES['file']
        file_name = uploaded_file.name
        file_type = uploaded_file.content_type
        file_size = uploaded_file.size
        
        # قراءة محتوى الملف
        file_content = uploaded_file.read()
        
        document = Document(
            title=title,
            document_type=document_type,
            description=description,
            document_date=document_date,
            expiry_date=expiry_date,
            related_to=related_to,
            # تخزين معلومات الملف في قاعدة البيانات
            file_name=file_name,
            file_type=file_type,
            file_size=file_size,
            file_content=file_content,
            tags=tags,
            added_by=request.user,
            folder=folder
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
        
        messages.success(request, f"تم إضافة المستند '{title}' إلى المجلد '{folder.name}' بنجاح")
        return redirect('admin_archive_folder', folder_id=folder_id)
    
    # الحصول على قوائم للعلاقات
    reservations = Reservation.objects.order_by('-created_at')[:50]
    cars = Car.objects.order_by('-id')[:50]
    users = User.objects.order_by('-date_joined')[:50]
    
    context = {
        'folder': folder,
        'document_types': Document.DOCUMENT_TYPE_CHOICES,
        'related_to_types': Document.RELATED_TO_CHOICES,
        'reservations': reservations,
        'cars': cars,
        'users': users,
        'today': timezone.now().date().strftime('%Y-%m-%d'),
        'is_english': is_english,
        'is_rtl': is_rtl,
        'current_user': request.user,
        'active_section': 'archive'
    }
    
    return render(request, 'admin/archive/add_document_to_folder.html', context)

@login_required
@admin_required
def admin_archive_tree(request):
    """عرض هيكل المجلدات بشكل شجري - الواجهة الجديدة للأرشيف"""
    # تحديد لغة العرض
    from django.utils.translation import get_language
    current_language = get_language()
    is_english = current_language == 'en'
    is_rtl = current_language == 'ar'
    
    # البحث والتصفية
    search = request.GET.get('search', '')
    
    # الحصول على مجلدات الجذر
    root_folders = ArchiveFolder.get_root_folders()
    
    # الحصول على المستندات في المجلد الرئيسي (بدون مجلد) مع تطبيق البحث إذا وجد
    files = Document.objects.filter(folder__isnull=True).order_by('-created_at')
    if search:
        files = files.filter(
            Q(title__icontains=search) | 
            Q(description__icontains=search) | 
            Q(reference_number__icontains=search) |
            Q(tags__icontains=search)
        )
    
    # بناء هيكل البيانات الشجري للعرض في jsTree
    def build_tree(folder):
        # حساب عدد المستندات في المجلد
        document_count = folder.documents.count() if hasattr(folder, 'documents') else 0
        
        # تحديد ما إذا كان المجلد نظامي
        is_system_folder = folder.is_system_folder if hasattr(folder, 'is_system_folder') else False
        
        # تحديد نص العقدة
        folder_text = folder.name
        
        # إضافة عدد المستندات إذا كان هناك مستندات
        if document_count > 0:
            folder_text += f' <span class="badge bg-primary rounded-pill">{document_count}</span>'
        
        # إضافة شارة للمجلد النظامي
        if is_system_folder:
            folder_text += ' <span class="badge bg-secondary">نظامي</span>'
        
        result = {
            'id': f'folder-{folder.id}',
            'text': folder_text,
            'icon': 'fas fa-folder' + ('-open' if document_count > 0 else ''),
            'type': 'system-folder' if is_system_folder else ('document-folder' if document_count > 0 else 'default'),
            'state': {
                'opened': False
            },
            'a_attr': {
                'href': f'/dashboard/archive/folder/{folder.id}/',
                'data-folder-id': folder.id
            },
            'children': []
        }
        
        # إضافة المجلدات الفرعية
        for child in folder.children.all().order_by('name'):
            result['children'].append(build_tree(child))
        
        return result
    
    # بناء شجرة المجلدات للعرض في جافاسكريبت
    folder_tree = []
    
    # إضافة نقطة الجذر (الرئيسية)
    folder_tree.append({
        'id': '#',
        'text': _('الرئيسية'),
        'icon': 'fas fa-hdd',
        'state': {
            'opened': True
        }
    })
    
    # إضافة المجلدات الرئيسية
    for folder in root_folders:
        folder_tree.append(build_tree(folder))
    
    # إحصائيات النظام
    total_folders = ArchiveFolder.objects.count()
    total_files = Document.objects.count()
    system_folders = ArchiveFolder.objects.filter(is_system_folder=True).count()
    custom_folders = total_folders - system_folders
    
    context = {
        'folder_tree': json.dumps(folder_tree),
        'subfolders': root_folders,
        'files': files,
        'total_folders': total_folders,
        'total_files': total_files,
        'total_documents': total_files,  # لتوافق اسم المتغير في القالب
        'system_folders': system_folders,
        'custom_folders': custom_folders,
        'search': search,
        'today': timezone.now().date().strftime('%Y-%m-%d'),
        'is_english': is_english,
        'is_rtl': is_rtl,
        'current_user': request.user,
        'active_section': 'archive'
    }
    
    return render(request, 'admin/archive/folder_tree.html', context)

@login_required
def view_document(request, document_id):
    """
    عرض المستند مباشرة في المتصفح
    """
    # الحصول على المستند من قاعدة البيانات
    document = get_object_or_404(Document, id=document_id)
    
    # معلومات تشخيصية للمستند
    print(f"DEBUG - طلب عرض المستند: ID={document.id}, العنوان={document.title}")
    print(f"DEBUG - معلومات الملف: اسم={document.file_name}, نوع={document.file_type}, حجم={document.file_size} بايت")
    print(f"DEBUG - حجم محتوى الملف: {len(document.file_content) if document.file_content else 0} بايت")
    
    # إذا كان المستند غير موجود، نعرض رسالة خطأ
    if not document.file_content:
        print(f"ERROR - محتوى الملف غير موجود للمستند ID={document.id}, العنوان={document.title}")
        messages.error(request, _("هذا المستند غير متوفر للعرض."))
        return redirect('admin_archive')
    
    # دائماً سنعرض الملف في المتصفح
    content_type = document.file_type or mimetypes.guess_type(document.file_name)[0] or 'application/octet-stream'
    response = HttpResponse(document.file_content, content_type=content_type)
    
    # إضافة رأس Content-Disposition لإخبار المتصفح بعرض الملف بدلاً من تنزيله
    response['Content-Disposition'] = f'inline; filename="{document.file_name}"'
    
    return response

def download_document(request, document_id):
    """
    تنزيل المستند من قاعدة البيانات أو عرضه مباشرة في المتصفح
    """
    # الحصول على المستند من قاعدة البيانات
    document = get_object_or_404(Document, id=document_id)
    
    # معلومات تشخيصية للمستند
    print(f"DEBUG - طلب تنزيل المستند: ID={document.id}, العنوان={document.title}")
    print(f"DEBUG - معلومات الملف: اسم={document.file_name}, نوع={document.file_type}, حجم={document.file_size} بايت")
    print(f"DEBUG - حجم محتوى الملف: {len(document.file_content) if document.file_content else 0} بايت")
    
    # إذا كان المستند غير موجود، نعرض رسالة خطأ
    if not document.file_content:
        print(f"ERROR - محتوى الملف غير موجود للمستند ID={document.id}, العنوان={document.title}")
        messages.error(request, _("هذا المستند غير متوفر للتحميل."))
        return redirect('admin_archive')
    
    # تحديد ما إذا كان يجب عرض الملف مباشرة أو تنزيله
    # سنعرض الصور وملفات PDF مباشرة في المتصفح
    is_viewable = False
    if document.file_type:
        if document.file_type.startswith('image/') or document.file_type == 'application/pdf':
            is_viewable = True
    
    # تكوين استجابة الملف
    response = HttpResponse(
        document.file_content,
        content_type=document.file_type or 'application/octet-stream'
    )
    
    # تحديد اسم الملف
    filename = document.file_name or f"{document.title}.{document.file_type.split('/')[-1] if document.file_type else 'pdf'}"
    
    # إذا كان الملف قابل للعرض، عرضه مباشرة في المتصفح
    if is_viewable:
        # عرض الملف مباشرة في المتصفح
        response['Content-Disposition'] = f'inline; filename="{filename}"'
        print(f"DEBUG - تم عرض الملف مباشرة في المتصفح: {filename}, الحجم={len(document.file_content)} بايت")
    else:
        # تنزيل الملف
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        print(f"DEBUG - تم إرسال الملف للتنزيل: {filename}, الحجم={len(document.file_content)} بايت")
    
    return response

@login_required
@admin_required
def admin_archive_upload(request):
    """وظيفة رفع الملفات المباشرة للأرشيف - نسخة محسنة تتجاوز منع المستندات التلقائية"""
    import traceback
    
    # طباعة معلومات الطلب للتشخيص
    print("\n=== بدء معالجة طلب رفع مستند جديد ===")
    print(f"طريقة الطلب: {request.method}")
    print(f"البيانات المرسلة: {request.POST}")
    print(f"الملفات المرفوعة: {request.FILES.keys() if request.FILES else 'لا يوجد'}")
    
    if request.method != 'POST':
        messages.error(request, "طريقة طلب غير صالحة")
        return redirect('admin_archive')
    
    # استخراج البيانات المرسلة
    title = request.POST.get('title', '').strip()
    description = request.POST.get('description', '')
    folder_id = request.POST.get('folder', None)
    document_type = request.POST.get('document_type', 'other')
    
    print(f"البيانات المستلمة: العنوان='{title}', النوع='{document_type}', المجلد={folder_id}")
    
    # التحقق من وجود البيانات المطلوبة
    if not title:
        print("خطأ: لم يتم تحديد عنوان للمستند")
        messages.error(request, "يرجى إدخال عنوان للمستند")
        return redirect('admin_archive')
    
    if 'file' not in request.FILES:
        print("خطأ: لم يتم تحديد ملف للتحميل")
        messages.error(request, "يرجى تحديد ملف للتحميل")
        return redirect('admin_archive')
    
    # معالجة الملف المرفوع
    uploaded_file = request.FILES['file']
    file_name = uploaded_file.name
    file_type = uploaded_file.content_type
    file_size = uploaded_file.size
    
    print(f"معلومات الملف: اسم='{file_name}', النوع='{file_type}', الحجم={file_size} بايت")
    
    # تحديد المجلد إذا كان موجوداً
    folder = None
    if folder_id:
        try:
            folder = ArchiveFolder.objects.get(id=folder_id)
            print(f"تم تحديد المجلد: {folder.name} (ID: {folder.id})")
        except ArchiveFolder.DoesNotExist:
            print(f"خطأ: المجلد المحدد غير موجود (ID: {folder_id})")
            messages.error(request, "المجلد المحدد غير موجود")
            return redirect('admin_archive')
    
    # تعطيل إشارات منع المستندات التلقائية مؤقتاً
    from django.db.models.signals import pre_save
    
    # حفظ الإشارات الأصلية
    original_handlers = pre_save._live_receivers(Document)
    
    # تعطيل جميع إشارات pre_save للمستندات
    pre_save.receivers = [r for r in pre_save.receivers if not (hasattr(r[0], '__self__') and r[0].__self__.__class__ == Document)]
    print("⚠️ تم تعطيل إشارات منع المستندات التلقائية مؤقتاً")
    
    try:
        # تجربة الطريقة المباشرة باستخدام Django ORM
        try:
            with transaction.atomic():
                # قراءة محتوى الملف
                file_content = uploaded_file.read()
                print(f"📄 تم قراءة محتوى الملف: {len(file_content)} بايت")
                
                # إعادة تعيين مؤشر الملف
                uploaded_file.seek(0)
                
                # إنشاء المستند باستخدام نموذج Django
                document = Document(
                    title=title,
                    description=description,
                    document_type=document_type,
                    folder=folder,
                    file_name=file_name,
                    file_type=file_type,
                    file_size=file_size,
                    file_content=file_content,
                    created_by=request.user,
                    added_by=request.user,
                    is_auto_created=False,  # علامة مهمة لتمييز المستند اليدوي
                    document_date=timezone.now()
                )
                
                # تعيين علامة تجاوز إشارات منع المستندات التلقائية
                setattr(document, '_ignore_auto_document_signal', True)
                
                # حفظ المستند
                document.save()
                print(f"✅ تم إنشاء المستند بنجاح: ID={document.id}")
                
                # حفظ الملف في مجلد الوسائط
                import os
                from django.conf import settings
                
                # إنشاء مجلد للملفات
                upload_dir = os.path.join(settings.MEDIA_ROOT, 'uploads')
                os.makedirs(upload_dir, exist_ok=True)
                
                # إنشاء اسم ملف فريد
                timestamp = int(timezone.now().timestamp())
                unique_filename = f"direct_{timestamp}_{timestamp % 10000}_{file_name}"
                file_path = os.path.join(upload_dir, unique_filename)
                
                # حفظ الملف
                with open(file_path, 'wb+') as destination:
                    for chunk in uploaded_file.chunks():
                        destination.write(chunk)
                
                # تحديث مسار الملف في المستند
                rel_path = os.path.relpath(file_path, settings.MEDIA_ROOT)
                document.file = rel_path
                document.save(update_fields=['file'])
                
                print(f"📂 تم حفظ الملف المادي في: {rel_path}")
                
                # عرض رسالة نجاح للمستخدم
                messages.success(request, f"تم رفع المستند '{title}' بنجاح")
                
                # تحديد عنوان إعادة التوجيه
                if folder:
                    return redirect('admin_archive_folder', folder_id=folder.id)
                else:
                    return redirect('admin_archive')
                    
        except Exception as orm_err:
            print(f"❌ فشل في استخدام Django ORM: {str(orm_err)}")
            print(f"تفاصيل الخطأ: {traceback.format_exc()}")
            
            # الطريقة البديلة: استخدام SQL مباشر
            try:
                with transaction.atomic():
                    from django.db import connection
                    
                    # قراءة محتوى الملف
                    uploaded_file.seek(0)
                    file_content = uploaded_file.read()
                    print(f"📄 تم قراءة محتوى الملف ثانية: {len(file_content)} بايت")
                    
                    # إعادة تعيين مؤشر الملف
                    uploaded_file.seek(0)
                    
                    # إنشاء استعلام SQL مباشر لتجاوز كل الإشارات
                    cursor = connection.cursor()
                    
                    # تعطيل المحفزات مؤقتًا
                    cursor.execute("SET session_replication_role = 'replica';")
                    
                    # استعلام SQL المباشر لإدراج المستند
                    query = """
                    INSERT INTO rental_document 
                    (title, description, document_type, folder_id, created_by_id, added_by_id,
                    file_name, file_type, file_size, file_content, created_at, updated_at, is_auto_created,
                    document_date) 
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, NOW(), NOW(), %s, %s) 
                    RETURNING id;
                    """
                    
                    # تنفيذ الاستعلام
                    cursor.execute(query, [
                        title, 
                        description, 
                        document_type, 
                        folder.id if folder else None, 
                        request.user.id,
                        request.user.id,
                        file_name, 
                        file_type, 
                        file_size, 
                        file_content,
                        False,  # is_auto_created
                        timezone.now()
                    ])
                    
                    # الحصول على معرف المستند المدرج
                    document_id = cursor.fetchone()[0]
                    print(f"✅ تم إنشاء المستند باستخدام SQL: ID={document_id}")
                    
                    # حفظ الملف في مجلد الوسائط
                    import os
                    from django.conf import settings
                    
                    # إنشاء مجلد للملفات
                    upload_dir = os.path.join(settings.MEDIA_ROOT, 'uploads')
                    os.makedirs(upload_dir, exist_ok=True)
                    
                    # إنشاء اسم ملف فريد
                    timestamp = int(timezone.now().timestamp())
                    unique_filename = f"direct_{timestamp}_{timestamp % 10000}_{file_name}"
                    file_path = os.path.join(upload_dir, unique_filename)
                    
                    # حفظ الملف
                    with open(file_path, 'wb+') as destination:
                        for chunk in uploaded_file.chunks():
                            destination.write(chunk)
                    
                    # تحديث مسار الملف في قاعدة البيانات
                    rel_path = os.path.relpath(file_path, settings.MEDIA_ROOT)
                    cursor.execute("UPDATE rental_document SET file = %s WHERE id = %s", [rel_path, document_id])
                    
                    # إعادة تفعيل المحفزات
                    cursor.execute("SET session_replication_role = 'origin';")
                    
                    print(f"📂 تم حفظ الملف المادي في: {rel_path}")
                    
                    # عرض رسالة نجاح للمستخدم
                    messages.success(request, f"تم رفع المستند '{title}' بنجاح باستخدام SQL")
                    
                    # تحديد عنوان إعادة التوجيه
                    if folder:
                        return redirect('admin_archive_folder', folder_id=folder.id)
                    else:
                        return redirect('admin_archive')
                        
            except Exception as sql_err:
                print(f"❌ فشل في تنفيذ استعلام SQL: {str(sql_err)}")
                print(f"تفاصيل الخطأ: {traceback.format_exc()}")
                messages.error(request, "فشل في رفع الملف. يرجى المحاولة مرة أخرى.")
                
    finally:
        # إعادة ضبط الإشارات إلى حالتها الأصلية
        pre_save.receivers = original_handlers
        print("✅ تمت إعادة إشارات منع المستندات التلقائية")
    
    return redirect('admin_archive')

@login_required
@admin_required
def admin_archive_upload_form(request):
    """عرض نموذج رفع ملف جديد (مستقل)"""
    # الحصول على رقم المجلد الحالي من المعلمات
    folder_id = request.GET.get('folder', None)
    current_folder = None
    
    # إذا تم تحديد مجلد، نحصل على معلوماته
    if folder_id:
        try:
            current_folder = ArchiveFolder.objects.get(id=folder_id)
        except ArchiveFolder.DoesNotExist:
            messages.error(request, "المجلد المحدد غير موجود")
    
    # الحصول على قائمة المجلدات للاختيار
    folders = ArchiveFolder.objects.all().order_by('name')
    
    context = {
        'current_folder': current_folder,
        'folders': folders,
    }
    
    return render(request, 'admin/archive/direct_upload_form.html', context)

@login_required
@admin_required
def edit_folder(request, folder_id):
    """تعديل مجلد"""
    
    folder = get_object_or_404(ArchiveFolder, id=folder_id)
    
    if request.method == "POST":
        # تحديث معلومات المجلد
        folder.name = request.POST.get("name")
        folder.description = request.POST.get("description", "")
        
        # تحديث المجلد الأب إذا تم اختياره
        parent_id = request.POST.get("parent_id")
        if parent_id and parent_id != str(folder.id):
            folder.parent = ArchiveFolder.objects.get(id=parent_id)
        elif not parent_id:
            folder.parent = None
        
        folder.save()
        messages.success(request, "تم تحديث المجلد بنجاح")
        
        # العودة إلى المجلد الأب إذا كان موجودًا
        if folder.parent:
            return redirect("admin_archive_folder", folder_id=folder.parent.id)
        else:
            return redirect("admin_archive")
    
    # إعداد سياق العرض للنموذج
    context = {
        "folder": folder,
        "folders": ArchiveFolder.objects.exclude(id=folder_id).order_by("name"),
    }
    
    return render(request, "admin/archive/edit_folder.html", context)

@login_required
@admin_required
def delete_folder(request, folder_id):
    """حذف مجلد"""
    
    folder = get_object_or_404(ArchiveFolder, id=folder_id)
    
    # الاحتفاظ بالمجلد الأب للعودة إليه بعد الحذف
    parent_id = None
    if folder.parent:
        parent_id = folder.parent.id
    
    # التحقق من عدم وجود مجلدات فرعية أو مستندات
    subfolders = ArchiveFolder.objects.filter(parent=folder).exists()
    documents = Document.objects.filter(folder=folder).exists()
    
    if subfolders or documents:
        messages.error(request, "لا يمكن حذف المجلد لأنه يحتوي على مجلدات فرعية أو مستندات")
        if parent_id:
            return redirect("admin_archive_folder", folder_id=parent_id)
        else:
            return redirect("admin_archive")
    
    # حذف المجلد
    folder.delete()
    messages.success(request, "تم حذف المجلد بنجاح")
    
    # العودة إلى المجلد الأب إذا كان موجودًا
    if parent_id:
        return redirect("admin_archive_folder", folder_id=parent_id)
    else:
        return redirect("admin_archive")

@login_required
@admin_required
def folder_documents(request, folder_id):
    """عرض جميع المستندات المرتبطة بمجلد معين"""
    folder = get_object_or_404(ArchiveFolder, id=folder_id)
    
    # الحصول على جميع المستندات في المجلد (مع التنظيف)
    documents = clean_document_list(Document.objects.filter(folder=folder).order_by('-created_at'))
    
    # الحصول على مسار المجلد (الهيكل التسلسلي للوصول إليه)
    folder_path = []
    current = folder
    while current:
        folder_path.insert(0, current)
        current = current.parent
    
    # تحديد لغة المستخدم
    from django.utils.translation import get_language
    current_language = get_language()
    is_english = current_language == 'en'
    is_rtl = current_language == 'ar'
    
    context = {
        'folder': folder,
        'documents': documents,
        'folder_path': folder_path,
        'is_english': is_english,
        'is_rtl': is_rtl,
        'current_user': request.user,
        'active_section': 'archive'
    }
    
    return render(request, 'admin/archive/folder_documents.html', context)

@login_required
@admin_required
def add_document_to_folder(request, folder_id):
    """إضافة مستند جديد إلى مجلد محدد"""
    # التحقق من وجود المجلد
    folder = get_object_or_404(ArchiveFolder, id=folder_id)
    
    if request.method == 'POST':
        # استخراج البيانات من النموذج
        title = request.POST.get('title')
        document_type = request.POST.get('document_type', 'other')
        description = request.POST.get('description', '')
        document_date = request.POST.get('document_date')
        expiry_date = request.POST.get('expiry_date')
        related_to = request.POST.get('related_to', '')
        related_id = request.POST.get('related_id')
        tags = request.POST.get('tags', '')
        
        # التحقق من وجود عنوان للمستند
        if not title:
            messages.error(request, "يرجى إدخال عنوان المستند")
            return redirect('admin_archive_folder_add_document', folder_id=folder_id)
        
        # تحميل الملف إذا تم تقديمه
        file_name = None
        file_type = None
        file_size = 0
        file_content = None
        
        if 'file' in request.FILES:
            uploaded_file = request.FILES['file']
            file_name = uploaded_file.name
            file_type = uploaded_file.content_type
            file_size = uploaded_file.size
            file_content = uploaded_file.read()
        
        # إنشاء المستند وحفظه
        document = Document(
            title=title,
            document_type=document_type,
            description=description,
            document_date=document_date,
            expiry_date=expiry_date,
            related_to=related_to,
            file_name=file_name,
            file_type=file_type,
            file_size=file_size,
            file_content=file_content,
            tags=tags,
            added_by=request.user,
            folder=folder
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
        
        # منع إنشاء المستندات التلقائية عند الحفظ
        setattr(document, '_ignore_auto_document_signal', True)
        print(f"DEBUG - تم تعيين علامة التجاوز: {getattr(document, '_ignore_auto_document_signal', False)}")
        
        # حفظ المستند باستخدام المعاملات لضمان نجاح العملية
        with transaction.atomic():
            document.save()
        
        messages.success(request, f"تم إضافة المستند '{title}' إلى المجلد '{folder.name}' بنجاح")
        return redirect('admin_archive_folder', folder_id=folder_id)
    
    # الحصول على قوائم للعلاقات
    reservations = Reservation.objects.order_by('-created_at')[:50]
    cars = Car.objects.order_by('-id')[:50]
    users = User.objects.order_by('-date_joined')[:50]
    
    # الحصول على مسار المجلد (الهيكل التسلسلي للوصول إليه)
    folder_path = []
    current = folder
    while current:
        folder_path.insert(0, current)
        current = current.parent
    
    # تحديد لغة المستخدم
    from django.utils.translation import get_language
    current_language = get_language()
    is_english = current_language == 'en'
    is_rtl = current_language == 'ar'
    
    context = {
        'folder': folder,
        'folder_path': folder_path,
        'document_types': Document.DOCUMENT_TYPE_CHOICES,
        'related_to_types': Document.RELATED_TO_CHOICES,
        'reservations': reservations,
        'cars': cars,
        'users': users,
        'today': timezone.now().date().strftime('%Y-%m-%d'),
        'is_english': is_english,
        'is_rtl': is_rtl,
        'current_user': request.user,
        'active_section': 'archive'
    }
    
    return render(request, 'admin/archive/add_document_to_folder.html', context)

@login_required
@admin_required
def admin_archive_upload_direct(request):
    """وظيفة رفع مباشر للملفات - نسخة محسّنة تماماً"""
    import traceback, os
    from django.conf import settings
    
    # طباعة معلومات الطلب للتشخيص
    print("\n=== بدء معالجة طلب رفع مستند مباشر ===")
    print(f"طريقة الطلب: {request.method}")
    
    if request.method == 'POST':
        # استخراج البيانات المرسلة
        title = request.POST.get('title', '').strip()
        description = request.POST.get('description', '')
        folder_id = request.POST.get('folder', None)
        document_type = request.POST.get('document_type', 'other')
        
        print(f"البيانات المستلمة: العنوان='{title}', النوع='{document_type}', المجلد={folder_id}")
        
        # التحقق من وجود البيانات المطلوبة
        if not title:
            print("خطأ: لم يتم تحديد عنوان للمستند")
            messages.error(request, "يرجى إدخال عنوان للمستند")
            return redirect('admin_archive_upload_direct')
        
        if 'file' not in request.FILES:
            print("خطأ: لم يتم تحديد ملف للتحميل")
            messages.error(request, "يرجى تحديد ملف للتحميل")
            return redirect('admin_archive_upload_direct')
        
        # معالجة الملف المرفوع
        uploaded_file = request.FILES['file']
        file_name = uploaded_file.name
        file_type = uploaded_file.content_type
        file_size = uploaded_file.size
        
        print(f"معلومات الملف: اسم='{file_name}', النوع='{file_type}', الحجم={file_size} بايت")
        
        # تحديد المجلد إذا كان موجوداً
        folder = None
        if folder_id:
            try:
                folder = ArchiveFolder.objects.get(id=folder_id)
                print(f"تم تحديد المجلد: {folder.name} (ID: {folder.id})")
            except ArchiveFolder.DoesNotExist:
                print(f"خطأ: المجلد المحدد غير موجود (ID: {folder_id})")
                messages.error(request, "المجلد المحدد غير موجود")
                return redirect('admin_archive_upload_direct')
        
        try:
            # قراءة محتوى الملف
            file_content = uploaded_file.read()
            print(f"📄 تم قراءة محتوى الملف: {len(file_content)} بايت")
            
            # إعادة تعيين مؤشر الملف
            uploaded_file.seek(0)
            
            # إنشاء مجلد للملفات المرفوعة
            upload_folder = 'direct_uploads'
            upload_dir = os.path.join(settings.MEDIA_ROOT, upload_folder)
            os.makedirs(upload_dir, exist_ok=True)
            
            # إنشاء اسم ملف فريد
            timestamp = int(timezone.now().timestamp())
            unique_filename = f"direct_upload_{timestamp}_{file_name}"
            file_path = os.path.join(upload_dir, unique_filename)
            
            # حفظ الملف
            with open(file_path, 'wb') as destination:
                for chunk in uploaded_file.chunks():
                    destination.write(chunk)
            
            # المسار النسبي للملف
            relative_path = os.path.join(upload_folder, unique_filename)
            print(f"📂 تم حفظ الملف في: {relative_path}")
            
            # إنشاء المستند
            with transaction.atomic():
                # إنشاء المستند في قاعدة البيانات باستخدام SQL المباشر لضمان نجاح العملية
                from django.db import connection
                
                cursor = connection.cursor()
                
                # تعطيل المحفزات مؤقتًا
                cursor.execute("SET session_replication_role = 'replica';")
                
                # استعلام SQL المباشر لإدراج المستند
                query = """
                INSERT INTO rental_document 
                (title, description, document_type, folder_id, created_by_id, added_by_id,
                file_name, file_type, file_size, file_content, file, created_at, updated_at, is_auto_created,
                document_date) 
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, NOW(), NOW(), %s, %s) 
                RETURNING id;
                """
                
                # تنفيذ الاستعلام
                cursor.execute(query, [
                    title, 
                    description, 
                    document_type, 
                    folder.id if folder else None, 
                    request.user.id,
                    request.user.id,
                    file_name, 
                    file_type, 
                    file_size, 
                    file_content,
                    relative_path,
                    False,  # is_auto_created
                    timezone.now().date()
                ])
                
                # الحصول على معرف المستند المدرج
                document_id = cursor.fetchone()[0]
                
                # إعادة تفعيل المحفزات
                cursor.execute("SET session_replication_role = 'origin';")
                
                print(f"✅ تم إنشاء المستند باستخدام SQL: ID={document_id}")
            
            # عرض رسالة نجاح للمستخدم
            messages.success(request, f"تم رفع المستند '{title}' بنجاح")
            
            # إعادة التوجيه إلى صفحة الأرشيف المناسبة
            if folder:
                return redirect('admin_archive_folder', folder_id=folder.id)
            else:
                return redirect('admin_archive')
            
        except Exception as e:
            print(f"❌ فشل في رفع المستند: {str(e)}")
            print(f"تفاصيل الخطأ: {traceback.format_exc()}")
            messages.error(request, f"فشل في رفع المستند: {str(e)[:100]}")
    
    # الحصول على قائمة المجلدات للاختيار
    folders = ArchiveFolder.objects.all().order_by('name')
    
    # الحصول على معرف المجلد الحالي من المعلمات
    folder_id = request.GET.get('folder', None)
    current_folder = None
    
    if folder_id:
        try:
            current_folder = ArchiveFolder.objects.get(id=folder_id)
        except ArchiveFolder.DoesNotExist:
            pass
    
    context = {
        'folders': folders,
        'current_folder': current_folder,
        'folder_id': folder_id
    }
    
    return render(request, 'admin/archive/direct_upload_fix.html', context)
@login_required
@admin_required
def admin_profile(request):
    """عرض وتعديل الملف الشخصي للمشرف العادي"""
    # محاولة الحصول على بيانات المشرف
    try:
        admin_user = AdminUser.objects.get(user=request.user)
    except AdminUser.DoesNotExist:
        # إذا لم يكن هناك ملف شخصي للمشرف، نقوم بإنشاء واحد
        admin_user = None
        messages.warning(request, "لم يتم العثور على ملف المشرف الخاص بك. يرجى الاتصال بالمسؤول الأعلى.")
        return redirect('admin_index')
    
    # إذا تم إرسال النموذج للتحديث
    if request.method == 'POST':
        # تحديث بيانات المستخدم الأساسية
        user = request.user
        user.first_name = request.POST.get('first_name', user.first_name)
        user.last_name = request.POST.get('last_name', user.last_name)
        user.email = request.POST.get('email', user.email)
        user.save()
        
        # تحديث بيانات ملف المشرف
        admin_user.full_name = request.POST.get('full_name', admin_user.full_name)
        admin_user.phone_number = request.POST.get('phone_number', admin_user.phone_number)
        admin_user.current_job = request.POST.get('current_job', admin_user.current_job)
        admin_user.qualification = request.POST.get('qualification', admin_user.qualification)
        admin_user.department = request.POST.get('department', admin_user.department)
        admin_user.save()
        
        messages.success(request, "تم تحديث بياناتك الشخصية بنجاح")
        return redirect('admin_profile')
    
    # إحصائيات للمشرف
    stats = {
        'reservations_count': Reservation.objects.count(),
        'active_reservations': Reservation.objects.filter(status='confirmed').count(),
        'cars_count': Car.objects.count(),
        'users_count': User.objects.count(),
    }
    
    # أنشطة المشرف
    admin_activities = []
    if hasattr(admin_user, 'activities'):
        admin_activities = admin_user.activities.all().order_by('-id')[:10]
    
    # الحصول على معلومات المصادقة الثنائية
    security, created = UserSecurity.objects.get_or_create(user=request.user)
    
    context = {
        'admin_user': admin_user,
        'stats': stats,
        'admin_activities': admin_activities,
        'security': security,
    }
    
    return render(request, 'admin/admin_profile.html', context)

@login_required
@admin_required
def admin_2fa_setup(request):
    """إعداد المصادقة الثنائية للمشرف"""
    # التحقق من وجود معلومات أمان للمستخدم أو إنشائها
    security, created = UserSecurity.objects.get_or_create(user=request.user)
    
    # الحصول على بيانات QR ورموز النسخ الاحتياطية
    qr_code = None
    backup_codes = None
    
    # معالجة إجراءات المشرف
    if request.method == 'POST':
        action = request.POST.get('action')
        
        # إعداد المصادقة الثنائية
        if action == 'setup_2fa':
            # إعداد TOTP وإنشاء السر
            security = setup_2fa_for_user(request.user)
            
            # إنشاء رمز QR باستخدام السر - دائماً نعرض الباركود عند التفعيل
            qr_code = generate_qr_code_image(request.user)
            
            # الحصول على رموز النسخ الاحتياطية
            backup_codes = security.backup_codes
            
            # تفعيل المصادقة الثنائية مباشرة
            security.two_factor_enabled = True
            security.save(update_fields=['two_factor_enabled', 'totp_secret', 'backup_codes'])
            
            messages.success(request, _("تم تفعيل المصادقة الثنائية بنجاح. قم بمسح رمز QR باستخدام تطبيق المصادقة."))
            
        # تعطيل المصادقة الثنائية
        elif action == 'disable_2fa':
            # استخدام الوظيفة مع خيار القوة لتجاوز شرط التحقق من رمز TOTP
            disable_2fa_for_user(request.user, force=True)
            security.refresh_from_db()
            messages.success(request, _("تم تعطيل المصادقة الثنائية."))
    
    # إنشاء رمز QR إذا طلب المشرف إعداد المصادقة الثنائية
    if request.method == 'POST' and request.POST.get('action') == 'setup_2fa':
        qr_code = generate_qr_code_image(request.user)
        backup_codes = security.backup_codes
    # إذا كانت المصادقة الثنائية مفعلة ولكن تم فتح الصفحة فقط (ليس من خلال POST)
    elif security.two_factor_enabled and not request.method == 'POST':
        if not security.totp_secret:
            # إذا كان المستخدم لديه المصادقة الثنائية مفعلة ولكن بدون سر، نعيد إنشاء السر
            security = setup_2fa_for_user(request.user)
            
        # نعرض الرموز الاحتياطية فقط - لا داعي لعرض QR مرة أخرى بعد التفعيل
        backup_codes = security.backup_codes

    # عرض صفحة إعداد المصادقة الثنائية
    context = {
        'security': security,
        'qr_code': qr_code,
        'backup_codes': backup_codes,
    }
    
    return render(request, 'admin/admin_2fa_setup.html', context)


@login_required
@admin_required
def admin_reports(request):
    """
    عرض صفحة إدارة التقارير
    
    هذه الصفحة تعرض واجهة متقدمة لإدارة التقارير المختلفة في النظام
    مع إمكانيات فلترة وتصدير وطباعة التقارير
    
    الوظيفة معدلة لتوفير جميع الحقول المتاحة في قاعدة البيانات،
    وتضمين بيانات العهدة وحالة السيارات والمدفوعات
    """
    # الحصول على اللغة الحالية
    current_language = get_language()
    is_english = current_language == 'en'
    
    # إحصائيات للتقارير المختلفة
    reservations_stats = {
        'total': Reservation.objects.count(),
        'confirmed': Reservation.objects.filter(status='confirmed').count(),
        'pending': Reservation.objects.filter(status='pending').count(),
        'completed': Reservation.objects.filter(status='completed').count(),
        'cancelled': Reservation.objects.filter(status='cancelled').count(),
    }
    
    cars_stats = {
        'total': Car.objects.count(),
        'available': Car.objects.filter(is_available=True).count(),
        'unavailable': Car.objects.filter(is_available=False).count(),
    }
    
    # إحصائيات وثائق الأرشيف
    documents_stats = {
        'total': Document.objects.count(),
        'contracts': Document.objects.filter(document_type='contract').count(),
        'receipts': Document.objects.filter(document_type='receipt').count(),
        'custody': Document.objects.filter(document_type='custody').count(),
        'other': Document.objects.filter(document_type='other').count(),
    }
    
    # إحصائيات العملاء
    customers_stats = {
        'total': User.objects.filter(is_staff=False, is_admin=False, is_superuser=False).count(),
        'active': User.objects.filter(is_staff=False, is_admin=False, is_superuser=False, is_active=True).count(),
        'inactive': User.objects.filter(is_staff=False, is_admin=False, is_superuser=False, is_active=False).count(),
    }
    
    # إحصائيات العهدة
    # استخدام قيم تقديرية حيث أن جدول العهدة ليس موجود بعد
    custody_stats = {
        'total': Document.objects.filter(document_type='custody').count(),
        'active': Document.objects.filter(document_type='custody', is_archived=False).count(),
        'returned': Document.objects.filter(document_type='custody', is_archived=True).count(),
        'withheld': 0,  # سيتم تحديثه عندما يتم تنفيذ نموذج العهدة
        'total_value': 0,  # سيتم تحديثه عندما يتم تنفيذ نموذج العهدة
    }
    
    # إحصائيات حالة السيارات
    # الحصول على بيانات حالة السيارات من نموذج CarConditionReport إذا كان موجودًا
    car_condition_stats = {
        'total': 0,
        'delivery': 0,
        'return': 0,
        'maintenance': 0,
        'inspection': 0,
    }
    
    # إحصائيات المدفوعات
    payment_stats = {
        'total': Reservation.objects.filter(payment_status='paid').count(),
        'pending': Reservation.objects.filter(payment_status='pending').count(),
        'refunded': 0,  # سيتم تحديثه عندما يتم تنفيذ نموذج المدفوعات
        'total_amount': Reservation.objects.filter(payment_status='paid').aggregate(Sum('total_price'))['total_price__sum'] or 0,
    }
    
    # بيانات جميع الحجوزات للجدول مع جميع الحقول ذات الصلة (مع prefetch للعلاقات)
    reservations = Reservation.objects.select_related('car', 'user').prefetch_related('documents').all().order_by('-created_at')
    
    # استخراج جميع السيارات مع معلوماتها الكاملة
    cars = Car.objects.all().order_by('-id')
    
    # بيانات العملاء مع جميع الحقول ذات الصلة
    customers = User.objects.filter(is_staff=False, is_admin=False, is_superuser=False).order_by('-date_joined')
    
    # بيانات المستندات مع جميع المعلومات
    documents = Document.objects.select_related('folder', 'user', 'car', 'reservation').order_by('-created_at')
    
    # بيانات العهدة (استخدام وثائق العهدة مؤقتًا)
    custody_items = Document.objects.filter(document_type='custody').order_by('-created_at')
    
    # بيانات حالة السيارات (استخدام تقارير حالة السيارة الفعلية)
    car_conditions = Document.objects.filter(document_type__in=['car_report', 'maintenance_report', 'condition_report']).select_related('car', 'user').order_by('-created_at')
    
    # بيانات المدفوعات (استخدام بيانات الحجوزات المدفوعة مؤقتًا)
    payments = Reservation.objects.filter(payment_status='paid').select_related('car', 'user').order_by('-created_at')
    
    # استخراج أسماء جميع الحقول من النماذج لعرضها في الجداول
    reservation_fields = [field.name for field in Reservation._meta.fields]
    car_fields = [field.name for field in Car._meta.fields]
    user_fields = [field.name for field in User._meta.fields if not field.name.startswith('password')]
    document_fields = [field.name for field in Document._meta.fields]
    
    # إنشاء قواميس تعيين للحقول باستخدام verbose_name لعرض أسماء محسنة للحقول
    reservation_field_names = {field.name: field.verbose_name for field in Reservation._meta.fields}
    car_field_names = {field.name: field.verbose_name for field in Car._meta.fields}
    user_field_names = {field.name: field.verbose_name for field in User._meta.fields if not field.name.startswith('password')}
    document_field_names = {field.name: field.verbose_name for field in Document._meta.fields}
    
    # تحميل معلومات الوقت الحالي لكسر كاش المتصفح
    timestamp = int(datetime.now().timestamp())
    
    context = {
        'is_english': is_english,
        'reservations_stats': reservations_stats,
        'cars_stats': cars_stats,
        'documents_stats': documents_stats,
        'customers_stats': customers_stats,
        'custody_stats': custody_stats,
        'car_condition_stats': car_condition_stats,
        'payment_stats': payment_stats,
        'cars': cars,
        'reservations': reservations,
        'recent_reservations': reservations[:10],
        'customers': customers,
        'documents': documents,
        'custody_items': custody_items,
        'car_conditions': car_conditions,
        'payments': payments,
        'timestamp': timestamp,
        'now': datetime.now(),
        # إضافة حقول النماذج للقالب
        'reservation_fields': reservation_fields,
        'car_fields': car_fields,
        'user_fields': user_fields,
        'document_fields': document_fields,
        # إضافة أسماء الحقول المحسنة
        'reservation_field_names': reservation_field_names,
        'car_field_names': car_field_names,
        'user_field_names': user_field_names,
        'document_field_names': document_field_names,
    }
    
    return render(request, 'admin/reports/reports_management.html', context)

@login_required
@admin_required
def report_print_settings(request, report_type='reservations'):
    """
    عرض صفحة إعدادات طباعة التقرير
    
    تعرض هذه الصفحة إعدادات الطباعة المتقدمة للتقرير المحدد
    مع إمكانية ضبط حجم الورق والهوامش وخيارات أخرى
    
    :param report_type: نوع التقرير (reservations، cars، customers، إلخ)
    """
    # التحقق من وجود معلمة اتجاه الجدول
    orientation = request.GET.get('orientation', 'horizontal')
    
    # الحصول على بيانات التقرير حسب النوع
    if report_type == 'reservations':
        # بيانات الحجوزات للمعاينة
        # إنشاء حجوزات وهمية للمعاينة لتجنب الأخطاء
        # نستخدم تواريخ نموذجية بدلاً من تواريخ عشوائية لتجنب أخطاء المنطقة الزمنية
        reservations = []
        for i in range(1, 8):  # إنشاء 7 حجوزات نموذجية
            reservation = {
                'id': 1000 + i,
                'user': {'get_full_name': f'عميل نموذجي {i}'},
                'car': {'model_name': f'سيارة {i}', 'year': 2024},
                'start_date': datetime(2025, i, 1),  # تاريخ شهري للوضوح
                'end_date': datetime(2025, i, 10),  # 10 أيام من تاريخ البدء
                'total_price': 500 + (i * 100),  # أسعار مختلفة للتمييز
                'status': ['pending', 'confirmed', 'completed', 'cancelled'][i % 4]  # تناوب الحالات
            }
            reservations.append(reservation)
        title = _("تقرير الحجوزات")
    elif report_type == 'cars':
        # بيانات السيارات للمعاينة
        from rental.models import Car
        # الحصول على السيارات الحقيقية
        cars = Car.objects.all()[:10]  # الحصول على أول 10 سيارات فقط للمعاينة
        reservations = []  # نستخدم قائمة فارغة للحجوزات إذا كان التقرير ليس للحجوزات
        title = _("تقرير السيارات")
    else:
        # بيانات افتراضية للمعاينة
        reservations = []
        for i in range(1, 6):  # 5 حجوزات نموذجية افتراضية
            reservation = {
                'id': 2000 + i,
                'user': {'get_full_name': f'عميل {i}'},
                'car': {'model_name': f'سيارة نموذجية {i}', 'year': 2024},
                'start_date': datetime(2025, 6, i),
                'end_date': datetime(2025, 6, i + 5),
                'total_price': 300 + (i * 50),
                'status': 'confirmed'
            }
            reservations.append(reservation)
        title = _("تقرير العام")
    
    context = {
        'report_type': report_type,
        'title': title,
        'reservations': reservations,
        'now': datetime.now(),
        'orientation': orientation,
    }
    
    # إضافة السيارات إلى السياق إذا كان نوع التقرير "cars"
    if report_type == 'cars':
        context['cars'] = cars
    
    # استخدام القالب المطابق للتصميم الأصلي مع إصلاح الأخطاء البرمجية
    return render(request, 'admin/reports/exact_print_settings.html', context)