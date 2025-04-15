"""
وحدة middleware مخصصة للتعامل مع CSRF في بيئة Replit
"""

from django.conf import settings
from django.utils.deprecation import MiddlewareMixin
from django.middleware.csrf import get_token

class CSRFFixMiddleware(MiddlewareMixin):
    """
    MiddleWare مخصص لإصلاح مشكلة CSRF في بيئة Replit
    يقوم بإعداد ملفات تعريف الارتباط بشكل صحيح ويضمن وجود توكن CSRF في كل صفحة
    """
    
    def process_request(self, request):
        """
        إعداد توكن CSRF لكل طلب للتأكد من توفره
        """
        # تفعيل توكن CSRF مباشرة في بداية الطلب
        # هذا يضمن أن Django سيقوم بإنشاء CSRF cookie
        get_token(request)
        return None
    
    def process_response(self, request, response):
        """
        تعديل إعدادات ملفات تعريف الارتباط لـ CSRF للعمل في بيئة Replit
        """
        # إذا كانت الاستجابة تحتوي على ملف تعريف ارتباط CSRF
        if 'csrftoken' in response.cookies:
            # تعديل خصائص ملف تعريف الارتباط
            # للعمل في بيئة Replit
            response.cookies['csrftoken']['samesite'] = 'Lax'
            response.cookies['csrftoken']['secure'] = False
            response.cookies['csrftoken']['httponly'] = False
            # زيادة وقت انتهاء الصلاحية
            response.cookies['csrftoken']['max-age'] = 60 * 60 * 24 * 7  # أسبوع واحد
            # السماح بالتشغيل في نطاق الجذر للمشروع
            response.cookies['csrftoken']['path'] = '/'
        
        # إذا كانت الاستجابة تحتوي على ملف تعريف ارتباط الجلسة
        if 'sessionid' in response.cookies:
            # تطبيق نفس التغييرات على ملف تعريف ارتباط الجلسة
            response.cookies['sessionid']['samesite'] = 'Lax'
            response.cookies['sessionid']['secure'] = False
            response.cookies['sessionid']['path'] = '/'
        
        # تضمين تعليمات لمنع التخزين المؤقت
        # هذا يساعد في تجنب مشاكل CSRF أثناء التغيير بين الصفحات
        response['Cache-Control'] = 'no-cache, no-store, must-revalidate, max-age=0'
        response['Pragma'] = 'no-cache'
        response['Expires'] = '0'
        
        return response