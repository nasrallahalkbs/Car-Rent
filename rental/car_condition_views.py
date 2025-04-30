from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils.translation import gettext_lazy as _
from django.db.models import Q, Count, Prefetch
from django.utils import timezone
from django.http import JsonResponse, HttpResponse, Http404
from django.core.paginator import Paginator
from django.views.decorators.http import require_POST
from django.conf import settings
import json
import base64
from django.core.files.base import ContentFile

from .models import (
    Car, Reservation, CarConditionReport, CarInspectionCategory,
    CarInspectionItem, CarInspectionDetail, CarInspectionImage,
    CustomerSignature
)
from .forms import (
    CarConditionReportForm, CarInspectionCategoryForm, CarInspectionItemForm,
    CarInspectionDetailForm, CarInspectionImageForm, CustomerSignatureForm,
    CompleteCarInspectionForm
)

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
    
    # تحميل تفاصيل الفحص للتقرير بطريقة فعالة
    if delivery_report:
        delivery_report.inspection_details_list = CarInspectionDetail.objects.filter(
            report=delivery_report
        ).select_related('inspection_item', 'inspection_item__category').order_by(
            'inspection_item__category__display_order', 'inspection_item__display_order'
        )
    
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
    
    return render(request, 'admin/car_condition/car_condition_comparison_modern.html', context)


# وظائف العرض الجديدة لنظام توثيق حالة السيارة المتقدم
@login_required
def inspection_category_list(request):
    """عرض قائمة فئات الفحص مع إمكانية الإضافة والتعديل"""
    
    categories = CarInspectionCategory.objects.all().order_by('display_order')
    
    if request.method == 'POST':
        form = CarInspectionCategoryForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, _('تم إضافة فئة الفحص بنجاح'))
            return redirect('inspection_category_list')
    else:
        form = CarInspectionCategoryForm()
    
    context = {
        'categories': categories,
        'form': form
    }
    
    return render(request, 'admin/car_condition/inspection_category_list.html', context)


@login_required
def inspection_category_edit(request, category_id):
    """تعديل فئة الفحص"""
    
    category = get_object_or_404(CarInspectionCategory, id=category_id)
    
    if request.method == 'POST':
        form = CarInspectionCategoryForm(request.POST, instance=category)
        if form.is_valid():
            form.save()
            messages.success(request, _('تم تحديث فئة الفحص بنجاح'))
            return redirect('inspection_category_list')
    else:
        form = CarInspectionCategoryForm(instance=category)
    
    context = {
        'form': form,
        'category': category
    }
    
    return render(request, 'admin/car_condition/inspection_category_form.html', context)


@login_required
def inspection_category_delete(request, category_id):
    """حذف فئة الفحص"""
    
    category = get_object_or_404(CarInspectionCategory, id=category_id)
    
    if request.method == 'POST':
        try:
            category.delete()
            messages.success(request, _('تم حذف فئة الفحص بنجاح'))
        except Exception as e:
            messages.error(request, _('لا يمكن حذف الفئة لأنها مرتبطة بعناصر فحص'))
        return redirect('inspection_category_list')
    
    context = {
        'category': category
    }
    
    return render(request, 'admin/car_condition/inspection_category_confirm_delete.html', context)


@login_required
def inspection_item_list(request):
    """عرض قائمة عناصر الفحص مع إمكانية الإضافة والتعديل"""
    
    items = CarInspectionItem.objects.all().select_related('category').order_by(
        'category__display_order', 'display_order'
    )
    
    if request.method == 'POST':
        form = CarInspectionItemForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, _('تم إضافة عنصر الفحص بنجاح'))
            return redirect('inspection_item_list')
    else:
        form = CarInspectionItemForm()
    
    context = {
        'items': items,
        'form': form
    }
    
    return render(request, 'admin/car_condition/inspection_item_list.html', context)


@login_required
def inspection_item_edit(request, item_id):
    """تعديل عنصر الفحص"""
    
    item = get_object_or_404(CarInspectionItem, id=item_id)
    
    if request.method == 'POST':
        form = CarInspectionItemForm(request.POST, instance=item)
        if form.is_valid():
            form.save()
            messages.success(request, _('تم تحديث عنصر الفحص بنجاح'))
            return redirect('inspection_item_list')
    else:
        form = CarInspectionItemForm(instance=item)
    
    context = {
        'form': form,
        'item': item
    }
    
    return render(request, 'admin/car_condition/inspection_item_form.html', context)


@login_required
def inspection_item_delete(request, item_id):
    """حذف عنصر الفحص"""
    
    item = get_object_or_404(CarInspectionItem, id=item_id)
    
    if request.method == 'POST':
        try:
            item.delete()
            messages.success(request, _('تم حذف عنصر الفحص بنجاح'))
        except Exception as e:
            messages.error(request, _('لا يمكن حذف العنصر لأنه مرتبط بتقارير فحص'))
        return redirect('inspection_item_list')
    
    context = {
        'item': item
    }
    
    return render(request, 'admin/car_condition/inspection_item_confirm_delete.html', context)


@login_required
def complete_car_inspection_create(request):
    """إنشاء تقرير فحص تفصيلي للسيارة"""
    
    car_id = request.GET.get('car_id')
    reservation_id = request.GET.get('reservation_id')
    report_type = request.GET.get('report_type', 'delivery')
    
    initial_data = {
        'report_type': report_type,
        'date': timezone.now()
    }
    
    # إذا تم تمرير معرف الحجز
    if reservation_id:
        try:
            reservation = Reservation.objects.get(id=reservation_id)
            initial_data['reservation'] = reservation
            initial_data['car'] = reservation.car
        except Reservation.DoesNotExist:
            pass
    # إذا تم تمرير معرف السيارة فقط
    elif car_id:
        try:
            car = Car.objects.get(id=car_id)
            initial_data['car'] = car
        except Car.DoesNotExist:
            pass
    
    if request.method == 'POST':
        form = CompleteCarInspectionForm(request.POST, user=request.user)
        if form.is_valid():
            # حفظ التقرير وتفاصيل الفحص
            report = form.save()
            
            messages.success(request, _('تم إنشاء تقرير فحص السيارة بنجاح'))
            
            # توجيه لإضافة الصور والتوقيعات
            return redirect('add_inspection_images', report_id=report.id)
    else:
        form = CompleteCarInspectionForm(initial=initial_data, user=request.user)
    
    context = {
        'form': form,
        'title': _('إنشاء تقرير فحص تفصيلي للسيارة'),
        'car_id': car_id,
        'reservation_id': reservation_id
    }
    
    return render(request, 'admin/car_condition/complete_car_inspection_form.html', context)


@login_required
def car_inspection_detail(request, report_id):
    """عرض تفاصيل تقرير فحص السيارة التفصيلي"""
    
    report = get_object_or_404(CarConditionReport, id=report_id)
    
    # تحميل تفاصيل الفحص بشكل منظم حسب الفئة
    inspection_details = CarInspectionDetail.objects.filter(
        report=report
    ).select_related('inspection_item', 'inspection_item__category').order_by(
        'inspection_item__category__display_order', 'inspection_item__display_order'
    )
    
    # تنظيم التفاصيل حسب الفئة
    categories = {}
    for detail in inspection_details:
        category = detail.inspection_item.category
        if category.id not in categories:
            categories[category.id] = {
                'name': category.name,
                'description': category.description,
                'items': []
            }
        
        # إضافة الصور لكل عنصر
        detail.images_list = detail.images.all()
        
        categories[category.id]['items'].append(detail)
    
    # تحميل الصور العامة للتقرير (غير المرتبطة بعنصر محدد)
    general_images = CarInspectionImage.objects.filter(
        report=report, inspection_detail__isnull=True
    )
    
    # تحميل التوقيعات
    customer_signature = CustomerSignature.objects.filter(
        report=report, is_customer=True
    ).first()
    
    staff_signature = CustomerSignature.objects.filter(
        report=report, is_customer=False
    ).first()
    
    context = {
        'report': report,
        'categories': categories,
        'general_images': general_images,
        'customer_signature': customer_signature,
        'staff_signature': staff_signature
    }
    
    return render(request, 'admin/car_condition/car_inspection_detail.html', context)


@login_required
def add_inspection_images(request, report_id):
    """إضافة صور لتقرير فحص السيارة"""
    
    report = get_object_or_404(CarConditionReport, id=report_id)
    
    # تحميل تفاصيل الفحص للتقرير
    inspection_details = CarInspectionDetail.objects.filter(
        report=report
    ).select_related('inspection_item').order_by(
        'inspection_item__category__display_order', 'inspection_item__display_order'
    )
    
    if request.method == 'POST':
        form = CarInspectionImageForm(request.POST, request.FILES)
        if form.is_valid():
            image = form.save(commit=False)
            image.report = report
            image.save()
            
            messages.success(request, _('تم إضافة الصورة بنجاح'))
            
            # إعادة تعيين النموذج لإضافة صورة أخرى
            form = CarInspectionImageForm(initial={'report': report})
    else:
        form = CarInspectionImageForm(initial={'report': report})
    
    # الحصول على الصور الحالية
    images = CarInspectionImage.objects.filter(report=report).order_by('-upload_date')
    
    context = {
        'form': form,
        'report': report,
        'images': images,
        'inspection_details': inspection_details,
        'title': _('إضافة صور لتقرير فحص السيارة')
    }
    
    return render(request, 'admin/car_condition/add_inspection_images.html', context)


@login_required
def delete_inspection_image(request, image_id):
    """حذف صورة من تقرير فحص السيارة"""
    
    image = get_object_or_404(CarInspectionImage, id=image_id)
    report_id = image.report.id
    
    if request.method == 'POST':
        image.delete()
        messages.success(request, _('تم حذف الصورة بنجاح'))
        return redirect('add_inspection_images', report_id=report_id)
    
    context = {
        'image': image
    }
    
    return render(request, 'admin/car_condition/delete_inspection_image.html', context)


@login_required
def add_customer_signature(request, report_id):
    """إضافة توقيع العميل على تقرير فحص السيارة"""
    
    report = get_object_or_404(CarConditionReport, id=report_id)
    
    if request.method == 'POST':
        form = CustomerSignatureForm(request.POST)
        if form.is_valid():
            signature = form.save(commit=False)
            signature.report = report
            signature.is_customer = True
            signature.ip_address = request.META.get('REMOTE_ADDR')
            signature.save()
            
            messages.success(request, _('تم إضافة توقيع العميل بنجاح'))
            return redirect('car_inspection_detail', report_id=report.id)
    else:
        # التحقق من وجود توقيع سابق
        existing_signature = CustomerSignature.objects.filter(
            report=report, is_customer=True
        ).first()
        
        if existing_signature:
            messages.warning(request, _('يوجد توقيع للعميل بالفعل. إضافة توقيع جديد سيحل محل التوقيع الحالي.'))
        
        form = CustomerSignatureForm(initial={'is_customer': True})
    
    context = {
        'form': form,
        'report': report,
        'title': _('إضافة توقيع العميل')
    }
    
    return render(request, 'admin/car_condition/add_signature.html', context)


@login_required
def add_staff_signature(request, report_id):
    """إضافة توقيع الموظف على تقرير فحص السيارة"""
    
    report = get_object_or_404(CarConditionReport, id=report_id)
    
    if request.method == 'POST':
        form = CustomerSignatureForm(request.POST)
        if form.is_valid():
            signature = form.save(commit=False)
            signature.report = report
            signature.is_customer = False
            signature.ip_address = request.META.get('REMOTE_ADDR')
            signature.save()
            
            messages.success(request, _('تم إضافة توقيع الموظف بنجاح'))
            return redirect('car_inspection_detail', report_id=report.id)
    else:
        # التحقق من وجود توقيع سابق
        existing_signature = CustomerSignature.objects.filter(
            report=report, is_customer=False
        ).first()
        
        if existing_signature:
            messages.warning(request, _('يوجد توقيع للموظف بالفعل. إضافة توقيع جديد سيحل محل التوقيع الحالي.'))
        
        # استخدام بيانات المستخدم الحالي
        initial_data = {
            'is_customer': False,
            'signed_by_name': request.user.get_full_name() or request.user.username
        }
        
        form = CustomerSignatureForm(initial=initial_data)
    
    context = {
        'form': form,
        'report': report,
        'title': _('إضافة توقيع الموظف')
    }
    
    return render(request, 'admin/car_condition/add_signature.html', context)


@login_required
def download_inspection_report_pdf(request, report_id):
    """تنزيل تقرير فحص السيارة بصيغة PDF"""
    
    report = get_object_or_404(CarConditionReport, id=report_id)
    
    # تحميل تفاصيل الفحص بشكل منظم حسب الفئة
    inspection_details = CarInspectionDetail.objects.filter(
        report=report
    ).select_related('inspection_item', 'inspection_item__category').order_by(
        'inspection_item__category__display_order', 'inspection_item__display_order'
    )
    
    # تنظيم التفاصيل حسب الفئة
    categories = {}
    for detail in inspection_details:
        category = detail.inspection_item.category
        if category.id not in categories:
            categories[category.id] = {
                'name': category.name,
                'description': category.description,
                'items': []
            }
        
        # إضافة الصور لكل عنصر
        detail.images_list = detail.images.all()
        
        categories[category.id]['items'].append(detail)
    
    # تحميل الصور العامة للتقرير (غير المرتبطة بعنصر محدد)
    general_images = CarInspectionImage.objects.filter(
        report=report, inspection_detail__isnull=True
    )
    
    # تحميل التوقيعات
    customer_signature = CustomerSignature.objects.filter(
        report=report, is_customer=True
    ).first()
    
    staff_signature = CustomerSignature.objects.filter(
        report=report, is_customer=False
    ).first()
    
    context = {
        'report': report,
        'categories': categories,
        'general_images': general_images,
        'customer_signature': customer_signature,
        'staff_signature': staff_signature,
        'domain': settings.ALLOWED_HOSTS[0] if settings.ALLOWED_HOSTS else request.get_host(),
        'protocol': 'https' if request.is_secure() else 'http'
    }
    
    # استخدام قالب HTML لإنشاء PDF
    html_template = 'admin/car_condition/car_inspection_pdf.html'
    html = render(request, html_template, context).content
    
    # إنشاء PDF من HTML
    from weasyprint import HTML, CSS
    from django.conf import settings
    import tempfile
    
    # استخدام ملف مؤقت لتخزين PDF
    pdf_file = tempfile.NamedTemporaryFile(delete=False)
    
    # تحويل HTML إلى PDF
    HTML(string=html.decode()).write_pdf(
        pdf_file.name,
        stylesheets=[
            CSS(string='@page { size: A4; margin: 1cm; }')
        ]
    )
    
    # إرسال الملف في الاستجابة
    with open(pdf_file.name, 'rb') as pdf:
        response = HttpResponse(pdf.read(), content_type='application/pdf')
        report_date = report.date.strftime('%Y%m%d')
        filename = f'car_inspection_{report.car.license_plate}_{report_date}.pdf'
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        return response