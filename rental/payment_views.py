from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils.translation import gettext as _
from django.utils.translation import get_language
from .models import Reservation, CartItem, Car
from .utils import get_car_availability, calculate_total_price
from datetime import datetime
import uuid
import json

def get_template_by_language(request, template_name):
    """اختيار القالب المناسب بناءً على اللغة"""
    from django.utils.translation import get_language
    current_language = get_language()
    
    # استخدم القالب المناسب بناءً على ما إذا كان المستخدم يستخدم اللغة الإنجليزية أو العربية
    if current_language == 'en':
        # إذا كان القالب المطلوب يحتوي على كلمة django، استخدمه كما هو
        if 'django' in template_name:
            return template_name
        # وإلا أضف _original إلى اسم القالب
        else:
            base_name = template_name.split('.')[0]
            extension = template_name.split('.')[-1]
            return f"{base_name}_original.{extension}"
    else:
        # للغة العربية، استخدم القالب الافتراضي
        if 'django' in template_name:
            return template_name
        else:
            base_name = template_name.split('.')[0]
            extension = template_name.split('.')[-1]
            return f"{base_name}_django.{extension}"

@login_required
def professional_payment(request):
    """واجهة دفع متطورة واحترافية"""
    # التحقق مما إذا كان المستخدم يأتي من حجز محدد
    reservation_id = request.GET.get('reservation_id')
    
    if reservation_id:
        # المستخدم يدفع لحجز محدد
        reservation = get_object_or_404(
            Reservation, 
            id=reservation_id, 
            user=request.user, 
            status='confirmed', 
            payment_status='pending'
        )
        
        # معالجة طلب الدفع
        if request.method == 'POST':
            payment_method = request.POST.get('payment_method', 'credit_card')
            
            # إنشاء رقم مرجعي للدفع
            payment_reference = f"PAY-{uuid.uuid4().hex[:8].upper()}"
            
            # تحديث حالة الحجز
            reservation.payment_status = 'paid'
            reservation.payment_reference = payment_reference
            reservation.payment_method = payment_method
            reservation.payment_date = datetime.now()
            
            # إذا تم الدفع، قم بتحديث الحالة إلى "مكتمل" إذا كان "مؤكد"
            if reservation.status == 'confirmed':
                reservation.status = 'completed'
            
            reservation.save()
            
            # رسالة نجاح
            messages.success(request, _("تم إتمام عملية الدفع بنجاح!"))
            
            # تخزين معرف الحجز في الجلسة لصفحة التأكيد
            request.session['last_paid_reservation_id'] = reservation.id
            
            return redirect('confirmation')
        
        context = {
            'reservation': reservation,
            'total_amount': reservation.total_price,
            'from_cart': False
        }
    else:
        # المستخدم يدفع لعناصر من السلة
        cart_items = CartItem.objects.filter(user=request.user)
        
        if not cart_items:
            messages.warning(request, _("سلة التسوق فارغة!"))
            return redirect('cart')
        
        # حساب المجاميع باستخدام الخصائص المحسوبة
        # نستخدم الخواص المحسوبة days و total التي أضفناها لنموذج CartItem
        grand_total = sum(item.total for item in cart_items)
        
        if request.method == 'POST':
            payment_method = request.POST.get('payment_method', 'credit_card')
            
            # إنشاء رقم مرجعي للدفع
            payment_reference = f"PAY-{uuid.uuid4().hex[:8].upper()}"
            
            # إنشاء حجوزات لجميع عناصر السلة
            for item in cart_items:
                # التحقق من توفر السيارة
                if get_car_availability(item.car.id, item.start_date, item.end_date):
                    total_price = calculate_total_price(item.car, item.start_date, item.end_date)
                    
                    # إنشاء حجز بحالة معلقة في البداية
                    reservation = Reservation.objects.create(
                        user=request.user,
                        car=item.car,
                        start_date=item.start_date,
                        end_date=item.end_date,
                        total_price=total_price,
                        status='pending',  # جميع الحجوزات تبدأ كمعلقة
                        payment_status='pending',
                        payment_method=payment_method,
                        payment_reference=payment_reference
                    )
                else:
                    messages.error(
                        request, 
                        _("عذرًا، السيارة {make} {model} لم تعد متاحة في التواريخ المحددة.").format(
                            make=item.car.make, model=item.car.model
                        )
                    )
                    return redirect('cart')
            
            # تفريغ السلة
            cart_items.delete()
            
            messages.success(request, _("تم إرسال طلب الحجز بنجاح! يرجى انتظار موافقة المسؤول."))
            return redirect('confirmation')
        
        context = {
            'cart_items': cart_items,
            'total_amount': grand_total,
            'total_days': sum(item.days for item in cart_items),
            'from_cart': True
        }
    
    return render(request, 'payment_modern.html', context)

@login_required
def international_payment(request):
    """واجهة دفع دولية متطورة تتوافق مع معايير بوابات الدفع العالمية"""
    # التحقق مما إذا كان المستخدم يأتي من حجز محدد
    reservation_id = request.GET.get('reservation_id')
    
    # تحديد لغة المستخدم
    current_language = get_language()
    is_english = current_language == 'en'
    is_rtl = current_language == 'ar'
    
    if reservation_id:
        # المستخدم يدفع لحجز محدد
        reservation = get_object_or_404(
            Reservation, 
            id=reservation_id, 
            user=request.user, 
            status='confirmed', 
            payment_status='pending'
        )
        
        # مسح السطرين التاليين لأن days هي خاصية محسوبة (@property)
        # وسيتم حسابها تلقائيًا عند الوصول إليها
        
        # معالجة طلب الدفع
        if request.method == 'POST':
            payment_method = request.POST.get('payment_method', 'credit_card')
            
            # إنشاء رقم مرجعي للدفع
            payment_reference = f"PAY-{uuid.uuid4().hex[:8].upper()}"
            
            # تحديث حالة الحجز
            reservation.payment_status = 'paid'
            reservation.payment_reference = payment_reference
            reservation.payment_method = payment_method
            reservation.payment_date = datetime.now()
            
            # إذا تم الدفع، قم بتحديث الحالة إلى "مكتمل" إذا كان "مؤكد"
            if reservation.status == 'confirmed':
                reservation.status = 'completed'
            
            reservation.save()
            
            # رسالة نجاح
            if is_english:
                success_message = "Payment completed successfully!"
            else:
                success_message = "تم إتمام عملية الدفع بنجاح!"
            
            messages.success(request, success_message)
            
            # تخزين معرف الحجز في الجلسة لصفحة التأكيد
            request.session['last_paid_reservation_id'] = reservation.id
            
            return redirect('confirmation')
        
        context = {
            'reservation': reservation,
            'total_amount': reservation.total_price,
            'from_cart': False,
            'is_english': is_english,
            'is_rtl': is_rtl
        }
    else:
        # المستخدم يدفع لعناصر من السلة
        cart_items = CartItem.objects.filter(user=request.user)
        
        if not cart_items:
            if is_english:
                warning_message = "Your cart is empty!"
            else:
                warning_message = "سلة التسوق فارغة!"
                
            messages.warning(request, warning_message)
            return redirect('cart')
        
        # حساب المجاميع باستخدام الخصائص المحسوبة
        # نستخدم الخواص المحسوبة days و total التي أضفناها لنموذج CartItem
        grand_total = sum(item.total for item in cart_items)
        
        if request.method == 'POST':
            payment_method = request.POST.get('payment_method', 'credit_card')
            
            # إنشاء رقم مرجعي للدفع
            payment_reference = f"PAY-{uuid.uuid4().hex[:8].upper()}"
            
            # إنشاء حجوزات لجميع عناصر السلة
            for item in cart_items:
                # التحقق من توفر السيارة
                if get_car_availability(item.car.id, item.start_date, item.end_date):
                    total_price = calculate_total_price(item.car, item.start_date, item.end_date)
                    
                    # إنشاء حجز بحالة معلقة في البداية
                    reservation = Reservation.objects.create(
                        user=request.user,
                        car=item.car,
                        start_date=item.start_date,
                        end_date=item.end_date,
                        total_price=total_price,
                        status='pending',  # جميع الحجوزات تبدأ كمعلقة
                        payment_status='pending',
                        payment_method=payment_method,
                        payment_reference=payment_reference
                    )
                else:
                    if is_english:
                        error_message = f"Sorry, the car {item.car.make} {item.car.model} is no longer available for the selected dates."
                    else:
                        error_message = f"عذرًا، السيارة {item.car.make} {item.car.model} لم تعد متاحة في التواريخ المحددة."
                    
                    messages.error(request, error_message)
                    return redirect('cart')
            
            # تفريغ السلة
            cart_items.delete()
            
            if is_english:
                success_message = "Booking request submitted successfully! Please wait for administrator approval."
            else:
                success_message = "تم إرسال طلب الحجز بنجاح! يرجى انتظار موافقة المسؤول."
                
            messages.success(request, success_message)
            return redirect('confirmation')
        
        context = {
            'cart_items': cart_items,
            'total_amount': grand_total,
            'total_days': sum(item.days for item in cart_items),
            'from_cart': True,
            'is_english': is_english,
            'is_rtl': is_rtl
        }
    
    return render(request, 'payment_international.html', context)

# تم استبدال الدالة payment_gateway الأولى بواسطة الدالة الثانية في النص لاحقاً

@login_required
def paypal_payment(request):
    """
    واجهة دفع PayPal متطورة مطابقة للواجهة العالمية
    تحول المستخدم إلى PayPal لإتمام عملية الدفع
    
    يتم استدعاء هذه الدالة من قبل:
    1. عند النقر على زر "متابعة الدفع عبر PayPal" مع goto_paypal=1 - لعرض واجهة PayPal المحسنة
    2. عند تقديم نموذج PayPal - لمعالجة الدفع
    """
    # التحقق مما إذا كان المستخدم يأتي من حجز محدد
    reservation_id = request.GET.get('reservation_id')
    
    # تحديد لغة المستخدم
    current_language = get_language()
    is_english = current_language == 'en'
    is_rtl = current_language == 'ar'
    
    # التحقق من وجود معلمة goto_paypal - تعني أن المستخدم اختار PayPal كطريقة دفع ونريد عرض واجهة PayPal المحسنة
    goto_paypal = request.POST.get('goto_paypal') == '1'
    
    # التعامل مع عملية تسجيل الدخول PayPal وإتمام الدفع
    if request.method == 'POST' and (request.POST.get('paypal_submit') == 'login' or request.POST.get('paypal_submit') == 'card'):
        payment_method = request.POST.get('payment_method', 'paypal')
        
        # التحقق من تواجد الحقول المطلوبة حسب طريقة الدفع
        if payment_method == 'paypal':
            paypal_email = request.POST.get('paypal_email')
            paypal_password = request.POST.get('paypal_password')
            
            if not paypal_email or not paypal_password:
                if is_english:
                    error_message = "Please enter your email and password."
                else:
                    error_message = "يرجى إدخال البريد الإلكتروني وكلمة المرور."
                
                messages.error(request, error_message)
                
                # إعادة تقديم نموذج PayPal مع بيانات السياق
                if reservation_id:
                    return redirect(f'/payment/paypal/?reservation_id={reservation_id}')
                else:
                    return redirect('/payment/paypal/')
        elif payment_method == 'credit_card':
            card_number = request.POST.get('card_number')
            card_expiry = request.POST.get('card_expiry')
            card_cvv = request.POST.get('card_cvv')
            card_name = request.POST.get('card_name')
            
            if not card_number or not card_expiry or not card_cvv or not card_name:
                if is_english:
                    error_message = "Please fill in all card details."
                else:
                    error_message = "يرجى ملء جميع تفاصيل البطاقة."
                
                messages.error(request, error_message)
                
                # إعادة تقديم نموذج البطاقة مع بيانات السياق
                if reservation_id:
                    return redirect(f'/payment/paypal/?reservation_id={reservation_id}')
                else:
                    return redirect('/payment/paypal/')
        
        # في الواقع، هنا سنتواصل مع API الخاص بـ PayPal أو معالج بطاقة الائتمان
        # لكن في هذا المثال، سنفترض أن عملية الدفع تمت بنجاح
        
        # معالجة الدفع لكل من الحجز والسلة
        if reservation_id:
            # المستخدم يدفع لحجز محدد
            reservation = get_object_or_404(
                Reservation, 
                id=reservation_id, 
                user=request.user, 
                status='confirmed', 
                payment_status='pending'
            )
            
            # إنشاء رقم مرجعي للدفع حسب طريقة الدفع
            if payment_method == 'paypal':
                payment_reference = f"PP-{uuid.uuid4().hex[:8].upper()}"
            else:
                payment_reference = f"CC-{uuid.uuid4().hex[:8].upper()}"
            
            # تحديث حالة الحجز
            reservation.payment_status = 'paid'
            reservation.payment_reference = payment_reference
            reservation.payment_method = payment_method
            reservation.payment_date = datetime.now()
            
            # إذا تم الدفع، قم بتحديث الحالة إلى "مكتمل" إذا كان "مؤكد"
            if reservation.status == 'confirmed':
                reservation.status = 'completed'
            
            reservation.save()
            
            # تخزين معرف الحجز في الجلسة لصفحة التأكيد
            request.session['last_paid_reservation_id'] = reservation.id
            
            # رسالة نجاح حسب طريقة الدفع المستخدمة
            if payment_method == 'paypal':
                if is_english:
                    success_message = "Payment completed successfully via PayPal!"
                else:
                    success_message = "تم إتمام عملية الدفع بنجاح عبر PayPal!"
            else:
                if is_english:
                    success_message = "Payment completed successfully via Credit Card!"
                else:
                    success_message = "تم إتمام عملية الدفع بنجاح عبر بطاقة الائتمان!"
            
            messages.success(request, success_message)
            
        else:
            # المستخدم يدفع لعناصر من السلة
            cart_items = CartItem.objects.filter(user=request.user)
            
            if not cart_items:
                if is_english:
                    warning_message = "Your cart is empty!"
                else:
                    warning_message = "سلة التسوق فارغة!"
                    
                messages.warning(request, warning_message)
                return redirect('cart')
            
            # إنشاء رقم مرجعي للدفع حسب طريقة الدفع
            if payment_method == 'paypal':
                payment_reference = f"PP-{uuid.uuid4().hex[:8].upper()}"
            else:
                payment_reference = f"CC-{uuid.uuid4().hex[:8].upper()}"
            
            # إنشاء حجوزات لجميع عناصر السلة
            for item in cart_items:
                # التحقق من توفر السيارة
                if get_car_availability(item.car.id, item.start_date, item.end_date):
                    total_price = calculate_total_price(item.car, item.start_date, item.end_date)
                    
                    # إنشاء حجز جديد
                    reservation = Reservation.objects.create(
                        user=request.user,
                        car=item.car,
                        start_date=item.start_date,
                        end_date=item.end_date,
                        total_price=total_price,
                        status='confirmed',  # تأكيد مباشر عند الدفع
                        payment_status='paid',
                        payment_method=payment_method,
                        payment_reference=payment_reference,
                        payment_date=datetime.now()
                    )
                    
                    # تخزين معرف الحجز الأخير في الجلسة لصفحة التأكيد
                    request.session['last_paid_reservation_id'] = reservation.id
                else:
                    if is_english:
                        error_message = f"Sorry, the car {item.car.make} {item.car.model} is no longer available."
                    else:
                        error_message = f"عذرًا، السيارة {item.car.make} {item.car.model} لم تعد متاحة."
                    
                    messages.error(request, error_message)
                    return redirect('cart')
            
            # تفريغ السلة
            cart_items.delete()
            
            # رسالة نجاح حسب طريقة الدفع المستخدمة
            if payment_method == 'paypal':
                if is_english:
                    success_message = "Payment completed successfully via PayPal!"
                else:
                    success_message = "تم إتمام عملية الدفع بنجاح عبر PayPal!"
            else:
                if is_english:
                    success_message = "Payment completed successfully via Credit Card!"
                else:
                    success_message = "تم إتمام عملية الدفع بنجاح عبر بطاقة الائتمان!"
                
            messages.success(request, success_message)
        
        # توجيه إلى صفحة التأكيد
        return redirect('confirmation')
    
    # عرض واجهة PayPal (عند وصول المستخدم لأول مرة أو عند إعادة تحميل الصفحة)
    # عند الوصول بطريقة GET أو POST، نعرض واجهة PayPal المحسنة
    if reservation_id:
        # المستخدم يدفع لحجز محدد
        reservation = get_object_or_404(
            Reservation, 
            id=reservation_id, 
            user=request.user, 
            status='confirmed', 
            payment_status='pending'
        )
        
        context = {
            'reservation': reservation,
            'total_amount': reservation.total_price,
            'is_english': is_english,
            'is_rtl': is_rtl,
            'reservation_id': reservation_id
        }
    else:
        # المستخدم يدفع لعناصر من السلة
        cart_items = CartItem.objects.filter(user=request.user)
        
        if not cart_items:
            if is_english:
                warning_message = "Your cart is empty!"
            else:
                warning_message = "سلة التسوق فارغة!"
                
            messages.warning(request, warning_message)
            return redirect('cart')
        
        # حساب المجاميع باستخدام الخصائص المحسوبة
        grand_total = sum(item.total for item in cart_items)
        
        context = {
            'cart_items': cart_items,
            'total_amount': grand_total,
            'total_days': sum(item.days for item in cart_items),
            'is_english': is_english,
            'is_rtl': is_rtl
        }
    
    # عرض واجهة دفع PayPal المحسنة (سواء كان الطلب GET أو POST)
    return render(request, 'payment_paypal_enhanced.html', context)

@login_required
@login_required
def payment_gateway_backup(request):
    """
    واجهة دفع عالمية متطورة تطابق معايير بوابات الدفع العالمية
    بما في ذلك تنسيق البطاقة والتحقق من صحتها والمصادقة ثنائية العوامل
    """
    # التحقق مما إذا كان المستخدم يأتي من حجز محدد
    reservation_id = request.GET.get('reservation_id')
    
    # تحديد لغة المستخدم
    current_language = get_language()
    is_english = current_language == 'en'
    is_rtl = current_language == 'ar'
    
    # بيانات وسائل الدفع المتاحة - فقط بطاقة ائتمانية وتحويل بنكي
    payment_methods = [
        {
            'id': 'credit_card',
            'name': 'Credit Card' if is_english else 'بطاقة ائتمان',
            'icon': 'fa-credit-card',
            'processing_time': '0-1 hours' if is_english else '0-1 ساعات'
        },
        {
            'id': 'bank_transfer',
            'name': 'Bank Transfer' if is_english else 'تحويل بنكي',
            'icon': 'fa-university',
            'processing_time': '1-2 days' if is_english else '1-2 أيام'
        }
    ]
    
    if reservation_id:
        # المستخدم يدفع لحجز محدد
        reservation = get_object_or_404(
            Reservation, 
            id=reservation_id, 
            user=request.user
        )
        
        # معالجة طلب الدفع
        if request.method == 'POST':
            payment_method = request.POST.get('payment_method', 'visa')
            
            # إنشاء رقم مرجعي للدفع
            payment_reference = f"PAY-{uuid.uuid4().hex[:8].upper()}"
            
            # تحديث حالة الحجز
            reservation.payment_status = 'paid'
            reservation.payment_reference = payment_reference
            reservation.payment_method = payment_method
            reservation.payment_date = datetime.now()
            
            # إذا تم الدفع، قم بتحديث الحالة إلى "مكتمل" إذا كان "مؤكد"
            if reservation.status == 'confirmed':
                reservation.status = 'completed'
            
            reservation.save()
            
            # رسالة نجاح
            if is_english:
                success_message = "Payment completed successfully!"
            else:
                success_message = "تم إتمام عملية الدفع بنجاح!"
            
            messages.success(request, success_message)
            
            # تخزين معرف الحجز في الجلسة لصفحة التأكيد
            request.session['last_paid_reservation_id'] = reservation.id
            
            return redirect('confirmation')
        
        context = {
            'reservation': reservation,
            'total_amount': reservation.total_price,
            'from_cart': False,
            'is_english': is_english,
            'is_rtl': is_rtl,
            'payment_methods': payment_methods
        }
    else:
        # المستخدم يدفع لعناصر من السلة
        cart_items = CartItem.objects.filter(user=request.user)
        
        if not cart_items:
            if is_english:
                warning_message = "Your cart is empty!"
            else:
                warning_message = "سلة التسوق فارغة!"
                
            messages.warning(request, warning_message)
            return redirect('cart')
        
        # حساب المجاميع باستخدام الخصائص المحسوبة
        grand_total = sum(item.total for item in cart_items)
        
        if request.method == 'POST':
            payment_method = request.POST.get('payment_method', 'visa')
            
            # إنشاء رقم مرجعي للدفع
            payment_reference = f"PAY-{uuid.uuid4().hex[:8].upper()}"
            
            # إنشاء حجوزات لجميع عناصر السلة
            for item in cart_items:
                # التحقق من توفر السيارة
                if get_car_availability(item.car.id, item.start_date, item.end_date):
                    total_price = calculate_total_price(item.car, item.start_date, item.end_date)
                    
                    # إنشاء حجز بحالة معلقة في البداية
                    reservation = Reservation.objects.create(
                        user=request.user,
                        car=item.car,
                        start_date=item.start_date,
                        end_date=item.end_date,
                        total_price=total_price,
                        status='pending',  # جميع الحجوزات تبدأ كمعلقة
                        payment_status='pending',
                        payment_method=payment_method,
                        payment_reference=payment_reference
                    )
                else:
                    if is_english:
                        error_message = f"Sorry, the car {item.car.make} {item.car.model} is no longer available for the selected dates."
                    else:
                        error_message = f"عذرًا، السيارة {item.car.make} {item.car.model} لم تعد متاحة في التواريخ المحددة."
                    
                    messages.error(request, error_message)
                    return redirect('cart')
            
            # تفريغ السلة
            cart_items.delete()
            
            if is_english:
                success_message = "Booking request submitted successfully! Please wait for administrator approval."
            else:
                success_message = "تم إرسال طلب الحجز بنجاح! يرجى انتظار موافقة المسؤول."
                
            messages.success(request, success_message)
            return redirect('confirmation')
        
        context = {
            'cart_items': cart_items,
            'total_amount': grand_total,
            'total_days': sum(item.days for item in cart_items),
            'from_cart': True,
            'is_english': is_english,
            'is_rtl': is_rtl,
            'payment_methods': payment_methods
        }
    
    return render(request, 'payment_gateway.html', context)
@login_required
def bank_transfer_payment(request):
    """Bank transfer payment interface - allows users to view bank account details and enter transfer information"""
    # التحقق مما إذا كان المستخدم يأتي من حجز محدد
    reservation_id = request.GET.get('reservation_id')
    
    # تحديد لغة المستخدم
    current_language = get_language()
    is_english = current_language == 'en'
    is_rtl = current_language == 'ar'
    
    if not reservation_id:
        # إذا لم يتم تحديد معرف الحجز، إعادة توجيه المستخدم إلى صفحة الحجوزات
        messages.error(
            request, 
            "Reservation ID is required for bank transfer payment." if is_english else 
            "رقم الحجز مطلوب للدفع عبر التحويل البنكي."
        )
        return redirect('my_reservations')
    
    # الحصول على تفاصيل الحجز
    reservation = get_object_or_404(
        Reservation, 
        id=reservation_id, 
        user=request.user, 
        status='confirmed', 
        payment_status='pending'
    )
    
    context = {
        'reservation': reservation,
        'total_amount': reservation.total_price,
        'is_english': is_english,
        'is_rtl': is_rtl
    }
    
    return render(request, 'payment_bank_transfer.html', context)
