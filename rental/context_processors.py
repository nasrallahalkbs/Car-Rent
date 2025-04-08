from .models import CartItem
from django.utils.translation import get_language

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
    # Get language from Django's i18n system, cookies, or session
    language = get_language() or 'ar'
    
    # Also check from request directly (cookie or session) for redundancy
    if hasattr(request, 'COOKIES'):
        cookie_lang = request.COOKIES.get('django_language')
        if cookie_lang:
            language = cookie_lang
    
    # Set boolean flags for template use
    is_arabic = language.startswith('ar')
    is_english = language.startswith('en')
    
    # Debug
    print(f"Current language: {language}, is_arabic: {is_arabic}, is_english: {is_english}")
    
    # Additional context variables for layout adaptation
    return {
        'current_language': language,
        'LANGUAGE_CODE': language,  # Django's default context variable name
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