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
    """الحصول على إحصائيات النظام"""
    # إحصائيات نظام التشغيل
    cpu_usage = psutil.cpu_percent(interval=1)
    memory = psutil.virtual_memory()
    disk = psutil.disk_usage('/')
    
    # إحصائيات قاعدة البيانات
    db_size = get_database_size()
    db_connections = connection.settings_dict['CONN_MAX_AGE']
    
    stats = {
        'os_info': f"{os.name} {sys.platform}",
        'python_version': sys.version.split(' ')[0],
        'django_version': django.__version__,
        'cpu_usage': cpu_usage,
        'memory_usage': memory.percent,
        'memory_total': f"{memory.total / (1024**3):.2f} GB",
        'memory_available': f"{memory.available / (1024**3):.2f} GB",
        'disk_usage': disk.percent,
        'disk_total': f"{disk.total / (1024**3):.2f} GB",
        'disk_free': f"{disk.free / (1024**3):.2f} GB",
        'db_size': db_size,
        'db_type': settings.DATABASES['default']['ENGINE'].split('.')[-1],
        'db_connections': db_connections if db_connections is not None else _('غير محدد'),
        'uptime': get_system_uptime(),
    }
    
    return stats

def get_database_size():
    """الحصول على حجم قاعدة البيانات"""
    try:
        db_engine = settings.DATABASES['default']['ENGINE']
        db_name = settings.DATABASES['default']['NAME']
        
        if 'sqlite3' in db_engine:
            # قاعدة بيانات SQLite
            if os.path.exists(db_name):
                size_bytes = os.path.getsize(db_name)
                return f"{size_bytes / (1024**2):.2f} MB"
            return "0 MB"
        elif 'postgresql' in db_engine:
            # قاعدة بيانات PostgreSQL
            with connection.cursor() as cursor:
                cursor.execute("SELECT pg_database_size(%s)", [db_name])
                size_bytes = cursor.fetchone()[0]
                return f"{size_bytes / (1024**2):.2f} MB"
        
        return _('غير متاح')
    except Exception as e:
        return _('غير متاح')

def get_system_uptime():
    """الحصول على مدة تشغيل النظام"""
    try:
        boot_time = datetime.datetime.fromtimestamp(psutil.boot_time())
        uptime = datetime.datetime.now() - boot_time
        days = uptime.days
        hours, remainder = divmod(uptime.seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        
        if days > 0:
            return f"{days} {_('يوم')} {hours} {_('ساعة')} {minutes} {_('دقيقة')}"
        else:
            return f"{hours} {_('ساعة')} {minutes} {_('دقيقة')} {seconds} {_('ثانية')}"
    except Exception as e:
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
    """تشغيل فحص النظام"""
    issues = []
    warnings = []
    success = []
    
    # فحص مساحة القرص
    disk = psutil.disk_usage('/')
    if disk.percent > 90:
        issues.append({
            'title': _('مساحة القرص منخفضة جداً'),
            'description': _('مساحة القرص المتبقية {free_space} فقط من أصل {total_space}').format(
                free_space=f"{disk.free / (1024**3):.2f} GB",
                total_space=f"{disk.total / (1024**3):.2f} GB"
            ),
            'solution': _('حرر مساحة على القرص بحذف الملفات غير الضرورية'),
            'severity': 'critical',
            'issue_id': 'disk_space_low',
        })
    elif disk.percent > 80:
        warnings.append({
            'title': _('مساحة القرص منخفضة'),
            'description': _('مساحة القرص المتبقية {free_space} من أصل {total_space}').format(
                free_space=f"{disk.free / (1024**3):.2f} GB",
                total_space=f"{disk.total / (1024**3):.2f} GB"
            ),
            'solution': _('فكر في تحرير مساحة على القرص قريباً'),
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
    
    # فحص استخدام المعالج
    cpu_usage = psutil.cpu_percent(interval=1)
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
            'title': _('استخدام المعالج طبيعي'),
            'description': _('استخدام المعالج الحالي {cpu_usage}%').format(cpu_usage=cpu_usage),
        })
    
    # فحص استخدام الذاكرة
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

def run_database_check():
    """تشغيل فحص قاعدة البيانات"""
    issues = []
    warnings = []
    success = []
    
    # التحقق من نوع قاعدة البيانات
    db_engine = settings.DATABASES['default']['ENGINE']
    db_name = settings.DATABASES['default']['NAME']
    
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
    
    # التحقق من وجود مجلد MEDIA_ROOT
    if not os.path.exists(settings.MEDIA_ROOT):
        issues.append({
            'title': _('مجلد الوسائط غير موجود'),
            'description': _('مجلد الوسائط {media_root} غير موجود').format(media_root=settings.MEDIA_ROOT),
            'solution': _('قم بإنشاء مجلد الوسائط'),
            'severity': 'high',
            'issue_id': 'missing_media_root',
        })
    else:
        success.append({
            'title': _('مجلد الوسائط موجود'),
            'description': _('مجلد الوسائط {media_root} موجود').format(media_root=settings.MEDIA_ROOT),
        })
        
        # فحص أذونات مجلد الوسائط
        if not os.access(settings.MEDIA_ROOT, os.W_OK):
            issues.append({
                'title': _('لا توجد أذونات كتابة لمجلد الوسائط'),
                'description': _('لا توجد أذونات كتابة لمجلد الوسائط {media_root}').format(media_root=settings.MEDIA_ROOT),
                'solution': _('قم بتغيير أذونات مجلد الوسائط للسماح بالكتابة'),
                'severity': 'high',
                'issue_id': 'media_root_not_writable',
            })
        else:
            success.append({
                'title': _('أذونات كتابة لمجلد الوسائط صحيحة'),
                'description': _('يمكن الكتابة إلى مجلد الوسائط {media_root}').format(media_root=settings.MEDIA_ROOT),
            })
    
    # التحقق من وجود مجلد STATIC_ROOT إذا كان محدداً
    if hasattr(settings, 'STATIC_ROOT') and settings.STATIC_ROOT:
        if not os.path.exists(settings.STATIC_ROOT):
            warnings.append({
                'title': _('مجلد الملفات الثابتة غير موجود'),
                'description': _('مجلد الملفات الثابتة {static_root} غير موجود').format(static_root=settings.STATIC_ROOT),
                'solution': _('قم بتشغيل أمر collectstatic لإنشاء مجلد الملفات الثابتة'),
            })
        else:
            success.append({
                'title': _('مجلد الملفات الثابتة موجود'),
                'description': _('مجلد الملفات الثابتة {static_root} موجود').format(static_root=settings.STATIC_ROOT),
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
                    area='media',
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

def run_cache_check():
    """تشغيل فحص ذاكرة التخزين المؤقت"""
    issues = []
    warnings = []
    success = []
    
    # فحص إعدادات ذاكرة التخزين المؤقت
    cache_backend = settings.CACHES.get('default', {}).get('BACKEND', '')
    if not cache_backend:
        warnings.append({
            'title': _('لم يتم تعريف ذاكرة التخزين المؤقت'),
            'description': _('لم يتم تعريف ذاكرة التخزين المؤقت في إعدادات Django'),
            'solution': _('قم بتعريف ذاكرة التخزين المؤقت لتحسين أداء النظام'),
        })
    else:
        success.append({
            'title': _('تم تعريف ذاكرة التخزين المؤقت'),
            'description': _('ذاكرة التخزين المؤقت معرفة باستخدام {backend}').format(backend=cache_backend.split('.')[-1]),
        })
    
    # التحقق من ملفات __pycache__
    pycache_count = 0
    for root, dirs, files in os.walk(settings.BASE_DIR):
        if '__pycache__' in dirs:
            pycache_count += 1
    
    if pycache_count > 50:  # عتبة افتراضية
        warnings.append({
            'title': _('عدد كبير من مجلدات __pycache__'),
            'description': _('تم العثور على {count} مجلد __pycache__').format(count=pycache_count),
            'solution': _('قم بتنظيف مجلدات __pycache__ لتوفير مساحة وتحسين الأداء'),
        })
    else:
        success.append({
            'title': _('عدد طبيعي من مجلدات __pycache__'),
            'description': _('تم العثور على {count} مجلد __pycache__').format(count=pycache_count),
        })
    
    return {
        'issues': issues,
        'warnings': warnings,
        'success': success,
    }

def run_permission_check():
    """تشغيل فحص الأذونات"""
    issues = []
    warnings = []
    success = []
    
    # فحص أذونات مجلد المشروع
    project_dir_writable = os.access(settings.BASE_DIR, os.W_OK)
    if not project_dir_writable:
        issues.append({
            'title': _('لا توجد أذونات كتابة لمجلد المشروع'),
            'description': _('لا توجد أذونات كتابة لمجلد المشروع {base_dir}').format(base_dir=settings.BASE_DIR),
            'solution': _('قم بتغيير أذونات مجلد المشروع للسماح بالكتابة'),
            'severity': 'high',
            'issue_id': 'project_dir_not_writable',
        })
    else:
        success.append({
            'title': _('أذونات كتابة لمجلد المشروع صحيحة'),
            'description': _('يمكن الكتابة إلى مجلد المشروع {base_dir}').format(base_dir=settings.BASE_DIR),
        })
    
    # فحص أذونات ملف قاعدة البيانات إذا كانت SQLite
    db_engine = settings.DATABASES['default']['ENGINE']
    if 'sqlite3' in db_engine:
        db_file = settings.DATABASES['default']['NAME']
        if os.path.exists(db_file):
            db_file_writable = os.access(db_file, os.W_OK)
            if not db_file_writable:
                issues.append({
                    'title': _('لا توجد أذونات كتابة لملف قاعدة البيانات SQLite'),
                    'description': _('لا توجد أذونات كتابة لملف قاعدة البيانات {db_file}').format(db_file=db_file),
                    'solution': _('قم بتغيير أذونات ملف قاعدة البيانات للسماح بالكتابة'),
                    'severity': 'high',
                    'issue_id': 'db_file_not_writable',
                })
            else:
                success.append({
                    'title': _('أذونات كتابة لملف قاعدة البيانات SQLite صحيحة'),
                    'description': _('يمكن الكتابة إلى ملف قاعدة البيانات {db_file}').format(db_file=db_file),
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
                    area='permissions',
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
def fix_system_issue(request, issue_id):
    """معالجة مشكلة النظام"""
    if not is_superadmin(request.user):
        messages.error(request, _('ليس لديك صلاحية لإصلاح مشاكل النظام'))
        return redirect('superadmin_diagnostics')
    
    # التحقق إذا كان issue_id رقمي (معرف قاعدة بيانات) أو نصي (معرف مشكلة)
    if issue_id.isdigit():
        # الحصول على المشكلة من قاعدة البيانات باستخدام المعرف
        issue = get_object_or_404(SystemIssue, id=issue_id)
    else:
        # الحصول على المشكلة من قاعدة البيانات باستخدام المعرف النصي (issue_id)
        issue = SystemIssue.objects.filter(title__contains=issue_id).first()
        if not issue:
            messages.error(request, _('المشكلة غير موجودة'))
            return redirect('superadmin_diagnostics')
    
    # التحقق من حالة المشكلة
    if issue.status == 'fixed':
        messages.error(request, _('هذه المشكلة تم إصلاحها بالفعل'))
        return redirect('superadmin_diagnostics')
    
    # محاولة إصلاح المشكلة
    success = False
    error_message = None
    
    try:
        # تنفيذ الإصلاح حسب نوع المشكلة
        if 'missing_media_root' in issue.title:
            # إنشاء مجلد الوسائط
            os.makedirs(settings.MEDIA_ROOT, exist_ok=True)
            success = True
        
        elif 'media_root_not_writable' in issue.title:
            # تغيير أذونات مجلد الوسائط
            subprocess.run(['chmod', '-R', '755', settings.MEDIA_ROOT])
            success = True
        
        elif 'db_file_not_writable' in issue.title:
            # تغيير أذونات ملف قاعدة البيانات
            db_file = settings.DATABASES['default']['NAME']
            if os.path.exists(db_file):
                subprocess.run(['chmod', '666', db_file])
                success = True
        
        elif 'disk_space_low' in issue.title:
            # تنظيف الملفات المؤقتة
            temp_dirs = ['/tmp', tempfile.gettempdir()]
            for temp_dir in temp_dirs:
                if os.path.exists(temp_dir):
                    subprocess.run(['find', temp_dir, '-type', 'f', '-mtime', '+7', '-delete'])
            
            # تنظيف ملفات __pycache__
            subprocess.run(['find', settings.BASE_DIR, '-name', '__pycache__', '-type', 'd', '-exec', 'rm', '-rf', '{}', '\;'])
            success = True
        
        else:
            # التعامل مع باقي أنواع المشاكل
            if 'database_integrity' in issue.title or issue_id == 'database_integrity':
                # محاولة إصلاح سلامة قاعدة البيانات
                try:
                    from django.core.management import call_command
                    call_command('migrate', verbosity=0)
                    call_command('check', '--database', 'default')
                    success = True
                except Exception as e:
                    error_message = str(e)
            
            elif 'cache_error' in issue.title or issue_id == 'cache_error':
                # تنظيف ذاكرة التخزين المؤقت
                try:
                    from django.core.cache import cache
                    cache.clear()
                    success = True
                except Exception as e:
                    error_message = str(e)
            
            elif 'media_files' in issue.title or issue_id == 'media_files':
                # إصلاح ملفات الوسائط المفقودة
                try:
                    os.makedirs(settings.MEDIA_ROOT, exist_ok=True)
                    os.makedirs(os.path.join(settings.MEDIA_ROOT, 'documents'), exist_ok=True)
                    os.makedirs(os.path.join(settings.MEDIA_ROOT, 'uploads'), exist_ok=True)
                    os.makedirs(os.path.join(settings.MEDIA_ROOT, 'profiles'), exist_ok=True)
                    success = True
                except Exception as e:
                    error_message = str(e)
            
            # مشكلة غير معروفة
            else:
                error_message = _('لا يوجد إصلاح تلقائي لهذه المشكلة')
        
        if success:
            # تحديث حالة المشكلة
            issue.status = 'fixed'
            issue.fixed_at = timezone.now()
            issue.fixed_by = request.user
            issue.fix_notes = _('تم إصلاحها تلقائياً بواسطة أداة التشخيص')
            issue.save()
            
            messages.success(request, _('تم إصلاح المشكلة بنجاح'))
        else:
            # تعيين حالة قيد المعالجة
            issue.status = 'in_progress'
            issue.save()
            
            messages.error(request, error_message or _('تعذر إصلاح المشكلة تلقائياً. يرجى الإصلاح يدوياً'))
    except Exception as e:
        # تسجيل الخطأ
        issue.fix_notes = f"{_('حدث خطأ أثناء محاولة الإصلاح')}: {str(e)}"
        issue.save()
        
        messages.error(request, _('حدث خطأ أثناء محاولة إصلاح المشكلة: {error}').format(error=str(e)))
    
    return redirect('superadmin_diagnostics')
