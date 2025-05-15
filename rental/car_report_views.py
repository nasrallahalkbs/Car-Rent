from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.utils.translation import gettext as _
from django.shortcuts import get_object_or_404
from rental.models import Car

@login_required
def car_print_settings(request):
    """صفحة إعدادات طباعة تقارير السيارات"""
    context = {
        'title': _('إعدادات طباعة تقارير السيارات'),
        'section': 'reports',
        'report_type': 'cars'
    }
    
    # استخدام قالب إعدادات الطباعة العام
    return render(request, 'admin/reports/print_settings.html', context)

@login_required
def car_print_settings_with_id(request, car_id):
    """صفحة إعدادات طباعة تقرير سيارة محددة"""
    car = get_object_or_404(Car, id=car_id)
    
    context = {
        'title': _('إعدادات طباعة تقرير السيارة: {}').format(car),
        'section': 'reports',
        'report_type': 'car',
        'car': car
    }
    
    # استخدام قالب إعدادات الطباعة العام
    return render(request, 'admin/reports/print_settings.html', context)