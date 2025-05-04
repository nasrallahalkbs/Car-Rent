from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils.translation import gettext_lazy as _
from django.db.models import Q
from django.core.paginator import Paginator
from django.http import HttpResponse
from django.utils import timezone
from django.views.decorators.http import require_POST
from django.urls import reverse

from rental.models_custody import CustomerGuarantee
from rental.models import Reservation, User, Car
from rental.forms_custody import (
    CustomerGuaranteeForm, 
    CustomerGuaranteeReturnForm,
    CustomerGuaranteeFilterForm
)

import datetime
import csv


@login_required
def custody_dashboard(request):
    """عرض لوحة تحكم إدارة العهدة"""
    
    # إحصائيات العهدة
    total_guarantees = CustomerGuarantee.objects.count()
    active_guarantees = CustomerGuarantee.objects.filter(status='active').count()
    returned_guarantees = CustomerGuarantee.objects.filter(status__in=['returned', 'partially_returned']).count()
    withheld_guarantees = CustomerGuarantee.objects.filter(status='withheld').count()
    
    # العهدات النشطة الأخيرة
    recent_guarantees = CustomerGuarantee.objects.filter(
        status='active'
    ).order_by('-created_at')[:5]
    
    # إجمالي قيمة العهدات النشطة
    total_active_value = CustomerGuarantee.objects.filter(
        status='active'
    ).values_list('value', flat=True)
    total_active_value_sum = sum(total_active_value)
    
    # العهدات المستردة مؤخرًا
    recent_returned = CustomerGuarantee.objects.filter(
        status__in=['returned', 'partially_returned']
    ).order_by('-return_date')[:5]
    
    context = {
        'total_guarantees': total_guarantees,
        'active_guarantees': active_guarantees,
        'returned_guarantees': returned_guarantees,
        'withheld_guarantees': withheld_guarantees,
        'recent_guarantees': recent_guarantees,
        'total_active_value_sum': total_active_value_sum,
        'recent_returned': recent_returned,
    }
    
    return render(request, 'admin/custody/dashboard.html', context)


@login_required
def custody_list(request):
    """عرض قائمة العهدات"""
    
    # نموذج التصفية
    filter_form = CustomerGuaranteeFilterForm(request.GET)
    
    # استرجاع العهدات
    guarantees = CustomerGuarantee.objects.all().order_by('-created_at')
    
    # تطبيق عوامل التصفية
    if filter_form.is_valid():
        data = filter_form.cleaned_data
        
        # البحث العام
        search = data.get('search')
        if search:
            guarantees = guarantees.filter(
                Q(name__icontains=search) | 
                Q(customer__first_name__icontains=search) | 
                Q(customer__last_name__icontains=search) | 
                Q(reservation__reservation_number__icontains=search) |
                Q(identifier__icontains=search)
            )
            
        # تصفية حسب الحالة
        status = data.get('status')
        if status:
            guarantees = guarantees.filter(status=status)
            
        # تصفية حسب نوع العهدة
        guarantee_type = data.get('guarantee_type')
        if guarantee_type:
            guarantees = guarantees.filter(guarantee_type=guarantee_type)
            
        # تصفية حسب نطاق التاريخ
        date_from = data.get('date_from')
        if date_from:
            guarantees = guarantees.filter(handover_date__gte=date_from)
            
        date_to = data.get('date_to')
        if date_to:
            guarantees = guarantees.filter(handover_date__lte=date_to)
    
    # التقسيم لصفحات
    paginator = Paginator(guarantees, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'filter_form': filter_form,
        'guarantees': page_obj,
    }
    
    return render(request, 'admin/custody/list.html', context)


@login_required
def custody_create(request):
    """إنشاء عهدة جديدة"""
    
    # إذا تم تمرير معرف الحجز، استخدمه للتعبئة المسبقة
    reservation_id = request.GET.get('reservation')
    customer_id = request.GET.get('customer')
    
    initial_data = {}
    
    if reservation_id:
        try:
            reservation = Reservation.objects.get(id=reservation_id)
            initial_data['reservation'] = reservation
            initial_data['customer'] = reservation.user
            initial_data['car'] = reservation.car
        except Reservation.DoesNotExist:
            pass
    elif customer_id:
        try:
            customer = User.objects.get(id=customer_id)
            initial_data['customer'] = customer
        except User.DoesNotExist:
            pass
    
    # دالة لإنشاء وعرض نموذج العهدة
    if request.method == 'POST':
        form = CustomerGuaranteeForm(request.POST)
        if form.is_valid():
            guarantee = form.save(commit=False)
            guarantee.created_by = request.user
            guarantee.save()
            
            messages.success(request, _('تم إنشاء العهدة بنجاح'))
            
            # الانتقال إما إلى قائمة العهدات أو إلى تفاصيل الحجز
            next_url = request.POST.get('next')
            if next_url:
                return redirect(next_url)
            return redirect('custody_detail', guarantee.id)
    else:
        form = CustomerGuaranteeForm(initial=initial_data)
    
    context = {
        'form': form,
        'is_add': True,
        'title': _('إضافة عهدة جديدة'),
        'next': request.GET.get('next', ''),
    }
    
    return render(request, 'admin/custody/form.html', context)


@login_required
def custody_detail(request, guarantee_id):
    """عرض تفاصيل العهدة"""
    
    guarantee = get_object_or_404(CustomerGuarantee, id=guarantee_id)
    
    # حساب المدة منذ تاريخ التسليم
    today = timezone.now().date()
    days_since_handover = (today - guarantee.handover_date).days
    
    context = {
        'guarantee': guarantee,
        'days_since_handover': days_since_handover,
    }
    
    return render(request, 'admin/custody/detail.html', context)


@login_required
def custody_edit(request, guarantee_id):
    """تعديل العهدة"""
    
    guarantee = get_object_or_404(CustomerGuarantee, id=guarantee_id)
    
    # لا يمكن تعديل العهدة إذا كانت مستردة
    if guarantee.status in ['returned', 'partially_returned']:
        messages.error(request, _('لا يمكن تعديل العهدة بعد استردادها'))
        return redirect('custody_detail', guarantee.id)
    
    if request.method == 'POST':
        form = CustomerGuaranteeForm(request.POST, instance=guarantee)
        if form.is_valid():
            form.save()
            messages.success(request, _('تم تحديث العهدة بنجاح'))
            return redirect('custody_detail', guarantee.id)
    else:
        form = CustomerGuaranteeForm(instance=guarantee)
    
    context = {
        'form': form,
        'is_add': False,
        'guarantee': guarantee,
        'title': _('تعديل العهدة'),
    }
    
    return render(request, 'admin/custody/form.html', context)


@login_required
def custody_return(request, guarantee_id):
    """استرداد العهدة"""
    
    guarantee = get_object_or_404(CustomerGuarantee, id=guarantee_id)
    
    # لا يمكن استرداد العهدة إذا كانت مستردة بالفعل
    if guarantee.status in ['returned', 'partially_returned']:
        messages.error(request, _('تم استرداد هذه العهدة مسبقاً'))
        return redirect('custody_detail', guarantee.id)
    
    if request.method == 'POST':
        form = CustomerGuaranteeReturnForm(request.POST, instance=guarantee)
        if form.is_valid():
            returned_guarantee = form.save(commit=False)
            returned_guarantee.returned_by = request.user
            
            # حساب المبلغ المسترد
            if returned_guarantee.status in ['returned', 'partially_returned']:
                returned_guarantee.returned_amount = returned_guarantee.value - returned_guarantee.deductions
            
            returned_guarantee.save()
            messages.success(request, _('تم استرداد العهدة بنجاح'))
            return redirect('custody_detail', guarantee.id)
    else:
        form = CustomerGuaranteeReturnForm(instance=guarantee)
    
    context = {
        'form': form,
        'guarantee': guarantee,
        'title': _('استرداد العهدة'),
    }
    
    return render(request, 'admin/custody/return_form.html', context)


@login_required
def custody_print(request, guarantee_id):
    """طباعة إيصال استلام أو استرداد العهدة"""
    
    guarantee = get_object_or_404(CustomerGuarantee, id=guarantee_id)
    
    # تحديد نوع الإيصال (استلام أو استرداد)
    receipt_type = request.GET.get('type', 'receipt')
    if receipt_type not in ['receipt', 'return']:
        receipt_type = 'receipt'
    
    # إذا كان إيصال استرداد ولم يتم استرداد العهدة بعد
    if receipt_type == 'return' and not guarantee.return_date:
        messages.error(request, _('لا يمكن طباعة إيصال استرداد لعهدة لم يتم استردادها بعد'))
        return redirect('custody_detail', guarantee.id)
    
    context = {
        'guarantee': guarantee,
        'receipt_type': receipt_type,
        'today': timezone.now().date(),
    }
    
    template_name = 'admin/custody/print_receipt.html'
    return render(request, template_name, context)


@login_required
def custody_export(request):
    """تصدير بيانات العهدات إلى ملف CSV"""
    
    # استرجاع بيانات العهدات
    guarantees = CustomerGuarantee.objects.all().order_by('-created_at')
    
    # تطبيق عوامل التصفية
    filter_form = CustomerGuaranteeFilterForm(request.GET)
    if filter_form.is_valid():
        data = filter_form.cleaned_data
        
        # البحث العام
        search = data.get('search')
        if search:
            guarantees = guarantees.filter(
                Q(name__icontains=search) | 
                Q(customer__first_name__icontains=search) | 
                Q(customer__last_name__icontains=search) | 
                Q(reservation__reservation_number__icontains=search) |
                Q(identifier__icontains=search)
            )
            
        # تصفية حسب الحالة
        status = data.get('status')
        if status:
            guarantees = guarantees.filter(status=status)
            
        # تصفية حسب نوع العهدة
        guarantee_type = data.get('guarantee_type')
        if guarantee_type:
            guarantees = guarantees.filter(guarantee_type=guarantee_type)
            
        # تصفية حسب نطاق التاريخ
        date_from = data.get('date_from')
        if date_from:
            guarantees = guarantees.filter(handover_date__gte=date_from)
            
        date_to = data.get('date_to')
        if date_to:
            guarantees = guarantees.filter(handover_date__lte=date_to)
    
    # إنشاء استجابة CSV
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="customer_guarantees.csv"'
    
    # تحديد الترميز للغة العربية
    response.write(u'\ufeff'.encode('utf8'))
    
    writer = csv.writer(response)
    writer.writerow([
        _('المعرف'),
        _('اسم العهدة'),
        _('نوع العهدة'),
        _('فئة العهدة'),
        _('اسم العميل'),
        _('رقم الحجز'),
        _('تاريخ التسليم'),
        _('تاريخ الاسترداد'),
        _('القيمة'),
        _('الخصومات'),
        _('المبلغ المسترد'),
        _('الحالة'),
    ])
    
    for guarantee in guarantees:
        writer.writerow([
            guarantee.id,
            guarantee.name,
            guarantee.get_guarantee_type_display(),
            guarantee.category or '',
            guarantee.customer.get_full_name(),
            guarantee.reservation.reservation_number,
            guarantee.handover_date,
            guarantee.return_date or '',
            guarantee.value,
            guarantee.deductions or 0,
            guarantee.returned_amount or 0,
            guarantee.get_status_display(),
        ])
    
    return response