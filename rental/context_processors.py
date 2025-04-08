from .models import CartItem

def cart_count(request):
    """Add cart_count to all templates"""
    count = 0
    if request.user.is_authenticated:
        count = CartItem.objects.filter(user=request.user).count()
    return {'cart_count': count}

def dark_mode(request):
    """Add dark_mode to all templates"""
    dark_mode = request.session.get('dark_mode', False)
    return {'dark_mode': dark_mode}

def language_context(request):
    """
    إضافة سياق اللغة لجميع القوالب
    
    تقوم هذه الدالة بتوفير متغيرات السياق اللازمة للقوالب للتكيف مع اللغة المناسبة
    (العربية أو الإنجليزية)، بالاعتماد على نظام الترجمة الأصلي في Django.
    
    نستخدم متغير LANGUAGE_CODE المتوفر من خلال middleware اللغة في Django.
    """
    # تعتمد على LANGUAGE_CODE الذي يوفره Django
    # والذي يتم تحديثه تلقائيًا من خلال middleware اللغة

    # 1. تعيين العلامات المنطقية للاستخدام في القوالب
    language_code = getattr(request, 'LANGUAGE_CODE', None)
    if language_code is None:
        from django.utils.translation import get_language
        language_code = get_language()
    
    is_arabic = (language_code == 'ar')
    is_english = (language_code == 'en' or not is_arabic)
    
    # 2. متغيرات سياق لدعم تكييف القوالب مع اتجاه اللغة
    context_data = {
        # المتغيرات الأساسية للغة (احتفظنا بها للتوافق مع القوالب الحالية)
        'current_language': language_code,
        'LANGUAGE_CODE': language_code, 
        'is_arabic': is_arabic,
        'is_english': is_english,
        
        # متغيرات اتجاه النص والتنسيق
        'html_dir': 'rtl' if is_arabic else 'ltr',
        'html_lang': 'ar' if is_arabic else 'en',
        'text_align': 'right' if is_arabic else 'left',
        
        # متغيرات هوامش Bootstrap المعتمدة على اللغة
        'margin_right_class': 'ms' if is_arabic else 'me',
        'margin_left_class': 'me' if is_arabic else 'ms',
        
        # متغيرات الخط والتنسيق
        'font_family': "'Tajawal', sans-serif" if is_arabic else "'Roboto', sans-serif",
        'bootstrap_css': 'bootstrap.rtl.min.css' if is_arabic else 'bootstrap.min.css'
    }
    
    return context_data