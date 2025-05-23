"""دالة عرض مؤقتة ومباشرة لتحليلات المدفوعات

هذا الملف يحتوي على دالة عرض تقارير التحليلات بشكل مباشر وصريح،
وتم إنشاؤه خصيصاً لتجاوز مشكلة القوالب.
"""

from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Sum, Count, Avg, F, Q
from django.db.models.functions import TruncMonth, TruncDay, TruncWeek
from django.utils import timezone
from django.utils.translation import gettext as _
from django.utils.translation import get_language
from django.urls import reverse

from .models import Reservation, User, Car

import calendar
import json
from datetime import datetime, timedelta

from .decorators import admin_required

@login_required
@admin_required
def direct_payment_analytics(request):
    """
    عرض تحليلات المدفوعات بشكل مباشر 
    """
    # الإحصائيات العامة للمدفوعات
    total_revenue = Reservation.objects.filter(payment_status='paid').aggregate(total=Sum('total_price'))['total'] or 0
    pending_revenue = Reservation.objects.filter(payment_status='pending', status='confirmed').aggregate(total=Sum('total_price'))['total'] or 0
    refunded_amount = Reservation.objects.filter(payment_status='refunded').aggregate(total=Sum('total_price'))['total'] or 0
    
    # عدد المدفوعات حسب الحالة
    paid_count = Reservation.objects.filter(payment_status='paid').count()
    pending_count = Reservation.objects.filter(payment_status='pending').count()
    refunded_count = Reservation.objects.filter(payment_status='refunded').count()
    
    # حساب متوسط قيمة الحجز
    avg_reservation_value = 0
    if paid_count > 0:
        avg_reservation_value = total_revenue / paid_count

    # الإيرادات حسب فترات زمنية محددة
    today = timezone.now().date()
    daily_revenue = Reservation.objects.filter(payment_status='paid', created_at__date=today).aggregate(total=Sum('total_price'))['total'] or 0
    
    week_ago = timezone.now() - timedelta(days=7)
    weekly_revenue = Reservation.objects.filter(payment_status='paid', created_at__gte=week_ago).aggregate(total=Sum('total_price'))['total'] or 0
    
    month_start = timezone.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    monthly_revenue = Reservation.objects.filter(payment_status='paid', created_at__gte=month_start).aggregate(total=Sum('total_price'))['total'] or 0
    
    # الإيرادات الشهرية للسنة الحالية
    current_year = timezone.now().year
    monthly_revenue_data = Reservation.objects.filter(
        payment_status='paid',
        created_at__year=current_year
    ).annotate(
        month=TruncMonth('created_at')
    ).values('month').annotate(
        total=Sum('total_price')
    ).order_by('month')
    
    # تحويل البيانات إلى تنسيق مناسب للرسم البياني
    months_data = [0] * 12  # إعداد مصفوفة فارغة للأشهر
    for item in monthly_revenue_data:
        month_index = item['month'].month - 1  # الفهرس يبدأ من 0
        months_data[month_index] = float(item['total'])
    
    # أسماء الأشهر
    months_labels = [_(calendar.month_name[i]) for i in range(1, 13)]
    
    # المدفوعات حسب طريقة الدفع
    payment_methods = Reservation.objects.filter(
        payment_status='paid'
    ).values('payment_method').annotate(
        count=Count('id'),
        total=Sum('total_price')
    ).order_by('-total')
    
    # تحضير بيانات طرق الدفع للرسم البياني
    payment_methods_labels = [method['payment_method'] or "غير محدد" for method in payment_methods]
    payment_methods_data = [float(method['total'] or 0) for method in payment_methods]
    payment_methods_count = [method['count'] for method in payment_methods]
    
    # أكثر المستخدمين إنفاقاً
    top_spending_users = Reservation.objects.filter(
        payment_status='paid'
    ).values(
        'user__id', 'user__first_name', 'user__last_name', 'user__email'
    ).annotate(
        total_spent=Sum('total_price'),
        reservation_count=Count('id')
    ).order_by('-total_spent')[:10]  # أفضل 10 مستخدمين

    # الإيرادات حسب أنواع السيارات
    car_type_revenue = Reservation.objects.filter(
        payment_status='paid'
    ).values('car__category').annotate(
        total=Sum('total_price'),
        count=Count('id')
    ).order_by('-total')
    
    car_types_labels = [car_type['car__category'] for car_type in car_type_revenue]
    car_types_data = [float(car_type['total'] or 0) for car_type in car_type_revenue]
    
    # مؤشرات النمو (مقارنة بالشهر السابق)
    previous_month_start = (month_start - timedelta(days=1)).replace(day=1)
    previous_month_revenue = Reservation.objects.filter(
        payment_status='paid',
        created_at__gte=previous_month_start,
        created_at__lt=month_start
    ).aggregate(total=Sum('total_price'))['total'] or 0
    
    previous_month_count = Reservation.objects.filter(
        payment_status='paid',
        created_at__gte=previous_month_start,
        created_at__lt=month_start
    ).count()
    
    # حساب معدلات النمو
    revenue_growth = 0
    reservation_growth = 0
    
    if previous_month_revenue > 0:
        revenue_growth = ((monthly_revenue - previous_month_revenue) / previous_month_revenue) * 100
    
    if previous_month_count > 0:
        current_month_count = Reservation.objects.filter(
            payment_status='paid',
            created_at__gte=month_start
        ).count()
        reservation_growth = ((current_month_count - previous_month_count) / previous_month_count) * 100
    
    current_language = get_language()
    is_english = current_language == 'en'
    is_rtl = current_language == 'ar'
    
    context = {
        "is_english": is_english,
        "is_rtl": is_rtl,
        'title': _('Payment Analytics'),
        'total_revenue': total_revenue,
        'pending_revenue': pending_revenue,
        'refunded_amount': refunded_amount,
        'paid_count': paid_count,
        'pending_count': pending_count,
        'refunded_count': refunded_count,
        'avg_reservation_value': avg_reservation_value,
        'daily_revenue': daily_revenue,
        'weekly_revenue': weekly_revenue,
        'monthly_revenue': monthly_revenue,
        'months_labels': json.dumps(months_labels),
        'months_data': json.dumps(months_data),
        'payment_methods': payment_methods,
        'payment_methods_labels': json.dumps(payment_methods_labels),
        'payment_methods_data': json.dumps(payment_methods_data),
        'payment_methods_count': json.dumps(payment_methods_count),
        'top_spending_users': top_spending_users,
        'car_type_revenue': car_type_revenue,
        'car_types_labels': json.dumps(car_types_labels),
        'car_types_data': json.dumps(car_types_data),
        'revenue_growth': revenue_growth,
        'reservation_growth': reservation_growth,
        'cache_buster': int(datetime.now().timestamp()),
    }
    
    # استخدام القالب الأصلي مباشرة
    return render(request, 'admin/analytics_reports_fixed.html', context)
