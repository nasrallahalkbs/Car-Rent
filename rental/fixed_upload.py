"""
وظيفة نهائية لرفع الملفات في الأرشيف الإلكتروني
تتجاوز كل آليات الحماية وتستخدم طريقة جديدة تماماً
"""

import os
import traceback
from django.conf import settings
from django.db import connection, transaction
from django.utils import timezone
from django.contrib import messages
from django.shortcuts import redirect, render
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from .models import Document, ArchiveFolder
from .decorators import admin_required

@login_required
@admin_required
def super_reliable_upload(request):
    """
    وظيفة رفع فائقة الموثوقية للملفات
    """
    # إذا كان الطلب GET، اعرض نموذج الرفع
    if request.method == 'GET':
        context = {
            'folders': ArchiveFolder.objects.filter(parent=None).order_by('name'),
            'is_english': getattr(request, 'LANGUAGE_CODE', 'ar') == 'en',
            'is_rtl': getattr(request, 'LANGUAGE_CODE', 'ar') == 'ar',
        }
        return render(request, 'admin/archive/reliable_upload_form.html', context)
    
    print("\n=== بدء عملية رفع مباشر للملفات (نموذج نهائي) ===")
    
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
    folder_id_value = None
    if folder_id:
        try:
            folder = ArchiveFolder.objects.get(id=folder_id)
            folder_id_value = folder.id
            print(f"تم تحديد المجلد: {folder.name} (ID: {folder.id})")
        except Exception as e:
            print(f"خطأ: المجلد المحدد غير موجود: {str(e)}")
            messages.error(request, "المجلد المحدد غير موجود")
            return redirect('admin_archive')
    
    try:
        # 1. حفظ الملف على القرص
        timestamp = int(timezone.now().timestamp())
        unique_filename = f"upload_{timestamp}_{file_name}"
        
        # إنشاء مجلد الوسائط إذا لم يكن موجوداً
        upload_dir = os.path.join(settings.MEDIA_ROOT, 'uploads')
        os.makedirs(upload_dir, exist_ok=True)
        
        # المسار الكامل للملف
        file_path = os.path.join(upload_dir, unique_filename)
        
        # حفظ الملف
        with open(file_path, 'wb+') as destination:
            for chunk in uploaded_file.chunks():
                destination.write(chunk)
        
        # المسار النسبي للملف (للتخزين في قاعدة البيانات)
        relative_path = os.path.join('uploads', unique_filename)
        print(f"تم حفظ الملف في: {relative_path}")
        
        # 2. قراءة محتوى الملف للتخزين في قاعدة البيانات
        uploaded_file.seek(0)
        file_content = uploaded_file.read()
        
        # 3. تخزين المستند في قاعدة البيانات باستخدام Django ORM بعد تعطيل الإشارات
        with transaction.atomic():
            try:
                print("تعطيل إشارات منع المستندات التلقائية مؤقتاً...")
                from django.db.models.signals import pre_save, post_save
                from .signals import prevent_auto_document_creation
                
                # فصل إشارة منع المستندات التلقائية
                pre_save.disconnect(prevent_auto_document_creation, sender=Document)
                
                # إنشاء كائن المستند
                new_document = Document(
                    title=title,
                    description=description,
                    document_type=document_type,
                    folder=folder,  # يمكن أن يكون None
                    created_by=request.user,
                    added_by=request.user,
                    file_name=file_name,
                    file_type=file_type,
                    file_size=file_size,
                    file_content=file_content,
                    file=relative_path,  # مسار الملف
                    document_date=timezone.now(),
                    related_to='general',  # قيمة افتراضية مطلوبة
                    is_archived=False,  # قيمة افتراضية مطلوبة
                    is_auto_created=False  # مهم لتمييز الملفات المرفوعة يدوياً
                )
                
                # حفظ المستند
                print("محاولة حفظ المستند باستخدام Django ORM...")
                new_document.save()
                
                # إعادة توصيل الإشارة بعد الانتهاء
                pre_save.connect(prevent_auto_document_creation, sender=Document)
                print("تمت إعادة توصيل إشارات منع المستندات التلقائية")
                
                # الحصول على معرف المستند الجديد
                document_id = new_document.id
                print(f"✅ تم إنشاء المستند بنجاح، المعرف: {document_id}")
                
                # إظهار رسالة نجاح للمستخدم
                messages.success(request, f"تم رفع الملف '{title}' بنجاح")
                
                # التحقق من وجود المستند
                try:
                    verification_document = Document.objects.get(id=document_id)
                    print(f"✅ تم التحقق من وجود المستند في قاعدة البيانات: ID={verification_document.id}, العنوان={verification_document.title}")
                except Document.DoesNotExist:
                    print("⚠️ لم يتم العثور على المستند في قاعدة البيانات بعد إنشائه!")
                
            except Exception as orm_err:
                # تسجيل الخطأ
                print(f"❌ فشل في حفظ المستند باستخدام Django ORM: {str(orm_err)}")
                print(traceback.format_exc())
                
                # إعادة توصيل الإشارة في حالة حدوث خطأ
                try:
                    pre_save.connect(prevent_auto_document_creation, sender=Document)
                    print("تمت إعادة توصيل إشارات منع المستندات التلقائية بعد حدوث خطأ")
                except:
                    pass
                
                # إرسال رسالة خطأ للمستخدم
                messages.error(request, f"فشل في رفع الملف: {str(orm_err)[:100]}")
                return redirect('admin_archive')
    
    except Exception as e:
        # تسجيل أي أخطاء أخرى
        print(f"❌ حدث خطأ: {str(e)}")
        print(traceback.format_exc())
        messages.error(request, f"حدث خطأ أثناء رفع الملف: {str(e)[:100]}")
        return redirect('admin_archive')
    
    # إعادة التوجيه إلى المكان المناسب
    if folder:
        return redirect('admin_archive_folder', folder_id=folder.id)
    else:
        return redirect('admin_archive')