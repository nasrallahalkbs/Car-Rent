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
from django.forms import modelform_factory, ChoiceField, SelectMultiple, CharField

from .models import User
from .models_superadmin import AdminUser

# استيراد دالة المهام المتاحة من وحدة تنفيذ المهام المجدولة
try:
    from .scheduler_executor import AVAILABLE_FUNCTIONS
except ImportError:
    AVAILABLE_FUNCTIONS = {}

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
        
# قائمة المهام المتاحة مع الوصف والمعاملات الافتراضية
PREDEFINED_TASKS = {
    'create_backup': {
        'name': _('إنشاء نسخة احتياطية'),
        'job_type': 'backup',
        'description': _('إنشاء نسخة احتياطية لقاعدة البيانات وملفات النظام'),
        'default_args': {
            'backup_type': 'full',
            'include_media': True,
            'notify_admin': True
        }
    },
    'clean_system': {
        'name': _('تنظيف النظام'),
        'job_type': 'cleanup',
        'description': _('تنظيف الملفات المؤقتة وملفات السجلات القديمة'),
        'default_args': {
            'clean_temp': True,
            'clean_logs': True,
            'days_old': 30
        }
    },
    'clean_empty_documents': {
        'name': _('تنظيف المستندات الفارغة'),
        'job_type': 'cleanup',
        'description': _('حذف المستندات الفارغة والمستندات التلقائية'),
        'default_args': {
            'delete_empty': True,
            'days_old': 7
        }
    },
    'clean_cache_files': {
        'name': _('تنظيف ملفات الكاش'),
        'job_type': 'cleanup',
        'description': _('تنظيف ملفات الكاش وملفات __pycache__'),
        'default_args': {
            'clean_pycache': True,
            'clean_django_cache': True
        }
    },
    'generate_report': {
        'name': _('إنشاء تقرير'),
        'job_type': 'report',
        'description': _('إنشاء تقارير دورية للمبيعات والمستخدمين والحجوزات'),
        'default_args': {
            'report_type': 'sales',
            'format': 'pdf',
            'period': 'monthly'
        }
    },
    'send_reminder_emails': {
        'name': _('إرسال رسائل تذكير'),
        'job_type': 'custom',
        'description': _('إرسال رسائل تذكير للحجوزات والمدفوعات والمراجعات'),
        'default_args': {
            'reminder_type': 'reservation',
            'days_before': 1,
            'template_id': 'default_reminder'
        }
    },
    'archive_old_reservations': {
        'name': _('أرشفة الحجوزات القديمة'),
        'job_type': 'custom',
        'description': _('أرشفة الحجوزات القديمة المكتملة والملغاة'),
        'default_args': {
            'days_old': 90,
            'status_list': ['completed', 'cancelled']
        }
    },
    'update_exchange_rates': {
        'name': _('تحديث أسعار العملات'),
        'job_type': 'custom',
        'description': _('تحديث أسعار العملات من مصادر API خارجية'),
        'default_args': {
            'currency_list': ['USD', 'EUR', 'GBP'],
            'api_source': 'default'
        }
    }
}

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
    
    # إنشاء قائمة الوظائف المتاحة
    available_tasks = []
    for function_name, task_info in PREDEFINED_TASKS.items():
        available_tasks.append((function_name, task_info['name']))
    
    # إنشاء نموذج المهمة المجدولة
    JobForm = modelform_factory(
        ScheduledJob,
        fields=['job_type', 'interval_type', 'interval_value', 'cron_expression', 'is_active'],
    )
    
    if request.method == 'POST':
        # الحصول على الوظيفة المحددة
        selected_function = request.POST.get('predefined_task', '')
        
        # تعبئة النموذج
        form = JobForm(request.POST)
        
        if form.is_valid() and selected_function in PREDEFINED_TASKS:
            job = form.save(commit=False)
            
            # تعيين اسم الوظيفة والاسم من المهام المحددة مسبقًا
            task_info = PREDEFINED_TASKS[selected_function]
            job.function_name = selected_function
            job.name = task_info['name']
            
            # إضافة معلومات إضافية
            job.created_by = request.user
            
            # تعيين المعاملات من النموذج أو استخدام المعاملات الافتراضية
            args_json = request.POST.get('args_json', '{}')
            try:
                custom_args = json.loads(args_json)
                # إذا لم يتم تخصيص معاملات، استخدم المعاملات الافتراضية
                if not custom_args:
                    job.args = task_info['default_args']
                else:
                    job.args = custom_args
            except json.JSONDecodeError:
                # استخدام المعاملات الافتراضية في حالة الخطأ
                job.args = task_info['default_args']
            
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
            if not selected_function:
                messages.error(request, _('يجب اختيار وظيفة محددة'))
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
        'predefined_tasks': available_tasks,
        'task_descriptions': {func: info['description'] for func, info in PREDEFINED_TASKS.items()},
        'task_types': {func: info['job_type'] for func, info in PREDEFINED_TASKS.items()},
        'task_args': {func: json.dumps(info['default_args'], indent=2) for func, info in PREDEFINED_TASKS.items()},
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

@login_required
def run_job_now(request, job_id):
    """تنفيذ مهمة الآن (وضع الاختبار)"""
    if not is_superadmin(request.user):
        messages.error(request, _('ليس لديك صلاحية لتنفيذ المهام'))
        return redirect('superadmin_scheduler')
    
    # الحصول على المهمة المجدولة
    job = get_object_or_404(ScheduledJob, id=job_id)
    
    # تنفيذ المهمة
    try:
        from .scheduler_executor import execute_job
        result = execute_job(job)
        
        if result.get('status') == 'success':
            messages.success(request, _('تم تنفيذ المهمة بنجاح: ') + result.get('message', ''))
        else:
            messages.error(request, _('فشل تنفيذ المهمة: ') + result.get('message', ''))
            
    except Exception as e:
        messages.error(request, _('حدث خطأ أثناء تنفيذ المهمة: ') + str(e))
    
    return redirect('superadmin_scheduler')
