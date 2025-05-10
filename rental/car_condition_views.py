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
import io
from PIL import Image
from django.core.files.base import ContentFile

from .models import (
    Car, Reservation, CarConditionReport, CarInspectionCategory,
    CarInspectionItem, CarInspectionDetail, CarInspectionImage,
    CustomerSignature
)
from .forms import (
    CarConditionReportForm, CarInspectionCategoryForm, CarInspectionItemForm,
    CarInspectionDetailForm, CarInspectionImageForm, CustomerSignatureForm,
    CompleteCarInspectionForm, CarRepairForm
)

def compress_image(image_file, max_size=(800, 600), quality=85):
    """
    ضغط الصورة وتقليل حجمها
    
    Parameters:
    - image_file: ملف الصورة المرفوع
    - max_size: الحجم الأقصى للصورة (العرض، الارتفاع)
    - quality: جودة الصورة (1-100)
    
    Returns:
    - ملف الصورة المضغوطة
    """
    # فتح الصورة باستخدام PIL
    img = Image.open(image_file)
    
    # تغيير حجم الصورة إذا كانت أكبر من الحجم الأقصى
    if img.width > max_size[0] or img.height > max_size[1]:
        img.thumbnail(max_size, Image.Resampling.LANCZOS)
    
    # حفظ الصورة المضغوطة إلى ذاكرة مؤقتة
    output = io.BytesIO()
    
    # حفظ الصورة بتنسيق JPEG مع جودة محددة
    if img.mode == 'RGBA':
        img = img.convert('RGB')
    
    img.save(output, format='JPEG', quality=quality, optimize=True)
    output.seek(0)
    
    # إرجاع الصورة المضغوطة
    return ContentFile(output.getvalue(), name=image_file.name)

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
        # طباعة بيانات الطلب للتصحيح
        print("Form submitted with data:", request.POST)
        print("Files:", request.FILES)
        
        form = CarConditionReportForm(request.POST, request.FILES, user=request.user, initial=initial_data)
        if form.is_valid():
            report = form.save(commit=False)
            report.created_by = request.user
            
            # إضافة معالجة ملف PDF للفحص الإلكتروني
            inspection_type = request.POST.get('inspection_type', 'manual')
            if inspection_type == 'electronic':
                # حفظ ملخص الفحص في ملاحظات التقرير
                inspection_summary = request.POST.get('inspection_summary', '')
                if inspection_summary:
                    report.notes = inspection_summary
                
                # معالجة ملف PDF المرفق
                if 'inspection_pdf_file' in request.FILES:
                    # حفظ ملف PDF كمستند مرفق
                    pdf_file = request.FILES['inspection_pdf_file']
                    report.electronic_report_pdf = pdf_file
                    # إضافة علامة لتوضيح أن هذا فحص إلكتروني
                    report.is_electronic_inspection = True
            
            report.save()
            
            # معالجة صور الهيكل الخارجي
            image_types = ['front_image', 'rear_image', 'side_image', 'interior_image']
            
            for image_type in image_types:
                if image_type in request.FILES:
                    image_file = request.FILES[image_type]
                    notes = request.POST.get(f'{image_type}_notes', '')
                    
                    description = ''
                    if image_type == 'front_image':
                        description = 'صورة أمامية'
                    elif image_type == 'rear_image':
                        description = 'صورة خلفية'
                    elif image_type == 'side_image':
                        description = 'صورة جانبية'
                    elif image_type == 'interior_image':
                        description = 'صورة داخلية'
                    
                    if notes:
                        description = f"{description} - {notes}"
                    
                    # ضغط الصورة قبل الحفظ
                    compressed_image = compress_image(image_file, max_size=(800, 600), quality=80)
                    
                    # إنشاء سجل لصورة الفحص
                    CarInspectionImage.objects.create(
                        report=report,
                        image=compressed_image,
                        description=description,
                        inspection_detail=None  # صورة عامة للهيكل الخارجي
                    )
            
            # حفظ تفاصيل الفحص من النموذج المرسل (فقط للفحص اليدوي)
            if inspection_type == 'manual':
                for key, value in request.POST.items():
                    # معالجة حقول عناصر الفحص
                    if key.startswith('inspection_item_') and value:
                        item_id = int(key.replace('inspection_item_', ''))
                        
                        # البحث عن عنصر الفحص
                        try:
                            inspection_item = CarInspectionItem.objects.get(id=item_id)
                            
                            # تخطي عناصر "الهيكل الخارجي" لأننا نستخدم الصور بدلاً منها
                            if inspection_item.category.name == 'الهيكل الخارجي':
                                continue
                            
                            # الحصول على الملاحظات واحتياج الإصلاح
                            notes = request.POST.get(f'notes_item_{item_id}', '')
                            needs_repair = request.POST.get(f'needs_repair_{item_id}', '') == 'on'
                            
                            # إنشاء تفاصيل الفحص
                            CarInspectionDetail.objects.create(
                                report=report,
                                inspection_item=inspection_item,
                                condition=value,
                                notes=notes,
                                needs_repair=needs_repair
                            )
                        except CarInspectionItem.DoesNotExist:
                            pass
            
            messages.success(request, _('تم إنشاء تقرير حالة السيارة وتفاصيل الفحص بنجاح'))
            
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
            # طباعة أخطاء النموذج للتصحيح
            print("Form errors:", form.errors)
    else:
        form = CarConditionReportForm(user=request.user, initial=initial_data)
    
    # جلب فئات الفحص وعناصرها المنشطة
    inspection_categories = CarInspectionCategory.objects.filter(is_active=True).prefetch_related(
        Prefetch('inspection_items', queryset=CarInspectionItem.objects.filter(is_active=True).order_by('display_order'))
    ).order_by('display_order')
    
    # تحديد العناصر المهمة والمكلفة والحساسة
    important_items = set()  # مجموعة العناصر المهمة
    expensive_items = set()  # مجموعة العناصر المكلفة
    critical_items = set()  # مجموعة العناصر الحساسة
    
    # تعيين العناصر المهمة والمكلفة والحرجة في حالة عدم وجود بيانات في قاعدة البيانات
    default_important_items = {
        'محرك': True,
        'فرامل': True,
        'نظام التعليق': True,
        'ناقل الحركة': True, 
        'توجيه': True,
        'كهرباء': True,
        'بطارية': True,
        'مكيف': True
    }
    
    default_expensive_items = {
        'محرك': True,
        'ناقل الحركة': True,
        'نظام التعليق': True,
        'مكيف': True,
        'رادييتر': True,
        'بطارية': True,
        'كمبيوتر': True
    }
    
    default_critical_items = {
        'فرامل': True,
        'توجيه': True,
        'وسائد هوائية': True,
        'سلامة': True,
        'أمان': True,
        'إطارات': True
    }
    
    # المرور على جميع فئات وعناصر الفحص لتحديد العناصر المهمة والمكلفة والحرجة
    for category in inspection_categories:
        for item in category.inspection_items.all():
            # إضافة العناصر المهمة
            if hasattr(item, 'is_important') and item.is_important:
                important_items.add(item.id)
                print(f"إضافة العنصر المهم من قاعدة البيانات: {item.name} (ID: {item.id})")
            else:
                # إذا لم يكن لدينا الحقل الجديد، نستخدم الكلمات المفتاحية
                for keyword in default_important_items:
                    if keyword in item.name:
                        important_items.add(item.id)
                        print(f"إضافة العنصر المهم بناءً على الاسم: {item.name} (ID: {item.id})")
                        break
            
            # إضافة العناصر المكلفة
            if hasattr(item, 'is_expensive') and item.is_expensive:
                expensive_items.add(item.id)
                print(f"إضافة العنصر المكلف من قاعدة البيانات: {item.name} (ID: {item.id})")
            else:
                # إذا لم يكن لدينا الحقل الجديد، نستخدم الكلمات المفتاحية
                for keyword in default_expensive_items:
                    if keyword in item.name:
                        expensive_items.add(item.id)
                        print(f"إضافة العنصر المكلف بناءً على الاسم: {item.name} (ID: {item.id})")
                        break
            
            # إضافة العناصر الحرجة
            if hasattr(item, 'is_critical') and item.is_critical:
                critical_items.add(item.id)
                print(f"إضافة العنصر الحرج من قاعدة البيانات: {item.name} (ID: {item.id})")
            else:
                # إذا لم يكن لدينا الحقل الجديد، نستخدم الكلمات المفتاحية
                for keyword in default_critical_items:
                    if keyword in item.name:
                        critical_items.add(item.id)
                        print(f"إضافة العنصر الحرج بناءً على الاسم: {item.name} (ID: {item.id})")
                        break
    
    context = {
        'form': form,
        'title': _('إنشاء تقرير حالة سيارة جديد'),
        'inspection_categories': inspection_categories,
        'exterior_images': [],  # قائمة فارغة لصور الهيكل الخارجي في حالة الإنشاء
        'important_items': important_items,
        'expensive_items': expensive_items,
        'critical_items': critical_items,
    }
    
    return render(request, 'admin/car_condition/car_condition_form.html', context)

@login_required
def car_condition_edit(request, report_id):
    """تعديل تقرير حالة السيارة"""
    
    report = get_object_or_404(CarConditionReport, id=report_id)
    
    # الحصول على صور الهيكل الخارجي الحالية
    exterior_images = CarInspectionImage.objects.filter(
        report=report,
        inspection_detail__isnull=True  # صور عامة للهيكل الخارجي
    )
    
    if request.method == 'POST':
        # طباعة بيانات الطلب للتصحيح
        print("Form submitted with data:", request.POST)
        print("Files:", request.FILES)
        
        form = CarConditionReportForm(request.POST, request.FILES, instance=report, user=request.user)
        if form.is_valid():
            updated_report = form.save(commit=False)
            
            # إضافة معالجة ملف PDF للفحص الإلكتروني
            inspection_type = request.POST.get('inspection_type', 'manual')
            if inspection_type == 'electronic':
                # حفظ ملخص الفحص في ملاحظات التقرير
                inspection_summary = request.POST.get('inspection_summary', '')
                if inspection_summary:
                    updated_report.notes = inspection_summary
                
                # معالجة ملف PDF المرفق
                if 'inspection_pdf_file' in request.FILES:
                    # حفظ ملف PDF كمستند مرفق
                    pdf_file = request.FILES['inspection_pdf_file']
                    updated_report.electronic_report_pdf = pdf_file
                    # إضافة علامة لتوضيح أن هذا فحص إلكتروني
                    updated_report.is_electronic_inspection = True
            
            updated_report.save()
            
            # معالجة صور الهيكل الخارجي الجديدة
            image_types = ['front_image', 'rear_image', 'side_image', 'interior_image']
            
            for image_type in image_types:
                if image_type in request.FILES:
                    image_file = request.FILES[image_type]
                    notes = request.POST.get(f'{image_type}_notes', '')
                    
                    description = ''
                    if image_type == 'front_image':
                        description = 'صورة أمامية'
                    elif image_type == 'rear_image':
                        description = 'صورة خلفية'
                    elif image_type == 'side_image':
                        description = 'صورة جانبية'
                    elif image_type == 'interior_image':
                        description = 'صورة داخلية'
                    
                    if notes:
                        description = f"{description} - {notes}"
                    
                    # البحث عن الصورة الحالية وتحديثها أو إنشاء صورة جديدة
                    existing_image = None
                    for img in exterior_images:
                        if (image_type == 'front_image' and 'صورة أمامية' in img.description) or \
                           (image_type == 'rear_image' and 'صورة خلفية' in img.description) or \
                           (image_type == 'side_image' and 'صورة جانبية' in img.description) or \
                           (image_type == 'interior_image' and 'صورة داخلية' in img.description):
                            existing_image = img
                            break
                    
                    # ضغط الصورة قبل الحفظ
                    compressed_image = compress_image(image_file, max_size=(800, 600), quality=80)
                    
                    if existing_image:
                        existing_image.image = compressed_image
                        existing_image.description = description
                        existing_image.save()
                    else:
                        # إنشاء صورة جديدة
                        CarInspectionImage.objects.create(
                            report=report,
                            image=compressed_image,
                            description=description,
                            inspection_detail=None
                        )
            
            # حذف تفاصيل الفحص السابقة قبل إضافة البيانات الجديدة (للفحص اليدوي فقط)
            # إذا كان يتم التحويل من فحص إلكتروني إلى يدوي، نحذف أي تفاصيل سابقة
            if inspection_type == 'manual':
                CarInspectionDetail.objects.filter(report=report).delete()
                
                # حفظ تفاصيل الفحص من النموذج المرسل (للفحص اليدوي فقط)
                for key, value in request.POST.items():
                    # معالجة حقول عناصر الفحص
                    if key.startswith('inspection_item_') and value:
                        item_id = int(key.replace('inspection_item_', ''))
                        
                        # البحث عن عنصر الفحص
                        try:
                            inspection_item = CarInspectionItem.objects.get(id=item_id)
                            
                            # تخطي عناصر "الهيكل الخارجي" لأننا نستخدم الصور بدلاً منها
                            if inspection_item.category.name == 'الهيكل الخارجي':
                                continue
                            
                            # الحصول على الملاحظات واحتياج الإصلاح
                            notes = request.POST.get(f'notes_item_{item_id}', '')
                            needs_repair = request.POST.get(f'needs_repair_{item_id}', '') == 'on'
                            
                            # إنشاء تفاصيل الفحص
                            CarInspectionDetail.objects.create(
                                report=report,
                                inspection_item=inspection_item,
                                condition=value,
                                notes=notes,
                                needs_repair=needs_repair
                            )
                        except CarInspectionItem.DoesNotExist:
                            pass
            
            messages.success(request, _('تم تحديث تقرير حالة السيارة وتفاصيل الفحص بنجاح'))
            return redirect('car_condition_list')
        else:
            # طباعة أخطاء النموذج للتصحيح
            print("Form errors:", form.errors)
    else:
        form = CarConditionReportForm(instance=report, user=request.user)
    
    # جلب فئات الفحص وعناصرها المنشطة
    inspection_categories = CarInspectionCategory.objects.filter(is_active=True).prefetch_related(
        Prefetch('inspection_items', queryset=CarInspectionItem.objects.filter(is_active=True).order_by('display_order'))
    ).order_by('display_order')
    
    # الحصول على تفاصيل الفحص الحالية للتقرير إن وجدت
    inspection_details = {}
    for detail in CarInspectionDetail.objects.filter(report=report):
        inspection_details[detail.inspection_item_id] = {
            'condition': detail.condition,
            'notes': detail.notes,
            'needs_repair': detail.needs_repair
        }
    
    context = {
        'form': form,
        'report': report,
        'title': _('تعديل تقرير حالة السيارة'),
        'inspection_categories': inspection_categories,
        'inspection_details': inspection_details,
        'exterior_images': exterior_images,
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
    
    # الحصول على صور الهيكل الخارجي
    exterior_images = CarInspectionImage.objects.filter(
        report=report,
        inspection_detail__isnull=True  # صور عامة للهيكل الخارجي ليست مرتبطة بتفاصيل فحص محددة
    ).order_by('upload_date')
    
    # الحصول على تفاصيل الفحص المتعلقة بالتقرير
    inspection_details = CarInspectionDetail.objects.filter(
        report=report
    ).select_related('inspection_item', 'inspection_item__category').order_by(
        'inspection_item__category__display_order', 'inspection_item__display_order'
    )
    
    # الحصول على قائمة الحجوزات التي يمكن مقارنتها
    comparable_reservations = []
    if report.reservation_id:
        # البحث عن الحجوزات التي لها كل من تقرير تسليم وتقرير استلام
        reservation_ids_with_delivery = set(CarConditionReport.objects.filter(
            report_type='delivery').values_list('reservation_id', flat=True))
        reservation_ids_with_return = set(CarConditionReport.objects.filter(
            report_type='return').values_list('reservation_id', flat=True))
        
        # الحجوزات التي لها كلا النوعين من التقارير
        comparable_reservations = list(reservation_ids_with_delivery.intersection(reservation_ids_with_return))
    
    # تنظيم تفاصيل الفحص حسب الفئة
    inspection_categories = {}
    if inspection_details:
        for detail in inspection_details:
            # تخطي عناصر "الهيكل الخارجي" لأننا نعرضها كصور
            if detail.inspection_item.category.name == 'الهيكل الخارجي':
                continue
            
            category = detail.inspection_item.category
            if category.id not in inspection_categories:
                inspection_categories[category.id] = {
                    'name': category.name,
                    'items': []
                }
            inspection_categories[category.id]['items'].append(detail)
    
    context = {
        'report': report,
        'related_reports': related_reports,
        'inspection_categories': inspection_categories,
        'exterior_images': exterior_images,
        'comparable_reservations': comparable_reservations,
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
    
    # تحميل تفاصيل الفحص لتقرير الإرجاع
    if return_report:
        return_report.inspection_details_list = CarInspectionDetail.objects.filter(
            report=return_report
        ).select_related('inspection_item', 'inspection_item__category').order_by(
            'inspection_item__category__display_order', 'inspection_item__display_order'
        )
    
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
    
    # استخدام القالب الجدولي الرسمي لعرض المقارنة دائماً
    template_name = 'admin/car_condition/car_condition_comparison_table.html'
    
    # إنشاء قائمة بفئات الفحص وعناصرها مع تجميع البيانات بطريقة أفضل
    categories = []
    important_items = set()  # مجموعة العناصر المهمة
    expensive_items = set() # مجموعة العناصر المكلفة
    critical_items = set()  # مجموعة العناصر الحساسة
    
    # تكوين قاموس لتخزين تفاصيل التقارير بشكل أسرع للوصول
    delivery_details = {detail.inspection_item_id: detail for detail in CarInspectionDetail.objects.filter(report=delivery_report)}
    return_details = {detail.inspection_item_id: detail for detail in CarInspectionDetail.objects.filter(report=return_report)}
    
    # حساب إجمالي تكاليف الإصلاح
    total_parts_cost = 0
    total_labor_cost = 0
    
    # الحصول على جميع فئات الفحص النشطة
    inspection_categories = CarInspectionCategory.objects.filter(is_active=True).order_by('display_order')
    
    for category in inspection_categories:
        category_items = []
        
        # الحصول على عناصر الفحص النشطة لهذه الفئة
        inspection_items = CarInspectionItem.objects.filter(category=category, is_active=True).order_by('display_order')
        
        for item in inspection_items:
            # تحديد العناصر المهمة والمكلفة والحساسة بناءً على خصائصها
            # مثال: العناصر المتعلقة بالمحرك أو ناقل الحركة تعتبر مهمة ومكلفة
            item_name_lower = item.name.lower()
            
            is_important = False
            is_expensive = False
            is_critical = False
            
            # تحديد العناصر المهمة
            important_keywords = ['محرك', 'فرامل', 'نظام التعليق', 'ناقل الحركة', 'توجيه', 'كهرباء رئيسية']
            for keyword in important_keywords:
                if keyword in item_name_lower:
                    is_important = True
                    important_items.add(item.id)
                    break
            
            # تحديد العناصر المكلفة
            expensive_keywords = ['محرك', 'ناقل الحركة', 'نظام التعليق', 'كمبيوتر', 'مكيف', 'رادييتر']
            for keyword in expensive_keywords:
                if keyword in item_name_lower:
                    is_expensive = True
                    expensive_items.add(item.id)
                    break
            
            # تحديد العناصر الحساسة (الحرجة)
            critical_keywords = ['فرامل', 'توجيه', 'وسائد هوائية', 'سلامة', 'أمان']
            for keyword in critical_keywords:
                if keyword in item_name_lower:
                    is_critical = True
                    critical_items.add(item.id)
                    break
            
            # إضافة معلومات إضافية للعنصر
            item.is_important = is_important
            item.is_expensive = is_expensive
            item.is_critical = is_critical
            
            # حساب تكاليف الإصلاح
            if item.id in return_details and return_details[item.id].repair_cost:
                total_parts_cost += return_details[item.id].repair_cost or 0
                
            if item.id in return_details and return_details[item.id].labor_cost:
                total_labor_cost += return_details[item.id].labor_cost or 0
            
            category_items.append(item)
        
        # إضافة الفئة وعناصرها للقائمة
        if category_items:  # فقط إضافة الفئات التي تحتوي على عناصر
            category.items = category_items
            categories.append(category)
    
    # إجمالي تكلفة الإصلاح
    total_repair_cost = total_parts_cost + total_labor_cost
    
    context = {
        'reservation': reservation,
        'car': car,
        'delivery_report': delivery_report,
        'return_report': return_report,
        'has_damages': has_damages,
        'current_date': timezone.now(),
        'categories': categories,
        'delivery_details': delivery_details,
        'return_details': return_details,
        'important_items': important_items,
        'expensive_items': expensive_items,
        'critical_items': critical_items,
        'total_parts_cost': total_parts_cost,
        'total_labor_cost': total_labor_cost,
        'total_repair_cost': total_repair_cost
    }
    
    return render(request, template_name, context)


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
            
            # معالجة صور السيارة (هذه الصور تحل محل "الهيكل الخارجي")
            image_types = ['front_image', 'rear_image', 'side_image', 'interior_image']
            
            for image_type in image_types:
                if image_type in request.FILES:
                    image_file = request.FILES[image_type]
                    notes = request.POST.get(f'{image_type}_notes', '')
                    
                    # إنشاء سجل لصورة الفحص
                    CarInspectionImage.objects.create(
                        report=report,
                        image=image_file,
                        description=notes or f'صورة {image_type.replace("_image", "")}',
                        inspection_detail=None  # صورة عامة
                    )
            
            # معالجة عناصر الفحص للفئات الأخرى (غير الهيكل الخارجي)
            for key, value in request.POST.items():
                # معالجة حقول عناصر الفحص
                if key.startswith('inspection_item_') and value:
                    item_id = int(key.replace('inspection_item_', ''))
                    
                    # البحث عن عنصر الفحص
                    try:
                        inspection_item = CarInspectionItem.objects.get(id=item_id)
                        
                        # تخطي عناصر "الهيكل الخارجي" لأننا نستخدم الصور بدلاً منها
                        if inspection_item.category.name == 'الهيكل الخارجي':
                            continue
                            
                        # الحصول على الملاحظات واحتياج الإصلاح
                        notes = request.POST.get(f'notes_item_{item_id}', '')
                        needs_repair = request.POST.get(f'needs_repair_{item_id}', '') == 'on'
                        
                        # إنشاء تفاصيل الفحص
                        CarInspectionDetail.objects.create(
                            report=report,
                            inspection_item=inspection_item,
                            condition=value,
                            notes=notes,
                            needs_repair=needs_repair
                        )
                    except CarInspectionItem.DoesNotExist:
                        pass
            
            messages.success(request, _('تم إنشاء تقرير فحص السيارة بنجاح'))
            
            # توجيه إلى صفحة تفاصيل التقرير
            return redirect('car_inspection_detail', report.id)
    else:
        form = CompleteCarInspectionForm(initial=initial_data, user=request.user)
    
    # جلب فئات الفحص وعناصرها المنشطة بطريقة مُحسنة
    # جلب جميع فئات الفحص المنشطة باستثناء فئة أنظمة السلامة
    inspection_categories = list(CarInspectionCategory.objects.filter(
        is_active=True
    ).exclude(
        name='أنظمة السلامة'  # استبعاد فئة أنظمة السلامة
    ).order_by('display_order'))
    
    # جلب فقط العناصر المهمة والمكلفة (حسب طلب المستخدم)
    inspection_items = CarInspectionItem.objects.filter(
        category__in=inspection_categories,
        is_active=True
    ).filter(
        # عرض العناصر المهمة أو المكلفة أو الحرجة فقط
        Q(is_important=True) | 
        Q(is_expensive=True) | 
        Q(is_critical=True)
    ).order_by('category__display_order', 'display_order')
    
    # تسجيل العناصر المهمة والمكلفة للتشخيص
    for item in inspection_items:
        properties = []
        if item.is_important:
            properties.append("مهم")
            print(f"إضافة العنصر المهم من قاعدة البيانات: {item.name} (ID: {item.id})")
        if item.is_expensive:
            properties.append("مكلف")
            print(f"إضافة العنصر المكلف من قاعدة البيانات: {item.name} (ID: {item.id})")
        if item.is_critical:
            properties.append("حرج")
            print(f"إضافة العنصر الحرج من قاعدة البيانات: {item.name} (ID: {item.id})")
    
    # إنشاء قاموس لربط عناصر الفحص بفئاتها
    category_items = {}
    for item in inspection_items:
        if item.category_id not in category_items:
            category_items[item.category_id] = []
        category_items[item.category_id].append(item)
    
    # إضافة عناصر الفحص كخاصية مؤقتة للفئات
    for category in inspection_categories:
        category.items_list = category_items.get(category.id, [])
    
    # تسجيل عدد الفئات والعناصر للتشخيص
    print(f"✅ عدد فئات الفحص: {len(inspection_categories)}")
    for category in inspection_categories:
        print(f"✅ فئة {category.name}: {len(category.items_list)} عنصر")
    
    # قائمة خيارات حالة العناصر
    condition_choices = CarInspectionItem.CONDITION_CHOICES
    
    context = {
        'form': form,
        'title': _('إنشاء تقرير فحص تفصيلي للسيارة'),
        'car_id': car_id,
        'reservation_id': reservation_id,
        'inspection_categories': inspection_categories,
        'condition_choices': condition_choices
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


@login_required
def car_repair_detail(request, detail_id):
    """عرض وتحديث معلومات الإصلاح والتكاليف للعنصر المتضرر"""
    
    inspection_detail = get_object_or_404(CarInspectionDetail, id=detail_id)
    report = inspection_detail.report
    
    if request.method == 'POST':
        form = CarRepairForm(request.POST, instance=inspection_detail)
        if form.is_valid():
            form.save()
            messages.success(request, _('تم تحديث معلومات الإصلاح بنجاح'))
            return redirect('car_inspection_detail', report_id=report.id)
    else:
        form = CarRepairForm(instance=inspection_detail)
    
    context = {
        'form': form,
        'detail': inspection_detail,
        'report': report,
        'title': _('تفاصيل إصلاح: {}').format(inspection_detail.inspection_item.name)
    }
    
    return render(request, 'admin/car_condition/car_repair_form.html', context)


@login_required
def car_repair_list(request):
    """عرض قائمة بجميع الإصلاحات المطلوبة للسيارات"""
    
    # الحصول على معلمات التصفية
    car_id = request.GET.get('car_id', '')
    repair_status = request.GET.get('repair_status', '')
    date_from = request.GET.get('date_from', '')
    date_to = request.GET.get('date_to', '')
    
    # البحث عن العناصر التي تحتاج إلى إصلاح
    repairs = CarInspectionDetail.objects.filter(needs_repair=True).select_related(
        'report', 'report__car', 'inspection_item', 'inspection_item__category'
    )
    
    # تطبيق التصفية
    if car_id:
        repairs = repairs.filter(report__car_id=car_id)
    
    if repair_status:
        repairs = repairs.filter(repair_status=repair_status)
    
    if date_from:
        repairs = repairs.filter(report__date__gte=date_from)
    
    if date_to:
        repairs = repairs.filter(report__date__lte=date_to)
    
    # ترتيب الإصلاحات حسب حالة الإصلاح والتاريخ
    repairs = repairs.order_by('repair_status', '-report__date')
    
    # الحصول على قائمة بجميع السيارات للفلترة
    cars = Car.objects.all().order_by('make', 'model')
    
    # حساب إجمالي تكاليف الإصلاح
    total_repair_cost = sum(repair.repair_cost or 0 for repair in repairs)
    total_labor_cost = sum(repair.labor_cost or 0 for repair in repairs)
    total_cost = total_repair_cost + total_labor_cost
    
    context = {
        'repairs': repairs,
        'cars': cars,
        'car_id': car_id,
        'repair_status': repair_status,
        'date_from': date_from,
        'date_to': date_to,
        'repair_status_choices': CarInspectionDetail.REPAIR_STATUS_CHOICES,
        'total_repair_cost': total_repair_cost,
        'total_labor_cost': total_labor_cost,
        'total_cost': total_cost,
    }
    
    return render(request, 'admin/car_condition/car_repair_list.html', context)


@login_required
def car_repair_report(request, car_id=None):
    """تقرير إصلاحات السيارات مع إجمالي التكاليف"""
    
    # البحث عن الإصلاحات
    repairs = CarInspectionDetail.objects.filter(needs_repair=True).select_related(
        'report', 'report__car', 'inspection_item', 'inspection_item__category'
    )
    
    # تصفية حسب السيارة إذا تم تحديدها
    if car_id:
        car = get_object_or_404(Car, id=car_id)
        repairs = repairs.filter(report__car=car)
        title = _('تقرير إصلاحات سيارة: {} {}').format(car.make, car.model)
    else:
        car = None
        title = _('تقرير إصلاحات جميع السيارات')
    
    # تجميع البيانات حسب السيارة
    cars_data = {}
    total_all_cars = 0
    
    for repair in repairs:
        car_id = repair.report.car.id
        car_name = f"{repair.report.car.make} {repair.report.car.model} ({repair.report.car.license_plate})"
        
        if car_id not in cars_data:
            cars_data[car_id] = {
                'car': repair.report.car,
                'car_name': car_name,
                'repairs': [],
                'total_cost': 0,
            }
        
        # إضافة تفاصيل الإصلاح
        repair_cost = repair.repair_cost or 0
        labor_cost = repair.labor_cost or 0
        total_item_cost = repair_cost + labor_cost
        
        cars_data[car_id]['repairs'].append({
            'detail': repair,
            'item_name': repair.inspection_item.name,
            'category_name': repair.inspection_item.category.name,
            'repair_cost': repair_cost,
            'labor_cost': labor_cost,
            'total_cost': total_item_cost,
            'status': repair.get_repair_status_display(),
        })
        
        # تحديث المجموع
        cars_data[car_id]['total_cost'] += total_item_cost
        total_all_cars += total_item_cost
    
    context = {
        'title': title,
        'cars_data': cars_data,
        'total_all_cars': total_all_cars,
        'car': car,
    }
    
    return render(request, 'admin/car_condition/car_repair_report.html', context)