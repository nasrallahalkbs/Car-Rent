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
    
    تقوم هذه الدالة بتوفير متغيرات سياق إضافية للقوالب للتكيف مع اللغة المناسبة
    (العربية أو الإنجليزية)، بالاعتماد على نظام الترجمة الأصلي في Django.
    """
    from django.utils.translation import get_language
    import logging
    
    # إعداد التسجيل
    logger = logging.getLogger(__name__)
    
    # get_language يقوم بإرجاع رمز اللغة الحالية مثل 'ar' أو 'en'
    language_code = get_language() or 'ar'  # الافتراضي هو العربية إذا لم يتم تعيين لغة
    
    # تعيين العلامات المنطقية
    is_arabic = (language_code == 'ar')
    is_english = (language_code == 'en')
    
    # طباعة معلومات تصحيح الأخطاء
    print(f"Current language: {language_code}")
    
    # التحقق من وجود ملف تعريف الارتباط للغة
    cookie_lang = request.COOKIES.get('django_language', 'none')
    print(f"Cookie language: {cookie_lang}")
    
    # التحقق من مسار URL
    path = request.path_info
    url_language = "none"
    if path.startswith('/ar/'):
        url_language = "ar"
    elif path.startswith('/en/'):
        url_language = "en"
    print(f"URL language: {url_language}")
    
    # تسجيل معلومات السياق
    logger.debug(f"Language context: code={language_code}, is_ar={is_arabic}, is_en={is_english}, url_lang={url_language}")
    
    # إنشاء متغيرات السياق
    context_data = {
        # متغيرات السياق المستخدمة في القوالب الحالية (للتوافق)
        'current_language': language_code,
        'is_arabic': is_arabic,
        'is_english': is_english,
        
        # متغيرات اتجاه النص
        'html_dir': 'rtl' if is_arabic else 'ltr',
        'html_lang': language_code,
        'text_align': 'right' if is_arabic else 'left',
        'float_dir': 'right' if is_arabic else 'left',
        'opposite_float_dir': 'left' if is_arabic else 'right',
        
        # متغيرات Bootstrap
        'margin_right_class': 'ms' if is_arabic else 'me',
        'margin_left_class': 'me' if is_arabic else 'ms',
        
        # متغيرات تنسيق الخطوط - مهمة للعربية
        'font_family': "'Tajawal', sans-serif" if is_arabic else "'Roboto', sans-serif",
        'font_size_adjust': '1.1' if is_arabic else '1',
        
        # فحص اللغة - الشفرة اللغوية الكاملة
        'is_ar': is_arabic,
        'is_en': is_english,
        
        # إضافة المزيد من المتغيرات المفيدة
        'is_rtl': is_arabic,
        'is_ltr': not is_arabic,
        'text_direction': 'rtl' if is_arabic else 'ltr',
        
        # معلومات تصحيح
        'debug_language_cookie': cookie_lang,
        'debug_url_language': url_language,
    }
    
    return context_data
