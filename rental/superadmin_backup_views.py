import os
import re
import json
import shutil
import zipfile
import tempfile
import datetime
import subprocess
import django
from pathlib import Path

from django.http import HttpResponse, FileResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.utils.translation import gettext as _
from django.conf import settings
from django.utils import timezone
from django.core import management
from django.db import connection

from .models import User
from .models_superadmin import AdminUser

# Import system models, with fallback for testing
try:
    from .models_system import SystemBackup, ScheduledJob
except ImportError:
    # Define minimal fallback classes for development
    class SystemBackup:
        objects = None
    
    class ScheduledJob:
        objects = None

# الدالة المساعدة للتحقق من صلاحيات المسؤول الأعلى
def is_superadmin(user):
    try:
        admin_user = AdminUser.objects.get(user=user)
        return admin_user.is_superadmin
    except AdminUser.DoesNotExist:
        return False

@login_required
def backup_system(request):
    """صفحة مدير النسخ الاحتياطي"""
    if not is_superadmin(request.user):
        messages.error(request, _('ليس لديك صلاحية الوصول إلى هذه الصفحة'))
        return redirect('superadmin_dashboard')
    
    # الحصول على قائمة النسخ الاحتياطية
    backups = SystemBackup.objects.all().order_by('-created_at')
    
    # الحصول على المهام المجدولة المتعلقة بالنسخ الاحتياطي
    scheduled_backups = ScheduledJob.objects.filter(job_type='backup').order_by('next_run')
    
    # إعداد السياق
    context = {
        'backups': backups,
        'scheduled_backups': scheduled_backups,
        'backup_count': backups.count(),
        'total_backup_size': sum(backup.file_size for backup in backups),
        'last_backup': backups.first(),
        'title': _('إدارة النسخ الاحتياطي'),
    }
    
    return render(request, 'superadmin/backup/index.html', context)

@login_required
def create_backup(request):
    """إنشاء نسخة احتياطية جديدة"""
    if not is_superadmin(request.user):
        messages.error(request, _('ليس لديك صلاحية لإنشاء نسخة احتياطية'))
        return redirect('superadmin_backup')
    
    # إنشاء اسم للنسخة الاحتياطية
    timestamp = timezone.now().strftime('%Y%m%d_%H%M%S')
    backup_name = f"backup_{timestamp}"
    
    # التأكد من وجود مجلد النسخ الاحتياطية
    backup_dir = os.path.join(settings.MEDIA_ROOT, 'backups')
    os.makedirs(backup_dir, exist_ok=True)
    
    # إنشاء مسار ملف النسخة الاحتياطية
    backup_file_path = os.path.join(backup_dir, f"{backup_name}.zip")
    
    # إنشاء سجل النسخة الاحتياطية في قاعدة البيانات
    backup = SystemBackup.objects.create(
        name=backup_name,
        file_path=backup_file_path,
        status='pending',
        created_by=request.user
    )
    
    try:
        # التأكد من أن مجلد temp موجود وقابل للكتابة
        temp_dir = tempfile.gettempdir()
        os.makedirs(temp_dir, exist_ok=True)
        
        # التحقق من وجود مجلد النسخ الاحتياطية
        if not os.path.exists(backup_dir):
            os.makedirs(backup_dir, exist_ok=True)
        
        # إنشاء ملف النسخة الاحتياطية
        with zipfile.ZipFile(backup_file_path, 'w', zipfile.ZIP_DEFLATED) as backup_zip:
            # إضافة معلومات النسخة الاحتياطية
            backup_info = {
                "name": backup_name,
                "created_at": timezone.now().isoformat(),
                "created_by": request.user.username,
                "django_version": django.__version__,
                "database_engine": settings.DATABASES['default']['ENGINE'],
                "backup_type": "full",
                "timestamp": int(timezone.now().timestamp()),
            }
            backup_zip.writestr('backup_info.json', json.dumps(backup_info, indent=4))
            
            # إضافة نسخة احتياطية لقاعدة البيانات
            try:
                temp_db_file = os.path.join(temp_dir, 'db_backup.json')
                management.call_command('dumpdata', output=temp_db_file, exclude=['contenttypes', 'auth.permission'])
                
                # التحقق من إنشاء الملف بنجاح
                if os.path.exists(temp_db_file):
                    backup_zip.write(temp_db_file, 'db_backup.json')
                    os.unlink(temp_db_file)
                else:
                    raise Exception(_("فشل في إنشاء ملف قاعدة البيانات المؤقت"))
            except Exception as db_error:
                raise Exception(_("خطأ في نسخ قاعدة البيانات: {}").format(str(db_error)))
            
            # إضافة الملفات المهمة
            try:
                media_files_count = 0
                for root, _, files in os.walk(settings.MEDIA_ROOT):
                    if 'backups' in root.split(os.sep):
                        continue  # تخطي مجلد النسخ الاحتياطية نفسه
                    
                    for file in files:
                        file_path = os.path.join(root, file)
                        # تخطي الملفات التي لا يمكن قراءتها
                        if not os.path.exists(file_path) or not os.access(file_path, os.R_OK):
                            continue
                        
                        try:
                            archive_path = os.path.relpath(file_path, settings.BASE_DIR)
                            backup_zip.write(file_path, archive_path)
                            media_files_count += 1
                        except Exception:
                            # تخطي الملفات التي تسبب أخطاء
                            continue
                
                backup_info["media_files_count"] = media_files_count
                backup_zip.writestr('backup_info.json', json.dumps(backup_info, indent=4))
            except Exception as media_error:
                # تسجيل الخطأ ولكن لا نفشل العملية بالكامل
                backup.notes = _("تم إنشاء النسخة الاحتياطية لقاعدة البيانات ولكن بعض ملفات الوسائط قد لا تكون مكتملة.")
        
        # تحديث حجم الملف وحالة النسخة الاحتياطية
        if os.path.exists(backup_file_path):
            backup.file_size = os.path.getsize(backup_file_path)
            backup.status = 'completed'
            backup.save()
            
            messages.success(request, _('تم إنشاء نسخة احتياطية بنجاح'))
        else:
            raise Exception(_("لم يتم إنشاء ملف النسخة الاحتياطية"))
    except Exception as e:
        # في حالة حدوث خطأ
        backup.status = 'failed'
        backup.notes = str(e)
        backup.save()
        messages.error(request, _('حدث خطأ أثناء إنشاء النسخة الاحتياطية: {}').format(str(e)))
    
    return redirect('superadmin_backup')

@login_required
def restore_backup(request, backup_id):
    """استعادة نسخة احتياطية"""
    if not is_superadmin(request.user):
        messages.error(request, _('ليس لديك صلاحية لاستعادة النسخ الاحتياطية'))
        return redirect('superadmin_backup')
    
    # الحصول على النسخة الاحتياطية
    backup = get_object_or_404(SystemBackup, id=backup_id)
    
    # التحقق من حالة النسخة الاحتياطية
    if backup.status != 'completed':
        messages.error(request, _('لا يمكن استعادة نسخة احتياطية غير مكتملة'))
        return redirect('superadmin_backup')
    
    # التحقق من وجود ملف النسخة الاحتياطية
    if not os.path.exists(backup.file_path):
        messages.error(request, _('ملف النسخة الاحتياطية غير موجود'))
        return redirect('superadmin_backup')
    
    if request.method == 'POST':
        try:
            # فتح ملف النسخة الاحتياطية
            with zipfile.ZipFile(backup.file_path, 'r') as backup_zip:
                # استخراج معلومات النسخة الاحتياطية
                backup_info = json.loads(backup_zip.read('backup_info.json'))
                
                # استعادة قاعدة البيانات
                temp_db_file = os.path.join(tempfile.gettempdir(), 'db_restore.json')
                backup_zip.extract('db_backup.json', path=tempfile.gettempdir())
                os.rename(os.path.join(tempfile.gettempdir(), 'db_backup.json'), temp_db_file)
                
                # إعادة تعيين قاعدة البيانات
                management.call_command('flush', interactive=False)
                management.call_command('loaddata', temp_db_file)
                os.unlink(temp_db_file)
                
                # استعادة الملفات
                for zip_info in backup_zip.infolist():
                    if zip_info.filename.startswith('media/') and not zip_info.filename.endswith('/'):
                        backup_zip.extract(zip_info, path=settings.BASE_DIR)
            
            # تحديث حالة النسخة الاحتياطية
            backup.status = 'restored'
            backup.notes = _('تمت الاستعادة بواسطة %(user)s في %(date)s') % {
                'user': request.user.username,
                'date': timezone.now().strftime('%Y-%m-%d %H:%M:%S')
            }
            backup.save()
            
            messages.success(request, _('تمت استعادة النسخة الاحتياطية بنجاح'))
        except Exception as e:
            messages.error(request, _('حدث خطأ أثناء استعادة النسخة الاحتياطية: %(error)s') % {'error': str(e)})
        
        return redirect('superadmin_backup')
    
    # عرض صفحة تأكيد الاستعادة
    return render(request, 'superadmin/backup/confirm_restore.html', {'backup': backup})

@login_required
def download_backup(request, backup_id):
    """تنزيل ملف النسخة الاحتياطية"""
    if not is_superadmin(request.user):
        messages.error(request, _('ليس لديك صلاحية لتنزيل النسخ الاحتياطية'))
        return redirect('superadmin_backup')
    
    # الحصول على النسخة الاحتياطية
    backup = get_object_or_404(SystemBackup, id=backup_id)
    
    # التحقق من وجود ملف النسخة الاحتياطية
    if not os.path.exists(backup.file_path):
        messages.error(request, _('ملف النسخة الاحتياطية غير موجود'))
        return redirect('superadmin_backup')
    
    # استخراج اسم الملف من المسار
    filename = os.path.basename(backup.file_path)
    
    # إرجاع الملف كاستجابة للتنزيل
    return FileResponse(open(backup.file_path, 'rb'), as_attachment=True, filename=filename)

@login_required
def delete_backup(request, backup_id):
    """حذف نسخة احتياطية"""
    if not is_superadmin(request.user):
        messages.error(request, _('ليس لديك صلاحية لحذف النسخ الاحتياطية'))
        return redirect('superadmin_backup')
    
    # الحصول على النسخة الاحتياطية
    backup = get_object_or_404(SystemBackup, id=backup_id)
    
    if request.method == 'POST':
        # حذف ملف النسخة الاحتياطية إذا كان موجوداً
        if os.path.exists(backup.file_path):
            os.remove(backup.file_path)
        
        # حذف سجل النسخة الاحتياطية من قاعدة البيانات
        backup.delete()
        
        messages.success(request, _('تم حذف النسخة الاحتياطية بنجاح'))
        return redirect('superadmin_backup')
    
    # عرض صفحة تأكيد الحذف
    return render(request, 'superadmin/backup/confirm_delete.html', {'backup': backup})
