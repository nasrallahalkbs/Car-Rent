"""
تعطيل آلية منع المستندات التلقائية تماماً مؤقتاً

هذا الملف يقوم بتعطيل إشارة pre_save المستخدمة لمنع المستندات التلقائية تماماً
"""

import os
import sys
import django
import traceback
import datetime
import time

# إعداد Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'car_rental_project.settings')
django.setup()

from django.db.models.signals import pre_save
from django.shortcuts import render, redirect
from django.contrib import messages
from django.conf import settings
from rental.models import Document, ArchiveFolder
from rental.signals import prevent_auto_document_creation
from django.urls import path
from django.contrib.auth.decorators import login_required
from rental.admin_views import admin_required

# تعطيل إشارة منع المستندات
print("⚠️ تعطيل إشارة منع المستندات التلقائية...")
pre_save.disconnect(prevent_auto_document_creation, sender=Document)
print("✅ تم تعطيل إشارة منع المستندات التلقائية")

@login_required
@admin_required
def super_upload(request):
    """وظيفة رفع فائقة بدون إشارات منع"""
    print("\n🚀 تم استدعاء وظيفة الرفع الفائقة")
    print(f"طريقة الطلب: {request.method}")
    
    # عرض النموذج فقط
    if request.method == 'GET':
        print("⚪ عرض نموذج الرفع الفائق")
        folders = ArchiveFolder.objects.all().order_by('name')
        context = {
            'folders': folders,
            'document_types': Document.DOCUMENT_TYPE_CHOICES,
            'related_to_types': Document.RELATED_TO_CHOICES,
        }
        print(f"📁 عدد المجلدات المتاحة: {len(folders)}")
        return render(request, 'admin/archive/super_upload_form.html', context)
    
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
            return redirect('super_upload')
            
        uploaded_file = request.FILES['file']
        file_name = uploaded_file.name
        file_size = uploaded_file.size
        file_type = uploaded_file.content_type
        
        print(f"📄 معلومات الملف: الاسم={file_name}, الحجم={file_size}, النوع={file_type}")
        
        # إنشاء مستند باستخدام Django مباشرة
        timestamp = int(time.time())
        document = Document()
        document.title = title
        document.description = description
        document.document_type = document_type
        document.related_to = related_to
        document.folder_id = folder_id
        document.file = uploaded_file
        document.file_name = file_name
        document.file_type = file_type
        document.file_size = file_size
        document.is_archived = True
        document.is_auto_created = False
        document.document_date = datetime.datetime.now().date()
        document.expiry_date = expiry_date_value
        document.added_by = request.user
        document._ignore_auto_document_signal = True
        
        # حفظ المستند
        print("💾 محاولة حفظ المستند...")
        document.save()
        
        # التحقق من نجاح الحفظ
        if document.id:
            print(f"✅ تم حفظ المستند بنجاح، المعرف: {document.id}")
            messages.success(request, f"تم رفع المستند '{title}' بنجاح")
        else:
            print("❌ فشل حفظ المستند")
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

def create_super_upload_template():
    """إنشاء قالب نموذج الرفع الفائق"""
    template_path = os.path.join('templates', 'admin', 'archive', 'super_upload_form.html')
    os.makedirs(os.path.dirname(template_path), exist_ok=True)
    
    template_content = """{% extends 'admin_layout.html' %}
{% load static %}
{% load i18n %}

{% block title %}{% trans "رفع مستند فائق" %}{% endblock %}

{% block page_title %}{% trans "رفع مستند بالطريقة الفائقة" %}{% endblock %}

{% block breadcrumb %}
<li class="breadcrumb-item"><a href="{% url 'admin_archive' %}">{% trans "أرشيف" %}</a></li>
<li class="breadcrumb-item active">{% trans "رفع مستند فائق" %}</li>
{% endblock %}

{% block content %}
<div class="container-fluid">
    <div class="row">
        <div class="col-12">
            <div class="card shadow">
                <div class="card-header bg-danger text-white">
                    <h3 class="my-0">{% trans "رفع مستند جديد (الطريقة الفائقة)" %}</h3>
                </div>
                <div class="card-body">
                    <div class="alert alert-danger">
                        <i class="fas fa-exclamation-triangle"></i>
                        {% trans "هذه الطريقة تعطل آلية منع المستندات التلقائية تماماً عن طريق فصل الإشارة" %}
                    </div>
                    
                    <form method="post" enctype="multipart/form-data" action="{% url 'super_upload' %}">
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
                            <button type="submit" class="btn btn-danger btn-lg">{% trans "رفع المستند" %}</button>
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
    
    print(f"✅ تم إنشاء قالب نموذج الرفع الفائق في {template_path}")

def add_url_route():
    """إضافة مسار URL للوظيفة الفائقة"""
    urls_path = 'rental/urls.py'
    with open(urls_path, 'r', encoding='utf-8') as f:
        urls_content = f.read()
    
    # التحقق من وجود الاستيراد
    if 'from super_upload_without_signal import super_upload' not in urls_content:
        import_line = 'from super_upload_without_signal import super_upload\n'
        from_line = 'from simple_upload_fix import very_simple_upload'
        urls_content = urls_content.replace(from_line, f"{from_line}\n{import_line}")
    
    # التحقق من وجود المسار
    path_line = "path('ar/dashboard/archive/super_upload/', super_upload, name='super_upload'),"
    if path_line not in urls_content:
        first_path = "path('ar/dashboard/archive/simple_upload/', very_simple_upload, name='very_simple_upload'),"
        urls_content = urls_content.replace(first_path, f"{first_path}\n    {path_line}")
    
    # كتابة المحتوى المحدث
    with open(urls_path, 'w', encoding='utf-8') as f:
        f.write(urls_content)
    
    print(f"✅ تم إضافة مسار URL للوظيفة الفائقة")

def add_link_to_archive_page():
    """إضافة رابط في صفحة الأرشيف للوصول إلى وظيفة الرفع الفائقة"""
    archive_template_path = 'templates/admin/archive/windows_explorer_enhanced.html'
    
    if not os.path.exists(archive_template_path):
        print(f"⚠️ قالب الأرشيف غير موجود في {archive_template_path}")
        return
    
    with open(archive_template_path, 'r', encoding='utf-8') as f:
        template_content = f.read()
    
    # التحقق من وجود الرابط
    if 'رفع مستند (فائق)' in template_content:
        print(f"⚠️ رابط الرفع الفائق موجود بالفعل")
        return
    
    # إضافة الرابط
    button_code = """
    <a href="{% url 'super_upload' %}" class="btn btn-danger mb-2">
        <i class="fas fa-file-upload"></i> {% trans "رفع مستند (فائق)" %}
    </a>"""
    
    simple_upload_button = """<a href="{% url 'very_simple_upload' %}" class="btn btn-success mb-2">
        <i class="fas fa-file-upload"></i> {% trans "رفع مستند (بسيط)" %}
    </a>"""
    
    template_content = template_content.replace(simple_upload_button, f"{simple_upload_button}\n    {button_code}")
    
    with open(archive_template_path, 'w', encoding='utf-8') as f:
        f.write(template_content)
    
    print(f"✅ تم إضافة رابط للوظيفة الفائقة في قالب الأرشيف")

def main():
    """تنفيذ الوظائف الرئيسية"""
    print("\n🛠️ تطبيق حل فائق لرفع الملفات...")
    
    create_super_upload_template()
    add_url_route()
    add_link_to_archive_page()
    
    print("✅ تم تطبيق الحل الفائق بنجاح")
    print("🔗 يمكنك الوصول إلى صفحة الرفع الفائقة من خلال /ar/dashboard/archive/super_upload/")
    print("⚠️ تذكر أن هذا الحل يعطل آلية منع المستندات التلقائية تماماً، استخدمه بحذر")

if __name__ == "__main__":
    main()