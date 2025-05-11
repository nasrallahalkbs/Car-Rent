from .models import Reservation
from rental.models import CartItem, FavoriteCar
from django.db.models import Sum

def cart_count(request):
    """
    إضافة عدد عناصر سلة التسوق إلى سياق القالب
    """
    cart_items_count = 0
    favorites_count = 0
    if request.user.is_authenticated:
        try:
            # تم إزالة الشرط is_active حيث لا يوجد هذا الحقل في نموذج CartItem
            cart_items_count = CartItem.objects.filter(user=request.user).count()
            favorites_count = FavoriteCar.objects.filter(user=request.user).count()
        except Exception as e:
            print(f"خطأ في حساب العناصر: {e}")
    return {
        'cart_items_count': cart_items_count,
        'favorites_count': favorites_count
    }

def dark_mode(request):
    """
    التحقق من وضع الألوان المفضل للمستخدم
    """
    is_dark_mode = request.session.get('dark_mode', False)
    return {'is_dark_mode': is_dark_mode}

def language_context(request):
    """
    إضافة معلومات اللغة الحالية إلى سياق القالب
    """
    current_language = getattr(request, 'LANGUAGE_CODE', 'ar')
    return {
        'current_language': current_language,
        'is_arabic': current_language == 'ar',
        'is_english': current_language == 'en',
    }

def admin_notifications(request):
    """
    يضيف معلومات الإشعارات والتنبيهات المتعلقة بالمشرف لجميع القوالب
    """
    context = {
        'pending_reservations_list': [],
    }
    
    # التحقق إذا كان المستخدم مسجل الدخول ومشرف
    if request.user.is_authenticated and hasattr(request.user, 'is_admin') and request.user.is_admin:
        try:
            # جلب آخر 5 حجوزات معلقة
            context['pending_reservations_list'] = Reservation.objects.filter(
                status='pending'
            ).order_by('-created_at')[:5]
        except Exception:
            # في حالة حدوث خطأ، نعيد قائمة فارغة
            pass
    
    return context