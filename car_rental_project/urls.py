from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.conf.urls.i18n import i18n_patterns
from django.utils.translation import gettext_lazy as _

# المسارات التي لا تحتاج بادئة لغة
urlpatterns = [
    # إضافة مسار العرض الخاص بتبديل اللغة من Django
    path('i18n/', include('django.conf.urls.i18n')),
    
    # مسار تسجيل الدخول الرئيسي
    path('login/', lambda request: redirect('login'), name='main_login'),
]

# استيراد redirect للتوجيه
from django.shortcuts import redirect

# المسارات مع بادئة اللغة (مثل /ar/، /en/)
urlpatterns += i18n_patterns(
    path(_('admin/'), admin.site.urls),  # يمكن ترجمة المسارات أيضًا
    path(_('superadmin/'), include('rental.superadmin_urls')),  # مسارات لوحة تحكم المسؤول الأعلى
    path('', include('rental.urls')),
    prefix_default_language=True,  # تضمين بادئة اللغة الافتراضية أيضًا
)

# خدمة ملفات الوسائط والملفات الثابتة
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)