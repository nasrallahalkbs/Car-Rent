"""
WSGI config for car_rental_project project.
تكوين WSGI لمشروع تأجير السيارات.
"""

import os
import re

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'car_rental_project.settings')

# الحصول على تطبيق WSGI
application = get_wsgi_application()

# تحديث النطاقات الموثوقة لـ CSRF ديناميكيًا
def update_csrf_trusted_origins():
    """
    تحديث قائمة النطاقات الموثوقة CSRF_TRUSTED_ORIGINS عند بدء التشغيل
    لتضمين جميع النطاقات المستندة إلى Replit
    """
    from django.conf import settings
    
    # الحصول على معلومات Replit من متغيرات البيئة
    replit_id = os.environ.get('REPL_ID', '')
    
    if replit_id:
        # إضافة أنماط عامة تغطي جميع احتمالات عناوين Replit
        general_patterns = [
            f'https://{replit_id}-*',
            f'https://{replit_id}.*',
            f'https://{replit_id}-*.*.replit.dev',
            f'https://{replit_id}-*.*.replit.dev:*',
            'https://*.replit.dev',
            'https://*.replit.dev:*',
            'https://*.sisko.replit.dev',
            'https://*.sisko.replit.dev:*',
        ]
        
        # إضافة النطاقات إلى قائمة النطاقات الموثوقة
        for pattern in general_patterns:
            if pattern not in settings.CSRF_TRUSTED_ORIGINS:
                settings.CSRF_TRUSTED_ORIGINS.append(pattern)
                
        # إضافة النطاق المحدد الحالي
        specific_domain = f'https://{replit_id}-00-26n4b48jep28q.sisko.replit.dev'
        if specific_domain not in settings.CSRF_TRUSTED_ORIGINS:
            settings.CSRF_TRUSTED_ORIGINS.append(specific_domain)
            settings.CSRF_TRUSTED_ORIGINS.append(f'{specific_domain}:8000')
    
    return settings.CSRF_TRUSTED_ORIGINS

# تحديث النطاقات الموثوقة عند بدء التشغيل
update_csrf_trusted_origins()