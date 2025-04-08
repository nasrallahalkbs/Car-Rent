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
    """Add language context to all templates"""
    # التحقق أولاً من الكوكيز ثم الجلسة
    language = 'en'  # اللغة الافتراضية هي الإنجليزية
    
    # الحصول على اللغة من الكوكيز
    if hasattr(request, 'COOKIES') and 'django_language' in request.COOKIES:
        language = request.COOKIES.get('django_language')
    # الحصول على اللغة من الجلسة كاحتياطي
    elif hasattr(request, 'session') and 'django_language' in request.session:
        language = request.session.get('django_language')
    
    # تأكد من أن القيمة هي إما 'ar' أو 'en'
    if language not in ['ar', 'en']:
        language = 'en'
    
    # تعيين العلامات المنطقية للاستخدام في القوالب
    is_arabic = (language == 'ar')
    is_english = (language == 'en')
    
    # معلومات تصحيح
    print(f"Context Processor - Language: {language}, is_arabic: {is_arabic}, is_english: {is_english}")
    
    # متغيرات سياق إضافية لتكييف التخطيط
    return {
        'current_language': language,
        'LANGUAGE_CODE': language,  # اسم متغير السياق الافتراضي لـ Django
        'is_arabic': is_arabic,
        'is_english': is_english,
        'html_dir': 'rtl' if is_arabic else 'ltr',
        'html_lang': 'ar' if is_arabic else 'en',
        'margin_right_class': 'ms' if is_arabic else 'me',
        'margin_left_class': 'me' if is_arabic else 'ms',
        'text_align': 'right' if is_arabic else 'left',
        'font_family': "'Tajawal', sans-serif" if is_arabic else "'Roboto', sans-serif",
        'bootstrap_css': 'bootstrap.rtl.min.css' if is_arabic else 'bootstrap.min.css'
    }