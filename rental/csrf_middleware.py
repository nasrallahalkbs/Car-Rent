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
            # إزالة خاصية SameSite لتمكين استخدام CSRF في بيئة Replit
            # إزالة خاصية Secure لتمكين استخدام CSRF في بيئة التطوير
            # ضبط مجال Domain ليكون فارغًا للسماح للنطاق الحالي
            response.cookies['csrftoken']['samesite'] = 'Lax'
            response.cookies['csrftoken']['secure'] = False
            response.cookies['csrftoken']['domain'] = ''
            
            # إذا كنا في بيئة Replit، نقوم بضبط قيمة HttpOnly إلى False
            # لتمكين قراءة البسكويت من JavaScript
            if getattr(settings, 'REPLIT_ENVIRONMENT', False):
                response.cookies['csrftoken']['httponly'] = False
        
        # إذا كانت الاستجابة تحتوي على ملف تعريف ارتباط الجلسة
        if 'sessionid' in response.cookies:
            # تطبيق نفس التغييرات على ملف تعريف ارتباط الجلسة
            response.cookies['sessionid']['samesite'] = 'Lax'
            response.cookies['sessionid']['secure'] = False
            response.cookies['sessionid']['domain'] = ''
            
            # عادة ما يكون HttpOnly لملف تعريف ارتباط الجلسة مضبوطًا على True
            # للأمان، لكن في بيئة Replit قد نحتاج إلى تغييره
            if getattr(settings, 'REPLIT_ENVIRONMENT', False):
                response.cookies['sessionid']['httponly'] = False
        
        return response