"""
إصلاح بسيط جدًا لوظيفة رفع الملفات

هذا السكريبت يقوم بإنشاء وظيفة رفع ملفات بسيطة جدًا بدون منطق معقد
"""

import os
import sys
import django
import traceback

# إضافة المسار الحالي إلى مسارات Python
sys.path.append(os.getcwd())

# إعداد Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'car_rental_project.settings')
django.setup()

from rental.admin_views import admin_required
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib import messages
from django.db import transaction
from rental.models import Document, ArchiveFolder

def create_simple_upload_view():
    """إنشاء وظيفة رفع ملفات بسيطة جدًا"""
    print("\n=== إنشاء وظيفة رفع ملفات بسيطة جدًا ===")
    
    @login_required
    @admin_required
    def simple_upload(request):
        """وظيفة رفع ملفات بسيطة جدًا"""
        if request.method != 'POST':
            return redirect('admin_archive')
        
        # استخراج البيانات
        title = request.POST.get('title', '').strip()
        description = request.POST.get('description', '')
        folder_id = request.POST.get('folder')
        document_type = request.POST.get('document_type', 'other')
        
        # التحقق من البيانات
        if not title:
            messages.error(request, "يرجى إدخال عنوان للمستند")
            return redirect('admin_archive')
        
        if 'file' not in request.FILES:
            messages.error(request, "يرجى تحديد ملف للتحميل")
            return redirect('admin_archive')
        
        # تحضير البيانات
        uploaded_file = request.FILES['file']
        folder = None
        if folder_id:
            try:
                folder = ArchiveFolder.objects.get(id=folder_id)
            except ArchiveFolder.DoesNotExist:
                messages.error(request, "المجلد المحدد غير موجود")
                return redirect('admin_archive')
        
        try:
            # قراءة محتوى الملف
            file_content = uploaded_file.read()
            file_name = uploaded_file.name
            file_type = uploaded_file.content_type
            file_size = uploaded_file.size
            
            # إعادة مؤشر الملف للبداية
            uploaded_file.seek(0)
            
            # تخزين المستند مباشرة في قاعدة البيانات باستخدام SQL
            from django.db import connection
            
            with transaction.atomic():
                # إنشاء استعلام SQL
                query = """
                INSERT INTO rental_document 
                (title, description, document_type, folder_id, created_by_id, added_by_id,
                file_name, file_type, file_size, file_content, created_at, updated_at, is_auto_created) 
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, NOW(), NOW(), %s) 
                RETURNING id
                """
                
                # تنفيذ الاستعلام
                with connection.cursor() as cursor:
                    cursor.execute(query, [
                        title,
                        description,
                        document_type,
                        folder.id if folder else None,
                        request.user.id,  # created_by_id
                        request.user.id,  # added_by_id
                        file_name,
                        file_type,
                        file_size,
                        file_content,
                        False  # is_auto_created
                    ])
                    
                    # الحصول على معرف المستند
                    document_id = cursor.fetchone()[0]
                
                # حفظ الملف في نظام الملفات
                import os
                from django.conf import settings
                
                # إنشاء مجلد للملفات
                upload_dir = os.path.join(settings.MEDIA_ROOT, 'documents')
                os.makedirs(upload_dir, exist_ok=True)
                
                # مسار الملف
                file_path = os.path.join(upload_dir, f"doc_{document_id}_{file_name}")
                
                # حفظ الملف
                with open(file_path, 'wb+') as destination:
                    for chunk in uploaded_file.chunks():
                        destination.write(chunk)
                
                # تحديث حقل file في قاعدة البيانات
                rel_path = os.path.relpath(file_path, settings.MEDIA_ROOT)
                
                update_query = "UPDATE rental_document SET file = %s WHERE id = %s"
                with connection.cursor() as cursor:
                    cursor.execute(update_query, [rel_path, document_id])
            
            # عرض رسالة نجاح
            messages.success(request, f"تم رفع المستند '{title}' بنجاح")
            
            # إعادة التوجيه
            if folder:
                return redirect('admin_archive_folder', folder_id=folder.id)
            else:
                return redirect('admin_archive')
                
        except Exception as e:
            print(f"حدث خطأ أثناء رفع المستند: {str(e)}")
            print(traceback.format_exc())
            messages.error(request, f"حدث خطأ أثناء رفع المستند: {str(e)[:100]}")
            return redirect('admin_archive')
    
    # حفظ الوظيفة في ملف admin_views.py
    from rental import admin_views
    admin_views.direct_simple_upload = simple_upload
    
    # إضافة مسار URL للوظيفة
    from django.urls import path, include
    from django.urls.resolvers import URLPattern
    
    # البحث عن ملف urls.py
    from car_rental_project import urls as main_urls
    from rental import urls as rental_urls
    
    # إضافة الإصلاح البسيط كخيار إضافي
    try:
        # فحص ما إذا كان المسار موجود بالفعل
        path_exists = False
        for pattern in rental_urls.urlpatterns:
            if hasattr(pattern, 'pattern') and 'direct_simple_upload' in str(pattern.pattern):
                path_exists = True
                break
        
        if not path_exists:
            # إضافة المسار إلى rental.urls
            simple_upload_pattern = path('ar/dashboard/archive/direct_simple_upload/', admin_views.direct_simple_upload, name='direct_simple_upload')
            rental_urls.urlpatterns.append(simple_upload_pattern)
            print("✓ تم إضافة المسار 'direct_simple_upload' إلى ملف URLs")
        else:
            print("✓ المسار 'direct_simple_upload' موجود بالفعل")
    except Exception as e:
        print(f"⚠️ فشل إضافة المسار: {str(e)}")
    
    # إنشاء نموذج HTML بسيط جدًا للرفع
    template_path = os.path.join('templates', 'admin', 'archive', 'simple_upload.html')
    os.makedirs(os.path.dirname(template_path), exist_ok=True)
    
    template_content = """{% extends 'admin/base.html' %}
{% load static %}
{% load i18n %}

{% block content %}
<div class="container py-4">
    <div class="card shadow">
        <div class="card-header bg-primary text-white">
            <h3 class="my-0">رفع مستند جديد (الإصلاح البسيط)</h3>
        </div>
        <div class="card-body">
            <form method="post" action="{% url 'direct_simple_upload' %}" enctype="multipart/form-data">
                {% csrf_token %}
                
                <div class="mb-3">
                    <label for="title" class="form-label">عنوان المستند *</label>
                    <input type="text" class="form-control" id="title" name="title" required>
                </div>
                
                <div class="mb-3">
                    <label for="document_type" class="form-label">نوع المستند</label>
                    <select class="form-select" id="document_type" name="document_type">
                        <option value="contract">عقد</option>
                        <option value="receipt">إيصال</option>
                        <option value="custody">عهدة</option>
                        <option value="custody_release">إخلاء عهدة</option>
                        <option value="official_document">وثيقة رسمية</option>
                        <option value="other" selected>أخرى</option>
                    </select>
                </div>
                
                <div class="mb-3">
                    <label for="folder" class="form-label">المجلد</label>
                    <select class="form-select" id="folder" name="folder">
                        <option value="">-- بدون مجلد --</option>
                        {% for folder in folders %}
                        <option value="{{ folder.id }}">{{ folder.name }}</option>
                        {% endfor %}
                    </select>
                </div>
                
                <div class="mb-3">
                    <label for="description" class="form-label">وصف المستند</label>
                    <textarea class="form-control" id="description" name="description" rows="3"></textarea>
                </div>
                
                <div class="mb-3">
                    <label for="file" class="form-label">الملف *</label>
                    <input type="file" class="form-control" id="file" name="file" required>
                </div>
                
                <div class="d-grid gap-2 d-md-flex justify-content-md-end">
                    <a href="{% url 'admin_archive' %}" class="btn btn-secondary me-md-2">إلغاء</a>
                    <button type="submit" class="btn btn-primary">رفع المستند</button>
                </div>
            </form>
        </div>
    </div>
</div>
{% endblock %}
"""
    
    try:
        with open(template_path, 'w', encoding='utf-8') as f:
            f.write(template_content)
        print(f"✓ تم إنشاء قالب 'simple_upload.html'")
    except Exception as e:
        print(f"⚠️ فشل إنشاء القالب: {str(e)}")
    
    # إضافة وظيفة لعرض النموذج
    @login_required
    @admin_required
    def simple_upload_form(request):
        """عرض نموذج الرفع البسيط"""
        folders = ArchiveFolder.objects.all().order_by('name')
        context = {
            'folders': folders,
        }
        return render(request, 'admin/archive/simple_upload.html', context)
    
    # حفظ الوظيفة في ملف admin_views.py
    admin_views.simple_upload_form = simple_upload_form
    
    # إضافة مسار URL للنموذج
    try:
        # فحص ما إذا كان المسار موجود بالفعل
        path_exists = False
        for pattern in rental_urls.urlpatterns:
            if hasattr(pattern, 'pattern') and 'simple_upload_form' in str(pattern.pattern):
                path_exists = True
                break
        
        if not path_exists:
            # إضافة المسار إلى rental.urls
            simple_form_pattern = path('ar/dashboard/archive/simple_upload_form/', admin_views.simple_upload_form, name='simple_upload_form')
            rental_urls.urlpatterns.append(simple_form_pattern)
            print("✓ تم إضافة المسار 'simple_upload_form' إلى ملف URLs")
        else:
            print("✓ المسار 'simple_upload_form' موجود بالفعل")
    except Exception as e:
        print(f"⚠️ فشل إضافة المسار: {str(e)}")
    
    # إضافة رابط للنموذج في صفحة الأرشيف
    try:
        archive_template_path = os.path.join('templates', 'admin', 'archive', 'archive.html')
        if os.path.exists(archive_template_path):
            with open(archive_template_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # إضافة الرابط إذا لم يكن موجودًا بالفعل
            if 'simple_upload_form' not in content:
                button_html = """<a href="{% url 'simple_upload_form' %}" class="btn btn-success ms-2">
                    <i class="fas fa-upload"></i> رفع مستند (طريقة بسيطة)
                </a>"""
                
                # البحث عن المكان المناسب لإضافة الزر
                import re
                pattern = r'<div class="d-flex justify-content-between align-items-center mb-3">'
                if re.search(pattern, content):
                    # إضافة الزر بعد العنصر div
                    content = re.sub(
                        pattern,
                        r'\g<0>\n            ' + button_html,
                        content
                    )
                    
                    # حفظ التعديلات
                    with open(archive_template_path, 'w', encoding='utf-8') as f:
                        f.write(content)
                    
                    print("✓ تم إضافة رابط للنموذج البسيط في صفحة الأرشيف")
                else:
                    print("⚠️ لم يتم العثور على المكان المناسب لإضافة الرابط")
            else:
                print("✓ الرابط موجود بالفعل في صفحة الأرشيف")
        else:
            print(f"⚠️ قالب 'archive.html' غير موجود")
    except Exception as e:
        print(f"⚠️ فشل تعديل قالب 'archive.html': {str(e)}")
    
    print("=== تم إنشاء وظيفة رفع ملفات بسيطة جدًا بنجاح ===\n")

if __name__ == "__main__":
    create_simple_upload_view()