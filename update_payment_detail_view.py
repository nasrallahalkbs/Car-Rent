"""
تحديث دالة تفاصيل الدفع في ملف admin_views.py
"""

# قم بتعديل ملف admin_views.py بحيث يستبدل دالة payment_details بالدالة التالية:

@login_required
@admin_required
def payment_details(request, payment_id):
    """Admin view to show payment details"""
    payment = get_object_or_404(Reservation, id=payment_id)
    
    # Calculate the number of days between start_date and end_date
    delta = (payment.end_date - payment.start_date).days + 1
    
    # Add additional payment fields needed by template
    payment.date = payment.created_at  # Use created_at for payment date
    payment.reference_number = ''  # Default empty reference number
    payment.status = payment.payment_status  # Map payment_status to status
    payment.amount = payment.total_price  # Map total_price to amount
    
    # Extract payment method and reference number from notes if available
    if payment.notes:
        notes_lines = payment.notes.split('\n')
        for line in notes_lines:
            if 'طريقة الدفع:' in line:
                payment.payment_method = line.split('طريقة الدفع:')[1].strip()
            elif 'رقم المرجع:' in line:
                payment.reference_number = line.split('رقم المرجع:')[1].strip()
    
    # Default values if not found in notes
    if not hasattr(payment, 'payment_method'):
        payment.payment_method = 'visa'  # Default payment method
    
    context = {
        'payment': payment,
        'days': delta,
        'amount': payment.total_price,
        'current_user': request.user,  # Add current user for template access
    }
    
    template_name = 'admin/payment_detail_invoice.html'
    # إضافة مكون زمني لإجبار المتصفح على تحديث الصفحة وعدم استخدام النسخة المخزنة
    context['cache_buster'] = '1744912021'
    return render(request, template_name, context)

