import json
import datetime
from croniter import croniter

from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.utils.translation import gettext as _
from django.utils import timezone
from django.core.exceptions import ValidationError
from django.forms import modelform_factory

from .models import User
from .models_superadmin import AdminUser

# Import system models, with fallback for testing
try:
    from .models_system import ScheduledJob
except ImportError:
    # Define minimal fallback class for development
    class ScheduledJob:
        objects = None
        JOB_TYPE_CHOICES = [
            ('backup', 'Backup'),
            ('cleanup', 'Cleanup'),
            ('report', 'Report'),
            ('custom', 'Custom'),
        ]
        
        INTERVAL_CHOICES = [
            ('hourly', 'Hourly'),
            ('daily', 'Daily'),
            ('weekly', 'Weekly'),
            ('monthly', 'Monthly'),
            ('custom', 'Custom'),
        ]

# الدالة المساعدة للتحقق من صلاحيات المسؤول الأعلى
def is_superadmin(user):
    try:
        admin_user = AdminUser.objects.get(user=user)
        return admin_user.is_superadmin
    except AdminUser.DoesNotExist:
        return False

# دالة لحساب وقت التشغيل التالي بناءً على نوع الفاصل الزمني
def calculate_next_run(interval_type, interval_value=1, cron_expression=None, base_time=None):
    if base_time is None:
        base_time = timezone.now()
    
    if interval_type == 'custom' and cron_expression:
        try:
            # استخدام croniter لحساب الوقت التالي بناءً على تعبير cron
            cron = croniter(cron_expression, base_time)
            return cron.get_next(datetime.datetime)
        except Exception as e:
            raise ValueError(f"تعبير cron غير صالح: {str(e)}")
    
    # حساب الوقت التالي بناءً على نوع الفاصل الزمني
    if interval_type == 'hourly':
        return base_time + datetime.timedelta(hours=interval_value)
    elif interval_type == 'daily':
        return base_time + datetime.timedelta(days=interval_value)
    elif interval_type == 'weekly':
        return base_time + datetime.timedelta(weeks=interval_value)
    elif interval_type == 'monthly':
        # حساب تقريبي للشهر (30 يوم)
        return base_time + datetime.timedelta(days=30 * interval_value)
    else:
        raise ValueError("نوع فاصل زمني غير مدعوم")

@login_required
def scheduler_dashboard(request):
    """لوحة تحكم جدولة المهام"""
    if not is_superadmin(request.user):
        messages.error(request, _('ليس لديك صلاحية الوصول إلى لوحة تحكم الجدولة'))
        return redirect('superadmin_dashboard')
    
    # الحصول على قائمة المهام المجدولة
    scheduled_jobs = ScheduledJob.objects.all().order_by('next_run')
    
    # تجميع إحصائيات المهام
    active_jobs = scheduled_jobs.filter(is_active=True).count()
    inactive_jobs = scheduled_jobs.filter(is_active=False).count()
    
    # تصنيف المهام حسب النوع
    job_types = {
        'backup': scheduled_jobs.filter(job_type='backup').count(),
        'cleanup': scheduled_jobs.filter(job_type='cleanup').count(),
        'report': scheduled_jobs.filter(job_type='report').count(),
        'custom': scheduled_jobs.filter(job_type='custom').count(),
    }
    
    context = {
        'jobs': scheduled_jobs,
        'active_jobs': active_jobs,
        'inactive_jobs': inactive_jobs,
        'job_types': job_types,
        'title': _('جدولة المهام'),
    }
    
    return render(request, 'superadmin/scheduler/index.html', context)

@login_required
def add_scheduled_job(request):
    """إضافة مهمة مجدولة جديدة"""
    if not is_superadmin(request.user):
        messages.error(request, _('ليس لديك صلاحية لإضافة مهام مجدولة'))
        return redirect('superadmin_scheduler')
    
    # إنشاء نموذج المهمة المجدولة
    JobForm = modelform_factory(
        ScheduledJob,
        fields=['name', 'job_type', 'function_name', 'interval_type', 'interval_value', 'cron_expression', 'is_active'],
    )
    
    if request.method == 'POST':
        form = JobForm(request.POST)
        if form.is_valid():
            job = form.save(commit=False)
            
            # إضافة معلومات إضافية
            job.created_by = request.user
            
            # تعيين المعاملات من النموذج
            args_json = request.POST.get('args_json', '{}')
            try:
                job.args = json.loads(args_json)
            except json.JSONDecodeError:
                job.args = {}
            
            # حساب وقت التشغيل التالي
            try:
                job.next_run = calculate_next_run(
                    job.interval_type,
                    job.interval_value,
                    job.cron_expression
                )
                job.save()
                messages.success(request, _('تمت إضافة المهمة المجدولة بنجاح'))
                return redirect('superadmin_scheduler')
            except Exception as e:
                form.add_error(None, str(e))
    else:
        # تعيين القيم الافتراضية
        initial_data = {
            'interval_type': 'daily',
            'interval_value': 1,
            'is_active': True,
        }
        form = JobForm(initial=initial_data)
    
    # إعداد السياق
    context = {
        'form': form,
        'title': _('إضافة مهمة مجدولة'),
        'job_types': dict(ScheduledJob.JOB_TYPE_CHOICES),
        'interval_types': dict(ScheduledJob.INTERVAL_CHOICES),
    }
    
    return render(request, 'superadmin/scheduler/job_form.html', context)

@login_required
def edit_scheduled_job(request, job_id):
    """تعديل مهمة مجدولة"""
    if not is_superadmin(request.user):
        messages.error(request, _('ليس لديك صلاحية لتعديل المهام المجدولة'))
        return redirect('superadmin_scheduler')
    
    # الحصول على المهمة المجدولة
    job = get_object_or_404(ScheduledJob, id=job_id)
    
    # إنشاء نموذج المهمة المجدولة
    JobForm = modelform_factory(
        ScheduledJob,
        fields=['name', 'job_type', 'function_name', 'interval_type', 'interval_value', 'cron_expression', 'is_active'],
    )
    
    if request.method == 'POST':
        form = JobForm(request.POST, instance=job)
        if form.is_valid():
            job = form.save(commit=False)
            
            # تعيين المعاملات من النموذج
            args_json = request.POST.get('args_json', '{}')
            try:
                job.args = json.loads(args_json)
            except json.JSONDecodeError:
                job.args = {}
            
            # حساب وقت التشغيل التالي
            try:
                job.next_run = calculate_next_run(
                    job.interval_type,
                    job.interval_value,
                    job.cron_expression
                )
                job.save()
                messages.success(request, _('تم تحديث المهمة المجدولة بنجاح'))
                return redirect('superadmin_scheduler')
            except Exception as e:
                form.add_error(None, str(e))
    else:
        form = JobForm(instance=job)
    
    # إعداد السياق
    context = {
        'form': form,
        'job': job,
        'args_json': json.dumps(job.args, indent=2) if job.args else '{}',
        'title': _('تعديل مهمة مجدولة'),
        'job_types': dict(ScheduledJob.JOB_TYPE_CHOICES),
        'interval_types': dict(ScheduledJob.INTERVAL_CHOICES),
    }
    
    return render(request, 'superadmin/scheduler/job_form.html', context)

@login_required
def delete_scheduled_job(request, job_id):
    """حذف مهمة مجدولة"""
    if not is_superadmin(request.user):
        messages.error(request, _('ليس لديك صلاحية لحذف المهام المجدولة'))
        return redirect('superadmin_scheduler')
    
    # الحصول على المهمة المجدولة
    job = get_object_or_404(ScheduledJob, id=job_id)
    
    if request.method == 'POST':
        # حذف المهمة المجدولة
        job.delete()
        messages.success(request, _('تم حذف المهمة المجدولة بنجاح'))
        return redirect('superadmin_scheduler')
    
    # عرض صفحة تأكيد الحذف
    return render(request, 'superadmin/scheduler/confirm_delete.html', {'job': job})

@login_required
def toggle_scheduled_job(request, job_id):
    """تفعيل/تعطيل مهمة مجدولة"""
    if not is_superadmin(request.user):
        messages.error(request, _('ليس لديك صلاحية لتعديل حالة المهام المجدولة'))
        return redirect('superadmin_scheduler')
    
    # الحصول على المهمة المجدولة
    job = get_object_or_404(ScheduledJob, id=job_id)
    
    # تبديل حالة المهمة
    job.is_active = not job.is_active
    job.save()
    
    status_message = _('تم تفعيل المهمة') if job.is_active else _('تم تعطيل المهمة')
    messages.success(request, f"{status_message}: {job.name}")
    
    return redirect('superadmin_scheduler')
