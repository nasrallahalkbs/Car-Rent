"""
حل مباشر لمشكلة رفع الملفات في الأرشيف.
هذا الملف يوفر وظيفة رفع ملفات موثوقة تستخدم SQL المباشر لتجاوز مشاكل منع المستندات التلقائية.
"""

import os
import uuid
import traceback
from django.utils import timezone
from django.shortcuts import render, redirect
from django.contrib import messages
from django.db import connection
from django.contrib.auth.decorators import login_required
from rental.admin_views import admin_required
from rental.models import ArchiveFolder

@login_required
@admin_required
def fixed_direct_upload(request):
    """وظيفة رفع ملفات مباشرة إلى الأرشيف"""
    if request.method != 'POST':
        # إذا لم تكن الطلب POST، إعادة التوجيه إلى الأرشيف
        return redirect('admin_archive')
    
    # طباعة معلومات للتصحيح
    print("\n=== معالجة رفع ملف مباشر ===")
    print(f"📝 بيانات النموذج: {request.POST}")
    print(f"📝 الملفات المرفقة: {request.FILES}")
    
    # البيانات الأساسية
    title = request.POST.get('title', '').strip()
    description = request.POST.get('description', '')
    folder_id = request.POST.get('folder')
    document_type = request.POST.get('document_type', 'other')
    
    # تحقق من البيانات الإلزامية
    if not title:
        messages.error(request, "يرجى إدخال عنوان للملف")
        return redirect('admin_archive')
    
    if 'file' not in request.FILES:
        messages.error(request, "يرجى تحديد ملف للرفع")
        return redirect('admin_archive')
    
    # معلومات الملف
    uploaded_file = request.FILES['file']
    file_name = uploaded_file.name
    file_type = uploaded_file.content_type
    file_size = uploaded_file.size
    
    print(f"📄 معلومات الملف: الاسم={file_name}, النوع={file_type}, الحجم={file_size}")
    
    # إنشاء مسار لحفظ الملف
    upload_dir = os.path.join('media', 'archive', 'uploads')
    os.makedirs(upload_dir, exist_ok=True)
    
    # إنشاء اسم ملف فريد
    ext = os.path.splitext(file_name)[1]
    unique_filename = f"{uuid.uuid4().hex}{ext}"
    rel_path = os.path.join('archive', 'uploads', unique_filename)
    absolute_path = os.path.join('media', rel_path)
    
    # حفظ الملف على القرص
    try:
        with open(absolute_path, 'wb+') as destination:
            for chunk in uploaded_file.chunks():
                destination.write(chunk)
        print(f"✅ تم حفظ الملف في: {absolute_path}")
    except Exception as e:
        print(f"❌ خطأ في حفظ الملف: {str(e)}")
        messages.error(request, f"حدث خطأ أثناء حفظ الملف: {str(e)[:100]}")
        return redirect('admin_archive')
    
    # استخدام SQL مباشرة لتجاوز المشاكل
    try:
        with connection.cursor() as cursor:
            # الوقت الحالي
            now = timezone.now()
            user_id = request.user.id
            
            # إنشاء المستند مباشرة في قاعدة البيانات
            cursor.execute("""
            INSERT INTO rental_document 
            (title, description, document_type, folder_id, file, file_name, file_type, file_size, 
            is_auto_created, added_by_id, created_at, updated_at, is_archived, document_date)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING id
            """, [
                title, description, document_type, 
                folder_id if folder_id else None, 
                rel_path, file_name, file_type, file_size,
                False, user_id, now, now, True, now.date()
            ])
            
            # الحصول على معرف المستند المدرج
            document_id = cursor.fetchone()[0]
            
            print(f"✅ تم إنشاء المستند في قاعدة البيانات: ID={document_id}")
            
            messages.success(request, f"تم رفع الملف '{title}' بنجاح")
            
            # إعادة التوجيه حسب المجلد
            if folder_id:
                return redirect('admin_archive_folder', folder_id=folder_id)
            else:
                return redirect('admin_archive')
            
    except Exception as e:
        print(f"❌ خطأ في قاعدة البيانات: {str(e)}")
        print(traceback.format_exc())
        messages.error(request, f"خطأ في قاعدة البيانات: {str(e)[:100]}")
        
        # حذف الملف المرفوع في حالة الفشل
        try:
            if os.path.exists(absolute_path):
                os.remove(absolute_path)
                print(f"✅ تم حذف الملف المرفوع بعد فشل العملية: {absolute_path}")
        except:
            pass
            
        return redirect('admin_archive')