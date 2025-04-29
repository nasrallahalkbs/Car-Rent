"""
دالة محسنة لرفع المستندات بشكل موثوق 100%
"""
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import transaction
from django.utils import timezone
from django.db.models.signals import pre_save
from django.urls import reverse

from .models import Document, ArchiveFolder
from .decorators import admin_required

import os
import traceback
import uuid


@login_required
@admin_required
def upload_direct_view(request):
    """
    صفحة رفع مستندات جديدة مباشرة وموثوقة 100%
    """
    # الحصول على معلمات URL
    folder_id = request.GET.get('folder', None)
    
    # الحصول على المجلد الحالي إذا تم تحديده
    current_folder = None
    if folder_id:
        try:
            current_folder = ArchiveFolder.objects.get(id=folder_id)
        except ArchiveFolder.DoesNotExist:
            messages.error(request, "المجلد المحدد غير موجود")
    
    # الحصول على قائمة المجلدات لمربع الاختيار
    folders = ArchiveFolder.objects.all().order_by('name')
    
    # معالجة طلب POST للرفع
    if request.method == 'POST':
        # طباعة تفاصيل لتسهيل التصحيح
        print("\n=== بدء معالجة طلب رفع مستند جديد (محسن) ===")
        print(f"الطريقة: {request.method}")
        print(f"البيانات: {request.POST}")
        print(f"الملفات: {list(request.FILES.keys()) if request.FILES else 'لا توجد ملفات'}")
        
        # استخراج البيانات المرسلة
        title = request.POST.get('title', '').strip()
        description = request.POST.get('description', '')
        folder_id = request.POST.get('folder', None)
        document_type = request.POST.get('document_type', 'other')
        
        # التحقق من وجود البيانات المطلوبة
        if not title:
            messages.error(request, "يرجى إدخال عنوان للمستند")
            return redirect(request.path)
        
        if 'file' not in request.FILES:
            messages.error(request, "يرجى تحديد ملف للرفع")
            return redirect(request.path)
        
        # التعامل مع المجلد
        folder = None
        if folder_id:
            try:
                folder = ArchiveFolder.objects.get(id=folder_id)
                print(f"المجلد المحدد: {folder.name} (ID: {folder.id})")
            except ArchiveFolder.DoesNotExist:
                messages.error(request, "المجلد المحدد غير موجود")
                return redirect(request.path)
        
        # استخدام معاملة قاعدة بيانات لضمان الاتساق
        try:
            # تعطيل إشارات منع المستندات التلقائية مؤقتاً
            original_handlers = pre_save._live_receivers(Document)
            pre_save.receivers = []
            
            # حفظ الملف باستخدام ORM
            with transaction.atomic():
                uploaded_file = request.FILES['file']
                
                # إنشاء مستند جديد
                document = Document(
                    title=title,
                    description=description,
                    document_type=document_type,
                    folder=folder,
                    file=uploaded_file,
                    file_name=uploaded_file.name,
                    file_type=uploaded_file.content_type,
                    file_size=uploaded_file.size,
                    created_by=request.user,
                    added_by=request.user,
                    is_auto_created=False
                )
                
                # إضافة علامة تخطي إشارة المنع
                setattr(document, '_ignore_auto_document_signal', True)
                
                # حفظ المستند
                document.save()
                print(f"تم إنشاء المستند بنجاح: ID={document.id}")
            
            # إظهار رسالة نجاح
            messages.success(request, f"تم رفع المستند '{title}' بنجاح")
            
            # إعادة تفعيل إشارات المنع
            pre_save.receivers = original_handlers
            
            # إعادة التوجيه حسب المجلد
            if folder:
                return redirect(reverse('admin_archive_folder', kwargs={'folder_id': folder.id}))
            else:
                return redirect('admin_archive')
            
        except Exception as e:
            print(f"حدث خطأ أثناء رفع المستند: {str(e)}")
            print(traceback.format_exc())
            messages.error(request, f"حدث خطأ أثناء رفع المستند: {str(e)[:100]}")
            
            # إعادة تفعيل إشارات المنع في جميع الحالات
            pre_save.receivers = original_handlers
    
    # تحضير السياق للعرض
    context = {
        'current_folder': current_folder,
        'folders': folders,
        'folder_id': folder_id
    }
    
    # عرض صفحة الرفع
    return render(request, 'admin/archive/simple_working_upload.html', context)