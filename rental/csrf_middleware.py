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
        # يتحقق مما إذا كانت الاستجابة تحتوي على ملف تعريف ارتباط CSRF
        if 'csrftoken' in response.cookies:
            # تعديل إعدادات ملف تعريف الارتباط CSRF
            response.cookies['csrftoken']['secure'] = False
            response.cookies['csrftoken']['samesite'] = 'None'
            # حل مشكلة نطاق ملف تعريف الارتباط (domain)
            if 'domain' in response.cookies['csrftoken']:
                del response.cookies['csrftoken']['domain']
                
        return response