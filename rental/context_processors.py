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
        'admin_notifications': [],
        'system_notifications': [],
    }
    
    # التحقق إذا كان المستخدم مسجل الدخول ومشرف
    if request.user.is_authenticated and hasattr(request.user, 'is_admin') and request.user.is_admin:
        try:
            # جلب آخر 5 حجوزات معلقة
            context['pending_reservations_list'] = Reservation.objects.filter(
                status='pending'
            ).order_by('-created_at')[:5]
            
            # التحقق إذا كان المستخدم مشرف أعلى
            if hasattr(request.user, 'is_superadmin') and request.user.is_superadmin:
                # استيراد نموذج نشاط المسؤولين
                from .models_superadmin import AdminActivity
                
                # جلب آخر 5 سجلات نشاط للمسؤولين
                context['admin_notifications'] = AdminActivity.objects.select_related(
                    'admin', 'admin__user'
                ).order_by('-created_at')[:10]
                
                # جلب إشعارات النظام
                from .models_system import SystemNotification
                try:
                    context['system_notifications'] = SystemNotification.objects.filter(
                        is_read=False
                    ).order_by('-created_at')[:5]
                except Exception:
                    # قد لا يكون جدول إشعارات النظام موجوداً
                    pass
        except Exception as e:
            # في حالة حدوث خطأ، نسجل الخطأ ونعيد قائمة فارغة
            print(f"خطأ في جلب الإشعارات: {e}")
    
    return context
def media_url_context(request):
    """
    إضافة مسار الوسائط الصحيح إلى سياق القالب
    """
    from django.conf import settings
    return {
        'MEDIA_URL': settings.MEDIA_URL,
        'MEDIA_ROOT': settings.MEDIA_ROOT,
    }
