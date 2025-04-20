"""
تحديث قالب تفاصيل الحجز وإضافة معرّف تخزين مؤقت جديد
"""
import os
import time

def update_reservation_detail_template():
    """
    تحديث قالب تفاصيل الحجز وإضافة معرّف تخزين مؤقت
    """
    template_path = 'templates/reservation_detail_django.html'
    
    if not os.path.exists(template_path):
        print(f"خطأ: الملف {template_path} غير موجود")
        return False
    
    print(f"فتح الملف: {template_path}")
    
    with open(template_path, 'r', encoding='utf-8') as file:
        content = file.read()
    
    # إضافة رقم عشوائي كمعرّف تخزين مؤقت
    timestamp = int(time.time())
    new_cache_buster = f"<!-- CACHE_BUSTER {timestamp} -->"
    
    # إذا كان هناك معرّف تخزين مؤقت قديم، قم باستبداله
    import re
    if re.search(r'<!-- CACHE_BUSTER \d+ -->', content):
        content = re.sub(r'<!-- CACHE_BUSTER \d+ -->', new_cache_buster, content, count=1)
    else:
        # إذا لم يكن هناك معرّف، أضفه بعد السطر الأول
        lines = content.split('\n')
        if len(lines) > 0:
            lines.insert(1, new_cache_buster)
            content = '\n'.join(lines)
    
    # تبديل ترتيب معلومات العميل والسيارة
    # تحديد نمط قسم معلومات العميل
    customer_info_pattern = r'<!-- معلومات العميل -->\s*<div class="col-md-6">.*?<div class="card h-100 border-0 shadow-sm">.*?</div>\s*</div>\s*</div>'
    
    # تحديد نمط قسم معلومات السيارة 
    car_info_pattern = r'<!-- معلومات السيارة -->\s*<div class="col-md-6">.*?<div class="card h-100 border-0 shadow-sm">.*?</div>\s*</div>\s*</div>'
    
    # العثور على الأقسام باستخدام تعبيرات منتظمة مع وضع DOTALL
    import re
    customer_info_match = re.search(customer_info_pattern, content, re.DOTALL)
    car_info_match = re.search(car_info_pattern, content, re.DOTALL)
    
    if customer_info_match and car_info_match:
        customer_info = customer_info_match.group(0)
        car_info = car_info_match.group(0)
        
        # تبديل ترتيب العناصر
        modified_content = content.replace(
            customer_info + '\n\n                        ' + car_info,
            car_info + '\n\n                        ' + customer_info
        )
        
        with open(template_path, 'w', encoding='utf-8') as file:
            file.write(modified_content)
            
        print(f"تم تحديث قالب تفاصيل الحجز بنجاح. معرّف التخزين المؤقت الجديد: {timestamp}")
        return True
    else:
        # إذا لم تعمل طريقة التعبيرات المنتظمة نستخدم طريقة بديلة
        # إنشاء محتوى جديد يدويًا مع تغيير ترتيب الأقسام
        
        # البحث عن معلومات العميل والسيارة
        sections = content.split('<!-- معلومات العميل والسيارة -->')
        if len(sections) > 1:
            before_sections = sections[0]
            after_header = sections[1]
            
            subsections = after_header.split('<!-- معلومات السيارة -->')
            if len(subsections) > 1:
                mid_section = subsections[0]
                after_customer = subsections[1]
                
                # استخراج قسم معلومات العميل
                customer_parts = mid_section.split('<!-- معلومات العميل -->')
                if len(customer_parts) > 1:
                    before_customer = customer_parts[0]
                    customer_section = '<!-- معلومات العميل -->' + customer_parts[1]
                    
                    # بناء محتوى جديد مع تبديل الترتيب
                    new_content = before_sections + '<!-- معلومات العميل والسيارة -->' + before_customer + '<!-- معلومات السيارة -->' + after_customer
                    
                    with open(template_path, 'w', encoding='utf-8') as file:
                        file.write(new_content)
                    
                    print(f"تم تحديث قالب تفاصيل الحجز باستخدام طريقة بديلة. معرّف التخزين المؤقت الجديد: {timestamp}")
                    return True
    
    print("فشل في تبديل ترتيب أقسام تفاصيل الحجز")
    return False

# تنفيذ الدالة مباشرة
print("بدء تحديث قالب تفاصيل الحجز...")
update_reservation_detail_template()