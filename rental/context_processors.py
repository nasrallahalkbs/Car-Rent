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
    
    LANGUAGE_CODE متاح في القوالب تلقائيًا من خلال template context processor
    المسمى django.template.context_processors.i18n
    """
    from django.utils.translation import get_language
    
    # get_language يقوم بإرجاع رمز اللغة الحالية مثل 'ar' أو 'en'
    language_code = get_language()
    
    # تعيين العلامات المنطقية
    is_arabic = (language_code == 'ar')
    is_english = (language_code == 'en')
    
    # إنشاء متغيرات السياق الإضافية
    context_data = {
        # متغيرات السياق المستخدمة في القوالب الحالية (للتوافق)
        'current_language': language_code,
        'is_arabic': is_arabic,
        'is_english': is_english,
        
        # متغيرات اتجاه النص
        'html_dir': 'rtl' if is_arabic else 'ltr',
        'html_lang': 'ar' if is_arabic else 'en',
        'text_align': 'right' if is_arabic else 'left',
        
        # متغيرات Bootstrap
        'margin_right_class': 'ms' if is_arabic else 'me',
        'margin_left_class': 'me' if is_arabic else 'ms',
        
        # متغيرات التنسيق
        'font_family': "'Tajawal', sans-serif" if is_arabic else "'Roboto', sans-serif"
    }
    
    return context_data