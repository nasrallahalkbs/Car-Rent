"""
إضافة زر مباشر للتحويل البنكي في صفحة الحجوزات
"""

import os
import re

def add_bank_transfer_button_to_reservations():
    """إضافة زر للتحويل البنكي في صفحة الحجوزات"""
    file_path = 'templates/my_reservations_django.html'
    
    if not os.path.exists(file_path):
        print(f"الملف {file_path} غير موجود")
        # البحث عن الملف بطريقة أخرى
        file_path = 'templates/reservations_django.html'
        if not os.path.exists(file_path):
            print(f"الملف {file_path} غير موجود أيضًا")
            return False
    
    # قراءة محتوى الملف
    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()
    
    # البحث عن زر الدفع الحالي
    payment_button_pattern = r'<a href="{% url \'payment_gateway\' %}[^"]*\?reservation_id={{ reservation\.id }}"[^>]*>'
    payment_button_match = re.search(payment_button_pattern, content)
    
    if payment_button_match:
        payment_button = payment_button_match.group(0)
        
        # إنشاء أزرار الدفع الجديدة مع التحويل البنكي
        new_payment_buttons = f"""<div class="d-flex gap-2">
                        {payment_button}
                            <i class="fas fa-credit-card me-1"></i>
                            {{% if is_english %}}Pay Now{{% else %}}ادفع الآن{{% endif %}}
                        </a>
                        <a href="{{% url 'bank_transfer_payment' %}}?reservation_id={{{{ reservation.id }}}}" class="btn btn-outline-primary btn-sm">
                            <i class="fas fa-university me-1"></i>
                            {{% if is_english %}}Bank Transfer{{% else %}}تحويل بنكي{{% endif %}}
                        </a>
                    </div>"""
        
        # استبدال زر الدفع الحالي بأزرار الدفع الجديدة
        new_content = re.sub(
            payment_button_pattern + r'[^<]*</a>', 
            new_payment_buttons, 
            content
        )
        
        # حفظ التغييرات
        with open(file_path, 'w', encoding='utf-8') as file:
            file.write(new_content)
        
        print(f"تم إضافة زر التحويل البنكي إلى صفحة الحجوزات بنجاح في الملف {file_path}")
        return True
    else:
        print("لم يتم العثور على زر الدفع في صفحة الحجوزات")
        return False

def add_bank_transfer_button_to_cart():
    """إضافة زر للتحويل البنكي في صفحة السلة"""
    file_path = 'templates/cart_django.html'
    
    if not os.path.exists(file_path):
        print(f"الملف {file_path} غير موجود")
        return False
    
    # قراءة محتوى الملف
    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()
    
    # البحث عن زر الدفع الحالي
    checkout_button_pattern = r'<a href="{% url \'checkout\' %}" class="btn btn-primary[^"]*"[^>]*>'
    checkout_button_match = re.search(checkout_button_pattern, content)
    
    if checkout_button_match:
        checkout_button = checkout_button_match.group(0)
        
        # إنشاء أزرار الدفع الجديدة
        new_checkout_buttons = f"""<div class="d-grid gap-2">
                        {checkout_button}
                            {{% if is_english %}}Proceed to Checkout{{% else %}}المتابعة للدفع{{% endif %}}
                        </a>
                        <a href="{{% url 'bank_transfer_payment' %}}" class="btn btn-outline-primary">
                            <i class="fas fa-university me-1"></i>
                            {{% if is_english %}}Pay via Bank Transfer{{% else %}}الدفع عبر التحويل البنكي{{% endif %}}
                        </a>
                    </div>"""
        
        # استبدال زر الدفع الحالي بأزرار الدفع الجديدة
        new_content = re.sub(
            checkout_button_pattern + r'[^<]*</a>', 
            new_checkout_buttons, 
            content
        )
        
        # حفظ التغييرات
        with open(file_path, 'w', encoding='utf-8') as file:
            file.write(new_content)
        
        print("تم إضافة زر التحويل البنكي إلى صفحة السلة بنجاح")
        return True
    else:
        print("لم يتم العثور على زر الدفع في صفحة السلة")
        return False

def add_bank_transfer_button_to_navbar():
    """إضافة رابط التحويل البنكي إلى شريط التنقل"""
    file_path = 'templates/layout_django.html'
    
    if not os.path.exists(file_path):
        print(f"الملف {file_path} غير موجود")
        return False
    
    # قراءة محتوى الملف
    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()
    
    # البحث عن قائمة المستخدم
    user_dropdown_pattern = r'{% if user\.is_authenticated %}(.*?){% else %}'
    user_dropdown_match = re.search(user_dropdown_pattern, content, re.DOTALL)
    
    if user_dropdown_match:
        user_dropdown = user_dropdown_match.group(1)
        
        # البحث عن آخر عنصر في قائمة المستخدم للإضافة بعده
        last_item_pattern = r'<li><a class="dropdown-item" href="{% url \'logout\' %}">'
        last_item_match = re.search(last_item_pattern, user_dropdown)
        
        if last_item_match:
            # إضافة رابط التحويل البنكي قبل تسجيل الخروج
            bank_transfer_item = """<li><a class="dropdown-item" href="{% url 'bank_transfer_payment' %}">
                <i class="fas fa-university me-2"></i>
                {% if is_english %}Bank Transfer{% else %}التحويل البنكي{% endif %}
            </a></li>
            """
            
            new_dropdown = user_dropdown.replace(
                last_item_match.group(0),
                bank_transfer_item + last_item_match.group(0)
            )
            
            new_content = content.replace(user_dropdown, new_dropdown)
            
            # حفظ التغييرات
            with open(file_path, 'w', encoding='utf-8') as file:
                file.write(new_content)
            
            print("تم إضافة رابط التحويل البنكي إلى شريط التنقل بنجاح")
            return True
        else:
            print("لم يتم العثور على رابط تسجيل الخروج في قائمة المستخدم")
            return False
    else:
        print("لم يتم العثور على قائمة المستخدم في القالب")
        return False

def main():
    """تنفيذ الدالة الرئيسية للسكريبت"""
    print("بدء إضافة أزرار التحويل البنكي إلى مختلف أجزاء الموقع...")
    
    # إضافة الأزرار
    add_bank_transfer_button_to_reservations()
    add_bank_transfer_button_to_cart()
    add_bank_transfer_button_to_navbar()
    
    print("تم إضافة أزرار التحويل البنكي بنجاح!")

if __name__ == "__main__":
    main()