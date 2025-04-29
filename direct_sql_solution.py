"""
حل نهائي ومباشر لمشكلة رفع الملفات في الأرشيف الإلكتروني.
باستخدام SQL مباشر وبدون Django ORM.
"""

from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import connection
from django.utils import timezone
from django.urls import reverse

import os
import traceback
import logging
import uuid
import psycopg2
import base64

from rental.decorators import admin_required
from rental.models import ArchiveFolder

# إعداد التسجيل
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

@login_required
@admin_required
def direct_sql_upload(request):
    """
    وظيفة رفع ملفات مباشرة باستخدام SQL
    """
    print("\n======== بدء معالجة رفع ملف بـ SQL المباشر ========")
    
    # الحصول على معلمات URL
    folder_id = request.GET.get('folder', None)
    
    # الحصول على قائمة المجلدات
    folders = []
    current_folder = None
    
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT id, name FROM rental_archivefolder ORDER BY name")
            folders = [{'id': row[0], 'name': row[1]} for row in cursor.fetchall()]
            
            if folder_id:
                cursor.execute("SELECT id, name FROM rental_archivefolder WHERE id = %s", [folder_id])
                folder_data = cursor.fetchone()
                if folder_data:
                    current_folder = {'id': folder_data[0], 'name': folder_data[1]}
    except Exception as e:
        print(f"خطأ في جلب المجلدات: {str(e)}")
    
    # معالجة طلب POST للرفع
    if request.method == 'POST':
        print(f"معالجة طلب POST: {request.POST}")
        print(f"ملفات: {request.FILES}")
        
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
        
        # الحصول على معلومات الملف
        file = request.FILES['file']
        file_name = file.name
        file_type = file.content_type
        file_size = file.size
        
        # قراءة محتويات الملف
        file_content = file.read()
        
        # تحويل المحتوى لقاعدة البيانات
        encoded_content = base64.b64encode(file_content).decode('utf-8')
        
        print(f"معلومات الملف المرفق: {file_name}, {file_type}, {file_size} بايت")
        
        try:
            # استخدام SQL مباشر لإدراج المستند
            with connection.cursor() as cursor:
                # الحصول على معلومات المستخدم
                user_id = request.user.id
                created_at = timezone.now()
                
                # إعداد استعلام SQL
                query = """
                INSERT INTO rental_document 
                (title, description, document_type, folder_id, created_by_id, added_by_id,
                file_content, file_name, file_type, file_size, created_at, updated_at, is_auto_created, document_date) 
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                RETURNING id;
                """
                
                # تنفيذ الاستعلام
                cursor.execute(query, [
                    title,
                    description,
                    document_type,
                    folder_id if folder_id else None,
                    user_id,
                    user_id,
                    encoded_content,
                    file_name,
                    file_type,
                    file_size,
                    created_at,
                    created_at,
                    False,  # ليس مستند تلقائي
                    created_at
                ])
                
                # استرجاع معرف المستند الجديد
                document_id = cursor.fetchone()[0]
                
                print(f"✅ تم إنشاء المستند بنجاح: ID={document_id}")
                
                # إظهار رسالة نجاح
                messages.success(request, f"تم رفع المستند '{title}' بنجاح")
                
                # إعادة التوجيه
                if folder_id:
                    return redirect(reverse('admin_archive_folder', kwargs={'folder_id': folder_id}))
                else:
                    return redirect('admin_archive')
                
        except Exception as e:
            print(f"❌ خطأ في رفع المستند: {str(e)}")
            print(traceback.format_exc())
            messages.error(request, f"حدث خطأ أثناء رفع المستند: {str(e)[:100]}")
            return redirect(request.path)
    
    # تحضير السياق للعرض
    context = {
        'current_folder': current_folder,
        'folders': folders,
        'folder_id': folder_id
    }
    
    # عرض صفحة الرفع
    return render(request, 'admin/archive/direct_sql_upload.html', context)