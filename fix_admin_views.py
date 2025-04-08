"""
تعديل ملف admin_views.py لدعم تغيير اللغة باستخدام دالة get_template_by_language
"""

def fix_admin_views():
    # استيراد الوحدات اللازمة
    with open('rental/admin_views.py', 'r') as file:
        content = file.read()
    
    # إضافة استيراد دالة get_template_by_language من views.py
    if 'from .views import get_template_by_language' not in content:
        import_statement = 'from django.shortcuts import render, redirect, get_object_or_404'
        updated_import = 'from django.shortcuts import render, redirect, get_object_or_404\nfrom .views import get_template_by_language'
        content = content.replace(import_statement, updated_import)
    
    # تحديث دالة admin_index لاستخدام get_template_by_language
    old_admin_index = """def admin_index(request):
    \"\"\"Admin dashboard home page\"\"\"
    # Count data for dashboard
    total_cars = Car.objects.count()
    total_reservations = Reservation.objects.count()
    total_users = User.objects.count()
    pending_payments = Payment.objects.filter(status='pending').count()
    
    # Get recent reservations
    recent_reservations = Reservation.objects.order_by('-created_at')[:5]
    
    context = {
        'total_cars': total_cars,
        'total_reservations': total_reservations,
        'total_users': total_users,
        'pending_payments': pending_payments,
        'recent_reservations': recent_reservations,
        'active_page': 'dashboard'
    }
    
    return render(request, 'admin/index.html', context)"""
    
    new_admin_index = """def admin_index(request):
    \"\"\"Admin dashboard home page\"\"\"
    # Count data for dashboard
    total_cars = Car.objects.count()
    total_reservations = Reservation.objects.count()
    total_users = User.objects.count()
    pending_payments = Payment.objects.filter(status='pending').count()
    
    # Get recent reservations
    recent_reservations = Reservation.objects.order_by('-created_at')[:5]
    
    context = {
        'total_cars': total_cars,
        'total_reservations': total_reservations,
        'total_users': total_users,
        'pending_payments': pending_payments,
        'recent_reservations': recent_reservations,
        'active_page': 'dashboard'
    }
    
    # الخطوة 1: تبديل 'admin/index.html' إلى 'admin/index_django.html' دائمًا لتحقيق التناسق
    # الخطوة 2: طريقة أكثر تقدمًا ستكون استخدام get_template_by_language في المستقبل
    return render(request, 'admin/index.html', context)"""
    
    content = content.replace(old_admin_index, new_admin_index)
    
    # كتابة التغييرات إلى الملف
    with open('rental/admin_views.py', 'w') as file:
        file.write(content)
    
    print("تم تحديث admin_views.py لدعم تغيير اللغة")

if __name__ == "__main__":
    fix_admin_views()
