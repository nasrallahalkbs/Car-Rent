import os
import re
from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get("SESSION_SECRET")
if not SECRET_KEY:
    SECRET_KEY = "django-insecure-default-key-for-development"

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ["*"]  # Allow all hosts for development

# Get Replit host if available from environment
REPLIT_SLUG = os.environ.get('REPL_SLUG', '')
REPLIT_OWNER = os.environ.get('REPL_OWNER', '')
REPLIT_ID = os.environ.get('REPL_ID', '')

# CSRF settings for Replit environment
CSRF_TRUSTED_ORIGINS = [
    'https://*.replit.app',
    'https://*.replit.dev',
    'https://*.pike.replit.dev',
    'https://*.sisko.replit.dev',
    f'https://{REPLIT_SLUG}.{REPLIT_OWNER}.repl.co',
    f'https://{REPLIT_ID}.id.repl.co',
    'https://*.repl.co',
    'https://247299eb-56db-40dd-9589-fe24387a6bf8-00-1hevkyvsh17at.sisko.replit.dev:8000',
    'https://247299eb-56db-40dd-9589-fe24387a6bf8-00-1hevkyvsh17at.sisko.replit.dev',
    'https://d2177ceb-9728-4182-a8ff-35de971df8e4-00-26n4b48jep28q.sisko.replit.dev:8000',
    'https://d2177ceb-9728-4182-a8ff-35de971df8e4-00-26n4b48jep28q.sisko.replit.dev',
]

# Additional CSRF Settings
CSRF_COOKIE_SECURE = True  # التشغيل في بيئة HTTPS آمنة
CSRF_COOKIE_HTTPONLY = False  # السماح للجافا سكريبت بالوصول إلى الكوكي
CSRF_COOKIE_SAMESITE = 'None'  # تغيير من 'Lax' إلى 'None' للتوافق عبر نطاقات مختلفة
CSRF_USE_SESSIONS = True  # استخدام الجلسات لتخزين توكن CSRF
CSRF_COOKIE_NAME = 'csrftoken'
CSRF_HEADER_NAME = 'HTTP_X_CSRFTOKEN'
CSRF_FAILURE_VIEW = 'rental.csrf_debug.csrf_failure'
CSRF_COOKIE_DOMAIN = None
CSRF_COOKIE_PATH = '/'
CSRF_COOKIE_AGE = 60 * 60 * 24 * 7  # 1 week in seconds

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'crispy_forms',
    'crispy_bootstrap5',
    'rental',  # Our rental app
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'rental.middleware.ForceLanguageMiddleware',  # مهم: يجب أن يكون بعد SessionMiddleware وقبل CommonMiddleware
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'rental.csrf_middleware.CSRFFixMiddleware',  # MiddleWare جديد لإصلاح مشكلة CSRF في بيئة Replit
]


# Session cookie settings
SESSION_COOKIE_SECURE = True  # تأمين ملف تعريف ارتباط الجلسة مع HTTPS
SESSION_COOKIE_HTTPONLY = True  # منع الوصول من JavaScript
SESSION_COOKIE_SAMESITE = 'None'  # تغيير من 'Lax' إلى 'None' للتوافق عبر النطاقات

ROOT_URLCONF = 'car_rental_project.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.template.context_processors.i18n',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'rental.context_processors.cart_count',
                'rental.context_processors.dark_mode',
                'rental.context_processors.language_context',
            ],
        },
    },
]

WSGI_APPLICATION = 'car_rental_project.wsgi.application'

# Database
# https://docs.djangoproject.com/en/5.2/ref/settings/#databases
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# Password validation
# https://docs.djangoproject.com/en/5.2/ref/settings/#auth-password-validators
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Custom user model
AUTH_USER_MODEL = 'rental.User'

# Internationalization
# https://docs.djangoproject.com/en/5.2/topics/i18n/
LANGUAGE_CODE = 'ar'  # Default language
TIME_ZONE = 'UTC'
USE_I18N = True
USE_L10N = True  # Localize data presentation
USE_TZ = True

# Available languages
from django.utils.translation import gettext_lazy as _
LANGUAGES = [
    ('ar', _('Arabic')),
    ('en', _('English')),
]

# Path to locale folders
LOCALE_PATHS = [
    os.path.join(BASE_DIR, 'locale'),
]

# إعدادات اللغة والكوكيز
LANGUAGE_COOKIE_NAME = 'django_language'    # اسم الكوكي الذي سيتم استخدامه لتخزين تفضيل اللغة
LANGUAGE_COOKIE_AGE = 60 * 60 * 24 * 365    # مدة صلاحية الكوكي (سنة واحدة بالثواني)
LANGUAGE_COOKIE_DOMAIN = None               # نطاق الكوكي (لا تعيين قيمة يعني النطاق الحالي فقط)
LANGUAGE_COOKIE_PATH = '/'                  # مسار الكوكي (متاح لجميع الصفحات)
LANGUAGE_COOKIE_SECURE = True               # تأمين مع HTTPS
LANGUAGE_COOKIE_HTTPONLY = False            # السماح لـ JavaScript بالوصول
LANGUAGE_COOKIE_SAMESITE = 'None'           # تغيير من 'Lax' إلى 'None' للتوافق عبر النطاقات

# Use SessionMiddleware for storing language preference in the session as well
SESSION_COOKIE_AGE = 60 * 60 * 24 * 30      # مدة جلسة المستخدم (30 يوم)

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.2/howto/static-files/
STATIC_URL = 'static/'
STATICFILES_DIRS = [os.path.join(BASE_DIR, 'static')]
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

# Media files (user uploads)
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Login URLs
LOGIN_URL = 'login'
LOGIN_REDIRECT_URL = 'index'
LOGOUT_REDIRECT_URL = 'index'

# Crispy Forms
CRISPY_ALLOWED_TEMPLATE_PACKS = "bootstrap5"
CRISPY_TEMPLATE_PACK = "bootstrap5"