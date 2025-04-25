"""
إصلاح مشكلة عدم ظهور المستندات المرفوعة في صفحة الأرشيف

هذا السكريبت يقوم بإصلاح مشكلة عدم ظهور المستندات المرفوعة في المجلدات
من خلال تحسين وظيفة رفع الملفات وعرضها في صفحة الأرشيف.
"""

import os
import django
import sys

# إعداد بيئة Django
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'carRental.settings')
django.setup()

from django.urls import path
from rental.models import Document, ArchiveFolder
from django.db import connection

def fix_upload_function():
    """
    إصلاح وظيفة رفع المستندات في ملف admin_views.py
    """
    views_path = "rental/admin_views.py"
    
    # قراءة الملف
    with open(views_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # إضافة وظيفة رفع المستندات المحسنة
    new_function = """
@login_required
@admin_required
def admin_archive_upload(request):
    \"\"\"وظيفة مخصصة لرفع المستندات إلى الأرشيف\"\"\"
    if request.method == 'POST':
        title = request.POST.get('title', '')
        description = request.POST.get('description', '')
        folder_id = request.POST.get('folder', None)
        document_type = request.POST.get('document_type', 'other')
        
        # التحقق من وجود عنوان وملف
        if not title:
            messages.error(request, "يرجى إدخال عنوان للمستند")
            return redirect('admin_archive')
        
        if 'file' not in request.FILES:
            messages.error(request, "يرجى اختيار ملف للرفع")
            return redirect('admin_archive')
        
        uploaded_file = request.FILES['file']
        
        # البحث عن المجلد إذا تم تحديده
        folder = None
        if folder_id:
            try:
                folder = ArchiveFolder.objects.get(id=folder_id)
                print(f"DEBUG - تم العثور على المجلد: {folder.name} (ID: {folder.id})")
            except ArchiveFolder.DoesNotExist:
                messages.error(request, "المجلد المحدد غير موجود")
                return redirect('admin_archive')
        
        try:
            # إضافة علامة واضحة لمنع إنشاء مستندات بشكل تلقائي
            if folder is not None:
                if not hasattr(folder, '_skip_auto_document_creation'):
                    setattr(folder, '_skip_auto_document_creation', True)
            
            # قراءة معلومات الملف لتخزينه في قاعدة البيانات
            file_name = uploaded_file.name
            file_type = uploaded_file.content_type
            file_size = uploaded_file.size
            file_content = uploaded_file.read()
            
            # إنشاء المستند مع تخزين الملف في قاعدة البيانات
            document = Document(
                title=title,
                description=description,
                document_type=document_type,
                folder=folder,
                created_by=request.user if hasattr(request, 'user') else None,
                file_name=file_name,
                file_type=file_type,
                file_size=file_size,
                file_content=file_content
            )
            
            # التأكد من تعيين علامات لمنع أي آليات تلقائية
            document._from_upload = True
            document.is_auto_created = False
            
            # حفظ المستند
            document.save()
            
            print(f"DEBUG - تم إنشاء مستند جديد: {document.title} في المجلد: {folder.name if folder else 'لا يوجد'}")
            
            messages.success(request, f"تم رفع المستند '{title}' بنجاح")
            
            # إعادة التوجيه إلى صفحة الأرشيف مع تحديد المجلد الحالي
            if folder:
                return redirect(f"/ar/dashboard/archive/?folder={folder.id}")
            else:
                return redirect('admin_archive')
            
        except Exception as e:
            print(f"ERROR - حدث خطأ أثناء رفع المستند: {str(e)}")
            messages.error(request, f"حدث خطأ أثناء رفع المستند: {str(e)}")
            return redirect('admin_archive')
    
    # إذا كانت الطريقة غير POST، إعادة التوجيه إلى صفحة الأرشيف
    return redirect('admin_archive')
"""
    
    # إضافة الوظيفة إلى الملف إذا لم تكن موجودة بالفعل
    if "def admin_archive_upload(request):" not in content:
        # إضافة الوظيفة في نهاية الملف
        updated_content = content + "\n" + new_function
        
        with open(views_path, 'w', encoding='utf-8') as f:
            f.write(updated_content)
        
        print(f"تم إضافة وظيفة admin_archive_upload إلى {views_path}")
        return True
    else:
        print("وظيفة admin_archive_upload موجودة بالفعل في ملف admin_views.py")
        return False

def fix_display_function():
    """
    تحسين وظيفة عرض المستندات في صفحة الأرشيف
    """
    views_path = "rental/admin_views.py"
    
    # قراءة الملف
    with open(views_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # البحث عن جزء استعلام المستندات في دالة admin_archive
    import re
    
    # نمط للبحث عن استعلام المستندات
    documents_query_pattern = r"# الحصول على المستندات في هذا المجلد مع تطبيق البحث إذا وجد.*?if search:"
    
    documents_query_match = re.search(documents_query_pattern, content, re.DOTALL)
    
    if documents_query_match:
        old_query = documents_query_match.group(0)
        
        # استبدال بكود محسن لاستعلام المستندات
        new_query = """# الحصول على المستندات في هذا المجلد مع تطبيق البحث إذا وجد
    # استعلام محسّن يعرض جميع المستندات الصالحة
    files = folder.documents.filter(
        title__isnull=False,
        is_auto_created=False  # استبعاد المستندات التلقائية
    ).exclude(
        title__in=["بدون عنوان", "", " ", "نموذج_استعلام_الارشيف", None]
    ).order_by('-created_at')
    
    print(f"🔍 عدد المستندات في المجلد {folder.id}: {files.count()}")
    
    # طباعة معلومات عن المستندات للتصحيح
    for doc in files:
        file_info = f"file_content: يوجد" if doc.file_content else "لا يوجد file_content"
        file_path = f"file: {doc.file.path}" if doc.file else "لا يوجد file"
        print(f"🧾 مستند: {doc.id} | {doc.title} | {file_info} | {file_path}")
    
    if search:"""
        
        # استبدال الجزء القديم بالجزء الجديد
        updated_content = content.replace(old_query, new_query)
        
        with open(views_path, 'w', encoding='utf-8') as f:
            f.write(updated_content)
        
        print(f"تم تحسين استعلام المستندات في {views_path}")
        return True
    else:
        print("لم يتم العثور على جزء استعلام المستندات في ملف admin_views.py")
        return False

def add_upload_url():
    """
    إضافة مسار URL للوظيفة الجديدة admin_archive_upload
    """
    urls_path = "rental/urls.py"
    
    # قراءة الملف
    with open(urls_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # البحث عن مسارات الأرشيف
    archive_urls_pattern = r"# مسار الأرشيف الإلكتروني.*?path\('dashboard/archive/document.*?\),"
    
    archive_urls_match = re.search(archive_urls_pattern, content, re.DOTALL)
    
    if archive_urls_match:
        old_urls = archive_urls_match.group(0)
        
        # إضافة مسار جديد إذا لم يكن موجوداً
        if "admin_archive_upload" not in old_urls:
            new_url = "\n    path('dashboard/archive/upload/', admin_views.admin_archive_upload, name='admin_archive_upload'),"
            
            # إضافة المسار الجديد بعد مسارات الأرشيف الحالية
            new_urls = old_urls + new_url
            
            # استبدال المسارات القديمة بالمسارات الجديدة
            updated_content = content.replace(old_urls, new_urls)
            
            with open(urls_path, 'w', encoding='utf-8') as f:
                f.write(updated_content)
            
            print(f"تم إضافة مسار admin_archive_upload إلى {urls_path}")
            return True
        else:
            print("مسار admin_archive_upload موجود بالفعل في ملف urls.py")
            return False
    else:
        print("لم يتم العثور على مسارات الأرشيف في ملف urls.py")
        return False

def update_template_form():
    """
    تحديث نموذج رفع الملفات في قالب الأرشيف
    """
    template_path = "templates/admin/archive/fixed_archive_main.html"
    
    # التحقق من وجود القالب
    if not os.path.exists(template_path):
        print(f"القالب {template_path} غير موجود")
        return False
    
    # قراءة الملف
    with open(template_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # البحث عن نموذج رفع الملفات
    file_form_pattern = r'<form action="{% url \'admin_archive_upload\' %}" method="post".*?</form>'
    
    file_form_match = re.search(file_form_pattern, content, re.DOTALL)
    
    if file_form_match:
        old_form = file_form_match.group(0)
        
        # التحقق من وجود حقل المجلد
        if "name=\"folder\"" not in old_form:
            # تحديث النموذج بإضافة حقل المجلد
            updated_form = old_form.replace(
                "{% if current_folder %}",
                """{% if current_folder %}
                                <input type="hidden" name="folder" value="{{ current_folder.id }}">"""
            )
            
            # استبدال النموذج القديم بالنموذج المحدث
            updated_content = content.replace(old_form, updated_form)
            
            with open(template_path, 'w', encoding='utf-8') as f:
                f.write(updated_content)
            
            print(f"تم تحديث نموذج رفع الملفات في {template_path}")
            return True
        else:
            print("حقل المجلد موجود بالفعل في نموذج رفع الملفات")
            return False
    else:
        print("لم يتم العثور على نموذج رفع الملفات في القالب")
        return False

def verify_document_uploads():
    """
    فحص قاعدة البيانات للتحقق من وجود مستندات مرفوعة في المجلدات
    """
    try:
        cursor = connection.cursor()
        
        # تنفيذ استعلام للحصول على عدد المستندات في كل مجلد
        query = """
        SELECT 
            f.id as folder_id, 
            f.name as folder_name, 
            COUNT(d.id) as document_count 
        FROM 
            rental_archivefolder f 
        LEFT JOIN 
            rental_document d ON f.id = d.folder_id 
        GROUP BY 
            f.id, f.name 
        ORDER BY 
            document_count DESC;
        """
        
        cursor.execute(query)
        results = cursor.fetchall()
        
        print("\n--- تقرير المستندات في المجلدات ---")
        for row in results:
            folder_id, folder_name, document_count = row
            print(f"المجلد: {folder_name} (ID: {folder_id}) | عدد المستندات: {document_count}")
        
        return True
    except Exception as e:
        print(f"ERROR - حدث خطأ أثناء التحقق من المستندات: {str(e)}")
        return False

def main():
    """
    الدالة الرئيسية لتنفيذ الإصلاحات
    """
    print("جاري إصلاح مشكلة عدم ظهور المستندات المرفوعة في صفحة الأرشيف...")
    
    # إصلاح وظيفة رفع المستندات
    fix_upload_function()
    
    # تحسين وظيفة عرض المستندات
    fix_display_function()
    
    # إضافة مسار URL للوظيفة الجديدة
    add_upload_url()
    
    # تحديث نموذج رفع الملفات في القالب
    update_template_form()
    
    # التحقق من المستندات في قاعدة البيانات
    verify_document_uploads()
    
    print("\nتم اكتمال الإصلاحات بنجاح. يرجى إعادة تشغيل التطبيق لتطبيق التغييرات.")

if __name__ == "__main__":
    main()