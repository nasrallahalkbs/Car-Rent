"""
أدوات ودوال مساعدة لتشخيص وإصلاح مشاكل النظام
"""

import os
import tempfile
from django.conf import settings
from django.db import connection

def fix_disk_space():
    """محاولة تحرير مساحة على القرص بإزالة الملفات المؤقتة"""
    try:
        # تنظيف مجلدات __pycache__
        for root, dirs, files in os.walk(settings.BASE_DIR):
            if '__pycache__' in dirs:
                pycache_path = os.path.join(root, '__pycache__')
                try:
                    for f in os.listdir(pycache_path):
                        os.remove(os.path.join(pycache_path, f))
                except:
                    pass

        # تنظيف الملفات المؤقتة في المجلد المؤقت
        temp_dir = tempfile.gettempdir()
        try:
            for f in os.listdir(temp_dir):
                try:
                    file_path = os.path.join(temp_dir, f)
                    if os.path.isfile(file_path) and os.access(file_path, os.W_OK):
                        os.remove(file_path)
                except:
                    pass
        except:
            pass

        return True
    except Exception as e:
        print(f"خطأ في fix_disk_space: {e}")
        return False

def fix_media_permissions():
    """تصحيح أذونات مجلد الوسائط"""
    try:
        if os.path.exists(settings.MEDIA_ROOT):
            # محاولة تغيير الأذونات إلى 0o755 (rwxr-xr-x)
            os.chmod(settings.MEDIA_ROOT, 0o755)
            return True
        return False
    except Exception as e:
        print(f"خطأ في fix_media_permissions: {e}")
        return False

def fix_project_permissions():
    """تصحيح أذونات مجلد المشروع"""
    try:
        if os.path.exists(settings.BASE_DIR):
            # محاولة تغيير الأذونات إلى 0o755 (rwxr-xr-x)
            os.chmod(settings.BASE_DIR, 0o755)
            return True
        return False
    except Exception as e:
        print(f"خطأ في fix_project_permissions: {e}")
        return False

def fix_db_permissions():
    """تصحيح أذونات ملف قاعدة البيانات"""
    try:
        db_engine = settings.DATABASES['default']['ENGINE']
        if 'sqlite3' in db_engine:
            db_file = settings.DATABASES['default']['NAME']
            if os.path.exists(db_file):
                # محاولة تغيير الأذونات إلى 0o644 (rw-r--r--)
                os.chmod(db_file, 0o644)
                return True
        return False
    except Exception as e:
        print(f"خطأ في fix_db_permissions: {e}")
        return False

def create_media_directory():
    """إنشاء مجلد الوسائط إذا لم يكن موجودًا"""
    try:
        if not os.path.exists(settings.MEDIA_ROOT):
            os.makedirs(settings.MEDIA_ROOT, exist_ok=True)
            return True
        return False
    except Exception as e:
        print(f"خطأ في create_media_directory: {e}")
        return False

def check_db_connection():
    """التحقق من اتصال قاعدة البيانات"""
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            return cursor.fetchone()[0] == 1
    except Exception as e:
        print(f"خطأ في check_db_connection: {e}")
        return False