"""
إضافة دالة عرض صفحة التحويل البنكي إلى ملف payment_views.py
"""

import os

def add_bank_transfer_view():
    """إضافة دالة عرض صفحة التحويل البنكي"""
    file_path = 'rental/payment_views.py'
    
    if not os.path.exists(file_path):
        print(f"الملف {file_path} غير موجود")
        return False
    
    # دالة عرض صفحة التحويل البنكي
    bank_transfer_view = """
@login_required
def bank_transfer_payment(request):
    \"\"\"Bank transfer payment interface - allows users to view bank account details and enter transfer information\"\"\"
    # التحقق مما إذا كان المستخدم يأتي من حجز محدد
    reservation_id = request.GET.get('reservation_id')
    
    # تحديد لغة المستخدم
    current_language = get_language()
    is_english = current_language == 'en'
    is_rtl = current_language == 'ar'
    
    if not reservation_id:
        # إذا لم يتم تحديد معرف الحجز، إعادة توجيه المستخدم إلى صفحة الحجوزات
        messages.error(
            request, 
            "Reservation ID is required for bank transfer payment." if is_english else 
            "رقم الحجز مطلوب للدفع عبر التحويل البنكي."
        )
        return redirect('my_reservations')
    
    # الحصول على تفاصيل الحجز
    reservation = get_object_or_404(
        Reservation, 
        id=reservation_id, 
        user=request.user, 
        status='confirmed', 
        payment_status='pending'
    )
    
    context = {
        'reservation': reservation,
        'total_amount': reservation.total_price,
        'is_english': is_english,
        'is_rtl': is_rtl
    }
    
    return render(request, 'payment_bank_transfer.html', context)
"""
    
    # قراءة محتوى الملف
    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()
    
    # إضافة الدالة الجديدة في نهاية الملف
    with open(file_path, 'a', encoding='utf-8') as file:
        file.write(bank_transfer_view)
    
    print("تم إضافة دالة عرض صفحة التحويل البنكي بنجاح")
    return True

if __name__ == "__main__":
    add_bank_transfer_view()