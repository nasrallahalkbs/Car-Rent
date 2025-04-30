from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils.translation import gettext_lazy as _
from django.db.models import Q, Count
from django.utils import timezone
from django.http import JsonResponse, HttpResponse, Http404

from .models import Car, Reservation, CarConditionReport
from .forms import CarConditionReportForm

@login_required
def car_condition_list(request):
    """عرض قائمة بجميع تقارير حالة السيارات"""
    
    # الحصول على معلمات التصفية
    report_type = request.GET.get('report_type', '')
    car_id = request.GET.get('car_id', '')
    date_from = request.GET.get('date_from', '')
    date_to = request.GET.get('date_to', '')
    
    # تطبيق التصفية
    reports = CarConditionReport.objects.all()
    
    if report_type:
        reports = reports.filter(report_type=report_type)
    
    if car_id:
        reports = reports.filter(car_id=car_id)
    
    if date_from:
        reports = reports.filter(date__gte=date_from)
    
    if date_to:
        reports = reports.filter(date__lte=date_to)
    
    # ترتيب التقارير من الأحدث إلى الأقدم
    reports = reports.order_by('-date')
    
    # الحصول على قائمة بجميع السيارات للفلترة
    cars = Car.objects.all().order_by('make', 'model')
    
    # البحث عن الحجوزات التي تحتوي على تقارير تسليم واستلام لإضافة زر المقارنة
    # استخراج الحجوزات التي لها كلا النوعين من التقارير
    reservation_ids_with_delivery = set(CarConditionReport.objects.filter(
        report_type='delivery').values_list('reservation_id', flat=True))
    reservation_ids_with_return = set(CarConditionReport.objects.filter(
        report_type='return').values_list('reservation_id', flat=True))
    
    # الحجوزات التي لها كلا النوعين من التقارير
    reservation_ids_with_both = reservation_ids_with_delivery.intersection(reservation_ids_with_return)
    comparable_reservations = list(reservation_ids_with_both)
    
    context = {
        'reports': reports,
        'cars': cars,
        'report_type': report_type,
        'car_id': car_id,
        'date_from': date_from,
        'date_to': date_to,
        'report_types': CarConditionReport.REPORT_TYPE_CHOICES,
        'comparable_reservations': comparable_reservations,
    }
    
    return render(request, 'admin/car_condition/car_condition_list.html', context)

@login_required
def car_condition_create(request):
    """إنشاء تقرير جديد لحالة السيارة"""
    
    # إذا تم تحديد سيارة أو حجز، ستكون هنا
    car_id = request.GET.get('car_id', None)
    reservation_id = request.GET.get('reservation_id', None)
    
    initial_data = {}
    
    # إذا تم تمرير معرف الحجز
    if reservation_id:
        try:
            reservation = Reservation.objects.get(id=reservation_id)
            initial_data['reservation'] = reservation.id
            initial_data['car'] = reservation.car.id
        except Reservation.DoesNotExist:
            pass
    # إذا تم تمرير معرف السيارة فقط
    elif car_id:
        try:
            car = Car.objects.get(id=car_id)
            initial_data['car'] = car.id
        except Car.DoesNotExist:
            pass
    
    if request.method == 'POST':
        form = CarConditionReportForm(request.POST, user=request.user, initial=initial_data)
        if form.is_valid():
            report = form.save(commit=False)
            report.created_by = request.user
            report.save()
            
            messages.success(request, _('تم إنشاء تقرير حالة السيارة بنجاح'))
            
            # إذا كان التقرير من نوع "فحص صيانة" وكانت الحالة "سيئة" أو "متضررة"، 
            # قم بتغيير حالة السيارة تلقائيًا إلى "في الصيانة"
            if report.report_type in ['maintenance', 'periodic'] and report.car_condition in ['poor', 'damaged']:
                car = report.car
                car.status = 'maintenance'
                car.is_available = False
                car.save()
                messages.warning(request, _('تم تحديث حالة السيارة إلى "في الصيانة" بناءً على التقرير'))
            
            # الرجوع إلى صفحة قائمة التقارير
            return redirect('car_condition_list')
    else:
        form = CarConditionReportForm(user=request.user, initial=initial_data)
    
    context = {
        'form': form,
        'title': _('إنشاء تقرير حالة سيارة جديد'),
    }
    
    return render(request, 'admin/car_condition/car_condition_form.html', context)

@login_required
def car_condition_edit(request, report_id):
    """تعديل تقرير حالة السيارة"""
    
    report = get_object_or_404(CarConditionReport, id=report_id)
    
    if request.method == 'POST':
        form = CarConditionReportForm(request.POST, instance=report, user=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, _('تم تحديث تقرير حالة السيارة بنجاح'))
            return redirect('car_condition_list')
    else:
        form = CarConditionReportForm(instance=report, user=request.user)
    
    context = {
        'form': form,
        'report': report,
        'title': _('تعديل تقرير حالة السيارة'),
    }
    
    return render(request, 'admin/car_condition/car_condition_form.html', context)

@login_required
def car_condition_detail(request, report_id):
    """عرض تفاصيل تقرير حالة السيارة"""
    
    report = get_object_or_404(CarConditionReport, id=report_id)
    
    # البحث عن تقارير أخرى لنفس السيارة
    related_reports = CarConditionReport.objects.filter(
        car=report.car
    ).exclude(
        id=report.id
    ).order_by('-date')[:5]
    
    context = {
        'report': report,
        'related_reports': related_reports,
    }
    
    return render(request, 'admin/car_condition/car_condition_detail.html', context)

@login_required
def car_condition_delete(request, report_id):
    """حذف تقرير حالة السيارة"""
    
    report = get_object_or_404(CarConditionReport, id=report_id)
    
    if request.method == 'POST':
        report.delete()
        messages.success(request, _('تم حذف تقرير حالة السيارة بنجاح'))
        return redirect('car_condition_list')
    
    context = {
        'report': report,
    }
    
    return render(request, 'admin/car_condition/car_condition_confirm_delete.html', context)

@login_required
def get_car_by_reservation(request):
    """استرجاع معلومات السيارة والعميل المرتبطة بالحجز لعرضها في النموذج بتقنية AJAX"""
    
    reservation_id = request.GET.get('reservation_id')
    if not reservation_id:
        return JsonResponse({'error': 'No reservation ID provided'}, status=400)
    
    try:
        reservation = Reservation.objects.get(id=reservation_id)
        
        # استرجاع معلومات السيارة والعميل
        return JsonResponse({
            'car_id': reservation.car.id,
            'car_info': f'{reservation.car.make} {reservation.car.model} ({reservation.car.license_plate})',
            'customer_name': reservation.user.get_full_name() or reservation.user.username,
            'customer_id': reservation.user.id,
            'reservation_number': reservation.reservation_number,
            'reservation_start_date': reservation.start_date.strftime('%Y-%m-%d'),
            'reservation_end_date': reservation.end_date.strftime('%Y-%m-%d'),
            'car_details': {
                'make': reservation.car.make,
                'model': reservation.car.model,
                'year': reservation.car.year,
                'color': reservation.car.color,
                'license_plate': reservation.car.license_plate,
                'category': reservation.car.get_category_display(),
                'transmission': reservation.car.get_transmission_display(),
                'fuel_type': reservation.car.get_fuel_type_display(),
            }
        })
    except Reservation.DoesNotExist:
        return JsonResponse({'error': 'Reservation not found'}, status=404)

@login_required
def car_history_reports(request, car_id):
    """عرض تاريخ جميع تقارير حالة سيارة محددة"""
    
    car = get_object_or_404(Car, id=car_id)
    reports = CarConditionReport.objects.filter(car=car).order_by('-date')
    
    context = {
        'car': car,
        'reports': reports,
    }
    
    return render(request, 'admin/car_condition/car_history_reports.html', context)

@login_required
def car_condition_statistics(request):
    """عرض إحصائيات وتحليلات عن تقارير حالة السيارات"""
    
    # إجمالي عدد التقارير
    total_reports = CarConditionReport.objects.count()
    
    # عدد التقارير حسب النوع
    reports_by_type = {}
    for report_type, label in CarConditionReport.REPORT_TYPE_CHOICES:
        count = CarConditionReport.objects.filter(report_type=report_type).count()
        reports_by_type[report_type] = {
            'label': label,
            'count': count,
            'percentage': round((count / total_reports * 100), 1) if total_reports > 0 else 0
        }
    
    # عدد التقارير حسب حالة السيارة
    reports_by_condition = {}
    for condition, label in CarConditionReport.CAR_CONDITION_CHOICES:
        count = CarConditionReport.objects.filter(car_condition=condition).count()
        reports_by_condition[condition] = {
            'label': label,
            'count': count,
            'percentage': round((count / total_reports * 100), 1) if total_reports > 0 else 0
        }
    
    # السيارات التي تعرضت لأكثر الأعطال
    cars_with_most_defects = Car.objects.annotate(
        defect_count=Count('condition_reports', filter=~Q(condition_reports__defects=''))
    ).order_by('-defect_count')[:10]
    
    context = {
        'total_reports': total_reports,
        'reports_by_type': reports_by_type,
        'reports_by_condition': reports_by_condition,
        'cars_with_most_defects': cars_with_most_defects,
    }
    
    return render(request, 'admin/car_condition/car_condition_statistics.html', context)


@login_required
def car_condition_comparison(request, reservation_id):
    """عرض مقارنة بين تقرير حالة السيارة عند التسليم والاستلام"""
    
    # الحصول على معلومات الحجز
    reservation = get_object_or_404(Reservation, id=reservation_id)
    car = reservation.car
    
    # البحث عن تقرير التسليم والاستلام
    delivery_report = CarConditionReport.objects.filter(
        reservation=reservation,
        report_type='delivery'
    ).order_by('-date').first()
    
    return_report = CarConditionReport.objects.filter(
        reservation=reservation,
        report_type='return'
    ).order_by('-date').first()
    
    # التحقق من وجود كلا التقريرين
    if not delivery_report or not return_report:
        messages.error(request, _('لا يمكن عرض المقارنة. يجب وجود تقرير تسليم وتقرير استلام للحجز.'))
        return redirect('car_condition_list')
    
    # تحديد ما إذا كانت هناك أضرار جديدة
    has_damages = False
    
    # تحقق من الأضرار الجديدة (إذا كان تقرير الاستلام يحتوي على أضرار لم تكن موجودة في تقرير التسليم)
    if return_report.defects and (not delivery_report.defects or delivery_report.defects != return_report.defects):
        has_damages = True
    
    # تحقق من تغير حالة السيارة للأسوأ
    condition_values = {
        'excellent': 5,
        'good': 4,
        'fair': 3,
        'poor': 2,
        'damaged': 1
    }
    
    delivery_condition = condition_values.get(delivery_report.car_condition, 0)
    return_condition = condition_values.get(return_report.car_condition, 0)
    
    if return_condition < delivery_condition:
        has_damages = True
    
    context = {
        'reservation': reservation,
        'car': car,
        'delivery_report': delivery_report,
        'return_report': return_report,
        'has_damages': has_damages,
        'current_date': timezone.now()
    }
    
    return render(request, 'admin/car_condition/car_condition_comparison.html', context)