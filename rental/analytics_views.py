"""
وحدة وظائف عرض التقارير والتحليلات الإحصائية للوحة التحكم
"""

from django.shortcuts import render
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db.models import Count, Sum, Avg, F, ExpressionWrapper, DecimalField, DateField
from django.db.models.functions import TruncMonth, TruncDay, Cast
from django.utils import timezone
from django.utils.translation import gettext as _
from django.utils.translation import get_language
from django.urls import reverse
from collections import defaultdict
from datetime import datetime, timedelta
import json
import calendar

from .models import Car, Reservation, User
from .admin_views import admin_required

def get_template_by_language(request, template_name):
    """اختيار القالب المناسب بناءً على اللغة"""
    current_language = get_language()
    is_english = current_language == 'en'
    is_rtl = current_language == 'ar'
    
    # اختيار القالب حسب اللغة المستخدمة
    if template_name.endswith('.html'):
        template_name = template_name[:-5]
    
    return f"{template_name}_django.html", {"is_english": is_english, "is_rtl": is_rtl}

@login_required
@admin_required
def admin_dashboard_analytics(request):
    """
    عرض الإحصائيات والتقارير الرئيسية للوحة التحكم
    """
    # الإحصائيات العامة
    total_cars = Car.objects.count()
    total_reservations = Reservation.objects.count()
    total_users = User.objects.filter(is_staff=False).count()
    total_payments = Reservation.objects.filter(payment_status='paid').aggregate(total=Sum('total_price'))['total'] or 0
    
    # احتساب متوسط تقييم السيارات (تعطيل مؤقتاً)
    avg_rating = 4.5  # قيمة افتراضية عند عدم وجود جدول للتقييمات
    
    # إحصائيات الحجوزات حسب الحالة
    reservation_by_status = Reservation.objects.values('status').annotate(
        count=Count('id')).order_by('status')
    
    # إحصائيات الحجوزات النشطة
    active_reservations = Reservation.objects.filter(
        status__in=['confirmed', 'active', 'pending']
    ).count()
    
    # إحصائيات المدفوعات حسب طريقة الدفع
    payment_by_method = Reservation.objects.filter(payment_status='paid').values('payment_method').annotate(
        count=Count('id'),
        total=Sum('total_price')
    ).order_by('-total')
    
    # الإيرادات الشهرية للسنة الحالية
    current_year = timezone.now().year
    monthly_revenue = Reservation.objects.filter(
        payment_status='paid',
        created_at__year=current_year
    ).annotate(
        month=TruncMonth('created_at')
    ).values('month').annotate(
        total=Sum('total_price')
    ).order_by('month')
    
    # تحويل البيانات إلى تنسيق مناسب للرسم البياني
    months_data = [0] * 12  # إعداد مصفوفة فارغة للأشهر
    for item in monthly_revenue:
        month_index = item['month'].month - 1  # الفهرس يبدأ من 0
        months_data[month_index] = float(item['total'])
    
    # أسماء الأشهر
    months_labels = [_(calendar.month_name[i]) for i in range(1, 13)]
    
    # استخدام 3 أشهر أو 7 أيام
    recent_dates = timezone.now() - timedelta(days=30)
    
    # الإيرادات اليومية لآخر 30 يوم
    daily_revenue = Reservation.objects.filter(
        payment_status='paid',
        created_at__gte=recent_dates
    ).annotate(
        day=TruncDay('created_at')
    ).values('day').annotate(
        total=Sum('total_price')
    ).order_by('day')
    
    # تحويل البيانات إلى تنسيق مناسب للرسم البياني
    daily_data = []
    daily_labels = []
    for item in daily_revenue:
        daily_data.append(float(item['total']))
        daily_labels.append(item['day'].strftime('%Y-%m-%d'))
    
    # معدل الإشغال للسيارات
    # احتساب عدد أيام الإيجار لكل سيارة خلال هذه السنة
    car_occupancy = Reservation.objects.filter(
        status__in=['confirmed', 'active', 'completed'],
        start_date__year=current_year
    ).annotate(
        rental_days=ExpressionWrapper(
            F('end_date') - F('start_date'),
            output_field=DecimalField()
        )
    ).values('car__id', 'car__make', 'car__model').annotate(
        total_days=Sum('rental_days'),
        reservation_count=Count('id')
    ).order_by('-total_days')[:10]  # أفضل 10 سيارات
    
    # السيارات الأكثر حجزاً
    most_booked_cars = Reservation.objects.values(
        'car__id', 'car__make', 'car__model', 'car__category'
    ).annotate(
        count=Count('id')
    ).order_by('-count')[:10]
    
    # تحضير بيانات السيارات الأكثر حجزاً للرسم البياني
    most_booked_labels = [f"{car['car__make']} {car['car__model']}" for car in most_booked_cars]
    most_booked_data = [car['count'] for car in most_booked_cars]
    
    # إحصائيات حسب الفئة
    category_stats = Reservation.objects.values('car__category').annotate(
        count=Count('id'),
        revenue=Sum('total_price')
    ).order_by('-count')
    
    # تحضير بيانات الفئات للرسم البياني دائري
    category_labels = [item['car__category'] for item in category_stats]
    category_data = [item['count'] for item in category_stats]
    category_revenue = [float(item['revenue'] or 0) for item in category_stats]
    
    template_name, context = get_template_by_language(request, 'admin/analytics_dashboard')
    
    context.update({
        'title': _('Analytics Dashboard'),
        'total_cars': total_cars,
        'total_reservations': total_reservations,
        'total_users': total_users,
        'total_payments': total_payments,
        'avg_rating': avg_rating,
        'active_reservations': active_reservations,
        'reservation_by_status': reservation_by_status,
        'payment_by_method': payment_by_method,
        'months_labels': json.dumps(months_labels),
        'months_data': json.dumps(months_data),
        'daily_labels': json.dumps(daily_labels),
        'daily_data': json.dumps(daily_data),
        'most_booked_labels': json.dumps(most_booked_labels),
        'most_booked_data': json.dumps(most_booked_data),
        'category_labels': json.dumps(category_labels),
        'category_data': json.dumps(category_data),
        'category_revenue': json.dumps(category_revenue),
        'car_occupancy': car_occupancy,
        'most_booked_cars': most_booked_cars,
        'category_stats': category_stats,
        'cache_buster': int(datetime.now().timestamp()),
    })
    
    return render(request, template_name, context)