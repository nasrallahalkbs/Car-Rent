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
    # Get language from Django's i18n system
    language = get_language() or 'ar'
    is_arabic = language.startswith('ar')
    is_english = language.startswith('en')
    
    # Additional context variables for layout adaptation
    return {
        'current_language': language,
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