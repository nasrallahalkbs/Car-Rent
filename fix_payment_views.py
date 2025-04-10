"""
إصلاح خطأ محاولة تعيين قيمة لخاصية days المحسوبة
"""

def fix_international_payment():
    """تصحيح دالة الدفع الدولي"""
    filepath = "rental/payment_views.py"
    
    with open(filepath, 'r', encoding='utf-8') as file:
        content = file.read()
    
    # إصلاح محاولة تعيين days في دالة professional_payment
    content = content.replace("""        # حساب المجاميع
        grand_total = 0
        for item in cart_items:
            delta = (item.end_date - item.start_date).days + 1
            item.days = delta
            item.total = item.car.daily_rate * delta
            grand_total += item.total""", """        # حساب المجاميع باستخدام الخصائص المحسوبة
        # نستخدم الخواص المحسوبة days و total التي أضفناها لنموذج CartItem
        grand_total = sum(item.total for item in cart_items)""")
    
    # إصلاح محاولة تعيين days في دالة international_payment
    content = content.replace("""        # حساب المجاميع
        grand_total = 0
        for item in cart_items:
            delta = (item.end_date - item.start_date).days + 1
            item.days = delta
            item.total = item.car.daily_rate * delta
            grand_total += item.total""", """        # حساب المجاميع باستخدام الخصائص المحسوبة
        # نستخدم الخواص المحسوبة days و total التي أضفناها لنموذج CartItem
        grand_total = sum(item.total for item in cart_items)""")
    
    with open(filepath, 'w', encoding='utf-8') as file:
        file.write(content)
    
    print("تم تعديل ملف payment_views.py بنجاح!")

if __name__ == "__main__":
    fix_international_payment()
