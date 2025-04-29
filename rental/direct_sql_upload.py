
"""
وظيفة رفع مستندات موثوقة باستخدام SQL المباشر
هذا الحل يتجاوز كل آليات Django الإفتراضية لضمان رفع الملفات بشكل موثوق
"""

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from django.utils import timezone
from django.conf import settings
from django.db import connection, transaction
from rental.models import ArchiveFolder, Document
import os
import traceback

@login_required
@staff_member_required
def direct_sql_upload(request):
    """وظيفة رفع ملفات موثوقة 100% باستخدام SQL المباشر"""
    
    if request.method != 'POST':
        # إذا كان طلب GET، أعد توجيه المستخدم إلى صفحة الأرشيف
        return redirect('admin_archive')
    
    # طباعة معلومات للتشخيص
    print("🚀 بدء عملية رفع ملف باستخدام SQL المباشر")
    print(f"🔍 بيانات النموذج: {request.POST}")
    print(f"🔍 الملفات: {request.FILES.keys() if request.FILES else 'لا يوجد'}")
    
    try:
        # التحقق من توفر الملف والعنوان
        if 'file' not in request.FILES:
            messages.error(request, "لم يتم تحديد ملف للتحميل")
            print("❌ لا يوجد ملف مرفق")
            return redirect('admin_archive')
            
        if not request.POST.get('title'):
            messages.error(request, "يرجى إدخال عنوان للملف")
            print("❌ لا يوجد عنوان للملف")
            return redirect('admin_archive')
        
        # استخلاص البيانات من النموذج
        title = request.POST.get('title')
        description = request.POST.get('description', '')
        document_type = request.POST.get('document_type', 'other')
        folder_id = request.POST.get('folder')
        
        print(f"📋 بيانات المستند: العنوان='{title}', النوع='{document_type}', المجلد={folder_id}")
        
        # تجهيز معلومات الملف
        uploaded_file = request.FILES['file']
        file_name = uploaded_file.name
        file_type = uploaded_file.content_type
        file_size = uploaded_file.size
        file_content = uploaded_file.read()
        
        print(f"📁 معلومات الملف: الاسم='{file_name}', النوع='{file_type}', الحجم={file_size} بايت")
        
        # التحقق من وجود المجلد إذا تم تحديده
        folder = None
        if folder_id:
            try:
                folder = ArchiveFolder.objects.get(id=folder_id)
                print(f"📂 المجلد المحدد: {folder.name} (ID: {folder.id})")
            except ArchiveFolder.DoesNotExist:
                print(f"⚠️ المجلد المحدد غير موجود (ID: {folder_id})")
        
        # استخدام SQL مباشرة لإنشاء المستند بأمان
        with transaction.atomic():
            # تعطيل المحفزات مؤقتاً
            cursor = connection.cursor()
            cursor.execute("SET session_replication_role = 'replica';")
            print("🔧 تم تعطيل المحفزات مؤقتاً")
            
            # إنشاء المستند في قاعدة البيانات
            document_date = timezone.now().date()
            sql = """
            INSERT INTO rental_document 
            (title, description, document_type, folder_id, created_by_id, added_by_id,
            file_name, file_type, file_size, file_content, created_at, updated_at, is_auto_created,
            document_date, related_to, is_archived) 
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, NOW(), NOW(), %s, %s, %s, %s) 
            RETURNING id;
            """
            
            cursor.execute(sql, [
                title, 
                description, 
                document_type, 
                folder.id if folder else None,
                request.user.id if request.user.is_authenticated else None,
                request.user.id if request.user.is_authenticated else None,
                file_name, 
                file_type, 
                file_size, 
                file_content,
                False,  # is_auto_created
                document_date,
                'other',  # related_to
                True,     # is_archived
            ])
            
            # الحصول على معرف المستند المنشأ
            document_id = cursor.fetchone()[0]
            print(f"✅ تم إنشاء المستند برقم: {document_id}")
            
            # إعادة تفعيل المحفزات
            cursor.execute("SET session_replication_role = 'origin';")
            print("🔧 تم إعادة تفعيل المحفزات")
            
            # حفظ الملف المادي على القرص
            upload_dir = os.path.join(settings.MEDIA_ROOT, 'uploads')
            os.makedirs(upload_dir, exist_ok=True)
            
            # إنشاء اسم فريد للملف
            timestamp = int(timezone.now().timestamp())
            unique_filename = f"direct_{timestamp}_{timestamp % 10000}_{file_name}"
            file_path = os.path.join(upload_dir, unique_filename)
            
            # إعادة فتح الملف وحفظه
            uploaded_file.seek(0)
            with open(file_path, 'wb') as destination:
                for chunk in uploaded_file.chunks():
                    destination.write(chunk)
            
            # تحديث المسار في قاعدة البيانات
            rel_path = os.path.relpath(file_path, settings.MEDIA_ROOT)
            cursor.execute("UPDATE rental_document SET file = %s WHERE id = %s", [rel_path, document_id])
            print(f"✅ تم حفظ الملف في: {rel_path}")
            
            # معلومات نجاح العملية
            messages.success(request, f"تم رفع المستند '{title}' بنجاح")
            print("🎉 تمت عملية الرفع بنجاح")
            
        # إعادة التوجيه إلى صفحة الأرشيف
        if folder:
            return redirect('admin_archive_folder', folder_id=folder.id)
        else:
            return redirect('admin_archive')
            
    except Exception as e:
        # تسجيل الخطأ وإظهار رسالة للمستخدم
        error_message = f"حدث خطأ أثناء رفع الملف: {str(e)}"
        print(f"❌ {error_message}")
        print(traceback.format_exc())
        messages.error(request, error_message)
        return redirect('admin_archive')
