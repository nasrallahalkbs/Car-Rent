"""
إصلاح مشكلة خطأ "حالة الحجز غير صالحة" في صفحة تفاصيل الحجز
"""

def fix_reservation_status_error():
    """
    تصحيح خطأ حالة الحجز غير صالحة في عرض التفاصيل
    
    المشكلة: عند النقر على زر "عرض" في صفحة الحجوزات، يظهر خطأ "حالة الحجز غير صالحة"
    السبب المحتمل: معلمة المسار URL تستخدم كلمة "view" في نهاية المسار مما يسبب تفسيرها كحالة
    الحل: تعديل الشيفرة للتعامل مع الحالة الخاصة "view" أو تعديل رابط URL
    """
    import os
    
    # تحديث ملف المسارات URLs
    urls_file = 'rental/urls.py'
    if os.path.exists(urls_file):
        with open(urls_file, 'r', encoding='utf-8') as file:
            content = file.read()
        
        # نغير مسار عرض التفاصيل ليكون له اسم مختلف
        if "path('dashboard/reservations/<int:reservation_id>/view/'" in content:
            content = content.replace(
                "path('dashboard/reservations/<int:reservation_id>/view/', admin_views.admin_reservation_detail, name='admin_reservation_detail')",
                "path('dashboard/reservations/<int:reservation_id>/details/', admin_views.admin_reservation_detail, name='admin_reservation_detail')"
            )
            
            with open(urls_file, 'w', encoding='utf-8') as file:
                file.write(content)
            print(f"تم تحديث مسار عرض التفاصيل في {urls_file}")
        
    # تحديث دالة update_reservation_status
    views_file = 'rental/admin_views.py'
    if os.path.exists(views_file):
        with open(views_file, 'r', encoding='utf-8') as file:
            content = file.read()
        
        # إضافة رسائل تشخيصية لفحص مشكلة الحالة
        status_validation = '''
    # تشخيص الأخطاء
    print(f"DIAGNOSTIC: Request received for reservation {reservation_id} with status {status}")
    
    valid_statuses = ['pending', 'confirmed', 'completed', 'cancelled', 'view', 'details']
    if status not in valid_statuses:
        print(f"ERROR: Invalid status '{status}' received for reservation {reservation_id}")
        messages.error(request, f"حالة الحجز غير صالحة: {status}")
        return redirect('admin_reservations')
        
    # معالجة حالة 'view' أو 'details' الخاصة
    if status in ['view', 'details']:
        # عرض التفاصيل بدلاً من تحديث الحالة
        return admin_reservation_detail(request, reservation_id)'''
        
        # استبدال التحقق من الحالة بالكود المحسن
        old_validation = '''
    valid_statuses = ['pending', 'confirmed', 'completed', 'cancelled']
    if status not in valid_statuses:
        messages.error(request, "حالة الحجز غير صالحة!")
        return redirect('admin_reservations')'''
        
        if old_validation in content:
            content = content.replace(old_validation, status_validation)
            
            with open(views_file, 'w', encoding='utf-8') as file:
                file.write(content)
            print(f"تم تحديث التحقق من حالة الحجز في {views_file}")
            
    # تحديث قالب الحجوزات لاستخدام المسار الجديد
    template_file = 'templates/admin/reservations_django.html'
    if os.path.exists(template_file):
        with open(template_file, 'r', encoding='utf-8') as file:
            content = file.read()
        
        # تحديث URL في القالب
        if '<a href="{% url \'admin_reservation_detail\' reservation.id %}"' in content:
            updated_content = content.replace(
                '<a href="{% url \'admin_reservation_detail\' reservation.id %}"',
                '<a href="/ar/dashboard/reservations/{{ reservation.id }}/details/"'
            )
            
            with open(template_file, 'w', encoding='utf-8') as file:
                file.write(updated_content)
            print(f"تم تحديث رابط عرض التفاصيل في {template_file}")
    
    # تأكد من وجود قالب تفاصيل الحجز
    template_path = 'templates/admin/reservation_detail_simple.html'
    if os.path.exists(template_path):
        print(f"تم التأكد من وجود قالب التفاصيل: {template_path}")
    else:
        print(f"تحذير: قالب التفاصيل غير موجود: {template_path}")
    
    print("تم الانتهاء من إصلاح مشكلة حالة الحجز غير صالحة")

if __name__ == "__main__":
    fix_reservation_status_error()