from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils.translation import gettext as _
from .models import Reservation, CartItem
from .utils import get_car_availability, calculate_total_price
from datetime import datetime
import uuid

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
        
        # حساب المجاميع
        grand_total = 0
        for item in cart_items:
            delta = (item.end_date - item.start_date).days + 1
            item.days = delta
            item.total = item.car.daily_rate * delta
            grand_total += item.total
        
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
    
    return render(request, 'payment_professional_advanced.html', context)