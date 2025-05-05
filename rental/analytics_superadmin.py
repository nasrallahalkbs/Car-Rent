#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
وحدة التحليلات والإحصائيات للمسؤول الأعلى

توفر هذه الوحدة بيانات تحليلية متقدمة للمسؤول الأعلى عن أداء النظام
ونشاط المستخدمين والمسؤولين والحجوزات وغيرها.
"""

from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Sum, Avg, F, FloatField, ExpressionWrapper
from django.db.models.functions import TruncMonth, TruncDay, ExtractMonth, ExtractYear
from django.utils import timezone
from django.utils.translation import gettext as _
from django.urls import reverse
import json
import datetime

# استيراد نماذج النظام
from django.contrib.auth import get_user_model
from rental.models import Car, Reservation, Review
from rental.models_superadmin import AdminUser, AdminActivity

User = get_user_model()


def get_system_overview_data():
    """الحصول على نظرة عامة على النظام"""
    # الوقت الحالي
    now = timezone.now()
    today = timezone.now().date()
    thirty_days_ago = today - datetime.timedelta(days=30)
    start_of_month = datetime.date(today.year, today.month, 1)
    
    # إحصائيات المستخدمين
    total_users = User.objects.count()
    total_admins = AdminUser.objects.count()
    new_users_this_month = User.objects.filter(date_joined__gte=start_of_month).count()
    
    # إحصائيات السيارات
    total_cars = Car.objects.count()
    active_cars = Car.objects.filter(is_available=True).count()
    
    # إحصائيات الحجوزات
    total_reservations = Reservation.objects.count()
    active_reservations = Reservation.objects.filter(
        start_date__lte=today,
        end_date__gte=today,
        is_cancelled=False
    ).count()
    recent_reservations = Reservation.objects.filter(
        created_at__gte=thirty_days_ago
    ).count()
    
    # إحصائيات المدفوعات (معطلة مؤقتًا لعدم وجود نموذج Payment)
    total_payments = {'count': 0, 'total': 0}
    recent_payments = {'count': 0, 'total': 0}
    
    # إحصائيات التقييمات
    total_reviews = Review.objects.count()
    avg_rating = Review.objects.aggregate(avg=Avg('rating')).get('avg') or 0
    recent_reviews = Review.objects.filter(
        created_at__gte=thirty_days_ago
    ).count()
    
    # إحصائيات النشاط
    admin_activities = AdminActivity.objects.filter(
        timestamp__gte=thirty_days_ago
    ).count()
    
    return {
        'users': {
            'total': total_users,
            'admins': total_admins,
            'new_this_month': new_users_this_month,
        },
        'cars': {
            'total': total_cars,
            'active': active_cars,
            'utilization': round((active_cars / total_cars * 100) if total_cars > 0 else 0, 2)
        },
        'reservations': {
            'total': total_reservations,
            'active': active_reservations,
            'recent': recent_reservations,
        },
        'payments': {
            'total_count': total_payments.get('count') or 0,
            'total_amount': total_payments.get('total') or 0,
            'recent_count': recent_payments.get('count') or 0,
            'recent_amount': recent_payments.get('total') or 0,
        },
        'reviews': {
            'total': total_reviews,
            'average': round(avg_rating, 2),
            'recent': recent_reviews,
        },
        'activities': {
            'admin_activities': admin_activities,
        },
        'date_info': {
            'today': today,
            'thirty_days_ago': thirty_days_ago,
            'start_of_month': start_of_month,
        }
    }


def get_monthly_reservation_data():
    """الحصول على بيانات الحجوزات الشهرية للرسوم البيانية"""
    today = timezone.now().date()
    one_year_ago = today - datetime.timedelta(days=365)
    
    # الحصول على الحجوزات مجمعة حسب الشهر
    reservations_by_month = Reservation.objects.filter(
        created_at__gte=one_year_ago
    ).annotate(
        month=TruncMonth('created_at')
    ).values('month').annotate(
        count=Count('id')
    ).order_by('month')
    
    # تنسيق البيانات للرسم البياني
    months = []
    counts = []
    
    for entry in reservations_by_month:
        month_name = entry['month'].strftime('%B %Y')
        months.append(month_name)
        counts.append(entry['count'])
    
    return {
        'labels': months,
        'data': counts
    }


def get_user_registration_data():
    """الحصول على بيانات تسجيل المستخدمين الشهرية"""
    today = timezone.now().date()
    one_year_ago = today - datetime.timedelta(days=365)
    
    # الحصول على المستخدمين مجمعين حسب الشهر
    users_by_month = User.objects.filter(
        date_joined__gte=one_year_ago
    ).annotate(
        month=TruncMonth('date_joined')
    ).values('month').annotate(
        count=Count('id')
    ).order_by('month')
    
    # تنسيق البيانات للرسم البياني
    months = []
    counts = []
    
    for entry in users_by_month:
        month_name = entry['month'].strftime('%B %Y')
        months.append(month_name)
        counts.append(entry['count'])
    
    return {
        'labels': months,
        'data': counts
    }


def get_payment_data():
    """الحصول على بيانات المدفوعات الشهرية (بيانات تجريبية لقالب العرض)"""
    # تنسيق البيانات للرسم البياني - بيانات تجريبية لقالب العرض
    months = [
        'يناير 2025', 'فبراير 2025', 'مارس 2025', 'أبريل 2025', 'مايو 2025'
    ]
    
    amounts = [12000, 15000, 13500, 17800, 14200]
    counts = [23, 28, 25, 30, 27]
    
    return {
        'labels': months,
        'amounts': amounts,
        'counts': counts
    }


def get_top_cars_data():
    """الحصول على بيانات أكثر السيارات حجزاً"""
    # الحصول على أكثر 10 سيارات حجزاً
    top_cars = Car.objects.annotate(
        reservations_count=Count('reservation')
    ).values(
        'id', 'make', 'model', 'year', 'reservations_count'
    ).order_by('-reservations_count')[:10]
    
    # تنسيق البيانات للرسم البياني
    cars = []
    counts = []
    
    for car in top_cars:
        car_name = f"{car['make']} {car['model']} ({car['year']})"
        cars.append(car_name)
        counts.append(car['reservations_count'])
    
    return {
        'labels': cars,
        'data': counts
    }


def get_admin_activity_data():
    """الحصول على بيانات نشاط المسؤولين"""
    today = timezone.now().date()
    thirty_days_ago = today - datetime.timedelta(days=30)
    
    # الحصول على نشاط المسؤولين حسب اليوم
    activities_by_day = AdminActivity.objects.filter(
        timestamp__gte=thirty_days_ago
    ).annotate(
        day=TruncDay('timestamp')
    ).values('day').annotate(
        count=Count('id')
    ).order_by('day')
    
    # تنسيق البيانات للرسم البياني
    days = []
    counts = []
    
    for entry in activities_by_day:
        day_name = entry['day'].strftime('%d %b')
        days.append(day_name)
        counts.append(entry['count'])
    
    return {
        'labels': days,
        'data': counts
    }


def get_reviews_distribution_data():
    """الحصول على بيانات توزيع التقييمات"""
    # الحصول على توزيع التقييمات
    rating_distribution = Review.objects.values('rating').annotate(
        count=Count('id')
    ).order_by('rating')
    
    # تنسيق البيانات للرسم البياني
    ratings = []
    counts = []
    
    # التأكد من وجود جميع التقييمات من 1 إلى 5
    rating_dict = {item['rating']: item['count'] for item in rating_distribution}
    
    for i in range(1, 6):
        ratings.append(str(i))
        counts.append(rating_dict.get(i, 0))
    
    return {
        'labels': ratings,
        'data': counts
    }


@login_required
def superadmin_analytics(request):
    """عرض صفحة التحليلات والإحصائيات للمسؤول الأعلى"""
    # التحقق من أن المستخدم هو مسؤول أعلى
    try:
        admin_user = AdminUser.objects.get(user=request.user)
        if not admin_user.is_superadmin:
            return render(request, 'superadmin/access_denied.html', {
                'message': _('لا يمكنك الوصول إلى لوحة التحليلات والإحصائيات')
            })
    except AdminUser.DoesNotExist:
        return render(request, 'superadmin/access_denied.html', {
            'message': _('لا يمكنك الوصول إلى لوحة التحليلات والإحصائيات')
        })
    
    # جمع البيانات التحليلية
    system_overview = get_system_overview_data()
    monthly_reservations = get_monthly_reservation_data()
    user_registrations = get_user_registration_data()
    payment_data = get_payment_data()
    top_cars = get_top_cars_data()
    admin_activity = get_admin_activity_data()
    reviews_distribution = get_reviews_distribution_data()
    
    # تسجيل نشاط المسؤول
    AdminActivity.objects.create(
        admin=admin_user,
        action=_('عرض لوحة التحليلات والإحصائيات'),
        ip_address=request.META.get('REMOTE_ADDR', ''),
        user_agent=request.META.get('HTTP_USER_AGENT', ''),
    )
    
    # تجهيز البيانات لمخططات ApexCharts
    charts_data = {
        'monthly_reservations': {
            'labels': json.dumps(monthly_reservations['labels']),
            'data': json.dumps(monthly_reservations['data']),
        },
        'user_registrations': {
            'labels': json.dumps(user_registrations['labels']),
            'data': json.dumps(user_registrations['data']),
        },
        'payment_data': {
            'labels': json.dumps(payment_data['labels']),
            'amounts': json.dumps(payment_data['amounts']),
            'counts': json.dumps(payment_data['counts']),
        },
        'top_cars': {
            'labels': json.dumps(top_cars['labels']),
            'data': json.dumps(top_cars['data']),
        },
        'admin_activity': {
            'labels': json.dumps(admin_activity['labels']),
            'data': json.dumps(admin_activity['data']),
        },
        'reviews_distribution': {
            'labels': json.dumps(reviews_distribution['labels']),
            'data': json.dumps(reviews_distribution['data']),
        },
    }
    
    context = {
        'admin_user': admin_user,
        'system_overview': system_overview,
        'charts_data': charts_data,
    }
    
    return render(request, 'superadmin/analytics_dashboard.html', context)
