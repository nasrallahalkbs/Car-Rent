"""
إصلاح مشكلة عدم ظهور صور السيارات في الصفحة الرئيسية

هذا السكريبت يقوم بإصلاح مشكلة مسارات الوسائط عند استخدام بادئات اللغة في تطبيق Django.
يضيف تعديلات على ملفات المشروع لمعالجة المسارات بشكل صحيح.
"""

import os

def fix_car_rental_urls():
    """
    تعديل ملف urls.py الرئيسي لخدمة ملفات الوسائط بشكل صحيح مع بادئات اللغة
    """
    urls_file = 'car_rental_project/urls.py'
    
    with open(urls_file, 'r', encoding='utf-8') as file:
        content = file.read()
    
    # تحديث إعدادات خدمة ملفات الوسائط
    # نقوم بنقل إعدادات الوسائط خارج شرط DEBUG لتعمل في جميع الحالات
    if 'if settings.DEBUG:' in content:
        # إزالة الشرط ووضع الأسطر خارج الشرط
        updated_content = content.replace(
            """# خدمة ملفات الوسائط والملفات الثابتة أثناء التطوير
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)""",
            
            """# خدمة ملفات الوسائط والملفات الثابتة
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)"""
        )
        
        with open(urls_file, 'w', encoding='utf-8') as file:
            file.write(updated_content)
            
        print(f"✅ تم تحديث {urls_file} لخدمة ملفات الوسائط بشكل صحيح")
    else:
        print("⚠️ لم يتم العثور على القسم المطلوب تعديله في ملف URLs")

def fix_base_template():
    """
    تعديل القالب الأساسي لتصحيح مسارات الصور
    """
    # هذه الدالة ستضيف تعديلات على القوالب الرئيسية إذا لزم الأمر
    pass

def add_view_context_processor():
    """
    إضافة معالج سياق لتصحيح مسارات الوسائط في القوالب
    """
    context_processor_file = 'rental/context_processors.py'
    
    with open(context_processor_file, 'r', encoding='utf-8') as file:
        content = file.read()
    
    if 'def media_url_context(request):' not in content:
        # إضافة معالج سياق جديد
        media_context_processor = '''
def media_url_context(request):
    """
    إضافة مسار الوسائط الصحيح إلى سياق القالب
    """
    from django.conf import settings
    return {
        'MEDIA_URL': settings.MEDIA_URL,
        'MEDIA_ROOT': settings.MEDIA_ROOT,
    }
'''
        with open(context_processor_file, 'a', encoding='utf-8') as file:
            file.write(media_context_processor)
        
        print(f"✅ تم إضافة معالج سياق MEDIA_URL إلى {context_processor_file}")
        
        # الآن نضيف المعالج الجديد إلى قائمة معالجات السياق في settings.py
        settings_file = 'car_rental_project/settings.py'
        with open(settings_file, 'r', encoding='utf-8') as file:
            settings_content = file.read()
        
        if "'rental.context_processors.media_url_context'," not in settings_content:
            # إضافة معالج السياق الجديد إلى قائمة معالجات السياق
            updated_settings = settings_content.replace(
                "'rental.context_processors.admin_notifications',",
                "'rental.context_processors.admin_notifications',\n                'rental.context_processors.media_url_context',"
            )
            
            with open(settings_file, 'w', encoding='utf-8') as file:
                file.write(updated_settings)
            
            print(f"✅ تم إضافة معالج سياق MEDIA_URL إلى قائمة معالجات السياق في {settings_file}")
    else:
        print("⚠️ معالج سياق MEDIA_URL موجود بالفعل")

def update_car_template():
    """
    تحديث قالب عرض السيارات لاستخدام مسار الوسائط الصحيح
    """
    template_file = 'templates/cars_enhanced_django.html'
    
    with open(template_file, 'r', encoding='utf-8') as file:
        content = file.read()
    
    # تصحيح رابط الصورة باستخدام MEDIA_URL من السياق
    updated_content = content.replace(
        '<img src="{{ car.image.url }}" class="card-img-top car-image" alt="{{ car.make }} {{ car.model }}">',
        '<img src="/media/{{ car.image.name }}" class="card-img-top car-image" alt="{{ car.make }} {{ car.model }}">'
    )
    
    with open(template_file, 'w', encoding='utf-8') as file:
        file.write(updated_content)
    
    print(f"✅ تم تحديث قالب عرض السيارات {template_file}")
    
    # تحديث القوالب الأخرى التي تعرض صور السيارات
    other_templates = [
        'templates/cars_enhanced.html',
        'templates/favorite_cars_django.html'
    ]
    
    for template in other_templates:
        if os.path.exists(template):
            with open(template, 'r', encoding='utf-8') as file:
                content = file.read()
            
            updated_content = content.replace(
                '<img src="{{ car.image.url }}" class="card-img-top car-image" alt="{{ car.make }} {{ car.model }}">',
                '<img src="/media/{{ car.image.name }}" class="card-img-top car-image" alt="{{ car.make }} {{ car.model }}">'
            )
            
            # تحديث أيضًا للسيارات المفضلة
            updated_content = updated_content.replace(
                '<img src="{{ favorite.car.image.url }}" class="card-img-top car-image" alt="{{ favorite.car.make }} {{ favorite.car.model }}">',
                '<img src="/media/{{ favorite.car.image.name }}" class="card-img-top car-image" alt="{{ favorite.car.make }} {{ favorite.car.model }}">'
            )
            
            with open(template, 'w', encoding='utf-8') as file:
                file.write(updated_content)
            
            print(f"✅ تم تحديث قالب {template}")

def main():
    """
    تنفيذ جميع إصلاحات مسارات الوسائط
    """
    print("بدء إصلاح مشكلة مسارات الوسائط...")
    
    # إصلاح ملف URLs الرئيسي
    fix_car_rental_urls()
    
    # إضافة معالج سياق للوسائط
    add_view_context_processor()
    
    # تحديث قوالب عرض السيارات
    update_car_template()
    
    print("✅ تم الانتهاء من إصلاح مشكلة مسارات الوسائط")

if __name__ == "__main__":
    main()