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
from rental.security import setup_2fa_for_user, disable_2fa_for_user, generate_qr_code_image
from rental.security_models import UserSecurity
from .forms import LoginForm, RegisterForm, CarSearchForm, ReservationForm, CheckoutForm, ReviewForm, ProfileForm, PasswordChangeForm
from .models import User, Car, Reservation, Review, CartItem, FavoriteCar
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
    
    تعديل: تم تغيير السلوك لتحديث حالة الحجوزات المنتهية بدلاً من حذفها
    لتمكين العملاء من رؤيتها في سجل الحجوزات
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
    count = expired_reservations.count()
    logger.info(f"Found {count} expired confirmed reservations.")

    # تحديث حالة الحجوزات المنتهية بدلاً من حذفها
    for reservation in expired_reservations:
        # استعادة حالة السيارة إلى "متاحة" لإتاحتها للحجوزات الجديدة
        car = reservation.car
        car.is_available = True
        car.save()
        
        # تغيير حالة الدفع إلى "expired" بدلاً من حذفها
        reservation.payment_status = 'expired'
        reservation.save()
        
        logger.info(f"Marked reservation #{reservation.id} as payment expired for car {car.id}.")

    # إرجاع عدد الحجوزات التي تم تحديثها
    return count

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
    if request and hasattr(request, 'COOKIES'):
        print(f"Cookie language: {request.COOKIES.get('django_language', 'none')}")

    # استثناء خاص لصفحة الحجوزات - استخدام القالب الجدولي دائمًا
    if base_template == 'my_reservations.html':
        print(f"Using table-based design for reservations page")
        return 'my_reservations.html'

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
        # استثناء لصفحة الحجوزات - تم تعليقه لاستخدام التصميم الجدولي
        # 'my_reservations.html': 'my_reservations_django.html',
        'booking.html': 'booking_django.html',
        'reservation_detail.html': 'reservation_detail_django.html',
        'error.html': 'error_django.html',
        'admin_dashboard.html': 'admin_dashboard_django.html',
        'favorite_cars.html': 'favorite_cars_django.html',
        # قوالب الأمان والمصادقة الثنائية
        'two_factor_auth.html': 'two_factor_auth_django.html',
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
    # قبل عرض الصفحة، تحقق من الحجوزات المنتهية وحدّث حالتها
    expired_count = check_expired_confirmations()
    if expired_count > 0:
        logger.info(f"Marked {expired_count} reservations as payment expired during index view.")

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
    """User login view with redirection based on user type"""
    # استيراد وحدات الأمان
    from .security import get_system_setting, record_login_attempt, check_account_lockout, verify_2fa_token
    from .security_models import UserSecurity, TwoFactorSession
    import uuid
    from django.utils import timezone
    import json
    
    # إذا كان المستخدم مسجل الدخول بالفعل، نوجهه للصفحة المناسبة
    if request.user.is_authenticated:
        # التحقق إذا كان المستخدم سوبر أدمن
        from .models_superadmin import AdminUser
        try:
            admin_profile = AdminUser.objects.get(user=request.user)
            if admin_profile.is_superadmin:
                return redirect('superadmin_dashboard')
            elif request.user.is_staff or request.user.is_admin:
                return redirect('admin_index')  # توجيه للوحة تحكم المسؤول العادي
        except (AdminUser.DoesNotExist, ImportError):
            # المستخدم ليس لديه ملف مسؤول
            if request.user.is_staff:
                return redirect('admin_index')  # توجيه للوحة تحكم المسؤول العادي
            else:
                return redirect('profile')  # توجيه لصفحة الملف الشخصي للمستخدم العادي

    # التحقق من وجود جلسة مصادقة ثنائية مؤقتة
    if 'two_factor_session' in request.session:
        # استرجاع معلومات جلسة المصادقة الثنائية
        session_key = request.session['two_factor_session']
        try:
            two_fa_session = TwoFactorSession.objects.get(session_key=session_key)
            
            # التحقق من صلاحية الجلسة
            if two_fa_session.is_valid():
                # تسجيل الدخول للمستخدم
                user = two_fa_session.user
                login(request, user)
                
                # حذف جلسة المصادقة الثنائية المؤقتة
                del request.session['two_factor_session']
                two_fa_session.delete()
                
                # تسجيل محاولة تسجيل الدخول الناجحة
                record_login_attempt(request, user.username, 'success', 'تم التحقق من المصادقة الثنائية')
                
                # التحقق من نوع المستخدم وتوجيهه للصفحة المناسبة
                from .models_superadmin import AdminUser
                try:
                    admin_profile = AdminUser.objects.get(user=user)
                    if admin_profile.is_superadmin:
                        messages.success(request, "تم تسجيل الدخول بنجاح كمسؤول أعلى!")
                        return redirect('superadmin_dashboard')
                    elif user.is_staff or user.is_admin:
                        messages.success(request, "تم تسجيل الدخول بنجاح كمسؤول!")
                        return redirect('admin_index')
                except (AdminUser.DoesNotExist, ImportError):
                    if user.is_staff:
                        messages.success(request, "تم تسجيل الدخول بنجاح كمسؤول!")
                        return redirect('admin_index')
                    else:
                        messages.success(request, "تم تسجيل الدخول بنجاح!")
                        return redirect('profile')
            else:
                # جلسة المصادقة الثنائية منتهية الصلاحية
                del request.session['two_factor_session']
                two_fa_session.delete()
                messages.error(request, "انتهت صلاحية جلسة المصادقة الثنائية، يرجى إعادة تسجيل الدخول.")
                
        except TwoFactorSession.DoesNotExist:
            # جلسة المصادقة الثنائية غير موجودة
            del request.session['two_factor_session']
            messages.error(request, "جلسة المصادقة الثنائية غير صالحة، يرجى إعادة تسجيل الدخول.")

    # التعامل مع نموذج التحقق من المصادقة الثنائية
    if request.method == 'POST' and 'two_factor_token' in request.POST and 'username' in request.POST:
        username = request.POST.get('username')
        token = request.POST.get('two_factor_token')
        user = User.objects.filter(username=username).first()
        
        if user and token:
            # التحقق من رمز المصادقة الثنائية
            if verify_2fa_token(user, token):
                # إنشاء جلسة مصادقة ثنائية مؤقتة
                session_key = str(uuid.uuid4())
                expires_at = timezone.now() + timezone.timedelta(minutes=5)
                
                # حفظ الجلسة في قاعدة البيانات
                TwoFactorSession.objects.create(
                    user=user,
                    session_key=session_key,
                    expires_at=expires_at,
                    is_verified=True
                )
                
                # حفظ معرف الجلسة في جلسة المستخدم
                request.session['two_factor_session'] = session_key
                
                # تسجيل محاولة تسجيل الدخول الناجحة
                record_login_attempt(request, username, 'success', 'تم التحقق من المصادقة الثنائية')
                
                # تسجيل الدخول للمستخدم
                login(request, user)
                
                # التوجيه حسب نوع المستخدم
                from .models_superadmin import AdminUser
                try:
                    admin_profile = AdminUser.objects.get(user=user)
                    if admin_profile.is_superadmin:
                        messages.success(request, "تم تسجيل الدخول بنجاح كمسؤول أعلى!")
                        return redirect('superadmin_dashboard')
                    elif user.is_staff or user.is_admin:
                        messages.success(request, "تم تسجيل الدخول بنجاح كمسؤول!")
                        return redirect('admin_index')
                except (AdminUser.DoesNotExist, ImportError):
                    if user.is_staff:
                        messages.success(request, "تم تسجيل الدخول بنجاح كمسؤول!")
                        return redirect('admin_index')
                    else:
                        messages.success(request, "تم تسجيل الدخول بنجاح!")
                        return redirect('profile')
            else:
                # رمز المصادقة الثنائية غير صحيح
                messages.error(request, "رمز المصادقة الثنائية غير صحيح، يرجى المحاولة مرة أخرى.")
                record_login_attempt(request, username, 'failed', 'رمز المصادقة الثنائية غير صحيح')
                
                # عرض نموذج المصادقة الثنائية مرة أخرى
                template = get_template_by_language(request, 'two_factor_auth.html')
                return render(request, template, {'username': username})
                
        else:
            # معلومات المصادقة الثنائية غير كاملة
            messages.error(request, "معلومات المصادقة الثنائية غير كاملة، يرجى إعادة تسجيل الدخول.")
            
    # تسجيل الدخول العادي
    if request.method == 'POST' and 'username' in request.POST and 'password' in request.POST:
        form = LoginForm(request, data=request.POST)
        username = request.POST.get('username')
        
        # التحقق من حالة قفل الحساب قبل محاولة المصادقة
        is_locked, locked_until = check_account_lockout(username)
        if is_locked:
            lock_minutes = round((locked_until - timezone.now()).total_seconds() / 60)
            lock_hour = lock_minutes // 60
            lock_minute = lock_minutes % 60
            time_format = ""
            if lock_hour > 0:
                time_format = f"{lock_hour} ساعة"
                if lock_minute > 0:
                    time_format += f" و {lock_minute} دقيقة"
            else:
                time_format = f"{lock_minute} دقيقة"
                
            messages.error(request, f"""
                <div class="alert-icon-container mb-2">
                    <i class="fas fa-lock fa-2x text-danger"></i>
                </div>
                <h5 class="mb-2">تم تجميد الحساب مؤقتاً</h5>
                <p>
                    تم قفل حسابك مؤقتاً بسبب محاولات دخول غير صحيحة متكررة.<br>
                    يمكنك المحاولة مرة أخرى بعد <strong>{time_format}</strong>.
                </p>
                <p class="small text-muted mt-2">
                    إذا كنت تواجه مشكلة في الدخول، يرجى التواصل مع المسؤول.
                </p>
            """)
            record_login_attempt(request, username, 'locked', f'الحساب مقفل حتى {locked_until}')
            
            template = get_template_by_language(request, 'login.html')
            return render(request, template, {'form': form})
        
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            
            if user is not None:
                # التحقق مما إذا كان المستخدم يحتاج للمصادقة الثنائية
                try:
                    security = UserSecurity.objects.get(user=user)
                    
                    # التحقق مما إذا كانت المصادقة الثنائية مفعلة للمستخدم
                    if security.two_factor_enabled and security.totp_secret:
                        # تحويل المستخدم إلى صفحة إدخال رمز المصادقة الثنائية
                        template = get_template_by_language(request, 'two_factor_auth.html')
                        return render(request, template, {'username': username})
                
                except UserSecurity.DoesNotExist:
                    # المستخدم ليس لديه معلومات أمان - ننشئ واحدة
                    UserSecurity.objects.create(user=user)
                    
                # إذا لم تكن المصادقة الثنائية مفعلة، قم بتسجيل الدخول مباشرة
                login(request, user)
                
                # تسجيل محاولة تسجيل الدخول الناجحة
                record_login_attempt(request, username, 'success', 'تسجيل دخول ناجح')
                
                # التحقق من نوع المستخدم وتوجيهه للصفحة المناسبة
                from .models_superadmin import AdminUser
                try:
                    admin_profile = AdminUser.objects.get(user=user)
                    if admin_profile.is_superadmin:
                        messages.success(request, "تم تسجيل الدخول بنجاح كمسؤول أعلى!")
                        return redirect('superadmin_dashboard')
                except (AdminUser.DoesNotExist, ImportError):
                    # المستخدم ليس لديه ملف مسؤول أعلى
                    pass
                
                # التحقق إذا كان مسؤول عادي
                if user.is_staff or getattr(user, 'is_admin', False):
                    messages.success(request, "تم تسجيل الدخول بنجاح كمسؤول!")
                    return redirect('admin_index')
                
                # المستخدم العادي
                messages.success(request, "تم تسجيل الدخول بنجاح!")
                
                # التحقق إذا كان هناك مسار إعادة توجيه محدد في الطلب
                next_url = request.GET.get('next')
                if next_url and next_url.strip():
                    return redirect(next_url)
                
                return redirect('profile')
            else:
                # تسجيل محاولة تسجيل دخول فاشلة
                record_login_attempt(request, username, 'failed', 'كلمة مرور غير صحيحة')
                messages.error(request, "خطأ في اسم المستخدم أو كلمة المرور!")
        else:
            # تسجيل محاولة تسجيل دخول فاشلة (بيانات النموذج غير صالحة)
            username = request.POST.get('username', '')
            record_login_attempt(request, username, 'failed', 'بيانات النموذج غير صالحة')
            messages.error(request, "خطأ في اسم المستخدم أو كلمة المرور!")
    else:
        form = LoginForm()

    template = get_template_by_language(request, 'login.html')
    return render(request, template, {'form': form})

def logout_view(request):
    """User logout view"""
    # تخزين اللغة قبل تسجيل الخروج
    from django.utils.translation import get_language
    current_language = get_language()
    
    # تسجيل الخروج
    logout(request)
    
    # إضافة رسالة نجاح
    messages.info(request, "تم تسجيل الخروج!")
    
    # التأكد من عدم فقدان ملفات الأنماط - ضبط الكوكيز للمحافظة على اللغة
    response = redirect('index')
    response.set_cookie('django_language', current_language)
    
    return response

@login_required
def profile_view(request):
    """User profile view"""
    # التأكد من وجود معلومات أمان للمستخدم
    security, created = UserSecurity.objects.get_or_create(user=request.user)
    
    password_form = PasswordChangeForm()
    password_form_submitted = False
    
    # تحديد نوع النموذج المرسل (معلومات المستخدم أو تغيير كلمة المرور)
    if request.method == 'POST':
        if 'change_password' in request.POST:
            password_form_submitted = True
            password_form = PasswordChangeForm(request.POST)
            if password_form.is_valid():
                # التحقق من كلمة المرور الحالية
                if request.user.check_password(password_form.cleaned_data['current_password']):
                    # تعيين كلمة المرور الجديدة
                    request.user.set_password(password_form.cleaned_data['new_password'])
                    request.user.save()
                    
                    # الحصول على اللغة الحالية للرسائل
                    from django.utils.translation import get_language
                    current_language = get_language()
                    is_english = (current_language == 'en')
                    
                    # رسالة نجاح مناسبة للغة
                    if is_english:
                        messages.success(request, "Password changed successfully. Please log in again.")
                    else:
                        messages.success(request, "تم تغيير كلمة المرور بنجاح. يرجى تسجيل الدخول مرة أخرى.")
                    
                    # تسجيل الخروج بعد تغيير كلمة المرور
                    from django.contrib.auth import logout
                    logout(request)
                    return redirect('login')
                else:
                    # خطأ في كلمة المرور الحالية
                    from django.utils.translation import get_language
                    current_language = get_language()
                    is_english = (current_language == 'en')
                    
                    if is_english:
                        messages.error(request, "Current password is incorrect.")
                    else:
                        messages.error(request, "كلمة المرور الحالية غير صحيحة.")
        else:
            # نموذج تحديث بيانات المستخدم
            form = ProfileForm(request.POST, instance=request.user)
            if form.is_valid():
                form.save()
                
                # الحصول على اللغة الحالية للرسائل
                from django.utils.translation import get_language
                current_language = get_language()
                is_english = (current_language == 'en')
                
                # رسالة نجاح مناسبة للغة
                if is_english:
                    messages.success(request, "Profile updated successfully!")
                else:
                    messages.success(request, "تم تحديث الملف الشخصي بنجاح!")
                
                return redirect('profile')
    else:
        form = ProfileForm(instance=request.user)

    # إضافة ختم زمني لتفادي مشكلة التخزين المؤقت
    from datetime import datetime
    context = {
        'form': form,
        'password_form': password_form,
        'password_form_submitted': password_form_submitted,
        'user': request.user,
        'security': security,  # إضافة معلومات الأمان للسياق
        'current_date': timezone.now(),
        'timestamp': datetime.now().timestamp(),  # إضافة ختم زمني
    }
    
    # الحصول على اللغة الحالية
    from django.utils.translation import get_language
    current_language = get_language()
    context['is_english'] = (current_language == 'en')
    context['is_rtl'] = (current_language == 'ar')
    
    # استخدام القالب مباشرة بدون الدالة المساعدة
    # تجاوز المشكلة باستخدام مسار مباشر للقالب المحدث
    return render(request, 'profile_django.html', context)

def car_listing(request):
    """Car listing page with search functionality"""
    # Initialize search form
    form = CarSearchForm(request.GET)

    # Get all available cars by default, ordered by id for consistent pagination
    cars = Car.objects.filter(is_available=True).order_by('id')
    
    # Process search query from the new search field
    search_query = request.GET.get('search', '')
    if search_query:
        cars = cars.filter(
            Q(make__icontains=search_query) | 
            Q(model__icontains=search_query) | 
            Q(description__icontains=search_query) |
            Q(features__icontains=search_query) |
            Q(category__icontains=search_query)
        )

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

    # Get user's favorite cars if user is authenticated
    favorite_car_ids = []
    if request.user.is_authenticated:
        favorite_car_ids = FavoriteCar.objects.filter(
            user=request.user
        ).values_list('car_id', flat=True)

    # الحصول على اللغة الحالية مباشرة من django i18n
    from django.utils.translation import get_language
    current_language = get_language()
    is_arabic = (current_language == 'ar')

    # تعيين فئات الهوامش بناءً على اتجاه اللغة
    margin_right_class = 'ms-2' if is_arabic else 'me-2'
    margin_left_class = 'me-1' if is_arabic else 'ms-1'

    # التحقق من وجود معلمة في URL لاستخدام الواجهة المحسنة
    use_enhanced = request.GET.get('enhanced', 'true')
    use_enhanced = use_enhanced.lower() in ['true', '1', 'yes']
    
    # إذا كان المستخدم يريد استخدام الواجهة المحسنة
    if use_enhanced:
        # التحقق من معلمة الترتيب إذا وجدت
        sort_param = request.GET.get('sort', '')
        if sort_param:
            if sort_param == 'price_asc':
                cars = cars.order_by('daily_rate')
            elif sort_param == 'price_desc':
                cars = cars.order_by('-daily_rate')
            elif sort_param == 'year_desc':
                cars = cars.order_by('-year')
            elif sort_param == 'year_asc':
                cars = cars.order_by('year')
                
        # ترتيب الصفحات بعد الفرز
        paginator = Paginator(cars, 9)  # عرض 9 سيارات في الصفحة
        page_obj = paginator.get_page(page_number)
    
    context = {
        'form': form,
        'cars': page_obj,
        'today': date.today(),
        'is_arabic': is_arabic,
        'margin_right_class': margin_right_class,
        'margin_left_class': margin_left_class,
        'favorite_car_ids': favorite_car_ids,
        'use_enhanced': use_enhanced,  # إضافة معلمة للتبديل بين الواجهتين
        'enhanced_url': request.path + '?enhanced=true',  # رابط للتصميم المحسن
        'standard_url': request.path + '?enhanced=false'  # رابط للتصميم القياسي
    }

    # استخدام قالب الواجهة المحسنة إذا تم تحديده
    if use_enhanced:
        # استخدام القالب المحسن بالطريقة المتوافقة مع نظام i18n
        # لكن تحديد اسم القالب مباشرة متجاوزًا نظام get_template_by_language
        if not hasattr(request, 'session'):
            request.session = {}
        
        # نضع القالب المحسن مباشرة
        return render(request, 'cars_enhanced_django.html', context)
    else:
        # استخدام نظام القوالب العادي
        template = get_template_by_language(request, 'cars.html')
        return render(request, template, context)

def car_detail(request, car_id):
    """Car detail page with reservation form"""
    car = get_object_or_404(Car, id=car_id)

    # Get reviews for this car
    reviews = Review.objects.filter(car=car).order_by('-created_at')

    # Calculate average rating and update it in the car model
    avg_rating = reviews.aggregate(Avg('rating'))['rating__avg'] or 0
    avg_rating = round(avg_rating, 1)
    
    # اذا كان متوسط التقييم في الكائن مختلف عما تم حسابه، قم بتحديثه
    if car.avg_rating != avg_rating:
        car.avg_rating = avg_rating
        car.save()

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
    
    # Check if the car is in user's favorites
    is_favorite = False
    if request.user.is_authenticated:
        is_favorite = FavoriteCar.objects.filter(user=request.user, car=car).exists()

    # احصل على معلومات اللغة للقالب
    from django.utils.translation import get_language
    current_language = get_language()
    is_english = current_language == 'en'
    is_rtl = current_language == 'ar'

    # إضافة رموز تصحيح
    today_value = date.today()
    print(f"DEBUG: car_detail view - car.is_available = {car.is_available}")
    print(f"DEBUG: car_detail view - user.is_authenticated = {request.user.is_authenticated}")
    print(f"DEBUG: car_detail view - today = {today_value}")
    
    context = {
        'car': car,
        'reviews': reviews,
        'avg_rating': avg_rating,
        'total_reviews': total_reviews,
        'rating_distribution': rating_distribution,
        'similar_cars': similar_cars,
        'today': today_value,
        'is_favorite': is_favorite,
        'is_english': is_english,
        'is_rtl': is_rtl,
        'LANGUAGE_CODE': current_language # إضافة LANGUAGE_CODE إلى السياق
    }

    template = get_template_by_language(request, 'car_detail.html')
    print(f"DEBUG: car_detail view - template selected = {template}")
    return render(request, template, context)

def car_reviews(request, car_id):
    """صفحة منفصلة لعرض تقييمات السيارة بشكل مشابه للمتاجر الإلكترونية"""
    car = get_object_or_404(Car, id=car_id)
    
    # Get reviews for this car
    reviews_list = Review.objects.filter(car=car).order_by('-created_at')
    
    # تطبيق الصفحات (Pagination)
    paginator = Paginator(reviews_list, 5)  # عرض 5 تقييمات في كل صفحة
    page = request.GET.get('page')
    reviews = paginator.get_page(page)
    
    # Calculate average rating
    avg_rating = reviews_list.aggregate(Avg('rating'))['rating__avg'] or 0
    avg_rating = round(avg_rating, 1)
    
    # Calculate rating distribution (percentage for each star level)
    total_reviews = reviews_list.count()
    rating_distribution = {}
    
    if total_reviews > 0:
        for i in range(1, 6):
            count = reviews_list.filter(rating=i).count()
            percentage = (count / total_reviews) * 100
            rating_distribution[i] = percentage
    else:
        for i in range(1, 6):
            rating_distribution[i] = 0
    
    # احصل على معلومات اللغة للقالب
    from django.utils.translation import get_language
    current_language = get_language()
    is_english = current_language == 'en'
    is_rtl = current_language == 'ar'
    
    context = {
        'car': car,
        'reviews': reviews,
        'avg_rating': avg_rating,
        'total_reviews': total_reviews,
        'rating_distribution': rating_distribution,
        'is_english': is_english,
        'is_rtl': is_rtl
    }
    
    return render(request, 'car_reviews_django.html', context)

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

def add_to_cart(request):
    """Add a car to shopping cart"""
    if request.method != 'POST':
        return redirect('cars')

    car_id = request.POST.get('car_id')
    car = get_object_or_404(Car, id=car_id, is_available=True)

    # التحقق مما إذا كان المستخدم مسجل الدخول
    if not request.user.is_authenticated:
        # حفظ معلومات التاريخ في نص التوجيه للرجوع إليها بعد تسجيل الدخول (اختياري)
        start_date_str = request.POST.get('start_date')
        end_date_str = request.POST.get('end_date')
        next_url = f"/car/{car_id}/?start_date={start_date_str}&end_date={end_date_str}"
        
        # استخدام اللغة الحالية للمستخدم عند التوجيه
        from django.utils.translation import get_language
        current_language = get_language()
        
        if current_language == 'ar':
            # رسالة بالعربية
            messages.info(request, "يرجى تسجيل الدخول أو إنشاء حساب لإضافة السيارة إلى سلة التسوق.")
            login_url = reverse('login') + f"?next=/ar/car/{car_id}/"
        else:
            # رسالة بالإنجليزية
            messages.info(request, "Please login or register to add this car to your cart.")
            login_url = reverse('login') + f"?next=/car/{car_id}/"
            
        return redirect(login_url)

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

    # توجيه المستخدم إلى صفحة السلة بدلاً من صفحة طلب الحجز
    from django.utils.translation import get_language
    current_language = get_language()
    
    if current_language == 'ar':
        return redirect('cart_ar')
    else:
        return redirect('cart')

@login_required
def remove_from_cart(request, item_id):
    """Remove item from cart"""
    item = get_object_or_404(CartItem, id=item_id, user=request.user)
    item.delete()
    messages.success(request, "تمت إزالة العنصر من السلة!")
    return redirect('cart')

@login_required
def user_2fa_setup(request):
    """إعداد المصادقة الثنائية للمستخدم العادي"""
    # التحقق من وجود معلومات أمان للمستخدم أو إنشائها
    security, created = UserSecurity.objects.get_or_create(user=request.user)
    
    # الحصول على بيانات QR ورموز النسخ الاحتياطية
    qr_code = None
    backup_codes = None
    
    # معالجة إجراءات المستخدم
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
            disable_2fa_for_user(request.user)
            security.refresh_from_db()
            messages.success(request, _("تم تعطيل المصادقة الثنائية."))
    
    # إنشاء رمز QR والرموز الاحتياطية إذا كانت المصادقة الثنائية مفعلة أو تم تفعيلها للتو
    if security.two_factor_enabled:
        if not security.totp_secret:
            # إذا كان المستخدم لديه المصادقة الثنائية مفعلة ولكن بدون سر، نعيد إنشاء السر
            security = setup_2fa_for_user(request.user)
        
        # إنشاء رمز QR دائماً إذا كانت المصادقة الثنائية مفعلة
        qr_code = generate_qr_code_image(request.user)
        backup_codes = security.backup_codes
        
    # عرض صفحة إعداد المصادقة الثنائية
    context = {
        'security': security,
        'qr_code': qr_code,
        'backup_codes': backup_codes,
    }
    
    return render(request, 'security/user_2fa_setup.html', context)

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
            elif reservation.status == 'confirmed' and reservation.payment_status == 'expired':
                # إعادة تفعيل الحجز المنتهي عن طريق إعادة تعيين حالة الدفع وتحديث تاريخ انتهاء التأكيد
                reservation.payment_status = 'pending'
                # تعيين مهلة جديدة للدفع (24 ساعة من الآن)
                reservation.confirmation_expiry = timezone.now() + timedelta(hours=24)
                reservation.save()
                
                # رسالة نجاح
                if is_english:
                    message = "Reservation has been reactivated successfully. You have 24 hours to complete the payment."
                else:
                    message = "تم إعادة تفعيل الحجز بنجاح. لديك 24 ساعة لإكمال عملية الدفع."

                messages.success(request, message)
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
        logger.info(f"Marked {expired_count} reservations as payment expired during my_reservations view.")

    # الحصول على الوقت الحالي (مطلوب للعداد التنازلي)
    now = timezone.now()

    # الحصول على كافة حجوزات المستخدم الحالي بما فيها المنتهية
    # استبعاد الحجوزات ذات حالة 'cancelled' بشكل صريح
    # اختيار حجوزات المستخدم الحالي مباشرة بغض النظر عن حالتها (باستثناء 'cancelled')
    reservations_query = Reservation.objects.filter(user=request.user).exclude(status='cancelled')
    
    # تسجيل عدد الحجوزات حسب الحالة للتشخيص
    pending_count = reservations_query.filter(status='pending').count()
    confirmed_count = reservations_query.filter(status='confirmed').count()
    completed_count = reservations_query.filter(status='completed').count()
    
    # طباعة معلومات تشخيصية
    print(f"عدد الحجوزات المعلقة: {pending_count}")
    print(f"عدد الحجوزات المؤكدة: {confirmed_count}")
    print(f"عدد الحجوزات المكتملة: {completed_count}")
    print(f"إجمالي الحجوزات: {reservations_query.count()}")
    
    # طباعة اسم المستخدم الحالي للتحقق
    print(f"المستخدم الحالي: {request.user.username}")
    expired_count = reservations_query.filter(payment_status='expired').count()
    logger.info(f"User {request.user.id} reservations - Pending: {pending_count}, Confirmed: {confirmed_count}, Completed: {completed_count}, Expired: {expired_count}")

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
            Q(id__icontains=search_query) |
            Q(reservation_number__icontains=search_query)
        )

    if status_filter and status_filter != 'cancelled':
        # تطبيق الفلتر على الحالة المطلوبة (باستثناء 'cancelled')
        reservations_query = reservations_query.filter(status=status_filter)
    elif status_filter == 'cancelled':
        # إذا تم طلب فلترة على الحالة 'cancelled'، ارجع قائمة فارغة
        reservations_query = Reservation.objects.none()

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

    # الحصول على معلومات اللغة للقالب
    from django.utils.translation import get_language
    current_language = get_language()
    is_english = current_language == 'en'
    is_rtl = current_language == 'ar'
    
    context = {
        'reservations': reservations,
        'search_query': search_query,
        'status_filter': status_filter,
        'date_from': date_from,
        'date_to': date_to,
        'status_choices': Reservation.STATUS_CHOICES,
        'today': date.today(),
        'now': now,  # إضافة الوقت الحالي للقالب (مطلوب للعداد التنازلي)
        'is_english': is_english,  # إضافة متغير اللغة الإنجليزية
        'is_rtl': is_rtl  # إضافة متغير للتنسيق من اليمين إلى اليسار
    }

    # استخدام القالب المحدث عبر دالة اختيار القالب بناءً على اللغة
    template = get_template_by_language(request, 'my_reservations.html')
    print(f"TEMPLATE BEING USED: {template}")  # طباعة تشخيصية للقالب المستخدم
    return render(request, template, context)

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

        # احصل على لغة المستخدم لعرض الرسائل المناسبة
        from django.utils.translation import get_language
        current_language = get_language()
        is_english = current_language == 'en'
        is_rtl = current_language == 'ar'

        context = {
            'reservation': reservation,
            'has_review': has_review,
            'is_english': is_english,
            'is_rtl': is_rtl
        }

        template = get_template_by_language(request, 'reservation_detail.html')
        return render(request, template, context)
    except Exception as e:
        # تسجيل الخطأ للتصحيح
        logger.error(f"Error in reservation_detail view: {str(e)}")
        
        # رسالة الخطأ بناءً على لغة المستخدم
        from django.utils.translation import get_language
        current_language = get_language()
        if current_language == 'en':
            messages.error(request, "Reservation not found or you don't have access to it.")
        else:
            messages.error(request, "الحجز غير موجود أو لا يمكنك الوصول إليه.")
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
        # استعادة حالة السيارة إلى "متاحة" إذا كانت محجوزة بواسطة هذا الحجز
        car = reservation.car
        if not car.is_available:
            car.is_available = True
            car.save()
            logger.info(f"Car {car.id} made available after cancellation of reservation {reservation.id}")
        
        # تغيير حالة الحجز إلى 'cancelled' بدلاً من حذفه
        reservation.status = 'cancelled'
        reservation.save()
        logger.info(f"Reservation {reservation.id} cancelled by user {request.user.id}")

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
        # تحديد رسالة الخطأ بناءً على لغة المستخدم
        from django.utils.translation import get_language
        current_language = get_language()
        is_english = current_language == 'en'
        
        if is_english:
            messages.warning(request, "You have already reviewed this trip!")
        else:
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

            # تحديث متوسط التقييم للسيارة
            car = reservation.car
            avg_rating = Review.objects.filter(car=car).aggregate(Avg('rating'))['rating__avg'] or 0
            car.avg_rating = round(avg_rating, 1)
            car.save()
            
            # تحديد رسالة النجاح بناءً على لغة المستخدم
            # استخدام الدالة المستوردة سابقًا
            current_language = get_language()
            is_english = current_language == 'en'
            
            if is_english:
                messages.success(request, "Thank you for your review!")
            else:
                messages.success(request, "شكراً لتقييمك!")
            
            # إعادة التوجيه إلى صفحة تفاصيل السيارة
            return redirect('car_detail', car_id=reservation.car.id)
    else:
        form = ReviewForm()

    # احصل على لغة المستخدم لعرض الرسائل المناسبة
    # استخدام الدالة المستوردة سابقًا
    current_language = get_language()
    is_english = current_language == 'en'
    is_rtl = current_language == 'ar'

    context = {
        'form': form,
        'reservation': reservation,
        'is_english': is_english,
        'is_rtl': is_rtl
    }

    template = get_template_by_language(request, 'add_review.html')
    return render(request, template, context)

@login_required
def add_direct_review(request, car_id):
    """
    إضافة تقييم مباشر للسيارة من صفحة تفاصيل السيارة
    هذه الدالة تسمح للمستخدم بإضافة تقييم للسيارة التي استخدمها سابقًا
    من خلال واجهة مشابهة لتقييمات جوجل بلاي
    """
    car = get_object_or_404(Car, id=car_id)
    
    # التحقق من أن المستخدم قد استأجر السيارة بالفعل
    completed_reservations = Reservation.objects.filter(
        user=request.user,
        car=car,
        status='completed',
        payment_status='paid'
    ).exists()
    
    # احصل على لغة المستخدم لعرض الرسائل المناسبة
    from django.utils.translation import get_language
    current_language = get_language()
    is_english = current_language == 'en'
    is_rtl = current_language == 'ar'
    
    # التحقق من وجود حجز مكتمل قبل السماح بالتقييم
    if not completed_reservations:
        if is_english:
            messages.error(request, "You can only review cars that you have rented and completed the reservation.")
        else:
            messages.error(request, "يمكنك فقط تقييم السيارات التي استأجرتها وأكملت الحجز الخاص بها.")
        return redirect('car_detail', car_id=car.id)
    
    # التحقق من أن المستخدم لم يقم بتقييم هذه السيارة مسبقًا
    existing_review = Review.objects.filter(car=car, user=request.user).first()
    if existing_review:
        if is_english:
            messages.warning(request, "You have already reviewed this car!")
        else:
            messages.warning(request, "لقد قمت بتقييم هذه السيارة بالفعل!")
        return redirect('car_detail', car_id=car.id)
    
    # الحصول على أحدث حجز مكتمل لهذه السيارة
    reservation = Reservation.objects.filter(
        user=request.user,
        car=car,
        status='completed',
        payment_status='paid'
    ).order_by('-created_at').first()
    
    if request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.user = request.user
            review.car = car
            review.reservation = reservation
            review.save()
            
            # تحديث متوسط التقييم للسيارة
            avg_rating = Review.objects.filter(car=car).aggregate(Avg('rating'))['rating__avg'] or 0
            car.avg_rating = round(avg_rating, 1)
            car.save()
            
            if is_english:
                messages.success(request, "Thank you for your review!")
            else:
                messages.success(request, "شكراً لتقييمك!")
            
            return redirect('car_detail', car_id=car.id)
    else:
        form = ReviewForm()
    
    context = {
        'form': form,
        'car': car,
        'is_english': is_english,
        'is_rtl': is_rtl
    }
    
    return render(request, 'add_review_django.html', context)

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
    مع الحفاظ على البقاء في نفس الصفحة بعد تغيير اللغة
    """
    from django.utils import translation
    from django.utils.translation import get_language
    from django.conf import settings
    import logging
    import re

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

    # الحصول على صفحة المصدر (إذا كانت متوفرة)
    referer = request.META.get('HTTP_REFERER')
    
    # مسار للعودة إليه
    redirect_url = f'/{new_language}/'
    
    # التحقق إذا كانت الصفحة المصدر متوفرة
    if referer:
        logger.debug(f"Referer URL: {referer}")
        
        # التحقق إذا كانت هذه صفحة إدارية
        if '/admin/' in referer or '/admin_' in referer:
            logger.debug("Admin page detected, redirecting back to admin panel")
            
            # الاحتفاظ بالمسار الإداري نفسه
            # تعديل المسار للعودة للوحة التحكم
            if 'admin_index' in referer:
                redirect_url = reverse('admin_index')
            elif 'admin_cars' in referer:
                redirect_url = reverse('admin_cars')
            elif 'admin_users' in referer:
                redirect_url = reverse('admin_users')
            elif 'admin_reservations' in referer:
                redirect_url = reverse('admin_reservations')
            elif 'admin_dashboard' in referer:
                redirect_url = reverse('admin_index')
            else:
                # إذا لم يكن أي من الصفحات الإدارية المعروفة، أعد التوجيه إلى لوحة التحكم
                redirect_url = reverse('admin_index')
                
            logger.debug(f"Redirecting to admin page: {redirect_url}")
        else:
            # بالنسبة للصفحات غير الإدارية، قم بإستبدال اللغة في المسار
            # مثل: /ar/cars/ -> /en/cars/
            match = re.search(r'/(ar|en)/(.+)', referer)
            if match:
                path_after_lang = match.group(2)
                redirect_url = f'/{new_language}/{path_after_lang}'
                logger.debug(f"Redirecting to: {redirect_url}")
    
    # إعادة توجيه إلى المسار المحدد
    response = redirect(redirect_url)

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

    logger.debug(f"Language switched to: {new_language}, redirecting to: {redirect_url}")
    return response



def about_us(request):
    """About Us page view"""
    template = get_template_by_language(request, 'about_us.html')
    return render(request, template)

# إزالة @login_required للسماح للمستخدمين غير المسجلين بالوصول لصفحة طلب الحجز
def book_from_cart(request):
    """وظيفة خاصة لحجز السيارة مباشرة من السلة"""
    # التأكد من أن المستخدم مسجل الدخول
    if not request.user.is_authenticated:
        return redirect('login')
    
    # الحصول على عناصر السلة للمستخدم
    cart_items = CartItem.objects.filter(user=request.user).order_by('-created_at')
    
    # التحقق من وجود عناصر في السلة
    if not cart_items.exists():
        messages.error(request, 'لا توجد سيارات في سلة التسوق')
        return redirect('cart')
    
    # استخدام السيارة الأولى من السلة
    first_cart_item = cart_items.first()
    return redirect('book_car', car_id=first_cart_item.car.id)


def book_car(request, car_id):
    """View for booking a car directly from car detail page"""
    car = get_object_or_404(Car, id=car_id, is_available=True)

    start_date = None
    end_date = None
    cart_item = None
    
    # التحقق مما إذا كان المستخدم مسجل الدخول قبل الوصول إلى البيانات المرتبطة بالمستخدم
    if request.user.is_authenticated:
        # First check if there's a cart item for this car
        cart_item = CartItem.objects.filter(user=request.user, car=car).order_by('-created_at').first()

        # If we have a cart item, use its dates
        if cart_item:
            start_date = cart_item.start_date
            end_date = cart_item.end_date

    # Check for dates in GET parameters regardless of authentication status
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

    # Calculate total price if dates are available
    total_price = None
    if start_date and end_date:
        total_price = calculate_total_price(car, start_date, end_date)

    # إعداد سياق العرض مع معلومات إضافية حول حالة تسجيل الدخول
    context = {
        'car': car,
        'start_date': start_date,
        'end_date': end_date,
        'today': date.today(),
        'cart_item': cart_item,
        'is_authenticated': request.user.is_authenticated,
        'total_price': total_price,
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

@login_required
def toggle_favorite(request, car_id):
    """إضافة أو إزالة سيارة من المفضلة"""
    # الحصول على السيارة أو إرجاع خطأ 404
    car = get_object_or_404(Car, id=car_id)
    
    # السماح بكل من طلبات GET و POST لتسهيل الاستخدام
    if request.method == 'POST' or request.method == 'GET':
        # التحقق مما إذا كانت السيارة بالفعل في المفضلة
        favorite = FavoriteCar.objects.filter(user=request.user, car=car).first()
        
        if favorite:
            # إذا كانت موجودة، قم بإزالتها
            favorite.delete()
            messages.success(request, _("تمت إزالة السيارة من المفضلة"))
        else:
            # إذا لم تكن موجودة، قم بإضافتها
            FavoriteCar.objects.create(user=request.user, car=car)
            messages.success(request, _("تمت إضافة السيارة إلى المفضلة"))
    
    # العودة إلى الصفحة السابقة أو صفحة تفاصيل السيارة
    referer = request.META.get('HTTP_REFERER')
    if referer:
        return redirect(referer)
    else:
        return redirect('car_detail', car_id=car_id)

@login_required
def favorite_cars(request):
    """عرض السيارات المفضلة للمستخدم الحالي"""
    # الحصول على جميع السيارات المفضلة للمستخدم الحالي
    favorites = FavoriteCar.objects.filter(user=request.user).select_related('car').order_by('-date_added')
    
    # الحصول على اللغة الحالية مباشرة من django i18n
    from django.utils.translation import get_language
    current_language = get_language()
    is_english = (current_language == 'en')
    is_rtl = (current_language == 'ar')
    
    context = {
        'favorites': favorites,
        'today': date.today(),
        'is_english': is_english,
        'is_rtl': is_rtl
    }
    
    # استخدام قالب محسن جديد مع تنسيق احترافي وجذاب
    # إضافة ختم زمني للمساعدة في تجنب مشكلة التخزين المؤقت
    context['timestamp'] = datetime.now().timestamp()
    
    # تغيير القالب إلى القالب الجديد المحدث
    return render(request, 'favorite_cars_django.html', context)

@login_required
def payment_receipt(request, reservation_id):
    """عرض إيصال الدفع للحجز"""
    reservation = get_object_or_404(
        Reservation, 
        id=reservation_id, 
        user=request.user,
        payment_status='paid'
    )
    
    # الحصول على معلومات اللغة
    from django.utils.translation import get_language
    current_language = get_language()
    is_english = current_language == 'en'
    is_rtl = current_language == 'ar'
    
    # Current date time for the receipt
    current_datetime = timezone.now()
    
    context = {
        'reservation': reservation,
        'current_datetime': current_datetime,
        'is_english': is_english,
        'is_rtl': is_rtl
    }
    
    return render(request, 'payment_receipt.html', context)