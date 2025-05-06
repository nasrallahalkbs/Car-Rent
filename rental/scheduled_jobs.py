"""
ملف الوظائف القابلة للتنفيذ من خلال نظام المهام المجدولة
هذا الملف يحتوي على الوظائف الفعلية التي يمكن للنظام استدعاؤها
"""

import os
import json
import logging
import tempfile
import zipfile
import shutil
import datetime
from pathlib import Path

from django.conf import settings
from django.core.mail import send_mail, mail_admins
from django.utils import timezone
from django.db.models import Count, Sum, Avg
from django.db import connection
from django.contrib.auth import get_user_model

from .models import Reservation, Payment, Car, ArchiveFolder, Document, Review
from .models_system import SystemBackup

# إعداد التسجيل
logger = logging.getLogger(__name__)

# ===================================
# وظائف النسخ الاحتياطي
# ===================================

def create_database_backup(**kwargs):
    """إنشاء نسخة احتياطية من قاعدة البيانات
    
    المعاملات:
        include_media: تضمين ملفات الوسائط (True/False)
        backup_name: اسم النسخة الاحتياطية (اختياري)
        notify_admin: إرسال إشعار للمسؤول (True/False)
    """
    include_media = kwargs.get('include_media', True)
    backup_name = kwargs.get('backup_name', f"backup_{timezone.now().strftime('%Y%m%d_%H%M%S')}")
    notify_admin = kwargs.get('notify_admin', True)
    
    logger.info(f"بدء إنشاء نسخة احتياطية من قاعدة البيانات: {backup_name}")
    logger.info(f"تضمين ملفات الوسائط: {include_media}")
    
    try:
        # إنشاء مجلد مؤقت
        temp_dir = tempfile.mkdtemp()
        backup_path = os.path.join(temp_dir, f"{backup_name}.zip")
        
        # إنشاء ملف SQL من قاعدة البيانات
        sql_path = os.path.join(temp_dir, "database.sql")
        
        with connection.cursor() as cursor:
            with open(sql_path, 'w') as f:
                # استخراج جداول قاعدة البيانات
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
                tables = cursor.fetchall()
                
                # كتابة نسخة لكل جدول
                for table in tables:
                    table_name = table[0]
                    if table_name != 'sqlite_sequence':
                        f.write(f"-- Table: {table_name}\n")
                        cursor.execute(f"SELECT sql FROM sqlite_master WHERE name='{table_name}';")
                        create_statement = cursor.fetchone()[0]
                        f.write(f"{create_statement};\n")
                        
                        cursor.execute(f"SELECT * FROM {table_name};")
                        rows = cursor.fetchall()
                        
                        if rows:
                            for row in rows:
                                values = ', '.join([f"'{str(v).replace(\"'\", \"''\")}'" if v is not None else 'NULL' for v in row])
                                f.write(f"INSERT INTO {table_name} VALUES ({values});\n")
        
        # إنشاء ملف ZIP
        with zipfile.ZipFile(backup_path, 'w') as zipf:
            # إضافة ملف SQL
            zipf.write(sql_path, "database.sql")
            
            # إضافة ملفات الوسائط إذا تم طلب ذلك
            if include_media and os.path.exists(settings.MEDIA_ROOT):
                for root, dirs, files in os.walk(settings.MEDIA_ROOT):
                    for file in files:
                        file_path = os.path.join(root, file)
                        arcname = os.path.relpath(file_path, start=settings.BASE_DIR)
                        zipf.write(file_path, arcname)
        
        # حفظ النسخة الاحتياطية في قاعدة البيانات
        file_size = os.path.getsize(backup_path)
        
        # نقل ملف النسخة الاحتياطية إلى مجلد دائم
        backup_dir = os.path.join(settings.BASE_DIR, 'backups')
        os.makedirs(backup_dir, exist_ok=True)
        
        final_path = os.path.join(backup_dir, f"{backup_name}.zip")
        shutil.copy2(backup_path, final_path)
        
        # إنشاء سجل النسخة الاحتياطية
        User = get_user_model()
        system_user = User.objects.filter(is_superuser=True).first()
        
        backup = SystemBackup.objects.create(
            name=backup_name,
            file_path=os.path.relpath(final_path, start=settings.BASE_DIR),
            file_size=file_size,
            status='completed',
            notes=f"تم إنشاء النسخة الاحتياطية بنجاح. حجم الملف: {file_size} بايت",
            created_by=system_user
        )
        
        # إرسال إشعار للمسؤول
        if notify_admin:
            mail_message = f"""
            تم إنشاء نسخة احتياطية بنجاح
            الاسم: {backup_name}
            الحجم: {file_size} بايت
            التاريخ: {timezone.now()}
            تضمين ملفات الوسائط: {'نعم' if include_media else 'لا'}
            """
            try:
                mail_admins("تقرير النسخ الاحتياطي التلقائي", mail_message)
            except Exception as e:
                logger.error(f"فشل في إرسال البريد: {str(e)}")
        
        # تنظيف
        shutil.rmtree(temp_dir)
        
        return {
            'status': 'success',
            'message': f"تم إنشاء نسخة احتياطية بنجاح: {backup_name}",
            'backup_id': backup.id
        }
        
    except Exception as e:
        logger.error(f"خطأ في إنشاء النسخة الاحتياطية: {str(e)}")
        # إنشاء سجل فشل النسخة الاحتياطية
        User = get_user_model()
        system_user = User.objects.filter(is_superuser=True).first()
        
        SystemBackup.objects.create(
            name=backup_name,
            file_path="",
            file_size=0,
            status='failed',
            notes=f"فشل إنشاء النسخة الاحتياطية: {str(e)}",
            created_by=system_user
        )
        
        return {
            'status': 'error',
            'message': f"فشل إنشاء النسخة الاحتياطية: {str(e)}"
        }

# ===================================
# وظائف تنظيف النظام
# ===================================

def clean_temp_files(**kwargs):
    """تنظيف الملفات المؤقتة من النظام
    
    المعاملات:
        days_old: حذف الملفات الأقدم من عدد معين من الأيام
        clean_logs: تنظيف ملفات السجلات (True/False)
        clean_sessions: تنظيف جلسات المستخدمين القديمة (True/False)
    """
    days_old = kwargs.get('days_old', 30)
    clean_logs = kwargs.get('clean_logs', True)
    clean_sessions = kwargs.get('clean_sessions', True)
    
    cutoff_date = timezone.now() - datetime.timedelta(days=days_old)
    files_removed = 0
    
    logger.info(f"بدء تنظيف الملفات المؤقتة الأقدم من {days_old} يوم")
    
    try:
        # تنظيف مجلد temp
        temp_dir = os.path.join(settings.BASE_DIR, 'temp')
        if os.path.exists(temp_dir):
            for root, dirs, files in os.walk(temp_dir):
                for file in files:
                    file_path = os.path.join(root, file)
                    file_time = datetime.datetime.fromtimestamp(os.path.getmtime(file_path))
                    file_time = timezone.make_aware(file_time)
                    
                    if file_time < cutoff_date:
                        try:
                            os.remove(file_path)
                            files_removed += 1
                        except Exception as e:
                            logger.error(f"فشل في حذف الملف {file_path}: {str(e)}")
        
        # تنظيف ملفات السجلات
        if clean_logs:
            log_dir = os.path.join(settings.BASE_DIR, 'logs')
            if os.path.exists(log_dir):
                for root, dirs, files in os.walk(log_dir):
                    for file in files:
                        if file.endswith('.log'):
                            file_path = os.path.join(root, file)
                            file_time = datetime.datetime.fromtimestamp(os.path.getmtime(file_path))
                            file_time = timezone.make_aware(file_time)
                            
                            if file_time < cutoff_date:
                                try:
                                    os.remove(file_path)
                                    files_removed += 1
                                except Exception as e:
                                    logger.error(f"فشل في حذف ملف السجل {file_path}: {str(e)}")
        
        # تنظيف جلسات المستخدمين القديمة
        if clean_sessions:
            from django.contrib.sessions.models import Session
            expired_sessions = Session.objects.filter(expire_date__lt=timezone.now())
            session_count = expired_sessions.count()
            expired_sessions.delete()
            
            logger.info(f"تم حذف {session_count} جلسة منتهية الصلاحية")
        
        logger.info(f"تم حذف {files_removed} ملف مؤقت بنجاح")
        
        return {
            'status': 'success',
            'message': f"تم تنظيف {files_removed} ملف مؤقت بنجاح",
            'files_removed': files_removed
        }
        
    except Exception as e:
        logger.error(f"خطأ في تنظيف الملفات المؤقتة: {str(e)}")
        return {
            'status': 'error',
            'message': f"فشل تنظيف الملفات المؤقتة: {str(e)}"
        }

def optimize_database(**kwargs):
    """تحسين أداء قاعدة البيانات
    
    المعاملات:
        vacuum: تنفيذ عملية VACUUM لتنظيف قاعدة البيانات (True/False)
        analyze: تنفيذ عملية ANALYZE لتحسين المؤشرات (True/False)
    """
    vacuum = kwargs.get('vacuum', True)
    analyze = kwargs.get('analyze', True)
    
    logger.info("بدء تحسين أداء قاعدة البيانات")
    
    try:
        with connection.cursor() as cursor:
            if vacuum:
                logger.info("تنفيذ عملية VACUUM...")
                cursor.execute("VACUUM;")
            
            if analyze:
                logger.info("تنفيذ عملية ANALYZE...")
                cursor.execute("ANALYZE;")
        
        return {
            'status': 'success',
            'message': "تم تحسين أداء قاعدة البيانات بنجاح",
            'vacuum': vacuum,
            'analyze': analyze
        }
        
    except Exception as e:
        logger.error(f"خطأ في تحسين أداء قاعدة البيانات: {str(e)}")
        return {
            'status': 'error',
            'message': f"فشل تحسين أداء قاعدة البيانات: {str(e)}"
        }

# ===================================
# وظائف التقارير
# ===================================

def generate_sales_report(**kwargs):
    """إنشاء تقرير المبيعات
    
    المعاملات:
        period: الفترة (daily, weekly, monthly, yearly)
        format: تنسيق التقرير (json, csv)
        email_to: عناوين البريد لإرسال التقرير إليها
    """
    period = kwargs.get('period', 'monthly')
    report_format = kwargs.get('format', 'json')
    email_to = kwargs.get('email_to', [])
    
    logger.info(f"بدء إنشاء تقرير المبيعات للفترة: {period}")
    
    try:
        # تحديد تاريخ البداية بناءً على الفترة
        now = timezone.now()
        
        if period == 'daily':
            start_date = now.replace(hour=0, minute=0, second=0, microsecond=0)
        elif period == 'weekly':
            start_date = (now - datetime.timedelta(days=now.weekday())).replace(hour=0, minute=0, second=0, microsecond=0)
        elif period == 'monthly':
            start_date = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        elif period == 'yearly':
            start_date = now.replace(month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
        else:
            start_date = now.replace(hour=0, minute=0, second=0, microsecond=0) - datetime.timedelta(days=30)
        
        # جمع بيانات المبيعات
        payments = Payment.objects.filter(created_at__gte=start_date)
        
        # إحصائيات عامة
        total_payments = payments.count()
        total_amount = payments.aggregate(Sum('amount'))['amount__sum'] or 0
        avg_amount = payments.aggregate(Avg('amount'))['amount__avg'] or 0
        
        # تصنيف المدفوعات حسب النوع
        payment_types = payments.values('payment_type').annotate(count=Count('id'), total=Sum('amount'))
        
        # تصنيف المدفوعات حسب الحالة
        payment_status = payments.values('status').annotate(count=Count('id'), total=Sum('amount'))
        
        # إعداد البيانات
        report_data = {
            'period': period,
            'start_date': start_date.isoformat(),
            'end_date': now.isoformat(),
            'total_payments': total_payments,
            'total_amount': float(total_amount),
            'avg_amount': float(avg_amount),
            'payment_types': list(payment_types),
            'payment_status': list(payment_status)
        }
        
        # تحويل البيانات إلى التنسيق المطلوب
        if report_format == 'json':
            report_content = json.dumps(report_data, indent=2, ensure_ascii=False)
        elif report_format == 'csv':
            import csv
            from io import StringIO
            
            output = StringIO()
            writer = csv.writer(output)
            
            # كتابة العناوين
            writer.writerow(['الفترة', 'تاريخ البداية', 'تاريخ النهاية', 'عدد المدفوعات', 'إجمالي المبلغ', 'متوسط المبلغ'])
            writer.writerow([period, start_date.strftime('%Y-%m-%d'), now.strftime('%Y-%m-%d'), total_payments, total_amount, avg_amount])
            
            # كتابة تفاصيل أنواع المدفوعات
            writer.writerow([])
            writer.writerow(['نوع المدفوعات', 'العدد', 'المبلغ الإجمالي'])
            for pt in payment_types:
                writer.writerow([pt['payment_type'], pt['count'], pt['total']])
            
            # كتابة تفاصيل حالات المدفوعات
            writer.writerow([])
            writer.writerow(['حالة المدفوعات', 'العدد', 'المبلغ الإجمالي'])
            for ps in payment_status:
                writer.writerow([ps['status'], ps['count'], ps['total']])
            
            report_content = output.getvalue()
        else:
            report_content = str(report_data)
        
        # حفظ التقرير في ملف
        reports_dir = os.path.join(settings.BASE_DIR, 'reports')
        os.makedirs(reports_dir, exist_ok=True)
        
        timestamp = now.strftime('%Y%m%d_%H%M%S')
        report_filename = f"sales_report_{period}_{timestamp}.{report_format}"
        report_path = os.path.join(reports_dir, report_filename)
        
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(report_content)
        
        # إرسال التقرير بالبريد الإلكتروني إذا تم تحديد بريد
        if email_to:
            subject = f"تقرير المبيعات - {period}"
            message = f"""
            مرفق تقرير المبيعات للفترة: {period}
            
            إحصائيات عامة:
            - عدد المدفوعات: {total_payments}
            - إجمالي المبلغ: {total_amount}
            - متوسط المبلغ: {avg_amount}
            
            تم إنشاء هذا التقرير تلقائياً بواسطة نظام جدولة المهام.
            """
            
            from_email = settings.DEFAULT_FROM_EMAIL
            
            for email in email_to:
                try:
                    send_mail(
                        subject,
                        message,
                        from_email,
                        [email],
                        fail_silently=False,
                        attachments=[(report_filename, report_content, 'text/plain')]
                    )
                except Exception as e:
                    logger.error(f"فشل في إرسال البريد إلى {email}: {str(e)}")
        
        return {
            'status': 'success',
            'message': f"تم إنشاء تقرير المبيعات للفترة {period} بنجاح",
            'report_path': report_path,
            'total_payments': total_payments,
            'total_amount': float(total_amount)
        }
        
    except Exception as e:
        logger.error(f"خطأ في إنشاء تقرير المبيعات: {str(e)}")
        return {
            'status': 'error',
            'message': f"فشل إنشاء تقرير المبيعات: {str(e)}"
        }

def generate_activity_report(**kwargs):
    """إنشاء تقرير نشاط المستخدمين
    
    المعاملات:
        days: عدد الأيام السابقة
        include_inactive: تضمين المستخدمين غير النشطين (True/False)
        email_to: عناوين البريد لإرسال التقرير إليها
    """
    days = kwargs.get('days', 30)
    include_inactive = kwargs.get('include_inactive', False)
    email_to = kwargs.get('email_to', [])
    
    logger.info(f"بدء إنشاء تقرير نشاط المستخدمين خلال {days} يوم")
    
    try:
        # تحديد تاريخ البداية
        start_date = timezone.now() - datetime.timedelta(days=days)
        
        # جمع بيانات المستخدمين
        User = get_user_model()
        
        if include_inactive:
            users = User.objects.all()
        else:
            users = User.objects.filter(is_active=True)
        
        # إحصائيات المستخدمين
        total_users = users.count()
        new_users = users.filter(date_joined__gte=start_date).count()
        
        # إحصائيات الحجوزات
        reservations = Reservation.objects.filter(created_at__gte=start_date)
        total_reservations = reservations.count()
        
        # إحصائيات التقييمات
        reviews = Review.objects.filter(created_at__gte=start_date)
        total_reviews = reviews.count()
        avg_rating = reviews.aggregate(Avg('rating'))['rating__avg'] or 0
        
        # إعداد البيانات
        report_data = {
            'period_days': days,
            'start_date': start_date.isoformat(),
            'end_date': timezone.now().isoformat(),
            'users': {
                'total': total_users,
                'new': new_users
            },
            'reservations': {
                'total': total_reservations
            },
            'reviews': {
                'total': total_reviews,
                'avg_rating': float(avg_rating)
            }
        }
        
        # تحويل البيانات إلى JSON
        report_content = json.dumps(report_data, indent=2, ensure_ascii=False)
        
        # حفظ التقرير في ملف
        reports_dir = os.path.join(settings.BASE_DIR, 'reports')
        os.makedirs(reports_dir, exist_ok=True)
        
        timestamp = timezone.now().strftime('%Y%m%d_%H%M%S')
        report_filename = f"activity_report_{days}days_{timestamp}.json"
        report_path = os.path.join(reports_dir, report_filename)
        
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(report_content)
        
        # إرسال التقرير بالبريد الإلكتروني إذا تم تحديد بريد
        if email_to:
            subject = f"تقرير نشاط المستخدمين - {days} يوم"
            message = f"""
            مرفق تقرير نشاط المستخدمين خلال {days} يوم الماضية
            
            إحصائيات عامة:
            - إجمالي المستخدمين: {total_users}
            - المستخدمين الجدد: {new_users}
            - عدد الحجوزات: {total_reservations}
            - عدد التقييمات: {total_reviews}
            - متوسط التقييم: {avg_rating:.2f}
            
            تم إنشاء هذا التقرير تلقائياً بواسطة نظام جدولة المهام.
            """
            
            from_email = settings.DEFAULT_FROM_EMAIL
            
            for email in email_to:
                try:
                    send_mail(
                        subject,
                        message,
                        from_email,
                        [email],
                        fail_silently=False,
                        attachments=[(report_filename, report_content, 'application/json')]
                    )
                except Exception as e:
                    logger.error(f"فشل في إرسال البريد إلى {email}: {str(e)}")
        
        return {
            'status': 'success',
            'message': f"تم إنشاء تقرير نشاط المستخدمين خلال {days} يوم بنجاح",
            'report_path': report_path,
            'total_users': total_users,
            'new_users': new_users
        }
        
    except Exception as e:
        logger.error(f"خطأ في إنشاء تقرير نشاط المستخدمين: {str(e)}")
        return {
            'status': 'error',
            'message': f"فشل إنشاء تقرير نشاط المستخدمين: {str(e)}"
        }

# ===================================
# وظائف التذكير والإشعارات
# ===================================

def send_reservation_reminders(**kwargs):
    """إرسال رسائل تذكير للحجوزات القادمة
    
    المعاملات:
        days_before: عدد الأيام قبل موعد الحجز
        send_email: إرسال تذكير بالبريد الإلكتروني (True/False)
        send_sms: إرسال تذكير برسالة SMS (True/False)
    """
    days_before = kwargs.get('days_before', 1)
    send_email = kwargs.get('send_email', True)
    send_sms = kwargs.get('send_sms', False)
    
    logger.info(f"بدء إرسال رسائل تذكير للحجوزات قبل {days_before} يوم")
    
    try:
        # تحديد تاريخ البداية والنهاية
        now = timezone.now()
        target_date = now + datetime.timedelta(days=days_before)
        start_date = target_date.replace(hour=0, minute=0, second=0, microsecond=0)
        end_date = target_date.replace(hour=23, minute=59, second=59, microsecond=999999)
        
        # استرجاع الحجوزات المؤكدة التي تبدأ في اليوم المحدد
        upcoming_reservations = Reservation.objects.filter(
            status='confirmed',
            start_date__gte=start_date,
            start_date__lte=end_date
        ).select_related('user', 'car')
        
        reminder_count = 0
        
        # إرسال تذكير لكل حجز
        for reservation in upcoming_reservations:
            user = reservation.user
            car = reservation.car
            
            # إنشاء رسالة التذكير
            subject = f"تذكير: حجز السيارة {car.make} {car.model} قادم"
            message = f"""
            مرحباً {user.first_name or user.username}،
            
            هذا تذكير بأن حجزك للسيارة {car.make} {car.model} سيبدأ في {reservation.start_date.strftime('%Y-%m-%d')}.
            
            تفاصيل الحجز:
            - رقم الحجز: {reservation.reservation_number}
            - السيارة: {car.make} {car.model} ({car.year})
            - تاريخ البداية: {reservation.start_date.strftime('%Y-%m-%d %H:%M')}
            - تاريخ النهاية: {reservation.end_date.strftime('%Y-%m-%d %H:%M')}
            - المبلغ الإجمالي: {reservation.total_amount}
            
            يرجى التواجد في الموعد المحدد لاستلام السيارة.
            
            مع أطيب التحيات،
            فريق تأجير السيارات
            """
            
            # إرسال بريد إلكتروني
            if send_email and user.email:
                try:
                    send_mail(
                        subject,
                        message,
                        settings.DEFAULT_FROM_EMAIL,
                        [user.email],
                        fail_silently=False
                    )
                    reminder_count += 1
                    logger.info(f"تم إرسال تذكير بالبريد الإلكتروني للحجز {reservation.reservation_number}")
                except Exception as e:
                    logger.error(f"فشل في إرسال تذكير بالبريد الإلكتروني للحجز {reservation.reservation_number}: {str(e)}")
            
            # إرسال رسالة SMS
            if send_sms and hasattr(user, 'phone_number') and user.phone_number:
                try:
                    # هنا يمكن إضافة رمز إرسال SMS باستخدام خدمة مثل Twilio
                    # ملاحظة: هذا مثال وليس تنفيذ فعلي
                    logger.info(f"تم إرسال تذكير برسالة SMS للحجز {reservation.reservation_number}")
                except Exception as e:
                    logger.error(f"فشل في إرسال تذكير برسالة SMS للحجز {reservation.reservation_number}: {str(e)}")
        
        return {
            'status': 'success',
            'message': f"تم إرسال {reminder_count} تذكير للحجوزات القادمة خلال {days_before} يوم",
            'reminder_count': reminder_count,
            'total_reservations': upcoming_reservations.count()
        }
        
    except Exception as e:
        logger.error(f"خطأ في إرسال رسائل التذكير: {str(e)}")
        return {
            'status': 'error',
            'message': f"فشل إرسال رسائل التذكير: {str(e)}"
        }

def archive_old_reservations(**kwargs):
    """أرشفة الحجوزات القديمة وإنشاء مستندات لها
    
    المعاملات:
        days_old: أرشفة الحجوزات الأقدم من عدد معين من الأيام
        create_documents: إنشاء مستندات للحجوزات المؤرشفة (True/False)
        archive_folder_id: معرف مجلد الأرشفة (اختياري)
    """
    days_old = kwargs.get('days_old', 90)
    create_documents = kwargs.get('create_documents', True)
    archive_folder_id = kwargs.get('archive_folder_id', None)
    
    logger.info(f"بدء أرشفة الحجوزات الأقدم من {days_old} يوم")
    
    try:
        # تحديد تاريخ القطع
        cutoff_date = timezone.now() - datetime.timedelta(days=days_old)
        
        # استرجاع الحجوزات القديمة والمكتملة
        old_reservations = Reservation.objects.filter(
            end_date__lt=cutoff_date,
            status__in=['completed', 'closed']
        ).select_related('user', 'car')
        
        archived_count = 0
        documents_created = 0
        
        # الحصول على مجلد الأرشيف
        if archive_folder_id:
            try:
                archive_folder = ArchiveFolder.objects.get(id=archive_folder_id)
            except ArchiveFolder.DoesNotExist:
                archive_folder = None
        else:
            # البحث عن مجلد "حجوزات" في النظام أو إنشاء واحد جديد
            archive_folder = ArchiveFolder.objects.filter(name='حجوزات').first()
            
            if not archive_folder:
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
        
        # أرشفة كل حجز
        for reservation in old_reservations:
            user = reservation.user
            car = reservation.car
            
            # تحديث حالة الحجز إلى "archived"
            if reservation.status != 'archived':
                reservation.status = 'archived'
                reservation.save(update_fields=['status'])
                archived_count += 1
            
            # إنشاء مستند للحجز إذا تم طلب ذلك
            if create_documents and archive_folder:
                # التحقق من وجود مستند للحجز
                existing_document = Document.objects.filter(
                    name__startswith=f"حجز {reservation.reservation_number}",
                    folder=archive_folder
                ).exists()
                
                if not existing_document:
                    # إنشاء محتوى المستند
                    document_content = f"""
                    معلومات الحجز:
                    -------------
                    رقم الحجز: {reservation.reservation_number}
                    العميل: {user.get_full_name() or user.username}
                    السيارة: {car.make} {car.model} ({car.year})
                    تاريخ البداية: {reservation.start_date.strftime('%Y-%m-%d %H:%M')}
                    تاريخ النهاية: {reservation.end_date.strftime('%Y-%m-%d %H:%M')}
                    المبلغ الإجمالي: {reservation.total_amount}
                    الحالة: {reservation.get_status_display()}
                    تاريخ الإنشاء: {reservation.created_at.strftime('%Y-%m-%d %H:%M')}
                    تاريخ التحديث: {reservation.updated_at.strftime('%Y-%m-%d %H:%M')}
                    
                    معلومات العميل:
                    -------------
                    الاسم: {user.get_full_name() or user.username}
                    البريد الإلكتروني: {user.email}
                    
                    معلومات السيارة:
                    -------------
                    الشركة المصنعة: {car.make}
                    الموديل: {car.model}
                    السنة: {car.year}
                    رقم اللوحة: {car.license_plate}
                    """
                    
                    # حفظ المستند
                    doc_filename = f"حجز_{reservation.reservation_number}_{reservation.start_date.strftime('%Y%m%d')}.txt"
                    
                    # إنشاء ملف مؤقت
                    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.txt')
                    temp_file.write(document_content.encode('utf-8'))
                    temp_file.close()
                    
                    # إنشاء المستند في قاعدة البيانات
                    with open(temp_file.name, 'rb') as f:
                        document = Document(
                            name=f"حجز {reservation.reservation_number}",
                            folder=archive_folder,
                            file_type='text/plain',
                            description=f"مستند أرشفة للحجز {reservation.reservation_number}",
                            is_system=True
                        )
                        document.file.save(doc_filename, f)
                        documents_created += 1
                    
                    # حذف الملف المؤقت
                    os.unlink(temp_file.name)
        
        return {
            'status': 'success',
            'message': f"تم أرشفة {archived_count} حجز وإنشاء {documents_created} مستند",
            'archived_count': archived_count,
            'documents_created': documents_created
        }
        
    except Exception as e:
        logger.error(f"خطأ في أرشفة الحجوزات القديمة: {str(e)}")
        return {
            'status': 'error',
            'message': f"فشل أرشفة الحجوزات القديمة: {str(e)}"
        }

# ===================================
# قائمة الوظائف المتاحة
# ===================================

AVAILABLE_FUNCTIONS = {
    # وظائف النسخ الاحتياطي
    'create_database_backup': create_database_backup,
    
    # وظائف تنظيف النظام
    'clean_temp_files': clean_temp_files,
    'optimize_database': optimize_database,
    
    # وظائف التقارير
    'generate_sales_report': generate_sales_report,
    'generate_activity_report': generate_activity_report,
    
    # وظائف التذكير والإشعارات
    'send_reservation_reminders': send_reservation_reminders,
    'archive_old_reservations': archive_old_reservations,
}