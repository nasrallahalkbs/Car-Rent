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

# CSRF trusted origins
# Include both HTTP and HTTPS variations of the domain
CSRF_TRUSTED_ORIGINS = [
    'https://*.replit.app',
    'https://*.replit.dev',
    'https://*.janeway.replit.dev',
    f'https://{REPLIT_SLUG}-{REPLIT_OWNER}.repl.co',
    f'https://{REPLIT_ID}.id.repl.co',
]

# Extract the hostname from environment
REPLIT_HOST = os.environ.get('HTTP_HOST', '')
if REPLIT_HOST:
    CSRF_TRUSTED_ORIGINS.append(f'https://{REPLIT_HOST}')
    
# Add explicit support for the specific domain in the error message
CSRF_TRUSTED_ORIGINS.append('https://372fe000-ff64-4ad8-84f9-611ea2a8e995-00-1c83kgq6nqqvn.janeway.replit.dev')

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
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# Additional CSRF settings for Replit environment
CSRF_COOKIE_SECURE = False  # Set to False for development
CSRF_COOKIE_SAMESITE = None  # Changed from 'None' to None
SESSION_COOKIE_SECURE = False  # Set to False for development
SESSION_COOKIE_SAMESITE = None  # Changed from 'None' to None
CSRF_USE_SESSIONS = True  # Store CSRF token in the session instead of cookie
CSRF_FAILURE_VIEW = 'django.views.csrf.csrf_failure'

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
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'rental.context_processors.cart_count',
                'rental.context_processors.dark_mode',
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
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

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