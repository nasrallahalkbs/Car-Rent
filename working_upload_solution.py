"""
حل نهائي وموثوق لمشكلة رفع الملفات في الأرشيف الإلكتروني.
هذا الملف يستخدم طريقة مباشرة لا تتأثر بإشارات منع المستندات التلقائية.
"""

from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.db import connection
from django.utils import timezone
from django.conf import settings
from django.urls import reverse
from django.utils.crypto import get_random_string

import os
import psycopg2
import traceback
import logging
import base64

from rental.decorators import admin_required
from rental.models import ArchiveFolder, Document

# إعداد التسجيل
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

@login_required
@admin_required
def guaranteed_upload_view(request):
    """
    وظيفة رفع ملفات مضمونة 100% دون استخدام ORM أو إشارات
    """
    print("\n======== بدء معالجة رفع ملف موثوق 100٪ ========")
    
    # الحصول على معلمات URL
    folder_id = request.GET.get('folder', None)
    
    # الحصول على المجلد الحالي إذا تم تحديده
    current_folder = None
    if folder_id:
        try:
            current_folder = ArchiveFolder.objects.get(id=folder_id)
            print(f"المجلد المحدد: {current_folder.name} (ID: {current_folder.id})")
        except ArchiveFolder.DoesNotExist:
            messages.error(request, "المجلد المحدد غير موجود")
    
    # الحصول على قائمة المجلدات لمربع الاختيار
    folders = ArchiveFolder.objects.all().order_by('name')
    
    # معالجة طلب POST للرفع
    if request.method == 'POST':
        print(f"طلب POST: {request.POST}")
        print(f"ملفات مرفقة: {request.FILES}")
        
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
        
        # معالجة الملف المرفوع
        uploaded_file = request.FILES['file']
        file_name = uploaded_file.name
        file_type = uploaded_file.content_type
        file_size = uploaded_file.size
        
        print(f"معلومات الملف: الاسم={file_name}, النوع={file_type}, الحجم={file_size}")
        
        # تحديد المجلد إذا كان موجوداً
        folder = None
        if folder_id:
            try:
                # استخدام استعلام SQL مباشر للحصول على المجلد
                with connection.cursor() as cursor:
                    cursor.execute("SELECT id, name FROM rental_archivefolder WHERE id = %s", [folder_id])
                    folder_data = cursor.fetchone()
                    if folder_data:
                        folder = {'id': folder_data[0], 'name': folder_data[1]}
                        print(f"تم العثور على المجلد: {folder['name']} (ID: {folder['id']})")
                    else:
                        messages.error(request, "المجلد المحدد غير موجود")
                        return redirect(request.path)
            except Exception as e:
                print(f"خطأ في البحث عن المجلد: {str(e)}")
                messages.error(request, "حدث خطأ في البحث عن المجلد")
                return redirect(request.path)
        
        try:
            # استخدام SQL مباشر للإدراج
            with connection.cursor() as cursor:
                # قراءة محتوى الملف
                file_content = uploaded_file.read()
                
                # توليد اسم ملف فريد
                unique_filename = get_random_string(8) + '_' + file_name
                file_path = os.path.join('documents', unique_filename)
                
                # حفظ الملف على القرص
                absolute_path = os.path.join(settings.MEDIA_ROOT, file_path)
                os.makedirs(os.path.dirname(absolute_path), exist_ok=True)
                
                with open(absolute_path, 'wb') as destination:
                    destination.write(file_content)
                
                # إعادة تهيئة الملف المرفوع
                uploaded_file.seek(0)
                
                # إدراج المستند في قاعدة البيانات
                created_at = timezone.now()
                user_id = request.user.id
                
                # استعلام SQL
                sql = """
                INSERT INTO rental_document 
                (title, description, document_type, folder_id, 
                file, file_name, file_type, file_size, 
                created_at, updated_at, created_by_id, added_by_id, 
                is_auto_created, document_date) 
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                RETURNING id;
                """
                
                cursor.execute(sql, [
                    title, 
                    description, 
                    document_type, 
                    folder_id, 
                    file_path,  # المسار المحفوظ في قاعدة البيانات
                    file_name, 
                    file_type, 
                    file_size, 
                    created_at, 
                    created_at, 
                    user_id, 
                    user_id, 
                    False,  # ليس مستند تلقائي
                    created_at
                ])
                
                # الحصول على معرف المستند الجديد
                document_id = cursor.fetchone()[0]
                print(f"✅ تم إنشاء المستند بنجاح: ID={document_id}")
                
                # إظهار رسالة نجاح
                messages.success(request, f"تم رفع المستند '{title}' بنجاح")
                
                # إعادة التوجيه حسب المجلد
                if folder:
                    return redirect(reverse('admin_archive_folder', kwargs={'folder_id': folder['id']}))
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
    return render(request, 'admin/archive/guaranteed_upload.html', context)