from django.utils import translation
from django.utils.deprecation import MiddlewareMixin
from django.conf import settings
import logging
import re

# إعداد التسجيل
logger = logging.getLogger(__name__)

class ForceLanguageMiddleware(MiddlewareMixin):
    """
    ميدلوير مخصص للتأكد من ضبط اللغة بشكل صحيح في كل طلب
    يعمل بالتزامن مع ميدلوير LocaleMiddleware الموجود في Django
    """
    
    def process_request(self, request):
        """
        معالجة الطلب وضبط اللغة المناسبة
        """
        # محاولة الحصول على اللغة من مسار URL أولاً
        url_language = None
        path = request.path_info
        language_prefix_pattern = re.compile(r'^/(ar|en)/')
        match = language_prefix_pattern.match(path)
        if match:
            url_language = match.group(1)
        
        # محاولة الحصول على اللغة من ملف تعريف الارتباط
        lang_cookie = request.COOKIES.get(settings.LANGUAGE_COOKIE_NAME)
        
        # التحقق من اللغة في جلسة المستخدم
        lang_session = request.session.get(settings.LANGUAGE_COOKIE_NAME)
        
        # تسجيل معلومات اللغة للتصحيح
        print(f"URL language: {url_language}")
        print(f"Language cookie: {lang_cookie}")
        print(f"Language session: {lang_session}")
        print(f"Accept-Language header: {request.META.get('HTTP_ACCEPT_LANGUAGE', '')}")
        
        # الأولوية: مسار URL، ثم ملف تعريف الارتباط، ثم الجلسة، ثم اللغة الافتراضية
        language = url_language or lang_cookie or lang_session or settings.LANGUAGE_CODE
        
        # تعيين اللغة النشطة
        translation.activate(language)
        
        # إضافة معلومات اللغة إلى الطلب
        request.LANGUAGE_CODE = language
        
        # تسجيل اللغة المستخدمة
        print(f"Using language: {language}")
        
        return None
    
    def process_response(self, request, response):
        """
        معالجة الاستجابة وضبط ملفات تعريف الارتباط للغة
        """
        # التأكد من وجود ملف تعريف ارتباط اللغة في كل استجابة
        lang = translation.get_language()
        
        # تعيين ملف تعريف الارتباط إذا لم يكن موجودًا
        if settings.LANGUAGE_COOKIE_NAME not in response.cookies:
            response.set_cookie(
                settings.LANGUAGE_COOKIE_NAME,
                lang,
                max_age=settings.LANGUAGE_COOKIE_AGE,
                path=settings.LANGUAGE_COOKIE_PATH,
                domain=settings.LANGUAGE_COOKIE_DOMAIN,
                secure=settings.LANGUAGE_COOKIE_SECURE,
                httponly=settings.LANGUAGE_COOKIE_HTTPONLY,
                samesite=settings.LANGUAGE_COOKIE_SAMESITE,
            )
        
        return response
