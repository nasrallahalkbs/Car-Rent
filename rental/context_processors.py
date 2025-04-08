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
    
    تقوم هذه الدالة بتحديد اللغة الحالية وتوفير متغيرات السياق اللازمة
    للقوالب للتكيف مع اللغة المناسبة (العربية أو الإنجليزية).
    
    ترتيب أولوية تحديد اللغة:
    1. الكوكيز (django_language)
    2. جلسة المستخدم (django_language)
    3. القيمة الافتراضية (الإنجليزية)
    """
    # 1. تحديد اللغة الحالية (القيمة الافتراضية هي الإنجليزية)
    language = 'en'
    
    # 2. محاولة الحصول على اللغة من الكوكيز (الأولوية الأولى)
    if hasattr(request, 'COOKIES') and 'django_language' in request.COOKIES:
        cookie_lang = request.COOKIES.get('django_language')
        if cookie_lang in ['ar', 'en']:
            language = cookie_lang
    
    # 3. محاولة الحصول على اللغة من جلسة المستخدم (الأولوية الثانية)
    elif hasattr(request, 'session') and 'django_language' in request.session:
        session_lang = request.session.get('django_language')
        if session_lang in ['ar', 'en']:
            language = session_lang
    
    # 4. تعيين العلامات المنطقية للاستخدام في القوالب
    is_arabic = (language == 'ar')
    is_english = (language == 'en')
    
    # 5. متغيرات سياق لدعم تكييف القوالب مع اتجاه اللغة
    context_data = {
        # المتغيرات الأساسية للغة
        'current_language': language,
        'LANGUAGE_CODE': language,  # اسم متغير السياق الافتراضي لـ Django
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