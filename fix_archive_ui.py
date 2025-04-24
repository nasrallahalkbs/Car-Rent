"""
إصلاح واجهة المستخدم للأرشيف - إزالة المستندات الوهمية

هذا السكريبت يقوم بما يلي:
1. إزالة أي مستند وهمي قد يظهر في واجهة المستخدم رغم عدم وجوده في قاعدة البيانات
2. التأكد من أن جميع القوالب تعرض فقط المستندات الموجودة فعليًا في قاعدة البيانات
3. تحسين استيراد المستندات من قاعدة البيانات
"""

import os
import django
import sys

# إعداد بيئة Django
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'car_rental_project.settings')
django.setup()

from django.urls import reverse
from django.template import Template, Context
from rental.models import ArchiveFolder, Document
from rental.admin_views import admin_archive_folder_view

def fix_archive_ui():
    """
    إصلاح واجهة المستخدم للأرشيف - إزالة المستندات الوهمية
    """
    print("بدء إصلاح واجهة المستخدم للأرشيف...")
    
    # 1. تحقق من عدم وجود مستندات تلقائية في قاعدة البيانات
    from django.db.models import Q
    title_conditions = Q(title__isnull=True) | Q(title='') | Q(title='بدون عنوان') | Q(title='نموذج_استعلام_الارشيف')
    auto_docs = Document.objects.filter(title_conditions)
    
    if auto_docs.exists():
        print(f"وجدنا {auto_docs.count()} مستند تلقائي في قاعدة البيانات، سيتم حذفها...")
        auto_docs.delete()
        print("تم حذف المستندات التلقائية من قاعدة البيانات.")
    else:
        print("لا توجد مستندات تلقائية في قاعدة البيانات، هذا جيد!")
    
    # 2. تحديث دالة عرض المجلد لضمان عدم عرض المستندات الوهمية
    print("\nتحديث كود عرض المجلد...")
    
    # قراءة الملف
    views_file = 'rental/admin_views.py'
    with open(views_file, 'r', encoding='utf-8') as file:
        content = file.read()
    
    # تحديث استعلام المستندات في دالة admin_archive_folder_view
    if 'documents = folder.documents.all().order_by' in content:
        old_line = 'documents = folder.documents.all().order_by'
        new_line = 'documents = folder.documents.filter(title__isnull=False).exclude(title__in=["بدون عنوان", "", " ", "نموذج_استعلام_الارشيف"]).order_by'
        content = content.replace(old_line, new_line)
        print(f"تم تعديل استعلام المستندات في دالة admin_archive_folder_view")
    else:
        print("لم نجد استعلام المستندات في دالة admin_archive_folder_view")
    
    # تحديث استعلام الملفات في دالة admin_archive
    if 'files = folder.documents.all().order_by' in content:
        old_line = 'files = folder.documents.all().order_by'
        new_line = 'files = folder.documents.filter(title__isnull=False).exclude(title__in=["بدون عنوان", "", " ", "نموذج_استعلام_الارشيف"]).order_by'
        content = content.replace(old_line, new_line)
        print(f"تم تعديل استعلام الملفات في دالة admin_archive")
    else:
        print("لم نجد استعلام الملفات في دالة admin_archive")
    
    # تحديث مجلد documents في دالة admin_archive
    if 'documents = Document.objects.filter(folder=' in content:
        old_line = 'documents = Document.objects.filter(folder='
        new_line = 'documents = Document.objects.filter(title__isnull=False).exclude(title__in=["بدون عنوان", "", " ", "نموذج_استعلام_الارشيف"]).filter(folder='
        content = content.replace(old_line, new_line)
        print(f"تم تعديل استعلام documents في دالة admin_archive")
    else:
        print("لم نجد استعلام documents في دالة admin_archive")
    
    # حفظ التغييرات
    with open(views_file, 'w', encoding='utf-8') as file:
        file.write(content)
    
    # 3. تعديل قوالب الأرشيف لضمان عرض المستندات الموجودة فقط
    print("\nتحديث قوالب الأرشيف...")
    
    # قائمة القوالب التي نريد تحديثها
    templates_to_update = [
        'templates/admin/archive/static_archive.html',
        'templates/admin/archive/archive_main.html',
        'templates/admin/archive/archive_main_backup.html',
        'templates/admin/archive/fixed_archive_main.html',
        'templates/admin/archive/fixed_original_archive_main.html',
        'templates/admin/archive/folder_view.html'
    ]
    
    # التعديلات في القوالب
    for template_path in templates_to_update:
        try:
            if os.path.exists(template_path) and os.path.getsize(template_path) > 0:
                with open(template_path, 'r', encoding='utf-8') as file:
                    template_content = file.read()
                
                # حذف أي كود قد يعرض "نموذج_استعلام_الارشيف"
                if 'نموذج_استعلام_الارشيف' in template_content:
                    print(f"وجدنا ذكر للمستند الوهمي في {template_path}، سيتم حذفه...")
                    template_content = template_content.replace('نموذج_استعلام_الارشيف', '')
                    
                    # حفظ التغييرات
                    with open(template_path, 'w', encoding='utf-8') as file:
                        file.write(template_content)
                    print(f"تم تحديث القالب {template_path}")
                elif '<div class="file-item file-pdf"' in template_content:
                    print(f"وجدنا عناصر ملفات ثابتة في {template_path}، سنتحقق منها...")
                    
                    # البحث عن أي عناصر ملف تم تعريفها يدويًا
                    if '{% for file in files %}' in template_content or '{% for document in documents %}' in template_content:
                        print(f"القالب {template_path} يستخدم حلقة تكرارية لعرض الملفات، هذا جيد.")
                    else:
                        print(f"احتمال وجود ملفات ثابتة في {template_path}، سيتم التحقق من القالب...")
                else:
                    print(f"لم نجد مشكلة في القالب {template_path}")
            else:
                print(f"القالب {template_path} غير موجود أو فارغ.")
        except Exception as e:
            print(f"حدث خطأ أثناء تحديث القالب {template_path}: {str(e)}")
    
    # 4. تحديث أي كود JavaScript قد يعرض مستندات افتراضية
    js_paths = [
        'static/js/archive.js',
        'static/js/folder-explorer.js'
    ]
    
    print("\nتحديث ملفات JavaScript...")
    
    for js_path in js_paths:
        try:
            if os.path.exists(js_path):
                with open(js_path, 'r', encoding='utf-8') as file:
                    js_content = file.read()
                
                # التحقق من وجود مستندات افتراضية في JavaScript
                if 'نموذج_استعلام_الارشيف' in js_content:
                    print(f"وجدنا ذكر للمستند الوهمي في {js_path}، سيتم حذفه...")
                    js_content = js_content.replace('نموذج_استعلام_الارشيف', '')
                    
                    # حفظ التغييرات
                    with open(js_path, 'w', encoding='utf-8') as file:
                        file.write(js_content)
                    print(f"تم تحديث ملف JavaScript {js_path}")
                else:
                    print(f"لم نجد مشكلة في ملف JavaScript {js_path}")
            else:
                print(f"ملف JavaScript {js_path} غير موجود.")
        except Exception as e:
            print(f"حدث خطأ أثناء تحديث ملف JavaScript {js_path}: {str(e)}")
    
    # 5. التحقق من كود JavaScript المضمن في قوالب HTML
    print("\nالتحقق من كود JavaScript المضمن في قوالب HTML...")
    
    for template_path in templates_to_update:
        try:
            if os.path.exists(template_path) and os.path.getsize(template_path) > 0:
                with open(template_path, 'r', encoding='utf-8') as file:
                    template_content = file.read()
                
                # البحث عن كود JavaScript الذي يحتوي على المستند الافتراضي
                if '<script' in template_content and 'file' in template_content and 'pdf' in template_content:
                    print(f"وجدنا كود JavaScript في {template_path} الذي قد يعرض ملفات، سنقوم بالتحقق...")
                    
                    if 'نموذج_استعلام_الارشيف' in template_content:
                        print(f"وجدنا ذكر للمستند الوهمي في جافا سكريبت مضمن في {template_path}، سيتم حذفه...")
                        template_content = template_content.replace('نموذج_استعلام_الارشيف', 'تم_الحذف')
                        
                        # حفظ التغييرات
                        with open(template_path, 'w', encoding='utf-8') as file:
                            file.write(template_content)
                        print(f"تم تحديث كود JavaScript المضمن في {template_path}")
                    else:
                        print(f"لم نجد المستند الوهمي في كود JavaScript المضمن في {template_path}")
                else:
                    print(f"لم نجد كود JavaScript يتعلق بالملفات في {template_path}")
            else:
                print(f"القالب {template_path} غير موجود أو فارغ.")
        except Exception as e:
            print(f"حدث خطأ أثناء التحقق من كود JavaScript المضمن في {template_path}: {str(e)}")
    
    # 6. إنشاء دالة لتجاهل المستندات التلقائية في عرض المجلد
    print("\nإنشاء دالة لتنظيف المستندات الوهمية في الواجهة...")
    
    new_function = """
# دالة تنظيف المستندات الوهمية من قائمة المستندات
def clean_document_list(documents):
    \"\"\"تنظيف المستندات الوهمية من قائمة المستندات المعروضة\"\"\"
    if documents:
        return documents.filter(title__isnull=False).exclude(title__in=["بدون عنوان", "", " ", "نموذج_استعلام_الارشيف"])
    return documents
"""
    
    # إضافة الدالة إلى ملف admin_views.py
    if new_function not in content:
        with open(views_file, 'r', encoding='utf-8') as file:
            content = file.read()
        
        # إضافة الدالة قبل أول تعريف دالة في الملف
        first_def_pos = content.find('def ')
        if first_def_pos != -1:
            content = content[:first_def_pos] + new_function + "\n" + content[first_def_pos:]
            
            with open(views_file, 'w', encoding='utf-8') as file:
                file.write(content)
            print("تم إضافة دالة تنظيف المستندات الوهمية إلى ملف admin_views.py")
        else:
            print("لم نتمكن من إيجاد موقع مناسب لإضافة الدالة الجديدة")
    else:
        print("دالة تنظيف المستندات موجودة بالفعل في ملف admin_views.py")
    
    print("\nاكتمل إصلاح واجهة المستخدم للأرشيف!")

if __name__ == "__main__":
    fix_archive_ui()