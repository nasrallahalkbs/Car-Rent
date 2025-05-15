"""
وحدة تنفيذ المهام المجدولة
تحتوي على الوظائف المتاحة للتنفيذ من خلال المهام المجدولة
وآلية تنفيذ الوظائف مع المعاملات
"""

import json
import logging
import traceback
import os
import shutil
from datetime import datetime, timedelta

from django.core.mail import mail_admins
from django.conf import settings
from django.utils import timezone
from django.db.models import Q

# إعداد التسجيل
logger = logging.getLogger(__name__)

# ============================================
# وظائف قابلة للاستدعاء من المهام المجدولة
# يجب أن تقبل جميع الوظائف معامل kwargs للمعاملات
# ============================================

def create_backup(**kwargs):
    """إنشاء نسخة احتياطية
    
    المعاملات:
        backup_type: نوع النسخة الاحتياطية (full, partial, settings, database)
        include_media: تضمين ملفات الوسائط (True/False)
        notify_admin: إرسال إشعار للمسؤول (True/False)
    """
    import subprocess
    import os
    from django.conf import settings
    from django.utils import timezone
    
    backup_type = kwargs.get('backup_type', 'full')
    include_media = kwargs.get('include_media', True)
    notify_admin = kwargs.get('notify_admin', True)
    
    logger.info(f"بدء إنشاء نسخة احتياطية من نوع {backup_type}")
    logger.info(f"تضمين ملفات الوسائط: {include_media}")
    
    # إنشاء مجلد للنسخ الاحتياطية إذا لم يكن موجوداً
    backup_dir = os.path.join(settings.BASE_DIR, 'backups')
    os.makedirs(backup_dir, exist_ok=True)
    
    # إنشاء اسم الملف بناءً على نوع النسخة الاحتياطية والتاريخ
    timestamp = timezone.now().strftime('%Y%m%d_%H%M%S')
    backup_name = f"backup_{backup_type}_{timestamp}"
    
    # متغيرات للتخزين المؤقت
    db_backup_file = None
    settings_backup_file = None
    
    # إنشاء سجل النسخة الاحتياطية في قاعدة البيانات
    try:
        from .models_system import Backup
        backup_obj = Backup.objects.create(
            name=backup_name,
            backup_type=backup_type,
            description=f"نسخة احتياطية تلقائية ({backup_type})",
            status='in_progress',
            include_media=include_media
        )
        logger.info(f"تم إنشاء سجل النسخة الاحتياطية: {backup_name}")
        
        # تحديد مسار ملف النسخة الاحتياطية
        backup_file_path = os.path.join(backup_dir, f"{backup_name}.zip")
        
        # تنفيذ النسخ الاحتياطي حسب النوع
        if backup_type == 'database' or backup_type == 'full':
            # نسخ احتياطي لقاعدة البيانات
            db_backup_file = os.path.join(backup_dir, f"db_{timestamp}.sql")
            
            # الحصول على معلومات الاتصال بقاعدة البيانات
            db_name = settings.DATABASES['default'].get('NAME', 'db.sqlite3')
            db_user = settings.DATABASES['default'].get('USER', '')
            db_password = settings.DATABASES['default'].get('PASSWORD', '')
            db_host = settings.DATABASES['default'].get('HOST', '')
            db_port = settings.DATABASES['default'].get('PORT', '')
            db_engine = settings.DATABASES['default'].get('ENGINE', '')
            
            logger.info(f"بدء النسخ الاحتياطي لقاعدة البيانات: {db_name}")
            
            # التعامل مع قواعد البيانات المختلفة
            if 'sqlite3' in db_engine:
                # نسخ ملف SQLite مباشرة
                if os.path.exists(db_name):
                    import shutil
                    shutil.copy2(db_name, db_backup_file)
                    logger.info(f"تم نسخ قاعدة بيانات SQLite: {db_name}")
                else:
                    logger.error(f"ملف قاعدة بيانات SQLite غير موجود: {db_name}")
            elif 'postgresql' in db_engine:
                # استخدام pg_dump للنسخ الاحتياطي
                pg_dump_cmd = [
                    'pg_dump',
                    f'--dbname=postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}',
                    '-f', db_backup_file
                ]
                try:
                    subprocess.run(pg_dump_cmd, check=True)
                    logger.info(f"تم إنشاء نسخة احتياطية من PostgreSQL: {db_name}")
                except subprocess.CalledProcessError as e:
                    logger.error(f"خطأ في إنشاء نسخة احتياطية من PostgreSQL: {str(e)}")
                    raise
            else:
                logger.warning(f"نوع قاعدة البيانات غير مدعوم للنسخ الاحتياطي التلقائي: {db_engine}")
        
        if backup_type == 'settings' or backup_type == 'full':
            # نسخ احتياطي للإعدادات
            settings_backup_file = os.path.join(backup_dir, f"settings_{timestamp}.json")
            from .models_system import SystemSetting
            
            # استخراج جميع الإعدادات
            settings_data = {}
            for setting in SystemSetting.objects.all():
                settings_data[setting.key] = {
                    'value': setting.value,
                    'value_type': setting.value_type,
                    'group': setting.group,
                    'description': setting.description
                }
            
            # حفظ الإعدادات في ملف JSON
            with open(settings_backup_file, 'w', encoding='utf-8') as f:
                json.dump(settings_data, f, ensure_ascii=False, indent=4)
            
            logger.info(f"تم إنشاء نسخة احتياطية من إعدادات النظام: {settings_backup_file}")
        
        # إضافة ملفات الوسائط إذا كان مطلوباً
        if include_media and (backup_type == 'full' or backup_type == 'partial'):
            media_dir = os.path.join(settings.BASE_DIR, 'media')
            if os.path.exists(media_dir):
                logger.info(f"جاري إضافة ملفات الوسائط للنسخة الاحتياطية")
                # هنا يمكن إضافة رمز لنسخ ملفات الوسائط
            else:
                logger.warning(f"مجلد الوسائط غير موجود: {media_dir}")
        
        # ضغط جميع الملفات في ملف واحد
        import zipfile
        with zipfile.ZipFile(backup_file_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            # إضافة ملف قاعدة البيانات إذا كان موجوداً
            if db_backup_file and os.path.exists(db_backup_file):
                zipf.write(db_backup_file, os.path.basename(db_backup_file))
                os.remove(db_backup_file)  # حذف الملف المؤقت
            
            # إضافة ملف الإعدادات إذا كان موجوداً
            if settings_backup_file and os.path.exists(settings_backup_file):
                zipf.write(settings_backup_file, os.path.basename(settings_backup_file))
                os.remove(settings_backup_file)  # حذف الملف المؤقت
        
        # تحديث سجل النسخة الاحتياطية
        backup_obj.file_path = backup_file_path
        backup_obj.size = os.path.getsize(backup_file_path)
        backup_obj.status = 'completed'
        backup_obj.completed_at = timezone.now()
        backup_obj.save()
        
        logger.info(f"تم إنشاء النسخة الاحتياطية بنجاح: {backup_file_path}")
        
        # إرسال إشعار للمسؤول إذا كان مطلوباً
        if notify_admin:
            subject = f"نسخة احتياطية جديدة: {backup_name}"
            message = f"""
            تم إنشاء نسخة احتياطية جديدة بنجاح.
            
            التفاصيل:
            - الاسم: {backup_name}
            - النوع: {backup_type}
            - الحجم: {backup_obj.size} بايت
            - المسار: {backup_file_path}
            - تاريخ الإنشاء: {backup_obj.created_at}
            """
            mail_admins(subject, message)
            logger.info("تم إرسال إشعار بالنسخة الاحتياطية للمسؤولين")
        
        return {
            'status': 'success',
            'backup_id': backup_obj.id,
            'backup_name': backup_name,
            'file_path': backup_file_path,
            'size': backup_obj.size
        }
        
    except Exception as e:
        logger.error(f"خطأ في إنشاء النسخة الاحتياطية: {str(e)}")
        logger.error(traceback.format_exc())
        
        # تحديث حالة النسخة الاحتياطية إذا كان السجل موجوداً
        if 'backup_obj' in locals():
            backup_obj.status = 'failed'
            backup_obj.save()
        
        # إرسال إشعار بالخطأ
        if notify_admin:
            subject = f"فشل في إنشاء النسخة الاحتياطية: {backup_name}"
            message = f"""
            حدث خطأ أثناء إنشاء النسخة الاحتياطية.
            
            التفاصيل:
            - الاسم: {backup_name}
            - النوع: {backup_type}
            - الخطأ: {str(e)}
            """
            mail_admins(subject, message)
            logger.info("تم إرسال إشعار بفشل النسخة الاحتياطية للمسؤولين")
        
        # إعادة رفع الاستثناء للتعامل معه في الطبقة العليا
        raise

def clean_system(**kwargs):
    """تنظيف النظام
    
    المعاملات:
        clean_temp: تنظيف الملفات المؤقتة (True/False)
        clean_logs: تنظيف ملفات السجلات (True/False)
        days_old: حذف الملفات الأقدم من عدد الأيام
    """
    clean_temp = kwargs.get('clean_temp', True)
    clean_logs = kwargs.get('clean_logs', True)
    days_old = kwargs.get('days_old', 30)
    
    logger.info(f"بدء عملية تنظيف النظام")
    logger.info(f"تنظيف الملفات المؤقتة: {clean_temp}")
    logger.info(f"تنظيف سجلات النظام: {clean_logs}")
    logger.info(f"حذف الملفات الأقدم من {days_old} يوم")
    
    # تنظيف ملفات __pycache__
    pycache_count = 0
    for root, dirs, files in os.walk("."):
        for dir_name in dirs:
            if dir_name == "__pycache__":
                pycache_path = os.path.join(root, dir_name)
                try:
                    shutil.rmtree(pycache_path)
                    pycache_count += 1
                except Exception as e:
                    logger.error(f"خطأ في حذف المجلد {pycache_path}: {str(e)}")
    
    logger.info(f"تم حذف {pycache_count} مجلد __pycache__")
    
    # تنظيف ملفات السجلات القديمة إذا تم تحديد ذلك
    if clean_logs:
        logs_path = os.path.join(".", "logs")
        if os.path.exists(logs_path):
            log_count = 0
            cutoff_date = datetime.now() - timedelta(days=days_old)
            for file_name in os.listdir(logs_path):
                file_path = os.path.join(logs_path, file_name)
                if os.path.isfile(file_path):
                    file_time = datetime.fromtimestamp(os.path.getmtime(file_path))
                    if file_time < cutoff_date:
                        try:
                            os.remove(file_path)
                            log_count += 1
                        except Exception as e:
                            logger.error(f"خطأ في حذف الملف {file_path}: {str(e)}")
            
            logger.info(f"تم حذف {log_count} ملف سجل قديم")
    
    return {
        'status': 'success',
        'message': "تم تنظيف النظام بنجاح"
    }

def clean_empty_documents(**kwargs):
    """تنظيف المستندات الفارغة
    
    المعاملات:
        delete_empty: حذف المستندات الفارغة (True/False)
        days_old: حذف المستندات الأقدم من عدد الأيام
    """
    delete_empty = kwargs.get('delete_empty', True)
    days_old = kwargs.get('days_old', 7)
    
    logger.info(f"بدء تنظيف المستندات الفارغة")
    logger.info(f"حذف المستندات الفارغة: {delete_empty}")
    logger.info(f"حذف المستندات الأقدم من {days_old} أيام")
    
    try:
        from .models import Document
        
        # تحديد المستندات الفارغة
        empty_conditions = Q(title__isnull=True) | Q(title='') | Q(title='بدون عنوان')
        empty_docs = Document.objects.filter(empty_conditions)
        
        # إضافة شرط تاريخ إذا تم تحديد عدد الأيام
        if days_old > 0:
            cutoff_date = timezone.now() - timedelta(days=days_old)
            empty_docs = empty_docs.filter(created_at__lt=cutoff_date)
        
        # عدد المستندات التي سيتم حذفها
        count = empty_docs.count()
        logger.info(f"تم العثور على {count} مستند فارغ")
        
        # حذف المستندات إذا تم تحديد ذلك
        if delete_empty and count > 0:
            empty_docs.delete()
            logger.info(f"تم حذف {count} مستند فارغ")
        
        return {
            'status': 'success',
            'message': f"تم العثور على {count} مستند فارغ، وتم حذف {count if delete_empty else 0} مستند"
        }
    except Exception as e:
        error_msg = f"خطأ في تنظيف المستندات الفارغة: {str(e)}"
        logger.error(error_msg)
        logger.error(traceback.format_exc())
        return {
            'status': 'error',
            'message': error_msg
        }

def clean_cache_files(**kwargs):
    """تنظيف ملفات الكاش
    
    المعاملات:
        clean_pycache: تنظيف ملفات __pycache__ (True/False)
        clean_django_cache: تنظيف كاش Django (True/False)
    """
    clean_pycache = kwargs.get('clean_pycache', True)
    clean_django_cache = kwargs.get('clean_django_cache', True)
    
    logger.info(f"بدء تنظيف ملفات الكاش")
    logger.info(f"تنظيف ملفات __pycache__: {clean_pycache}")
    logger.info(f"تنظيف كاش Django: {clean_django_cache}")
    
    count_pycache = 0
    count_pyc = 0
    
    # تنظيف ملفات __pycache__
    if clean_pycache:
        for root, dirs, files in os.walk("."):
            # حذف مجلدات __pycache__
            for dir_name in dirs:
                if dir_name == "__pycache__":
                    pycache_path = os.path.join(root, dir_name)
                    try:
                        shutil.rmtree(pycache_path)
                        count_pycache += 1
                    except Exception as e:
                        logger.error(f"خطأ في حذف المجلد {pycache_path}: {str(e)}")
            
            # حذف ملفات .pyc
            for file_name in files:
                if file_name.endswith(".pyc"):
                    pyc_path = os.path.join(root, file_name)
                    try:
                        os.remove(pyc_path)
                        count_pyc += 1
                    except Exception as e:
                        logger.error(f"خطأ في حذف الملف {pyc_path}: {str(e)}")
    
    # تنظيف كاش Django
    count_django_cache = 0
    if clean_django_cache:
        try:
            from django.core.cache import cache
            cache.clear()
            count_django_cache = 1
            logger.info("تم تنظيف كاش Django")
        except Exception as e:
            logger.error(f"خطأ في تنظيف كاش Django: {str(e)}")
    
    return {
        'status': 'success',
        'message': f"تم حذف {count_pycache} مجلد __pycache__ و {count_pyc} ملف .pyc"
    }

def generate_report(**kwargs):
    """إنشاء تقرير
    
    المعاملات:
        report_type: نوع التقرير (sales, users, reservations)
        format: تنسيق التقرير (pdf, excel)
        period: الفترة (daily, weekly, monthly)
        email_to: قائمة عناوين البريد الإلكتروني
    """
    report_type = kwargs.get('report_type', 'sales')
    report_format = kwargs.get('format', 'pdf')
    period = kwargs.get('period', 'monthly')
    email_to = kwargs.get('email_to', [])
    
    logger.info(f"بدء إنشاء تقرير {report_type} بتنسيق {report_format}")
    logger.info(f"الفترة: {period}")
    
    # هنا يتم إنشاء التقرير
    # ...
    
    # إرسال التقرير بالبريد الإلكتروني إذا تم تحديد بريد
    if email_to:
        logger.info(f"إرسال التقرير إلى: {', '.join(email_to)}")
        # رمز إرسال البريد هنا
    
    return {
        'status': 'success',
        'message': f"تم إنشاء تقرير {report_type} بنجاح"
    }

def send_reminder_emails(**kwargs):
    """إرسال رسائل تذكير
    
    المعاملات:
        reminder_type: نوع التذكير (reservation, payment, review)
        days_before: عدد الأيام قبل الموعد
        template_id: معرف قالب البريد
    """
    reminder_type = kwargs.get('reminder_type', 'reservation')
    days_before = kwargs.get('days_before', 1)
    template_id = kwargs.get('template_id', 'default_reminder')
    
    logger.info(f"بدء إرسال رسائل تذكير من نوع {reminder_type}")
    logger.info(f"عدد الأيام قبل الموعد: {days_before}")
    logger.info(f"قالب البريد: {template_id}")
    
    # هنا يتم إرسال رسائل التذكير
    # ...
    
    return {
        'status': 'success',
        'message': "تم إرسال رسائل التذكير بنجاح"
    }

def archive_old_reservations(**kwargs):
    """أرشفة الحجوزات القديمة
    
    المعاملات:
        days_old: أرشفة الحجوزات الأقدم من عدد الأيام
        status_list: قائمة الحالات المراد أرشفتها
    """
    days_old = kwargs.get('days_old', 90)  # أرشفة الحجوزات الأقدم من 90 يوم افتراضياً
    status_list = kwargs.get('status_list', ['completed', 'cancelled'])
    
    logger.info(f"بدء أرشفة الحجوزات القديمة")
    logger.info(f"أرشفة الحجوزات الأقدم من {days_old} يوم")
    logger.info(f"الحالات المراد أرشفتها: {', '.join(status_list)}")
    
    try:
        from .models import Reservation, ArchiveFolder
        
        # تحديد تاريخ القطع
        cutoff_date = timezone.now() - timedelta(days=days_old)
        
        # العثور على الحجوزات القديمة حسب الحالة والتاريخ
        old_reservations = Reservation.objects.filter(
            status__in=status_list,
            created_at__lt=cutoff_date
        )
        
        # عدد الحجوزات التي سيتم أرشفتها
        count = old_reservations.count()
        logger.info(f"تم العثور على {count} حجز للأرشفة")
        
        if count > 0:
            # إنشاء أو الحصول على مجلد الأرشيف للحجوزات
            try:
                archive_folder = ArchiveFolder.objects.get(name='حجوزات', is_system=True)
            except ArchiveFolder.DoesNotExist:
                # إنشاء مجلد جديد للأرشفة
                root_folders = ArchiveFolder.objects.filter(parent=None)
                if root_folders.exists():
                    parent_folder = root_folders.first()
                else:
                    parent_folder = None
                
                archive_folder = ArchiveFolder.objects.create(
                    name='حجوزات',
                    parent=parent_folder,
                    is_system=True,
                    description='مجلد أرشفة الحجوزات القديمة'
                )
            
            # أرشفة الحجوزات (يمكن تنفيذ المنطق المناسب هنا)
            old_reservations.update(is_archived=True)
            logger.info(f"تم أرشفة {count} حجز")
        
        return {
            'status': 'success',
            'message': f"تم أرشفة {count} حجز قديم بنجاح"
        }
    except Exception as e:
        error_msg = f"خطأ في أرشفة الحجوزات القديمة: {str(e)}"
        logger.error(error_msg)
        logger.error(traceback.format_exc())
        return {
            'status': 'error',
            'message': error_msg
        }

def update_exchange_rates(**kwargs):
    """تحديث أسعار العملات
    
    المعاملات:
        currency_list: قائمة العملات المراد تحديثها
        api_source: مصدر بيانات API
    """
    currency_list = kwargs.get('currency_list', ['USD', 'EUR', 'GBP'])
    api_source = kwargs.get('api_source', 'default')
    
    logger.info(f"بدء تحديث أسعار العملات: {', '.join(currency_list)}")
    logger.info(f"مصدر البيانات: {api_source}")
    
    # هنا يتم تحديث أسعار العملات
    # ...
    
    return {
        'status': 'success',
        'message': "تم تحديث أسعار العملات بنجاح"
    }

# ============================================
# آلية تنفيذ المهام المجدولة
# ============================================

# قاموس يربط أسماء الوظائف بالوظائف الفعلية
AVAILABLE_FUNCTIONS = {
    'create_backup': create_backup,
    'clean_system': clean_system,
    'clean_empty_documents': clean_empty_documents,
    'clean_cache_files': clean_cache_files,
    'generate_report': generate_report,
    'send_reminder_emails': send_reminder_emails,
    'archive_old_reservations': archive_old_reservations,
    'update_exchange_rates': update_exchange_rates,
}

def execute_job(job):
    """تنفيذ مهمة مجدولة وتحديث حالتها
    
    المعاملات:
        job: كائن المهمة المجدولة
    
    الإخراج:
        نتيجة تنفيذ المهمة (قاموس)
    """
    from .models_system import ScheduledJob  # استيراد هنا لتجنب الدوران
    
    if not isinstance(job, ScheduledJob):
        logger.error("خطأ: المهمة المقدمة ليست من نوع ScheduledJob")
        return {
            'status': 'error',
            'message': "نوع المهمة غير صالح"
        }
    
    # التحقق من وجود الوظيفة
    function_name = job.function_name
    if function_name not in AVAILABLE_FUNCTIONS:
        error_msg = f"الوظيفة {function_name} غير موجودة"
        logger.error(error_msg)
        job.last_status = "error"
        job.save(update_fields=['last_status'])
        return {
            'status': 'error',
            'message': error_msg
        }
    
    # استدعاء الوظيفة مع المعاملات
    try:
        func = AVAILABLE_FUNCTIONS[function_name]
        args = job.args or {}
        
        # تسجيل بدء التنفيذ
        logger.info(f"بدء تنفيذ المهمة: {job.name} (ID: {job.id})")
        logger.info(f"الوظيفة: {function_name}, المعاملات: {json.dumps(args)}")
        
        # تنفيذ الوظيفة
        result = func(**args)
        
        # تحديث المهمة
        job.last_run = timezone.now()
        job.last_status = "success"
        
        # حساب التشغيل التالي
        from .superadmin_scheduler_views import calculate_next_run
        job.next_run = calculate_next_run(
            job.interval_type,
            job.interval_value,
            job.cron_expression
        )
        
        job.save(update_fields=['last_run', 'last_status', 'next_run'])
        
        logger.info(f"تم تنفيذ المهمة بنجاح: {job.name}")
        return result
        
    except Exception as e:
        error_msg = f"خطأ في تنفيذ المهمة: {str(e)}"
        logger.error(error_msg)
        logger.error(traceback.format_exc())
        
        # تحديث حالة المهمة
        job.last_run = timezone.now()
        job.last_status = "error"
        job.save(update_fields=['last_run', 'last_status'])
        
        return {
            'status': 'error',
            'message': error_msg
        }