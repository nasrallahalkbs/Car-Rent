from django.utils import translation
from django.utils.deprecation import MiddlewareMixin
from django.conf import settings
from django.shortcuts import redirect
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
        # تدفق خاص لمعالجة تبديل اللغة
        if request.path_info.endswith('/toggle-language/'):
            print("Toggle language request detected, skipping language middleware processing")
            return None
            
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
        
        # الأولوية المعدلة: ملف تعريف الارتباط، ثم جلسة المستخدم، ثم مسار URL، ثم اللغة الافتراضية
        # هذا يسمح لاختيار المستخدم بتجاوز بادئة المسار
        language = lang_cookie or lang_session or url_language or settings.LANGUAGE_CODE
        
        # إذا كانت اللغة المختارة لا تتطابق مع بادئة URL واللغة ليست AR (وهي الافتراضية)،
        # نقوم بإعادة التوجيه إلى المسار الصحيح
        if lang_cookie and url_language and lang_cookie != url_language and request.method == 'GET':
            # إذا كان المستخدم قام بتغيير اللغة، نعيد توجيهه إلى المسار بالبادئة الصحيحة
            if lang_cookie == 'en' and url_language == 'ar':
                correct_path = path.replace('/ar/', '/en/', 1)
                print(f"Redirecting to correct language path: {correct_path}")
                return redirect(correct_path)
        
        # تعيين اللغة النشطة
        translation.activate(language)
        
        # إضافة معلومات اللغة إلى الطلب
        request.LANGUAGE_CODE = language
        
        # تخزين اللغة المحددة في الجلسة للاتساق
        if not lang_session or lang_session != language:
            request.session[settings.LANGUAGE_COOKIE_NAME] = language
            request.session.modified = True
        
        # تسجيل اللغة المستخدمة
        print(f"Using language: {language}")
        
        return None
    
    def process_response(self, request, response):
        """
        معالجة الاستجابة وضبط ملفات تعريف الارتباط للغة
        """
        # التأكد من وجود ملف تعريف ارتباط اللغة في كل استجابة
        lang = translation.get_language()
        
        # تحقق مما إذا كان هناك تغيير في اللغة تم ضبطه من خلال toggle_language
        toggle_language_cookie = request.COOKIES.get(settings.LANGUAGE_COOKIE_NAME)
        
        # إذا كان هناك ملف تعريف ارتباط للغة تم تعيينه عن طريق toggle_language،
        # فلا نقوم بتغييره هنا لتجنب التعارض
        if not toggle_language_cookie and settings.LANGUAGE_COOKIE_NAME not in response.cookies:
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
        
        # طباعة معلومات التصحيح
        print(f"Response language: {lang}, Cookie language: {toggle_language_cookie}")
        
        return response
