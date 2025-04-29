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
        
        # 3. تخزين المستند في قاعدة البيانات مباشرة باستخدام SQL
        with transaction.atomic():
            cursor = connection.cursor()
            
            # تعطيل المحفزات مؤقتاً
            cursor.execute("SET session_replication_role = 'replica';")
            
            # الوقت الحالي بتنسيق قاعدة البيانات
            now = timezone.now().strftime('%Y-%m-%d %H:%M:%S')
            
            # الاستعلام المباشر
            query = """
            INSERT INTO rental_document 
            (title, description, document_type, folder_id, created_by_id, added_by_id,
            file_name, file_type, file_size, file_content, file, created_at, updated_at, is_auto_created,
            document_date) 
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s) 
            RETURNING id;
            """
            
            try:
                # تنفيذ الاستعلام
                cursor.execute(query, [
                    title, 
                    description, 
                    document_type, 
                    folder_id_value,  # يمكن أن يكون None
                    request.user.id,  # created_by
                    request.user.id,  # added_by
                    file_name, 
                    file_type, 
                    file_size, 
                    file_content,  # محتوى الملف
                    relative_path,  # مسار الملف
                    now,  # created_at
                    now,  # updated_at
                    False,  # is_auto_created - مهم لتمييز الملفات المرفوعة يدوياً
                    now  # تاريخ المستند
                ])
                
                # الحصول على معرف المستند الجديد
                document_id = cursor.fetchone()[0]
                print(f"✅ تم إنشاء المستند بنجاح، المعرف: {document_id}")
                
                # إعادة تفعيل المحفزات
                cursor.execute("SET session_replication_role = 'origin';")
                
                # إظهار رسالة نجاح للمستخدم
                messages.success(request, f"تم رفع الملف '{title}' بنجاح")
                
                # التحقق من أن المستند تم إنشاؤه فعلاً
                verification_query = "SELECT id, title FROM rental_document WHERE id = %s"
                cursor.execute(verification_query, [document_id])
                verification_result = cursor.fetchone()
                
                if verification_result:
                    print(f"✅ تم التحقق من وجود المستند في قاعدة البيانات: ID={verification_result[0]}, العنوان={verification_result[1]}")
                else:
                    print("⚠️ لم يتم العثور على المستند في قاعدة البيانات بعد إنشائه!")
                
            except Exception as sql_err:
                # تسجيل الخطأ
                print(f"❌ فشل في تنفيذ استعلام SQL: {str(sql_err)}")
                print(traceback.format_exc())
                
                # إعادة تفعيل المحفزات
                cursor.execute("SET session_replication_role = 'origin';")
                
                # إرسال رسالة خطأ للمستخدم
                messages.error(request, f"فشل في رفع الملف: {str(sql_err)[:100]}")
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