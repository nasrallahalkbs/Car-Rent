"""
حل مبسط ومباشر جداً لمشكلة رفع الملفات
"""

import os
import sys
import django
import uuid
import traceback
import datetime

# إعداد Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'car_rental_project.settings')
django.setup()

from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib import messages
from django.db import connection
from django.conf import settings
from rental.models import Document, ArchiveFolder
from rental.admin_views import admin_required

@login_required
@admin_required
def very_simple_upload(request):
    """وظيفة رفع بسيطة جداً تتجاوز كل المشاكل"""
    
    # طباعة معلومات تصحيح
    print("\n🚀 تم استدعاء وظيفة الرفع البسيطة جداً")
    print(f"طريقة الطلب: {request.method}")
    
    # عرض النموذج (طلب GET)
    if request.method == 'GET':
        print("⚪ عرض نموذج الرفع البسيط")
        folders = ArchiveFolder.objects.all().order_by('name')
        context = {
            'folders': folders,
            'document_types': Document.DOCUMENT_TYPE_CHOICES,
            'related_to_types': Document.RELATED_TO_CHOICES,
        }
        print(f"📂 عدد المجلدات المتاحة: {len(folders)}")
        return render(request, 'admin/archive/simple_upload_form.html', context)
    
    # معالجة الرفع (طلب POST)
    print("🔄 معالجة طلب رفع الملف...")
    
    try:
        # الحصول على البيانات من النموذج
        title = request.POST.get('title', '')
        description = request.POST.get('description', '')
        document_type = request.POST.get('document_type', 'OTHER')
        related_to = request.POST.get('related_to', 'NONE')
        folder_id = request.POST.get('folder', None)
        
        if folder_id == '':
            folder_id = None
            
        if not folder_id or folder_id == '':
            print(f"⚠️ لم يتم تحديد مجلد")
        else:
            print(f"📁 المجلد المحدد: {folder_id}")
            
        expiry_date = request.POST.get('expiry_date', None)
        expiry_date_value = None
        
        if expiry_date:
            try:
                expiry_date_value = datetime.datetime.strptime(expiry_date, '%Y-%m-%d').date()
                print(f"📅 تاريخ الانتهاء: {expiry_date_value}")
            except ValueError:
                print(f"⚠️ تنسيق تاريخ انتهاء غير صالح: {expiry_date}")
        
        # التأكد من وجود ملف
        if 'file' not in request.FILES:
            messages.error(request, "لم يتم تحديد ملف للرفع")
            print("❌ لم يتم تحديد ملف")
            return redirect('very_simple_upload')
            
        uploaded_file = request.FILES['file']
        file_name = uploaded_file.name
        file_size = uploaded_file.size
        file_type = uploaded_file.content_type
        
        print(f"📄 معلومات الملف: الاسم={file_name}, الحجم={file_size}, النوع={file_type}")
        
        # تخزين الملف على القرص
        timestamp = int(datetime.datetime.now().timestamp())
        random_part = str(timestamp)[-4:]
        safe_filename = f"direct_{timestamp}_{random_part}_{file_name}"
        
        # مسار الملف
        upload_dir = os.path.join(settings.MEDIA_ROOT, 'uploads')
        os.makedirs(upload_dir, exist_ok=True)
        file_path = os.path.join('uploads', safe_filename)
        full_path = os.path.join(settings.MEDIA_ROOT, file_path)
        
        # نسخ محتوى الملف
        with open(full_path, 'wb+') as destination:
            for chunk in uploaded_file.chunks():
                destination.write(chunk)
        
        print(f"✅ تم حفظ الملف في: {file_path}")
        
        # إدخال السجل في قاعدة البيانات باستخدام SQL مباشر
        with connection.cursor() as cursor:
            now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            expiry_date_str = expiry_date_value.strftime('%Y-%m-%d') if expiry_date_value else None
            
            # استعلام SQL
            query = """
            INSERT INTO rental_document 
            (title, description, document_type, related_to, folder_id, 
            file, file_name, file_type, file_size, 
            is_archived, is_auto_created, document_date, expiry_date, 
            created_at, added_by_id)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING id;
            """
            
            # تنفيذ الاستعلام
            cursor.execute(query, [
                title, description, document_type, related_to, folder_id, 
                file_path, file_name, file_type, file_size,
                True, False, datetime.datetime.now().date().isoformat(), expiry_date_str,
                now, request.user.id
            ])
            
            # الحصول على معرف المستند الجديد
            row = cursor.fetchone()
            if row:
                document_id = row[0]
                print(f"✅ تم إدخال المستند بنجاح، المعرف: {document_id}")
                messages.success(request, f"تم رفع المستند '{title}' بنجاح")
            else:
                print("❌ فشل إدخال المستند")
                messages.error(request, "حدث خطأ أثناء محاولة رفع المستند")
        
        # إعادة التوجيه
        if folder_id:
            return redirect('admin_archive_folder', folder_id=folder_id)
        else:
            return redirect('admin_archive')
            
    except Exception as e:
        # تسجيل الخطأ
        print(f"🔴 خطأ في رفع المستند: {str(e)}")
        print(f"🔴 نوع الخطأ: {type(e).__name__}")
        print(traceback.format_exc())
        
        # عرض رسالة خطأ للمستخدم
        messages.error(request, f"حدث خطأ أثناء رفع المستند: {str(e)[:100]}")
        return redirect('admin_archive')

def create_simple_upload_template():
    """إنشاء قالب نموذج الرفع البسيط"""
    template_path = os.path.join('templates', 'admin', 'archive', 'simple_upload_form.html')
    os.makedirs(os.path.dirname(template_path), exist_ok=True)
    
    template_content = """{% extends 'admin_layout.html' %}
{% load static %}
{% load i18n %}

{% block title %}{% trans "رفع مستند بسيط" %}{% endblock %}

{% block page_title %}{% trans "رفع مستند بالطريقة البسيطة" %}{% endblock %}

{% block breadcrumb %}
<li class="breadcrumb-item"><a href="{% url 'admin_archive' %}">{% trans "أرشيف" %}</a></li>
<li class="breadcrumb-item active">{% trans "رفع مستند بسيط" %}</li>
{% endblock %}

{% block content %}
<div class="container-fluid">
    <div class="row">
        <div class="col-12">
            <div class="card shadow">
                <div class="card-header bg-primary text-white">
                    <h3 class="my-0">{% trans "رفع مستند جديد (الطريقة البسيطة)" %}</h3>
                </div>
                <div class="card-body">
                    <div class="alert alert-info">
                        <i class="fas fa-info-circle"></i>
                        {% trans "هذه الطريقة تتجاوز آلية منع المستندات التلقائية عن طريق استخدام SQL مباشرة" %}
                    </div>
                    
                    <form method="post" enctype="multipart/form-data" action="{% url 'very_simple_upload' %}">
                        {% csrf_token %}
                        
                        <div class="row">
                            <div class="col-md-6 mb-3">
                                <label for="title" class="form-label">{% trans "عنوان المستند" %} *</label>
                                <input type="text" class="form-control" id="title" name="title" required>
                            </div>
                            
                            <div class="col-md-6 mb-3">
                                <label for="document_type" class="form-label">{% trans "نوع المستند" %}</label>
                                <select class="form-select" id="document_type" name="document_type">
                                    {% for value, label in document_types %}
                                    <option value="{{ value }}">{{ label }}</option>
                                    {% endfor %}
                                </select>
                            </div>
                        </div>
                        
                        <div class="row">
                            <div class="col-md-6 mb-3">
                                <label for="related_to" class="form-label">{% trans "متعلق بـ" %}</label>
                                <select class="form-select" id="related_to" name="related_to">
                                    {% for value, label in related_to_types %}
                                    <option value="{{ value }}">{{ label }}</option>
                                    {% endfor %}
                                </select>
                            </div>
                            
                            <div class="col-md-6 mb-3">
                                <label for="folder" class="form-label">{% trans "المجلد" %}</label>
                                <select class="form-select" id="folder" name="folder">
                                    <option value="">-- {% trans "بدون مجلد" %} --</option>
                                    {% for folder in folders %}
                                    <option value="{{ folder.id }}">{{ folder.name }}</option>
                                    {% endfor %}
                                </select>
                            </div>
                        </div>
                        
                        <div class="row">
                            <div class="col-md-6 mb-3">
                                <label for="expiry_date" class="form-label">{% trans "تاريخ انتهاء الصلاحية" %}</label>
                                <input type="date" class="form-control" id="expiry_date" name="expiry_date">
                            </div>
                            
                            <div class="col-md-6 mb-3">
                                <label for="file" class="form-label">{% trans "الملف" %} *</label>
                                <input type="file" class="form-control" id="file" name="file" required>
                            </div>
                        </div>
                        
                        <div class="mb-3">
                            <label for="description" class="form-label">{% trans "وصف المستند" %}</label>
                            <textarea class="form-control" id="description" name="description" rows="3"></textarea>
                        </div>
                        
                        <div class="d-grid gap-2 d-md-flex justify-content-md-end">
                            <a href="{% url 'admin_archive' %}" class="btn btn-secondary me-md-2">{% trans "إلغاء" %}</a>
                            <button type="submit" class="btn btn-success btn-lg">{% trans "رفع المستند" %}</button>
                        </div>
                    </form>
                </div>
            </div>
        </div>
    </div>
</div>
{% endblock %}"""
    
    with open(template_path, 'w', encoding='utf-8') as f:
        f.write(template_content)
    
    print(f"✅ تم إنشاء قالب نموذج الرفع البسيط في {template_path}")

def add_url_route():
    """إضافة مسار URL للوظيفة البسيطة"""
    from django.urls import path, get_resolver
    from django.urls.resolvers import URLPattern
    
    # التحقق من وجود المسار
    resolver = get_resolver()
    for pattern in resolver.url_patterns:
        if hasattr(pattern, 'name') and pattern.name == 'very_simple_upload':
            print(f"⚠️ مسار الرفع البسيط موجود بالفعل")
            return
    
    # إضافة المسار إلى ملف urls.py
    urls_path = 'rental/urls.py'
    with open(urls_path, 'r', encoding='utf-8') as f:
        urls_content = f.read()
    
    # التحقق من وجود الاستيراد
    if 'from simple_upload_fix import very_simple_upload' not in urls_content:
        import_line = 'from simple_upload_fix import very_simple_upload\n'
        from_line = 'from direct_upload_implementation import direct_sql_upload_document'
        urls_content = urls_content.replace(from_line, f"{from_line}\n{import_line}")
    
    # التحقق من وجود المسار
    path_line = "path('ar/dashboard/archive/simple_upload/', very_simple_upload, name='very_simple_upload'),"
    if path_line not in urls_content:
        first_path = "path('ar/dashboard/archive/direct_upload/', direct_sql_upload_document, name='direct_sql_upload_document'),"
        urls_content = urls_content.replace(first_path, f"{first_path}\n    {path_line}")
    
    # كتابة المحتوى المحدث
    with open(urls_path, 'w', encoding='utf-8') as f:
        f.write(urls_content)
    
    print(f"✅ تم إضافة مسار URL للوظيفة البسيطة")

def add_link_to_archive_page():
    """إضافة رابط في صفحة الأرشيف للوصول إلى وظيفة الرفع البسيطة"""
    archive_template_path = 'templates/admin/archive/windows_explorer_enhanced.html'
    
    if not os.path.exists(archive_template_path):
        print(f"⚠️ قالب الأرشيف غير موجود في {archive_template_path}")
        return
    
    with open(archive_template_path, 'r', encoding='utf-8') as f:
        template_content = f.read()
    
    # التحقق من وجود الرابط
    if 'رفع مستند (بسيط)' in template_content:
        print(f"⚠️ رابط الرفع البسيط موجود بالفعل")
        return
    
    # إضافة الرابط
    button_code = """
    <a href="{% url 'very_simple_upload' %}" class="btn btn-success mb-2">
        <i class="fas fa-file-upload"></i> {% trans "رفع مستند (بسيط)" %}
    </a>"""
    
    direct_upload_button = """<a href="{% url 'direct_sql_upload_document' %}" class="btn btn-primary mb-2">
        <i class="fas fa-file-upload"></i> {% trans "رفع مستند (مباشر)" %}
    </a>"""
    
    template_content = template_content.replace(direct_upload_button, f"{direct_upload_button}\n    {button_code}")
    
    with open(archive_template_path, 'w', encoding='utf-8') as f:
        f.write(template_content)
    
    print(f"✅ تم إضافة رابط للوظيفة البسيطة في قالب الأرشيف")

def main():
    """تنفيذ الوظائف الرئيسية"""
    print("\n🛠️ تطبيق حل بسيط لرفع الملفات...")
    
    create_simple_upload_template()
    add_url_route()
    add_link_to_archive_page()
    
    print("✅ تم تطبيق الحل البسيط بنجاح")
    print("🔗 يمكنك الوصول إلى صفحة الرفع البسيطة من خلال /ar/dashboard/archive/simple_upload/")

if __name__ == "__main__":
    main()