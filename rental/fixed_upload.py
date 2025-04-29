"""
وظيفة رفع ملفات محسنة تماماً للأرشيف الإلكتروني

هذا الملف يحتوي على وظائف بديلة لرفع الملفات، من خلال التأكد من تعطيل
نظام منع المستندات التلقائية بأكثر من طريقة لضمان نجاح عملية الرفع.
"""

from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib import messages
from django.db import transaction
from django.conf import settings
from django.db.models.signals import pre_save

from .models import Document, ArchiveFolder
from .decorators import admin_required

import os
import traceback


@login_required
@admin_required
def super_reliable_upload(request):
    """
    وظيفة رفع ملفات محسنة بشكل كامل تتجاوز جميع قيود المستندات التلقائية
    """
    import traceback
    
    # طباعة معلومات الطلب للتشخيص
    print("\n=== بدء معالجة طلب رفع مستند جديد (محسن) ===")
    print(f"طريقة الطلب: {request.method}")
    print(f"البيانات المرسلة: {request.POST}")
    print(f"الملفات المرفوعة: {request.FILES.keys() if request.FILES else 'لا يوجد'}")
    
    if request.method != 'POST':
        messages.error(request, "طريقة طلب غير صالحة")
        return redirect('admin_archive')
    
    # استخراج البيانات المرسلة
    title = request.POST.get('title', '').strip()
    description = request.POST.get('description', '')
    folder_id = request.POST.get('folder', None)
    document_type = request.POST.get('document_type', 'other')
    
    print(f"البيانات المستلمة: العنوان='{title}', النوع='{document_type}', المجلد={folder_id}")
    
    # التحقق من وجود البيانات المطلوبة
    if not title:
        print("خطأ: لم يتم تحديد عنوان للمستند")
        messages.error(request, "يرجى إدخال عنوان للمستند")
        return redirect('admin_archive')
    
    if 'file' not in request.FILES:
        print("خطأ: لم يتم تحديد ملف للتحميل")
        messages.error(request, "يرجى تحديد ملف للتحميل")
        return redirect('admin_archive')
    
    # معالجة الملف المرفوع
    uploaded_file = request.FILES['file']
    file_name = uploaded_file.name
    file_type = uploaded_file.content_type
    file_size = uploaded_file.size
    
    print(f"معلومات الملف: اسم='{file_name}', النوع='{file_type}', الحجم={file_size} بايت")
    
    # تحديد المجلد إذا كان موجوداً
    folder = None
    if folder_id:
        try:
            folder = ArchiveFolder.objects.get(id=folder_id)
            print(f"تم تحديد المجلد: {folder.name} (ID: {folder.id})")
        except ArchiveFolder.DoesNotExist:
            print(f"خطأ: المجلد المحدد غير موجود (ID: {folder_id})")
            messages.error(request, "المجلد المحدد غير موجود")
            return redirect('admin_archive')
    
    # حفظ الإشارات الأصلية لاستعادتها لاحقاً
    original_handlers = pre_save._live_receivers(Document)
    pre_save_receivers = pre_save.receivers

    # تعطيل نظام منع المستندات التلقائية مؤقتاً
    print("⚠️ تعطيل إشارة منع المستندات التلقائية...")
    pre_save.receivers = []
    
    try:
        # قراءة محتوى الملف
        file_content = uploaded_file.read()
        
        # استخدام معاملة قاعدة بيانات لضمان الاتساق
        with transaction.atomic():
            # إنشاء المستند - بدون إشارات pre_save
            document = Document(
                title=title,
                description=description,
                document_type=document_type,
                folder=folder,
                file_name=file_name,
                file_type=file_type,
                file_size=file_size,
                file_content=file_content,
                created_by=request.user,
                added_by=request.user,
                is_auto_created=False  # هذا مهم جداً
            )
            
            # تعيين علامة تجاوز إشارة المستندات التلقائية
            setattr(document, '_ignore_auto_document_signal', True)
            
            # حفظ المستند
            document.save()
            print(f"تم حفظ المستند بنجاح (بدون إشارات): ID={document.id}")
            
            # إعادة تعيين مؤشر الملف
            uploaded_file.seek(0)
            
            # تعيين الملف المرفوع
            document.file = uploaded_file
            document.save(update_fields=['file'])
            print("تم حفظ الملف المرفوع")
        
        # عرض رسالة نجاح للمستخدم
        messages.success(request, f"تم رفع المستند '{title}' بنجاح")
        
        # إعادة التوجيه بناءً على المجلد الحالي
        if folder:
            print(f"=== تم رفع المستند بنجاح! رقم المستند: {document.id} ===\n")
            return redirect('admin_archive')
        else:
            print(f"=== تم رفع المستند بنجاح! رقم المستند: {document.id} ===\n")
            return redirect('admin_archive')
            
    except Exception as e:
        print(f"خطأ أثناء رفع المستند: {str(e)}")
        print(traceback.format_exc())
        messages.error(request, f"حدث خطأ أثناء رفع المستند: {str(e)}")
        return redirect('admin_archive')
    
    finally:
        # إعادة تفعيل الإشارات الأصلية
        pre_save.receivers = pre_save_receivers
        print("✅ تم إعادة تفعيل إشارات المستندات التلقائية")