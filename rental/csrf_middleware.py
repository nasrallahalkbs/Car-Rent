"""
وحدة middleware مخصصة للتعامل مع CSRF في بيئة Replit
"""

import os
from django.conf import settings
from django.utils.deprecation import MiddlewareMixin
from django.middleware.csrf import get_token
from urllib.parse import urlparse

def get_current_replit_domain():
    """
    الحصول على اسم النطاق الحالي لبيئة Replit
    يستخدم معرف REPL_ID من متغيرات البيئة
    """
    replit_id = os.environ.get('REPL_ID', '')
    if not replit_id:
        return None
    
    # يمكن أن يكون نطاق Replit واحدًا من عدة أنماط
    possible_domains = [
        f'https://{replit_id}-00-*.sisko.replit.dev',
        f'https://{replit_id}-00-*.sisko.replit.dev:8000',
    ]
    
    # إضافة النطاقات المحتملة إلى قائمة النطاقات الموثوقة
    for domain in possible_domains:
        if domain not in settings.CSRF_TRUSTED_ORIGINS:
            settings.CSRF_TRUSTED_ORIGINS.append(domain)
    
    return settings.CSRF_TRUSTED_ORIGINS

class CSRFFixMiddleware(MiddlewareMixin):
    """
    MiddleWare مخصص لإصلاح مشكلة CSRF في بيئة Replit
    يقوم بإعداد ملفات تعريف الارتباط بشكل صحيح ويضمن وجود توكن CSRF في كل صفحة
    """
    
    def process_request(self, request):
        """
        إعداد توكن CSRF لكل طلب للتأكد من توفره
        """
        # تحديث قائمة النطاقات الموثوقة ديناميكيًا بناءً على بيئة Replit الحالية
        get_current_replit_domain()
        
        # إضافة النطاق الحالي من الطلب إلى النطاقات الموثوقة
        if request.headers.get('Origin'):
            origin = request.headers.get('Origin')
            if origin not in settings.CSRF_TRUSTED_ORIGINS:
                settings.CSRF_TRUSTED_ORIGINS.append(origin)
        
        if request.method == "GET":
            # تفعيل توكن CSRF مباشرة في بداية الطلب GET
            # هذا يضمن أن Django سيقوم بإنشاء CSRF cookie
            get_token(request)
            
        # تأكد من وجود التوكن في الجلسة
        if 'csrftoken' not in request.COOKIES and hasattr(request, 'session'):
            request.session['csrftoken'] = get_token(request)
            
        return None
    
    def process_response(self, request, response):
        """
        تعديل إعدادات ملفات تعريف الارتباط لـ CSRF للعمل في بيئة Replit
        """
        # إذا كانت الاستجابة تحتوي على ملف تعريف ارتباط CSRF
        if 'csrftoken' in response.cookies:
            # تعديل خصائص ملف تعريف الارتباط
            # للعمل في بيئة Replit
            response.cookies['csrftoken']['samesite'] = 'None'  # تغيير من 'Lax' إلى 'None' لمزيد من التوافق
            response.cookies['csrftoken']['secure'] = True  # تمكين بشكل صريح للنطاقات الآمنة (https)
            response.cookies['csrftoken']['httponly'] = False
            # زيادة وقت انتهاء الصلاحية
            response.cookies['csrftoken']['max-age'] = 60 * 60 * 24 * 7  # أسبوع واحد
            # السماح بالتشغيل في نطاق الجذر للمشروع
            response.cookies['csrftoken']['path'] = '/'
        
        # إذا كانت الاستجابة تحتوي على ملف تعريف ارتباط الجلسة
        if 'sessionid' in response.cookies:
            # تطبيق نفس التغييرات على ملف تعريف ارتباط الجلسة
            response.cookies['sessionid']['samesite'] = 'None'  # تغيير من 'Lax' إلى 'None' لمزيد من التوافق
            response.cookies['sessionid']['secure'] = True  # تمكين بشكل صريح للنطاقات الآمنة (https)
            response.cookies['sessionid']['path'] = '/'
        
        # تضمين تعليمات لمنع التخزين المؤقت
        # هذا يساعد في تجنب مشاكل CSRF أثناء التغيير بين الصفحات
        response['Cache-Control'] = 'no-cache, no-store, must-revalidate, max-age=0'
        response['Pragma'] = 'no-cache'
        response['Expires'] = '0'
        
        return response