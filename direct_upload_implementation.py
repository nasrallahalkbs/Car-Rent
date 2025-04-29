"""
تنفيذ مباشر لوظيفة رفع الملفات باستخدام SQL مباشرة لتجاوز آلية منع المستندات التلقائية

يمكن استدعاء هذا الملف مباشرة أو استخدامه كمرجع لإضافة الوظيفة إلى admin_views.py
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

from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib import messages
from django.db import connection, transaction
from django.conf import settings
from rental.models import Document, ArchiveFolder
from rental.admin_views import admin_required
import datetime
import uuid

@login_required
@admin_required
def direct_sql_upload_document(request):
    """وظيفة رفع ملفات باستخدام SQL مباشرة لتجاوز نظام منع المستندات التلقائية"""
    if request.method != 'POST':
        # عرض نموذج الرفع فقط
        folders = ArchiveFolder.objects.all().order_by('name')
        context = {
            'folders': folders,
            'document_types': Document.DOCUMENT_TYPE_CHOICES,
            'related_to_types': Document.RELATED_TO_CHOICES,
        }
        return render(request, 'admin/archive/direct_upload_form.html', context)
    
    # مسار قاعدة البيانات - مطلوب للتحميل
    if not request.FILES.get('file'):
        messages.error(request, "يرجى تحديد ملف للتحميل")
        return redirect('admin_archive')
    
    # استخراج البيانات من النموذج
    title = request.POST.get('title', '').strip()
    description = request.POST.get('description', '')
    document_type = request.POST.get('document_type', 'other')
    related_to = request.POST.get('related_to', 'other')
    folder_id = request.POST.get('folder')
    expiry_date = request.POST.get('expiry_date')
    
    # التحقق من البيانات الإلزامية
    if not title:
        messages.error(request, "يرجى إدخال عنوان للمستند")
        return redirect('admin_archive')
    
    # معالجة الملف
    uploaded_file = request.FILES['file']
    file_name = uploaded_file.name
    file_size = uploaded_file.size
    file_type = uploaded_file.content_type
    
    try:
        # استخدام SQL مباشرة لإدراج المستند
        with transaction.atomic():
            # حفظ الملف في نظام الملفات
            media_dir = os.path.join(settings.MEDIA_ROOT, 'documents')
            os.makedirs(media_dir, exist_ok=True)
            
            # إنشاء اسم فريد للملف
            unique_id = uuid.uuid4().hex[:8]
            unique_filename = f"direct_upload_{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}_{unique_id}_{file_name}"
            destination_path = os.path.join(media_dir, unique_filename)
            
            # حفظ الملف
            with open(destination_path, 'wb') as destination:
                for chunk in uploaded_file.chunks():
                    destination.write(chunk)
            
            # المسار النسبي للملف
            relative_path = os.path.relpath(destination_path, settings.MEDIA_ROOT)
            
            # إدراج البيانات في قاعدة البيانات
            with connection.cursor() as cursor:
                # الحصول على معرف جديد
                cursor.execute("SELECT MAX(id) FROM rental_document")
                max_id = cursor.fetchone()[0]
                new_id = 1 if max_id is None else max_id + 1
                
                # إنشاء استعلام الإدراج
                query = '''
                INSERT INTO rental_document 
                (id, title, description, document_type, related_to, folder_id, 
                file, file_name, file_type, file_size, 
                created_at, updated_at, is_archived, is_auto_created, 
                document_date, expiry_date, added_by_id)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                '''
                
                # تحضير القيم
                now = datetime.datetime.now()
                
                # معالجة التاريخ
                document_date = now.date()
                expiry_date_value = None
                if expiry_date:
                    try:
                        expiry_date_value = datetime.datetime.strptime(expiry_date, '%Y-%m-%d').date()
                    except ValueError:
                        # في حالة الخطأ، نستخدم None
                        pass
                
                # تنفيذ الاستعلام
                cursor.execute(query, [
                    new_id,
                    title,
                    description,
                    document_type,
                    related_to,
                    folder_id if folder_id else None,
                    relative_path,
                    file_name,
                    file_type,
                    file_size,
                    now,
                    now,
                    True,  # is_archived
                    False,  # is_auto_created
                    document_date,
                    expiry_date_value,
                    request.user.id  # added_by_id
                ])
        
        # عرض رسالة نجاح
        messages.success(request, f"تم رفع المستند '{title}' بنجاح باستخدام الطريقة المباشرة")
        
        # إعادة التوجيه
        if folder_id:
            return redirect('admin_archive_folder', folder_id=folder_id)
        else:
            return redirect('admin_archive')
            
    except Exception as e:
        # تسجيل الخطأ للتصحيح
        print(f"خطأ في رفع المستند بالطريقة المباشرة: {str(e)}")
        print(traceback.format_exc())
        
        # عرض رسالة خطأ للمستخدم
        messages.error(request, f"حدث خطأ أثناء رفع المستند: {str(e)[:100]}")
        return redirect('admin_archive')

def create_upload_template():
    """إنشاء قالب نموذج الرفع المباشر"""
    template_path = os.path.join('templates', 'admin', 'archive', 'direct_upload_form.html')
    os.makedirs(os.path.dirname(template_path), exist_ok=True)
    
    template_content = """{% extends 'admin/base.html' %}
{% load static %}
{% load i18n %}

{% block content %}
<div class="container py-4">
    <div class="card shadow">
        <div class="card-header bg-primary text-white">
            <h3 class="my-0">رفع مستند جديد (الطريقة المباشرة)</h3>
        </div>
        <div class="card-body">
            <div class="alert alert-info">
                <i class="fas fa-info-circle"></i>
                هذه الطريقة تستخدم SQL مباشرة لتجاوز آلية منع المستندات التلقائية
            </div>
            
            <form method="post" enctype="multipart/form-data" action="{% url 'direct_sql_upload_document' %}">
                {% csrf_token %}
                
                <div class="row">
                    <div class="col-md-6 mb-3">
                        <label for="title" class="form-label">عنوان المستند *</label>
                        <input type="text" class="form-control" id="title" name="title" required>
                    </div>
                    
                    <div class="col-md-6 mb-3">
                        <label for="document_type" class="form-label">نوع المستند</label>
                        <select class="form-select" id="document_type" name="document_type">
                            {% for value, label in document_types %}
                            <option value="{{ value }}">{{ label }}</option>
                            {% endfor %}
                        </select>
                    </div>
                </div>
                
                <div class="row">
                    <div class="col-md-6 mb-3">
                        <label for="related_to" class="form-label">متعلق بـ</label>
                        <select class="form-select" id="related_to" name="related_to">
                            {% for value, label in related_to_types %}
                            <option value="{{ value }}">{{ label }}</option>
                            {% endfor %}
                        </select>
                    </div>
                    
                    <div class="col-md-6 mb-3">
                        <label for="folder" class="form-label">المجلد</label>
                        <select class="form-select" id="folder" name="folder">
                            <option value="">-- بدون مجلد --</option>
                            {% for folder in folders %}
                            <option value="{{ folder.id }}">{{ folder.name }}</option>
                            {% endfor %}
                        </select>
                    </div>
                </div>
                
                <div class="row">
                    <div class="col-md-6 mb-3">
                        <label for="expiry_date" class="form-label">تاريخ انتهاء الصلاحية</label>
                        <input type="date" class="form-control" id="expiry_date" name="expiry_date">
                    </div>
                    
                    <div class="col-md-6 mb-3">
                        <label for="file" class="form-label">الملف *</label>
                        <input type="file" class="form-control" id="file" name="file" required>
                    </div>
                </div>
                
                <div class="mb-3">
                    <label for="description" class="form-label">وصف المستند</label>
                    <textarea class="form-control" id="description" name="description" rows="3"></textarea>
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
    
    with open(template_path, 'w', encoding='utf-8') as f:
        f.write(template_content)
    
    print(f"✅ تم إنشاء قالب {template_path}")

def add_url_route():
    """إضافة مسار URL للوظيفة المباشرة"""
    urls_path = os.path.join('rental', 'urls.py')
    if not os.path.exists(urls_path):
        print(f"⚠️ ملف {urls_path} غير موجود")
        return
    
    with open(urls_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # التحقق من وجود المسار بالفعل
    if 'direct_sql_upload_document' in content:
        print("✅ مسار URL للوظيفة موجود بالفعل")
        return
    
    # إضافة الاستيراد والمسار
    import_line = "from direct_upload_implementation import direct_sql_upload_document"
    path_line = "    path('ar/dashboard/archive/direct_upload/', direct_sql_upload_document, name='direct_sql_upload_document'),"
    
    # إضافة الاستيراد بعد الاستيرادات الموجودة
    if 'from rental' in content:
        content = content.replace(
            'from rental',
            f'{import_line}\nfrom rental'
        )
    else:
        content = f"{import_line}\n{content}"
    
    # إضافة المسار ضمن urlpatterns
    if 'urlpatterns = [' in content:
        content = content.replace(
            'urlpatterns = [',
            f'urlpatterns = [\n{path_line}'
        )
    else:
        print("⚠️ لم يتم العثور على نمط urlpatterns")
        return
    
    with open(urls_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"✅ تمت إضافة مسار URL للوظيفة في {urls_path}")

def add_link_to_archive_page():
    """إضافة رابط في صفحة الأرشيف للوصول إلى وظيفة الرفع المباشر"""
    archive_path = os.path.join('templates', 'admin', 'archive', 'archive.html')
    if not os.path.exists(archive_path):
        print(f"⚠️ قالب {archive_path} غير موجود")
        return
    
    with open(archive_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # التحقق من وجود الرابط بالفعل
    if 'direct_sql_upload_document' in content:
        print("✅ رابط الوظيفة موجود بالفعل في قالب الأرشيف")
        return
    
    # إضافة الرابط
    button_html = """<a href="{% url 'direct_sql_upload_document' %}" class="btn btn-success me-2">
                <i class="fas fa-upload"></i> رفع ملف (طريقة مباشرة)
            </a>"""
    
    # البحث عن المكان المناسب
    import re
    pattern = r'<div class="d-flex justify-content-between align-items-center mb-3">'
    
    if re.search(pattern, content):
        # إضافة الرابط بعد نمط div
        content = re.sub(
            pattern,
            f'{pattern}\n            {button_html}',
            content
        )
        
        with open(archive_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"✅ تمت إضافة رابط الوظيفة في قالب {archive_path}")
    else:
        print("⚠️ لم يتم العثور على نمط div المناسب")

def main():
    """تنفيذ الوظائف الرئيسية"""
    print("\n=== بدء تنفيذ الوظائف المطلوبة ===\n")
    
    # إنشاء قالب النموذج
    create_upload_template()
    
    # إضافة مسار URL
    add_url_route()
    
    # إضافة رابط في صفحة الأرشيف
    add_link_to_archive_page()
    
    print("\n=== تم إكمال تنفيذ الوظائف بنجاح ===\n")
    print("لاختبار الوظيفة، قم بالذهاب إلى صفحة الأرشيف والنقر على الرابط 'رفع ملف (طريقة مباشرة)'")

if __name__ == "__main__":
    main()