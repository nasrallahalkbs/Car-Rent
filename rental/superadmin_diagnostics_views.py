import os
import sys
import json
import psutil
import datetime
import traceback
import subprocess
import sqlite3
import django
import tempfile
import time

from django.http import HttpResponse, JsonResponse
from django.utils import timezone
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.utils.translation import gettext as _
from django.db import connection
from django.conf import settings
from django.apps import apps

from .models_system import SystemIssue
from .models_superadmin import AdminUser
from .superadmin_diagnostics_utils import (
    fix_disk_space, fix_media_permissions, fix_project_permissions,
    fix_db_permissions, create_media_directory, check_db_connection
)

# الدالة المساعدة للتحقق من صلاحيات المسؤول الأعلى
def is_superadmin(user):
    try:
        admin_user = AdminUser.objects.get(user=user)
        return admin_user.is_superadmin
    except AdminUser.DoesNotExist:
        return False

@login_required
def system_diagnostics(request):
    """صفحة أدوات تشخيص وإصلاح النظام"""
    if not is_superadmin(request.user):
        messages.error(request, _('ليس لديك صلاحية الوصول إلى أدوات تشخيص النظام'))
        return redirect('superadmin_dashboard')
    
    # إحصائيات النظام
    system_stats = get_system_stats()
    
    # الحصول على مشاكل النظام
    system_issues = SystemIssue.objects.all().order_by('-severity', '-detected_at')
    
    # إحصائيات المشاكل
    issue_stats = {
        'total': system_issues.count(),
        'critical': system_issues.filter(severity='critical').count(),
        'high': system_issues.filter(severity='high').count(),
        'medium': system_issues.filter(severity='medium').count(),
        'low': system_issues.filter(severity='low').count(),
        'new': system_issues.filter(status='new').count(),
        'in_progress': system_issues.filter(status='in_progress').count(),
        'fixed': system_issues.filter(status='fixed').count(),
    }
    
    # إعداد السياق
    context = {
        'system_stats': system_stats,
        'system_issues': system_issues,
        'issue_stats': issue_stats,
        'diagnostic_tools': get_diagnostic_tools(),
        'title': _('أدوات تشخيص وإصلاح النظام'),
    }
    
    return render(request, 'superadmin/diagnostics/index.html', context)

def get_system_stats():
    """الحصول على إحصائيات النظام الحقيقية بشكل مؤكد"""
    stats = {}
    
    # معلومات حول البيئة
    try:
        # جلب معلومات نظام التشغيل الحقيقية
        stats['os_info'] = f"{os.name.upper()} {sys.platform}"
        # إضافة الإصدار إذا كان متاحاً
        if hasattr(os, 'uname'):
            stats['os_info'] += f" {os.uname().release}"
        
        # جلب إصدار بايثون وجانجو الحقيقي
        stats['python_version'] = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
        stats['django_version'] = django.__version__
        
        # مسارات حقيقية للنظام
        stats['app_path'] = str(settings.BASE_DIR)
        stats['media_path'] = str(settings.MEDIA_ROOT)
        
        # إضافة معلومات عن البيئة للتأكيد على أنها حقيقية
        stats['process_id'] = os.getpid()
        stats['process_username'] = os.getlogin() if hasattr(os, 'getlogin') else 'unknown'
        stats['python_executable'] = sys.executable
    except Exception as e:
        print(f"خطأ في جلب معلومات البيئة: {e}")
        stats['os_info'] = f"{os.name.upper()} {sys.platform}"
    
    # إحصائيات نظام التشغيل - CPU (بقياس فعلي)
    try:
        # قياس استخدام المعالج لمدة نصف ثانية للحصول على نتيجة أكثر دقة
        cpu_usage = psutil.cpu_percent(interval=0.5)
        stats['cpu_usage'] = cpu_usage
        
        # إضافة معلومات حول عدد نوى المعالج
        stats['cpu_cores'] = psutil.cpu_count(logical=False) or 1
        stats['cpu_threads'] = psutil.cpu_count(logical=True) or 1
        
        # قياس استخدام المعالج الحالي للعملية
        stats['process_cpu'] = psutil.Process(os.getpid()).cpu_percent(interval=0.1)
    except Exception as e:
        print(f"خطأ في جلب معلومات المعالج: {e}")
        stats['cpu_usage'] = 0
        stats['cpu_cores'] = 1
        stats['cpu_threads'] = 1
    
    # إحصائيات نظام التشغيل - الذاكرة (بيانات حقيقية)
    try:
        memory = psutil.virtual_memory()
        stats['memory_usage'] = memory.percent
        stats['memory_total'] = f"{memory.total / (1024**3):.2f} GB"
        stats['memory_available'] = f"{memory.available / (1024**3):.2f} GB"
        
        # قياس استخدام الذاكرة للعملية الحالية
        process_memory = psutil.Process(os.getpid()).memory_info()
        stats['process_memory_mb'] = f"{process_memory.rss / (1024**2):.2f} MB"
    except Exception as e:
        print(f"خطأ في جلب معلومات الذاكرة: {e}")
        stats['memory_usage'] = 0
        stats['memory_total'] = _('غير متاح')
        stats['memory_available'] = _('غير متاح')
    
    # إحصائيات نظام التشغيل - القرص (بيانات فعلية)
    try:
        disk = psutil.disk_usage('/')
        stats['disk_usage'] = disk.percent
        stats['disk_total'] = f"{disk.total / (1024**3):.2f} GB"
        stats['disk_free'] = f"{disk.free / (1024**3):.2f} GB"
        
        # إضافة معلومات عن نظام الملفات
        if hasattr(os, 'statvfs'):
            fs_stats = os.statvfs('/')
            stats['fs_type'] = 'Unix filesystem'
            stats['fs_block_size'] = fs_stats.f_bsize
    except Exception as e:
        print(f"خطأ في جلب معلومات القرص: {e}")
        stats['disk_usage'] = 0
        stats['disk_total'] = _('غير متاح')
        stats['disk_free'] = _('غير متاح')
    
    # إحصائيات قاعدة البيانات (بيانات فعلية)
    try:
        stats['db_size'] = get_database_size()
        db_engine = settings.DATABASES['default']['ENGINE']
        stats['db_type'] = db_engine.split('.')[-1]
        stats['db_name'] = settings.DATABASES['default']['NAME']
        stats['db_connections'] = connection.settings_dict.get('CONN_MAX_AGE', _('غير محدد'))
        
        # اختبار الاتصال بقاعدة البيانات
        db_connected = check_db_connection()
        stats['db_connected'] = _('متصل') if db_connected else _('غير متصل')
    except Exception as e:
        print(f"خطأ في جلب معلومات قاعدة البيانات: {e}")
        stats['db_size'] = _('غير متاح')
        stats['db_type'] = _('غير معروف')
        stats['db_connections'] = _('غير متاح')
    
    # وقت تشغيل النظام (بيانات حقيقية)
    try:
        stats['uptime'] = get_system_uptime()
        # إضافة معلومات مؤكدة عن وقت التشغيل
        stats['server_start_time'] = datetime.datetime.fromtimestamp(
            psutil.Process(os.getpid()).create_time()
        ).strftime('%Y-%m-%d %H:%M:%S')
    except Exception as e:
        print(f"خطأ في جلب وقت تشغيل النظام: {e}")
        stats['uptime'] = _('غير متاح')
    
    # إحصائيات قاعدة البيانات - المستخدمين والحجوزات (بيانات حقيقية)
    try:
        from rental.models import Reservation
        stats['active_reservations'] = Reservation.objects.filter(status='confirmed').count()
        
        from django.contrib.auth import get_user_model
        User = get_user_model()
        stats['total_users'] = User.objects.count()
        
        # إضافة إحصائيات أكثر تفصيلاً
        stats['confirmed_reservations'] = Reservation.objects.filter(status='confirmed').count()
        stats['cancelled_reservations'] = Reservation.objects.filter(status='cancelled').count()
        stats['completed_reservations'] = Reservation.objects.filter(status='completed').count()
    except Exception as e:
        print(f"خطأ في جلب معلومات المستخدمين والحجوزات: {e}")
        stats['active_reservations'] = 0
        stats['total_users'] = 0
    
    # إحصائيات المجلدات والمستندات (بيانات حقيقية)
    try:
        from rental.models import ArchiveFolder, Document
        stats['total_folders'] = ArchiveFolder.objects.count()
        stats['total_documents'] = Document.objects.count()
        
        # إضافة معلومات أكثر تفصيلاً
        stats['root_folders'] = ArchiveFolder.objects.filter(parent__isnull=True).count()
        stats['pdf_documents'] = Document.objects.filter(file_path__endswith='.pdf').count()
        stats['image_documents'] = Document.objects.filter(
            file_path__endswith=('.jpg', '.jpeg', '.png', '.gif')
        ).count()
    except Exception as e:
        print(f"خطأ في جلب معلومات المجلدات والمستندات: {e}")
        stats['total_folders'] = 0
        stats['total_documents'] = 0
    
    # معلومات الشبكة (بيانات حقيقية)
    try:
        net_io = psutil.net_io_counters()
        stats['network_sent'] = f"{net_io.bytes_sent / (1024**2):.2f} MB"
        stats['network_received'] = f"{net_io.bytes_recv / (1024**2):.2f} MB"
        stats['packets_sent'] = net_io.packets_sent
        stats['packets_recv'] = net_io.packets_recv
        
        # معلومات عن الاتصالات النشطة
        stats['active_connections'] = len(psutil.net_connections())
    except Exception as e:
        print(f"خطأ في جلب معلومات الشبكة: {e}")
    
    # إضافة معلومات الوقت الحالي للتأكيد على حداثة المعلومات
    stats['timestamp'] = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    return stats

def get_database_size():
    """الحصول على حجم قاعدة البيانات الحقيقي"""
    try:
        db_engine = settings.DATABASES['default']['ENGINE']
        db_name = settings.DATABASES['default']['NAME']
        
        if 'sqlite3' in db_engine:
            # قاعدة بيانات SQLite
            if os.path.exists(db_name):
                size_bytes = os.path.getsize(db_name)
                size_mb = size_bytes / (1024**2)
                # تحويل إلى وحدات مناسبة
                if size_mb < 1:
                    return f"{size_bytes / 1024:.2f} KB"
                elif size_mb < 1024:
                    return f"{size_mb:.2f} MB"
                else:
                    return f"{size_mb / 1024:.2f} GB"
            return "0 MB"
        elif 'postgresql' in db_engine:
            # قاعدة بيانات PostgreSQL
            size_bytes = 0
            db_info = {}
            
            # محاولة الحصول على حجم قاعدة البيانات الكاملة
            try:
                with connection.cursor() as cursor:
                    cursor.execute("SELECT pg_database_size(current_database())")
                    size_bytes = cursor.fetchone()[0]
                    
                    # الحصول على معلومات إضافية عن قاعدة البيانات
                    cursor.execute("""
                        SELECT count(*) as total_tables 
                        FROM information_schema.tables 
                        WHERE table_schema = 'public'
                    """)
                    db_info['total_tables'] = cursor.fetchone()[0]
                    
                    # قياس حجم الجداول المختلفة
                    cursor.execute("""
                        SELECT 
                            table_name, 
                            pg_relation_size(quote_ident(table_name)) as size_bytes
                        FROM 
                            information_schema.tables
                        WHERE 
                            table_schema = 'public'
                        ORDER BY 
                            size_bytes DESC
                        LIMIT 5
                    """)
                    largest_tables = cursor.fetchall()
                    db_info['largest_tables'] = [
                        {'name': table[0], 'size': f"{table[1] / (1024**2):.2f} MB"}
                        for table in largest_tables
                    ]
            except Exception as e:
                print(f"خطأ في الاستعلام عن قاعدة بيانات PostgreSQL: {e}")
                
                # محاولة بديلة للحصول على حجم البيانات
                try:
                    with connection.cursor() as cursor:
                        cursor.execute("""
                            SELECT sum(pg_relation_size(quote_ident(table_name)))
                            FROM information_schema.tables
                            WHERE table_schema = 'public'
                        """)
                        size_bytes = cursor.fetchone()[0] or 0
                except Exception as e2:
                    print(f"فشلت المحاولة البديلة: {e2}")
                    return _('غير متاح')
            
            # تحويل الحجم إلى وحدة مناسبة
            size_mb = size_bytes / (1024**2)
            if size_mb < 1:
                size_str = f"{size_bytes / 1024:.2f} KB"
            elif size_mb < 1024:
                size_str = f"{size_mb:.2f} MB"
            else:
                size_str = f"{size_mb / 1024:.2f} GB"
                
            # إرفاق معلومات إضافية إذا كانت متوفرة
            if db_info:
                return {
                    'size': size_str,
                    'total_tables': db_info.get('total_tables', 0),
                    'largest_tables': db_info.get('largest_tables', [])
                }
            return size_str
            
        elif 'mysql' in db_engine:
            # قاعدة بيانات MySQL/MariaDB
            try:
                with connection.cursor() as cursor:
                    cursor.execute("""
                        SELECT table_schema AS 'Database',
                        SUM(data_length + index_length) AS 'Size'
                        FROM information_schema.TABLES
                        WHERE table_schema = DATABASE()
                        GROUP BY table_schema
                    """)
                    result = cursor.fetchone()
                    if result and result[1]:
                        size_bytes = result[1]
                        size_mb = size_bytes / (1024**2)
                        if size_mb < 1:
                            return f"{size_bytes / 1024:.2f} KB"
                        elif size_mb < 1024:
                            return f"{size_mb:.2f} MB"
                        else:
                            return f"{size_mb / 1024:.2f} GB"
            except Exception as e:
                print(f"خطأ في قياس حجم MySQL: {e}")
                return _('غير متاح')
        
        # قواعد بيانات أخرى غير مدعومة
        return _('غير متاح للمحرك: {engine}').format(engine=db_engine.split('.')[-1])
    except Exception as e:
        print(f"خطأ في get_database_size: {e}")
        return _('غير متاح')

def get_system_uptime():
    """الحصول على مدة تشغيل النظام والخادم الحقيقية"""
    uptime_info = {}
    
    # محاولة الحصول على وقت تشغيل النظام
    try:
        # الحصول على وقت بدء تشغيل النظام
        boot_time = psutil.boot_time()
        boot_datetime = datetime.datetime.fromtimestamp(boot_time)
        current_time = datetime.datetime.now()
        uptime = current_time - boot_datetime
        
        # حساب الأيام والساعات والدقائق والثواني
        days = uptime.days
        hours, remainder = divmod(uptime.seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        
        uptime_info['system'] = {
            'total_seconds': int(uptime.total_seconds()),
            'days': days,
            'hours': hours,
            'minutes': minutes,
            'seconds': seconds,
            'boot_time': boot_datetime.strftime('%Y-%m-%d %H:%M:%S'),
            'current_time': current_time.strftime('%Y-%m-%d %H:%M:%S'),
        }
        
        # تنسيق المدة بشكل مناسب مع مراعاة التعريب
        if days > 0:
            uptime_info['system']['formatted'] = f"{days} {_('يوم')} {hours} {_('ساعة')} {minutes} {_('دقيقة')}"
        elif hours > 0:
            uptime_info['system']['formatted'] = f"{hours} {_('ساعة')} {minutes} {_('دقيقة')}"
        else:
            uptime_info['system']['formatted'] = f"{minutes} {_('دقيقة')} {seconds} {_('ثانية')}"
            
    except Exception as e:
        print(f"خطأ في الحصول على وقت تشغيل النظام: {e}")
        uptime_info['system'] = {'error': str(e)}
    
    # محاولة الحصول على وقت تشغيل عملية الخادم
    try:
        # الحصول على معلومات عملية جونيكورن الحالية
        process = psutil.Process(os.getpid())
        start_time = datetime.datetime.fromtimestamp(process.create_time())
        current_time = datetime.datetime.now()
        process_uptime = current_time - start_time
        
        days = process_uptime.days
        hours, remainder = divmod(process_uptime.seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        
        uptime_info['server'] = {
            'total_seconds': int(process_uptime.total_seconds()),
            'days': days,
            'hours': hours,
            'minutes': minutes,
            'seconds': seconds,
            'start_time': start_time.strftime('%Y-%m-%d %H:%M:%S'),
            'current_time': current_time.strftime('%Y-%m-%d %H:%M:%S'),
            'pid': os.getpid(),
            'name': process.name(),
        }
        
        # تنسيق المدة بشكل مناسب مع مراعاة التعريب
        if days > 0:
            uptime_info['server']['formatted'] = f"{days} {_('يوم')} {hours} {_('ساعة')} {minutes} {_('دقيقة')}"
        elif hours > 0:
            uptime_info['server']['formatted'] = f"{hours} {_('ساعة')} {minutes} {_('دقيقة')}"
        else:
            uptime_info['server']['formatted'] = f"{minutes} {_('دقيقة')} {seconds} {_('ثانية')}"
            
        # الحصول على مزيد من المعلومات عن العملية
        try:
            uptime_info['server']['memory_percent'] = process.memory_percent()
            uptime_info['server']['cpu_percent'] = process.cpu_percent(interval=0.1)
            uptime_info['server']['threads'] = len(process.threads())
            uptime_info['server']['connections'] = len(process.connections())
        except Exception as proc_detail_e:
            print(f"خطأ في الحصول على تفاصيل إضافية عن العملية: {proc_detail_e}")
            
    except Exception as proc_e:
        print(f"خطأ في الحصول على وقت تشغيل الخادم: {proc_e}")
        uptime_info['server'] = {'error': str(proc_e)}
    
    # معلومات إضافية عن النظام
    try:
        # عدد العمليات النشطة
        processes = len(psutil.pids())
        uptime_info['active_processes'] = processes
        
        # متوسط تحميل النظام (إذا كان نظام يونكس)
        if hasattr(os, 'getloadavg'):
            load_avg = os.getloadavg()
            uptime_info['load_avg'] = {
                '1min': round(load_avg[0], 2),
                '5min': round(load_avg[1], 2),
                '15min': round(load_avg[2], 2)
            }
        
        # عدد الاتصالات النشطة
        connections = len(psutil.net_connections())
        uptime_info['active_connections'] = connections
    except Exception as sys_info_e:
        print(f"خطأ في الحصول على معلومات إضافية عن النظام: {sys_info_e}")
    
    # إعادة المعلومات الأساسية عن وقت تشغيل النظام أو الخادم
    if 'system' in uptime_info and 'formatted' in uptime_info['system']:
        # إذا كانت معلومات النظام متاحة
        return uptime_info['system']['formatted']
    elif 'server' in uptime_info and 'formatted' in uptime_info['server']:
        # إذا كانت معلومات الخادم متاحة فقط (لكن النظام غير متاح)
        return f"{uptime_info['server']['formatted']} - {_('عملية الخادم')}"
    else:
        # في حالة عدم توفر أي معلومات
        return _('غير متاح')

def get_diagnostic_tools():
    """الحصول على قائمة أدوات التشخيص المتاحة"""
    tools = [
        {
            'id': 'system_check',
            'name': _('فحص النظام'),
            'description': _('تشغيل الفحص الأساسي للنظام للكشف عن المشاكل'),
            'icon': 'fa-check-circle',
        },
        {
            'id': 'database_check',
            'name': _('فحص قاعدة البيانات'),
            'description': _('فحص قاعدة البيانات للكشف عن المشاكل والاختناقات'),
            'icon': 'fa-database',
        },
        {
            'id': 'media_check',
            'name': _('فحص الوسائط'),
            'description': _('فحص ملفات الوسائط ومجلداتها للتأكد من سلامتها'),
            'icon': 'fa-images',
        },
        {
            'id': 'cache_check',
            'name': _('فحص ذاكرة التخزين المؤقت'),
            'description': _('فحص وتنظيف ذاكرة التخزين المؤقت'),
            'icon': 'fa-server',
        },
        {
            'id': 'permission_check',
            'name': _('فحص الأذونات'),
            'description': _('فحص أذونات الملفات والمجلدات'),
            'icon': 'fa-lock',
        },
    ]
    
    return tools

@login_required
def run_diagnostic(request, diagnostic_type):
    """تشغيل أداة تشخيص محددة"""
    if not is_superadmin(request.user):
        messages.error(request, _('ليس لديك صلاحية لتشغيل أدوات التشخيص'))
        return redirect('superadmin_diagnostics')
    
    # تنفيذ التشخيص المطلوب
    if diagnostic_type == 'system_check':
        results = run_system_check()
    elif diagnostic_type == 'database_check':
        results = run_database_check()
    elif diagnostic_type == 'media_check':
        results = run_media_check()
    elif diagnostic_type == 'cache_check':
        results = run_cache_check()
    elif diagnostic_type == 'permission_check':
        results = run_permission_check()
    else:
        messages.error(request, _('نوع التشخيص غير معروف'))
        return redirect('superadmin_diagnostics')
    
    # عرض نتائج التشخيص
    context = {
        'diagnostic_type': diagnostic_type,
        'results': results,
        'title': _('نتائج التشخيص'),
    }
    
    return render(request, 'superadmin/diagnostics/results.html', context)

def run_system_check():
    """تشغيل فحص النظام الحقيقي باستخدام معلومات فعلية"""
    issues = []
    warnings = []
    success = []
    
    try:
        # فحص مساحة القرص (بيانات حقيقية)
        disk = psutil.disk_usage('/')
        if disk.percent > 90:
            issues.append({
                'title': _('مساحة القرص منخفضة جداً'),
                'description': _('مساحة القرص المتبقية {free_space} فقط من أصل {total_space} ({used_percent}% مستخدم)').format(
                    free_space=f"{disk.free / (1024**3):.2f} GB",
                    total_space=f"{disk.total / (1024**3):.2f} GB",
                    used_percent=disk.percent
                ),
                'solution': _('حرر مساحة على القرص بحذف الملفات غير الضرورية'),
                'severity': 'critical',
                'issue_id': 'disk_space_low',
                'timestamp': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            })
        elif disk.percent > 80:
            warnings.append({
                'title': _('مساحة القرص منخفضة'),
                'description': _('مساحة القرص المتبقية {free_space} من أصل {total_space} ({used_percent}% مستخدم)').format(
                    free_space=f"{disk.free / (1024**3):.2f} GB",
                    total_space=f"{disk.total / (1024**3):.2f} GB",
                    used_percent=disk.percent
                ),
                'solution': _('فكر في تحرير مساحة على القرص قريباً'),
                'timestamp': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            })
        else:
            success.append({
                'title': _('مساحة القرص جيدة'),
                'description': _('مساحة القرص المتبقية {free_space} من أصل {total_space} ({percent}% مستخدم)').format(
                    free_space=f"{disk.free / (1024**3):.2f} GB",
                    total_space=f"{disk.total / (1024**3):.2f} GB",
                    percent=disk.percent
                ),
            })
    except Exception as e:
        warnings.append({
            'title': _('تعذر قراءة مساحة القرص'),
            'description': _('حدث خطأ أثناء قراءة مساحة القرص: {error}').format(error=str(e)),
            'solution': _('تحقق من أذونات النظام'),
        })
    
    try:
        # فحص استخدام المعالج
        cpu_usage = psutil.cpu_percent(interval=0.5)
        if cpu_usage > 90:
            issues.append({
                'title': _('استخدام المعالج مرتفع جداً'),
                'description': _('استخدام المعالج الحالي {cpu_usage}%').format(cpu_usage=cpu_usage),
                'solution': _('تحقق من العمليات التي تستهلك المعالج بشكل كبير'),
                'severity': 'high',
                'issue_id': 'cpu_usage_high',
            })
        elif cpu_usage > 70:
            warnings.append({
                'title': _('استخدام المعالج مرتفع'),
                'description': _('استخدام المعالج الحالي {cpu_usage}%').format(cpu_usage=cpu_usage),
                'solution': _('راقب استخدام المعالج وتحقق إذا كان يرتفع باستمرار'),
            })
        else:
            success.append({
                'title': _('استخدام المعالج ضمن الحدود الطبيعية'),
                'description': _('استخدام المعالج الحالي {cpu_usage}%').format(cpu_usage=cpu_usage),
            })
    except Exception as e:
        warnings.append({
            'title': _('تعذر قراءة استخدام المعالج'),
            'description': _('حدث خطأ أثناء قراءة استخدام المعالج: {error}').format(error=str(e)),
            'solution': _('تحقق من أذونات النظام'),
        })
    
    # فحص استخدام الذاكرة
    try:
        memory = psutil.virtual_memory()
        if memory.percent > 90:
            issues.append({
                'title': _('استخدام الذاكرة مرتفع جداً'),
                'description': _('استخدام الذاكرة الحالي {memory_usage}%').format(memory_usage=memory.percent),
                'solution': _('تحقق من العمليات التي تستهلك الذاكرة بشكل كبير'),
                'severity': 'high',
                'issue_id': 'memory_usage_high',
            })
        elif memory.percent > 80:
            warnings.append({
                'title': _('استخدام الذاكرة مرتفع'),
                'description': _('استخدام الذاكرة الحالي {memory_usage}%').format(memory_usage=memory.percent),
                'solution': _('راقب استخدام الذاكرة وتحقق إذا كان يرتفع باستمرار'),
            })
        else:
            success.append({
                'title': _('استخدام الذاكرة طبيعي'),
                'description': _('استخدام الذاكرة الحالي {memory_usage}%').format(memory_usage=memory.percent),
            })
    except Exception as e:
        warnings.append({
            'title': _('تعذر قراءة استخدام الذاكرة'),
            'description': _('حدث خطأ أثناء قراءة استخدام الذاكرة: {error}').format(error=str(e)),
            'solution': _('تحقق من أذونات النظام'),
        })
    
    # تسجيل المشاكل المكتشفة في قاعدة البيانات
    for issue in issues:
        if 'issue_id' in issue:
            # التحقق مما إذا كانت المشكلة موجودة بالفعل
            existing_issue = SystemIssue.objects.filter(title__contains=issue['issue_id'], status__in=['new', 'in_progress']).first()
            if not existing_issue:
                # إنشاء مشكلة جديدة
                db_issue = SystemIssue.objects.create(
                    title=issue['title'],
                    description=issue['description'],
                    area='system',
                    severity=issue['severity'],
                    status='new'
                )
                # إضافة معرف قاعدة البيانات إلى القاموس لاستخدامه في القالب
                issue['db_id'] = db_issue.id
    
    return {
        'issues': issues,
        'warnings': warnings,
        'success': success,
    }

@login_required
def fix_issue(request, issue_id):
    """إصلاح مشكلة محددة في النظام"""
    if not is_superadmin(request.user):
        messages.error(request, _('ليس لديك صلاحية لإصلاح مشاكل النظام'))
        return redirect('superadmin_diagnostics')
    
    try:
        # الحصول على تفاصيل المشكلة
        issue = SystemIssue.objects.get(id=issue_id)
        
        # محاولة إصلاح المشكلة حسب نوعها
        success = False
        if issue.issue_type == 'disk_space_low':
            success = fix_disk_space()
        elif issue.issue_type == 'media_permissions':
            success = fix_media_permissions()
        elif issue.issue_type == 'project_permissions':
            success = fix_project_permissions()
        elif issue.issue_type == 'db_permissions':
            success = fix_db_permissions()
        elif issue.issue_type == 'missing_media_dir':
            success = create_media_directory()
        elif issue.issue_type == 'db_connection':
            success = check_db_connection()
        
        # تحديث حالة المشكلة
        if success:
            issue.status = 'fixed'
            issue.fixed_at = timezone.now()
            issue.fixed_by = request.user
            issue.save()
            messages.success(request, _('تم إصلاح المشكلة بنجاح'))
        else:
            issue.status = 'in_progress'
            issue.save()
            messages.warning(request, _('تم محاولة إصلاح المشكلة، ولكن قد تحتاج إلى مزيد من الإجراءات'))
    except SystemIssue.DoesNotExist:
        messages.error(request, _('المشكلة المطلوبة غير موجودة'))
    except Exception as e:
        messages.error(request, _('حدث خطأ أثناء محاولة إصلاح المشكلة: {0}').format(str(e)))
    
    return redirect('superadmin_diagnostics')

def run_database_check():
    """تشغيل فحص قاعدة البيانات بناءً على معلومات حقيقية"""
    issues = []
    warnings = []
    success = []
    
    try:
        # اختبار الاتصال بقاعدة البيانات
        db_connected = check_db_connection()
        if not db_connected:
            issues.append({
                'title': _('فشل الاتصال بقاعدة البيانات'),
                'description': _('لا يمكن الاتصال بقاعدة البيانات. قد تكون قاعدة البيانات متوقفة أو هناك مشكلة في التكوين.'),
                'solution': _('تحقق من إعدادات الاتصال بقاعدة البيانات وتأكد من تشغيل خدمة قاعدة البيانات'),
                'severity': 'critical',
                'issue_id': 'db_connection_failed',
                'timestamp': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            })
        else:
            success.append({
                'title': _('الاتصال بقاعدة البيانات يعمل بشكل صحيح'),
                'description': _('تم الاتصال بقاعدة البيانات بنجاح')
            })
            
            # اختبار حجم قاعدة البيانات
            db_size_str = get_database_size()
            db_size_mb = 0
            
            try:
                if isinstance(db_size_str, str) and 'MB' in db_size_str:
                    db_size_mb = float(db_size_str.split()[0])
                    
                    if db_size_mb > 500:  # اختبار حجم قاعدة البيانات أكبر من 500 ميجا
                        warnings.append({
                            'title': _('حجم قاعدة البيانات كبير'),
                            'description': _('حجم قاعدة البيانات {size}. قد يؤثر ذلك على الأداء.').format(size=db_size_str),
                            'solution': _('فكر في تنظيف البيانات القديمة أو غير المستخدمة')
                        })
                    else:
                        success.append({
                            'title': _('حجم قاعدة البيانات مقبول'),
                            'description': _('حجم قاعدة البيانات الحالي {size}').format(size=db_size_str)
                        })
            except Exception:
                # في حالة عدم القدرة على تحويل حجم قاعدة البيانات، تخطي هذا الاختبار
                pass
                
            # اختبار أداء قاعدة البيانات
            try:
                # قياس وقت تنفيذ استعلام بسيط
                start_time = time.time()
                with connection.cursor() as cursor:
                    cursor.execute("SELECT 1")
                    cursor.fetchone()
                query_time = time.time() - start_time
                
                if query_time > 0.5:  # إذا استغرق الاستعلام أكثر من نصف ثانية
                    warnings.append({
                        'title': _('بطء في استجابة قاعدة البيانات'),
                        'description': _('استغرق الاستعلام البسيط {time:.4f} ثانية').format(time=query_time),
                        'solution': _('تحقق من أداء خادم قاعدة البيانات وإعدادات التكوين')
                    })
                else:
                    success.append({
                        'title': _('أداء قاعدة البيانات جيد'),
                        'description': _('استغرق الاستعلام البسيط {time:.4f} ثانية فقط').format(time=query_time)
                    })
                    
                # التحقق من الجداول والفهارس
                try:
                    db_engine = settings.DATABASES['default']['ENGINE']
                    if 'sqlite' in db_engine:
                        # اختبارات خاصة بقاعدة بيانات SQLite
                        with connection.cursor() as cursor:
                            cursor.execute("PRAGMA integrity_check")
                            integrity_result = cursor.fetchone()[0]
                            if integrity_result != 'ok':
                                issues.append({
                                    'title': _('مشكلة في سلامة قاعدة بيانات SQLite'),
                                    'description': _('نتيجة فحص السلامة: {result}').format(result=integrity_result),
                                    'solution': _('قم بإصلاح قاعدة البيانات أو استعادة نسخة احتياطية'),
                                    'severity': 'critical',
                                    'issue_id': 'sqlite_integrity_failed',
                                })
                            else:
                                success.append({
                                    'title': _('سلامة قاعدة بيانات SQLite جيدة'),
                                    'description': _('تم اجتياز فحص سلامة قاعدة البيانات')
                                })
                    elif 'postgresql' in db_engine:
                        # اختبارات خاصة بقاعدة بيانات PostgreSQL
                        with connection.cursor() as cursor:
                            # فحص الجداول بدون فهارس (قد يؤثر على الأداء)
                            cursor.execute("""
                                SELECT relname
                                FROM pg_class
                                WHERE relkind = 'r'
                                AND relname NOT LIKE 'pg_%'
                                AND relname NOT LIKE 'sql_%'
                                AND NOT EXISTS (
                                    SELECT 1
                                    FROM pg_index
                                    WHERE indrelid = pg_class.oid
                                );
                            """)
                            tables_without_indices = cursor.fetchall()
                            if tables_without_indices:
                                # إذا وجدت جداول بدون فهارس، قد يكون هذا يؤثر على الأداء
                                table_list = ', '.join([t[0] for t in tables_without_indices])
                                warnings.append({
                                    'title': _('جداول بدون فهارس'),
                                    'description': _('تم العثور على {count} جداول بدون فهارس: {tables}').format(
                                        count=len(tables_without_indices),
                                        tables=table_list
                                    ),
                                    'solution': _('فكر في إضافة فهارس للجداول المستخدمة بكثرة في الاستعلامات')
                                })
                except Exception as e:
                    print(f"خطأ أثناء فحص الجداول والفهارس: {e}")
            except Exception as e:
                print(f"خطأ أثناء اختبار أداء قاعدة البيانات: {e}")
                issues.append({
                    'title': _('خطأ أثناء اختبار أداء قاعدة البيانات'),
                    'description': _('حدث خطأ أثناء محاولة قياس أداء قاعدة البيانات: {error}').format(error=str(e)),
                    'solution': _('تحقق من سجلات الأخطاء للحصول على مزيد من المعلومات'),
                    'severity': 'medium',
                    'issue_id': 'db_performance_test_error',
                })
    except Exception as e:
        print(f"خطأ أثناء فحص قاعدة البيانات: {e}")
        issues.append({
            'title': _('خطأ أثناء فحص قاعدة البيانات'),
            'description': _('حدث خطأ غير متوقع أثناء إجراء فحص قاعدة البيانات: {error}').format(error=str(e)),
            'solution': _('تحقق من سجلات الأخطاء للحصول على مزيد من المعلومات'),
            'severity': 'high',
            'issue_id': 'db_check_error',
        })
    
    # إحصائيات قاعدة البيانات
    stats = {}
    try:
        with connection.cursor() as cursor:
            # عدد الجداول
            if 'sqlite' in settings.DATABASES['default']['ENGINE']:
                cursor.execute("SELECT count(*) FROM sqlite_master WHERE type='table'")
                table_count = cursor.fetchone()[0]
                stats['table_count'] = table_count
            elif 'postgresql' in settings.DATABASES['default']['ENGINE']:
                cursor.execute("SELECT count(*) FROM information_schema.tables WHERE table_schema = 'public'")
                table_count = cursor.fetchone()[0]
                stats['table_count'] = table_count
            
            # إضافة إحصائيات إلى النتائج
            success.append({
                'title': _('إحصائيات قاعدة البيانات'),
                'description': _('عدد الجداول: {table_count}').format(table_count=stats.get('table_count', 'غير متاح')),
            })
    except Exception as e:
        print(f"خطأ أثناء جمع إحصائيات قاعدة البيانات: {e}")
    
    return {
        'issues': issues,
        'warnings': warnings,
        'success': success,
        'stats': stats
    }
    # فحص اتصالات قاعدة البيانات
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            result = cursor.fetchone()[0]
            if result == 1:
                success.append({
                    'title': _('اتصال قاعدة البيانات يعمل بشكل صحيح'),
                    'description': _('تم الاتصال بقاعدة البيانات بنجاح: {db_type}').format(db_type=db_engine.split('.')[-1]),
                })
    except Exception as e:
        issues.append({
            'title': _('مشكلة في الاتصال بقاعدة البيانات'),
            'description': _('تعذر الاتصال بقاعدة البيانات: {error}').format(error=str(e)),
            'solution': _('تحقق من إعدادات الاتصال بقاعدة البيانات وتأكد من تشغيل خدمة قاعدة البيانات'),
            'severity': 'critical',
            'issue_id': 'db_connection_error',
        })
    
    # فحص جداول قاعدة البيانات
    try:
        all_models = apps.get_models()
        checked_tables = []
        
        for model in all_models:
            if hasattr(model, '_meta') and hasattr(model._meta, 'db_table'):
                table_name = model._meta.db_table
                checked_tables.append(table_name)
                
                # فحص وجود الجدول
                with connection.cursor() as cursor:
                    if 'sqlite3' in db_engine:
                        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name=?", [table_name])
                        table_exists = cursor.fetchone() is not None
                    elif 'postgresql' in db_engine:
                        cursor.execute("SELECT to_regclass(%s)", [table_name])
                        table_exists = cursor.fetchone()[0] is not None
                    else:
                        table_exists = True  # افتراضياً للمحركات الأخرى
                
                if not table_exists:
                    issues.append({
                        'title': _('جدول مفقود في قاعدة البيانات'),
                        'description': _('الجدول {table_name} غير موجود في قاعدة البيانات').format(table_name=table_name),
                        'solution': _('قم بتشغيل أمر migrate لإنشاء الجداول المفقودة'),
                        'severity': 'high',
                        'issue_id': f'missing_table_{table_name}',
                    })
        
        success.append({
            'title': _('تم فحص جداول قاعدة البيانات'),
            'description': _('تم فحص {count} جدول').format(count=len(checked_tables)),
        })
    except Exception as e:
        warnings.append({
            'title': _('تعذر فحص جداول قاعدة البيانات'),
            'description': _('حدث خطأ أثناء فحص جداول قاعدة البيانات: {error}').format(error=str(e)),
            'solution': _('تحقق من أذونات قاعدة البيانات وأن المستخدم لديه صلاحيات كافية'),
        })
    
    # تسجيل المشاكل المكتشفة في قاعدة البيانات
    for issue in issues:
        if 'issue_id' in issue:
            # التحقق مما إذا كانت المشكلة موجودة بالفعل
            existing_issue = SystemIssue.objects.filter(title__contains=issue['issue_id'], status__in=['new', 'in_progress']).first()
            if not existing_issue:
                # إنشاء مشكلة جديدة
                db_issue = SystemIssue.objects.create(
                    title=issue['title'],
                    description=issue['description'],
                    area='database',
                    severity=issue['severity'],
                    status='new'
                )
                # إضافة معرف قاعدة البيانات إلى القاموس لاستخدامه في القالب
                issue['db_id'] = db_issue.id
    
    return {
        'issues': issues,
        'warnings': warnings,
        'success': success,
    }

def run_media_check():
    """تشغيل فحص ملفات الوسائط"""
    issues = []
    warnings = []
    success = []
    
    try:
        # فحص وجود مجلد الوسائط
        media_root = settings.MEDIA_ROOT
        if not os.path.exists(media_root):
            issues.append({
                'title': _('مجلد الوسائط غير موجود'),
                'description': _('مجلد الوسائط (MEDIA_ROOT) غير موجود: {path}').format(path=media_root),
                'solution': _('قم بإنشاء مجلد الوسائط أو أعد تكوين MEDIA_ROOT'),
                'severity': 'high',
                'issue_id': 'media_root_missing',
            })
        else:
            # فحص أذونات مجلد الوسائط
            if not os.access(media_root, os.R_OK | os.W_OK):
                issues.append({
                    'title': _('مشكلة في أذونات مجلد الوسائط'),
                    'description': _('لا يمكن القراءة من أو الكتابة إلى مجلد الوسائط: {path}').format(path=media_root),
                    'solution': _('قم بتغيير أذونات مجلد الوسائط للسماح بالقراءة والكتابة'),
                    'severity': 'high',
                    'issue_id': 'media_root_permissions',
                })
            else:
                success.append({
                    'title': _('مجلد الوسائط موجود وقابل للوصول'),
                    'description': _('مجلد الوسائط (MEDIA_ROOT) قابل للقراءة والكتابة')
                })
            
            # فحص حجم مجلد الوسائط
            try:
                total_size = 0
                file_count = 0
                for dirpath, dirnames, filenames in os.walk(media_root):
                    for f in filenames:
                        fp = os.path.join(dirpath, f)
                        if os.path.exists(fp):
                            total_size += os.path.getsize(fp)
                            file_count += 1
                
                # تحويل الحجم إلى تنسيق مقروء (ميجابايت)
                size_mb = total_size / (1024 * 1024)
                
                # إضافة معلومات الحجم إلى نتائج النجاح
                success.append({
                    'title': _('إحصائيات مجلد الوسائط'),
                    'description': _('إجمالي الحجم: {size:.2f} ميجابايت، عدد الملفات: {count}').format(
                        size=size_mb, count=file_count)
                })
                
                # التحقق من الحجم الكبير (> 1 جيجابايت)
                if size_mb > 1024:  # أكثر من 1 جيجابايت
                    warnings.append({
                        'title': _('حجم مجلد الوسائط كبير'),
                        'description': _('مجلد الوسائط كبير جداً ({size:.2f} ميجابايت)').format(size=size_mb),
                        'solution': _('فكر في تنظيف الملفات القديمة أو غير المستخدمة')
                    })
            except Exception as e:
                warnings.append({
                    'title': _('مشكلة في حساب حجم مجلد الوسائط'),
                    'description': _('تعذر حساب حجم مجلد الوسائط: {error}').format(error=str(e)),
                    'solution': _('تحقق من حقوق الوصول وحجم مجلد الوسائط يدوياً')
                })
            
            # البحث عن أنواع ملفات غير مدعومة
            unsupported_extensions = ['.exe', '.dll', '.jar', '.sh', '.php', '.aspx', '.asp']
            unsupported_files = []
            for dirpath, dirnames, filenames in os.walk(media_root):
                for f in filenames:
                    ext = os.path.splitext(f)[1].lower()
                    if ext in unsupported_extensions:
                        unsupported_files.append(os.path.join(dirpath, f))
            
            if unsupported_files:
                warnings.append({
                    'title': _('ملفات ذات امتدادات غير آمنة'),
                    'description': _('تم العثور على {count} ملفات ذات امتدادات غير آمنة في مجلد الوسائط').format(
                        count=len(unsupported_files)),
                    'solution': _('قم بمراجعة وإزالة الملفات غير الآمنة')
                })
            else:
                success.append({
                    'title': _('لم يتم العثور على امتدادات ملفات غير آمنة'),
                    'description': _('لا توجد ملفات ذات امتدادات غير آمنة معروفة في مجلد الوسائط')
                })
            
            # البحث عن ملفات كبيرة جداً (> 50 ميجابايت)
            large_files = []
            for dirpath, dirnames, filenames in os.walk(media_root):
                for f in filenames:
                    fp = os.path.join(dirpath, f)
                    if os.path.exists(fp) and os.path.getsize(fp) > 50 * 1024 * 1024:  # > 50 ميجابايت
                        large_files.append(fp)
            
            if large_files:
                warnings.append({
                    'title': _('ملفات كبيرة جداً في مجلد الوسائط'),
                    'description': _('تم العثور على {count} ملفات أكبر من 50 ميجابايت').format(
                        count=len(large_files)),
                    'solution': _('راجع الملفات الكبيرة وتأكد من أنها ضرورية')
                })
    
    except Exception as e:
        issues.append({
            'title': _('خطأ أثناء فحص ملفات الوسائط'),
            'description': _('حدث خطأ غير متوقع أثناء فحص ملفات الوسائط: {error}').format(error=str(e)),
            'solution': _('تحقق من سجلات الأخطاء للحصول على مزيد من المعلومات'),
            'severity': 'high',
            'issue_id': 'media_check_error',
        })
    
    return {
        'issues': issues,
        'warnings': warnings,
        'success': success
    }
    
def run_permission_check():
    """تشغيل فحص الأذونات لمجلدات وملفات النظام"""
    issues = []
    warnings = []
    success = []
    
    try:
        # قائمة المجلدات المهمة للتحقق من أذوناتها
        important_dirs = [
            os.path.join(settings.BASE_DIR, 'media'),
            os.path.join(settings.BASE_DIR, 'static'),
            os.path.join(settings.BASE_DIR, 'staticfiles'),
            os.path.join(settings.BASE_DIR, 'temp'),
            os.path.join(settings.BASE_DIR, 'templates'),
            os.path.join(settings.BASE_DIR, 'locale'),
        ]
        
        # قائمة الملفات المهمة للتحقق من أذوناتها
        important_files = [
            settings.BASE_DIR / 'manage.py',
            settings.BASE_DIR / 'db.sqlite3',
        ]
        
        # فحص المجلدات
        for dir_path in important_dirs:
            if os.path.exists(dir_path):
                # التحقق من إمكانية القراءة
                if not os.access(dir_path, os.R_OK):
                    issues.append({
                        'title': _('مشكلة في أذونات القراءة للمجلد'),
                        'description': _('لا يمكن قراءة المجلد: {path}').format(path=dir_path),
                        'solution': _('قم بتغيير أذونات المجلد للسماح بالقراءة'),
                        'severity': 'high',
                        'issue_id': f'dir_read_permission_{os.path.basename(dir_path)}',
                    })
                
                # التحقق من إمكانية الكتابة
                if not os.access(dir_path, os.W_OK):
                    issues.append({
                        'title': _('مشكلة في أذونات الكتابة للمجلد'),
                        'description': _('لا يمكن الكتابة في المجلد: {path}').format(path=dir_path),
                        'solution': _('قم بتغيير أذونات المجلد للسماح بالكتابة'),
                        'severity': 'high',
                        'issue_id': f'dir_write_permission_{os.path.basename(dir_path)}',
                    })
                
                # في حالة عدم وجود مشاكل
                if os.access(dir_path, os.R_OK) and os.access(dir_path, os.W_OK):
                    success.append({
                        'title': _('أذونات المجلد صحيحة'),
                        'description': _('المجلد {path} لديه أذونات قراءة وكتابة صحيحة').format(path=dir_path),
                    })
            else:
                warnings.append({
                    'title': _('مجلد مهم غير موجود'),
                    'description': _('المجلد المهم غير موجود: {path}').format(path=dir_path),
                    'solution': _('قم بإنشاء المجلد المفقود')
                })
        
        # فحص الملفات
        for file_path in important_files:
            if os.path.exists(file_path):
                # التحقق من إمكانية القراءة
                if not os.access(file_path, os.R_OK):
                    issues.append({
                        'title': _('مشكلة في أذونات القراءة للملف'),
                        'description': _('لا يمكن قراءة الملف: {path}').format(path=file_path),
                        'solution': _('قم بتغيير أذونات الملف للسماح بالقراءة'),
                        'severity': 'high',
                        'issue_id': f'file_read_permission_{os.path.basename(file_path)}',
                    })
                
                # التحقق من إمكانية الكتابة
                if not os.access(file_path, os.W_OK):
                    warnings.append({
                        'title': _('مشكلة في أذونات الكتابة للملف'),
                        'description': _('لا يمكن الكتابة في الملف: {path}').format(path=file_path),
                        'solution': _('قم بتغيير أذونات الملف للسماح بالكتابة'),
                    })
                
                # في حالة عدم وجود مشاكل
                if os.access(file_path, os.R_OK):
                    success.append({
                        'title': _('أذونات الملف صحيحة للقراءة'),
                        'description': _('الملف {path} لديه أذونات قراءة صحيحة').format(path=file_path),
                    })
            else:
                if str(file_path).endswith('db.sqlite3'):
                    # إذا كان يستخدم PostgreSQL، فلا داعي لملف SQLite
                    if 'postgresql' in settings.DATABASES['default']['ENGINE']:
                        success.append({
                            'title': _('لا حاجة لملف SQLite'),
                            'description': _('النظام يستخدم PostgreSQL، لذا لا حاجة لملف db.sqlite3'),
                        })
                    else:
                        issues.append({
                            'title': _('ملف قاعدة البيانات مفقود'),
                            'description': _('ملف قاعدة البيانات SQLite غير موجود: {path}').format(path=file_path),
                            'solution': _('استعد ملف قاعدة البيانات من النسخة الاحتياطية أو أعد تهيئة قاعدة البيانات'),
                            'severity': 'critical',
                            'issue_id': 'sqlite_db_missing',
                        })
                else:
                    warnings.append({
                        'title': _('ملف مهم غير موجود'),
                        'description': _('الملف المهم غير موجود: {path}').format(path=file_path),
                        'solution': _('قم باستعادة الملف المفقود')
                    })
        
        # فحص أذونات مجلدات الوسائط بعمق
        if os.path.exists(settings.MEDIA_ROOT):
            try:
                # قم بعمل اختبار كتابة ملف صغير
                test_file_path = os.path.join(settings.MEDIA_ROOT, 'permission_test.txt')
                try:
                    with open(test_file_path, 'w') as f:
                        f.write('test')
                    os.remove(test_file_path)
                    success.append({
                        'title': _('اختبار الكتابة في مجلد الوسائط ناجح'),
                        'description': _('يمكن للنظام الكتابة في مجلد الوسائط بنجاح')
                    })
                except PermissionError:
                    issues.append({
                        'title': _('فشل اختبار الكتابة في مجلد الوسائط'),
                        'description': _('لا يمكن للنظام الكتابة في مجلد الوسائط: {path}').format(path=settings.MEDIA_ROOT),
                        'solution': _('قم بتغيير أذونات مجلد الوسائط للسماح بالكتابة'),
                        'severity': 'high',
                        'issue_id': 'media_write_test_failed',
                    })
                except Exception as e:
                    issues.append({
                        'title': _('خطأ في اختبار الكتابة في مجلد الوسائط'),
                        'description': _('حدث خطأ أثناء اختبار الكتابة في مجلد الوسائط: {error}').format(error=str(e)),
                        'solution': _('تحقق من أذونات مجلد الوسائط وحالته'),
                        'severity': 'medium',
                        'issue_id': 'media_write_test_error',
                    })
            except Exception as e:
                issues.append({
                    'title': _('خطأ في اختبار أذونات مجلد الوسائط'),
                    'description': _('حدث خطأ أثناء اختبار أذونات مجلد الوسائط: {error}').format(error=str(e)),
                    'solution': _('تحقق من حالة مجلد الوسائط'),
                    'severity': 'medium',
                    'issue_id': 'media_permission_test_error',
                })
        
        # فحص أذونات المجلدات المؤقتة
        temp_dir = settings.TEMP_DIR if hasattr(settings, 'TEMP_DIR') else os.path.join(settings.BASE_DIR, 'temp')
        if os.path.exists(temp_dir):
            try:
                # قم بعمل اختبار كتابة ملف صغير
                test_file_path = os.path.join(temp_dir, 'permission_test.txt')
                try:
                    with open(test_file_path, 'w') as f:
                        f.write('test')
                    os.remove(test_file_path)
                    success.append({
                        'title': _('اختبار الكتابة في المجلد المؤقت ناجح'),
                        'description': _('يمكن للنظام الكتابة في المجلد المؤقت بنجاح')
                    })
                except PermissionError:
                    issues.append({
                        'title': _('فشل اختبار الكتابة في المجلد المؤقت'),
                        'description': _('لا يمكن للنظام الكتابة في المجلد المؤقت: {path}').format(path=temp_dir),
                        'solution': _('قم بتغيير أذونات المجلد المؤقت للسماح بالكتابة'),
                        'severity': 'high',
                        'issue_id': 'temp_write_test_failed',
                    })
                except Exception as e:
                    issues.append({
                        'title': _('خطأ في اختبار الكتابة في المجلد المؤقت'),
                        'description': _('حدث خطأ أثناء اختبار الكتابة في المجلد المؤقت: {error}').format(error=str(e)),
                        'solution': _('تحقق من أذونات المجلد المؤقت وحالته'),
                        'severity': 'medium',
                        'issue_id': 'temp_write_test_error',
                    })
            except Exception as e:
                issues.append({
                    'title': _('خطأ في اختبار أذونات المجلد المؤقت'),
                    'description': _('حدث خطأ أثناء اختبار أذونات المجلد المؤقت: {error}').format(error=str(e)),
                    'solution': _('تحقق من حالة المجلد المؤقت'),
                    'severity': 'medium',
                    'issue_id': 'temp_permission_test_error',
                })
    
    except Exception as e:
        issues.append({
            'title': _('خطأ أثناء فحص الأذونات'),
            'description': _('حدث خطأ غير متوقع أثناء إجراء فحص الأذونات: {error}').format(error=str(e)),
            'solution': _('تحقق من سجلات الأخطاء للحصول على مزيد من المعلومات'),
            'severity': 'high',
            'issue_id': 'permission_check_error',
        })
    
    # تجميع الإحصائيات
    stats = {
        'total_issues': len(issues),
        'total_warnings': len(warnings),
        'total_success': len(success)
    }
    
    return {
        'issues': issues,
        'warnings': warnings,
        'success': success,
        'stats': stats
    }
    
def run_cache_check():
    """تشغيل فحص ذاكرة التخزين المؤقت"""
    issues = []
    warnings = []
    success = []
    
    try:
        # فحص وجود مجلد cache
        cache_dirs = []
        
        # مجلدات الكاش المعروفة
        cache_patterns = [
            os.path.join(settings.BASE_DIR, '__pycache__'),
            os.path.join(settings.BASE_DIR, 'rental', '__pycache__'),
            os.path.join(settings.BASE_DIR, '.cache'),
            os.path.join(settings.BASE_DIR, 'staticfiles'),
        ]
        
        # البحث عن جميع مجلدات __pycache__
        for root, dirnames, _ in os.walk(settings.BASE_DIR):
            for dirname in dirnames:
                if dirname == '__pycache__':
                    cache_dirs.append(os.path.join(root, dirname))
        
        if not cache_dirs and not any(os.path.exists(p) for p in cache_patterns):
            success.append({
                'title': _('لا توجد مجلدات تخزين مؤقت'),
                'description': _('لم يتم العثور على مجلدات تخزين مؤقت في المشروع')
            })
        else:
            # حساب حجم ملفات التخزين المؤقت
            total_size = 0
            file_count = 0
            
            # فحص المجلدات المكتشفة
            for cache_dir in cache_dirs:
                if os.path.exists(cache_dir):
                    dir_size = 0
                    dir_files = 0
                    
                    for root, _, filenames in os.walk(cache_dir):
                        for filename in filenames:
                            file_path = os.path.join(root, filename)
                            if os.path.exists(file_path):
                                try:
                                    file_size = os.path.getsize(file_path)
                                    dir_size += file_size
                                    dir_files += 1
                                except Exception:
                                    pass
                    
                    total_size += dir_size
                    file_count += dir_files
            
            # فحص المجلدات المعروفة
            for cache_pattern in cache_patterns:
                if os.path.exists(cache_pattern) and os.path.isdir(cache_pattern):
                    dir_size = 0
                    dir_files = 0
                    
                    for root, _, filenames in os.walk(cache_pattern):
                        for filename in filenames:
                            file_path = os.path.join(root, filename)
                            if os.path.exists(file_path):
                                try:
                                    file_size = os.path.getsize(file_path)
                                    dir_size += file_size
                                    dir_files += 1
                                except Exception:
                                    pass
                    
                    total_size += dir_size
                    file_count += dir_files
            
            # تحويل إلى ميجابايت
            size_mb = total_size / (1024 * 1024)
            
            if size_mb > 100:  # أكثر من 100 ميجابايت
                warnings.append({
                    'title': _('حجم ملفات التخزين المؤقت كبير'),
                    'description': _('حجم ملفات التخزين المؤقت {size:.2f} ميجابايت ({files} ملف)').format(
                        size=size_mb, files=file_count),
                    'solution': _('قم بتنظيف ملفات التخزين المؤقت باستخدام أداة التنظيف')
                })
            else:
                success.append({
                    'title': _('حجم ملفات التخزين المؤقت مقبول'),
                    'description': _('حجم ملفات التخزين المؤقت {size:.2f} ميجابايت ({files} ملف)').format(
                        size=size_mb, files=file_count),
                })
        
        # فحص إعدادات Django للتخزين المؤقت
        cache_backend = settings.CACHES.get('default', {}).get('BACKEND', '')
        
        if 'LocMemCache' in cache_backend or 'DummyCache' in cache_backend:
            warnings.append({
                'title': _('إعدادات التخزين المؤقت غير مثالية'),
                'description': _('يستخدم النظام {backend} كنظام تخزين مؤقت').format(backend=cache_backend),
                'solution': _('فكر في استخدام Redis أو Memcached لتحسين الأداء في بيئة الإنتاج')
            })
        elif 'Redis' in cache_backend or 'Memcached' in cache_backend:
            success.append({
                'title': _('إعدادات التخزين المؤقت مثالية'),
                'description': _('يستخدم النظام {backend} للتخزين المؤقت').format(backend=cache_backend),
            })
            
            # فحص اتصال Redis/Memcached
            try:
                from django.core.cache import cache
                cache.set('diagnostics_test', 'test', 10)
                test_value = cache.get('diagnostics_test')
                
                if test_value == 'test':
                    success.append({
                        'title': _('نظام التخزين المؤقت يعمل بشكل صحيح'),
                        'description': _('تم الاتصال بنظام التخزين المؤقت {backend} بنجاح').format(backend=cache_backend),
                    })
                else:
                    issues.append({
                        'title': _('مشكلة في نظام التخزين المؤقت'),
                        'description': _('فشل اختبار الكتابة والقراءة من نظام التخزين المؤقت {backend}').format(
                            backend=cache_backend),
                        'solution': _('تحقق من إعدادات الاتصال بنظام التخزين المؤقت'),
                        'severity': 'medium',
                        'issue_id': 'cache_test_failed',
                    })
            except Exception as e:
                issues.append({
                    'title': _('خطأ في الاتصال بنظام التخزين المؤقت'),
                    'description': _('حدث خطأ أثناء محاولة الاتصال بنظام التخزين المؤقت: {error}').format(
                        error=str(e)),
                    'solution': _('تحقق من إعدادات الاتصال بنظام التخزين المؤقت'),
                    'severity': 'medium',
                    'issue_id': 'cache_connection_error',
                })
        
        # فحص ملفات .pyc القديمة
        try:
            stale_pyc_files = []
            py_files_map = {}
            
            # جمع معلومات عن ملفات .py
            for root, _, filenames in os.walk(settings.BASE_DIR):
                for filename in filenames:
                    if filename.endswith('.py'):
                        file_path = os.path.join(root, filename)
                        py_files_map[file_path] = os.path.getmtime(file_path)
            
            # فحص ملفات .pyc
            for root, _, filenames in os.walk(settings.BASE_DIR):
                for filename in filenames:
                    if filename.endswith('.pyc'):
                        pyc_path = os.path.join(root, filename)
                        py_path = pyc_path.replace('.pyc', '.py')
                        
                        # إذا لم يكن هناك ملف .py مقابل، أو كان ملف .pyc أقدم من ملف .py
                        if py_path not in py_files_map or os.path.getmtime(pyc_path) < py_files_map[py_path]:
                            stale_pyc_files.append(pyc_path)
            
            if stale_pyc_files:
                warnings.append({
                    'title': _('ملفات .pyc قديمة'),
                    'description': _('تم العثور على {count} ملفات .pyc قديمة').format(count=len(stale_pyc_files)),
                    'solution': _('قم بتنظيف ملفات .pyc القديمة')
                })
        except Exception:
            # تجاهل أخطاء فحص ملفات .pyc
            pass
    
    except Exception as e:
        issues.append({
            'title': _('خطأ أثناء فحص ذاكرة التخزين المؤقت'),
            'description': _('حدث خطأ غير متوقع أثناء فحص ذاكرة التخزين المؤقت: {error}').format(error=str(e)),
            'solution': _('تحقق من سجلات الأخطاء للحصول على مزيد من المعلومات'),
            'severity': 'medium',
            'issue_id': 'cache_check_error',
        })
    
    return {
        'issues': issues,
        'warnings': warnings,
        'success': success
    }
    
