"""
وحدة middleware مخصصة للتعامل مع CSRF في بيئة Replit
"""

from django.conf import settings
from django.utils.deprecation import MiddlewareMixin

class CSRFFixMiddleware(MiddlewareMixin):
    """
    MiddleWare مخصص لإصلاح مشكلة CSRF في بيئة Replit
    """
    
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
        
        # إذا كانت الاستجابة تحتوي على ملف تعريف ارتباط الجلسة
        if 'sessionid' in response.cookies:
            # تطبيق نفس التغييرات على ملف تعريف ارتباط الجلسة
            response.cookies['sessionid']['samesite'] = 'Lax'
            response.cookies['sessionid']['secure'] = False
        
        return response