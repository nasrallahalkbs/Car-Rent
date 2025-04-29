"""
حل نهائي باستخدام SQL المباشر فقط بدون أي تفاعل مع Django
"""

import os
import time
import uuid
import psycopg2
import traceback
from datetime import datetime
from django.conf import settings
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.urls import reverse

from rental.decorators import admin_required

@login_required
@admin_required
def raw_sql_upload(request):
    """وظيفة رفع الملفات باستخدام SQL المباشر فقط"""
    
    print("\n====== بدء تنفيذ وظيفة رفع الملفات باستخدام SQL المباشر فقط ======")
    
    # الحصول على معلمات المسار
    folder_id = request.GET.get('folder', None)
    
    # بيانات الجلسة
    current_folder = None
    all_folders = []
    
    # معالجة طلب POST للرفع
    if request.method == 'POST':
        # استخراج البيانات
        title = request.POST.get('title', '').strip()
        description = request.POST.get('description', '')
        folder_id = request.POST.get('folder', None)
        document_type = request.POST.get('document_type', 'other')
        
        # التحقق من وجود العنوان والملف
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
        
        # قراءة الملف
        file_content = uploaded_file.read()
        
        # إنشاء اسم فريد للملف
        unique_filename = f"{uuid.uuid4().hex}_{file_name}"
        relative_path = os.path.join('documents', unique_filename)
        absolute_path = os.path.join(settings.MEDIA_ROOT, 'documents', unique_filename)
        
        # التأكد من وجود المجلد
        os.makedirs(os.path.dirname(absolute_path), exist_ok=True)
        
        # حفظ الملف على القرص
        try:
            with open(absolute_path, 'wb') as destination:
                destination.write(file_content)
            print(f"✅ تم حفظ الملف: {absolute_path}")
        except Exception as e:
            print(f"❌ خطأ في حفظ الملف: {str(e)}")
            messages.error(request, f"خطأ في حفظ الملف: {str(e)}")
            return redirect(request.path)
        
        # الاتصال بقاعدة البيانات باستخدام psycopg2 مباشرة
        try:
            # الحصول على معلومات الاتصال بقاعدة البيانات
            db_url = os.environ.get('DATABASE_URL')
            
            # التحقق من وجود رابط قاعدة البيانات
            if not db_url:
                messages.error(request, "لم يتم العثور على رابط قاعدة البيانات")
                return redirect(request.path)
            
            # الاتصال بقاعدة البيانات
            conn = psycopg2.connect(db_url)
            cursor = conn.cursor()
            
            # الحصول على المجلدات لعرضها في القالب
            cursor.execute("SELECT id, name FROM rental_archivefolder ORDER BY name")
            all_folders = [{'id': row[0], 'name': row[1]} for row in cursor.fetchall()]
            
            # الحصول على معلومات المجلد الحالي إذا كان موجود
            if folder_id:
                cursor.execute("SELECT id, name FROM rental_archivefolder WHERE id = %s", (folder_id,))
                folder_row = cursor.fetchone()
                if folder_row:
                    current_folder = {'id': folder_row[0], 'name': folder_row[1]}
            
            # إدراج المستند في قاعدة البيانات
            created_at = datetime.now()
            user_id = request.user.id
            
            # استعلام SQL لإضافة المستند
            insert_query = """
            INSERT INTO rental_document 
            (title, description, document_type, folder_id, 
            file, file_name, file_type, file_size, 
            created_at, updated_at, created_by_id, added_by_id, 
            is_auto_created, document_date) 
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING id;
            """
            
            cursor.execute(insert_query, [
                title, 
                description, 
                document_type, 
                folder_id, 
                relative_path,  # المسار المحفوظ في قاعدة البيانات
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
            
            # الحصول على معرف المستند المدرج
            document_id = cursor.fetchone()[0]
            
            # تأكيد التغييرات
            conn.commit()
            
            # إغلاق الاتصال
            cursor.close()
            conn.close()
            
            print(f"✅ تم إنشاء المستند بنجاح: ID={document_id}")
            
            # إظهار رسالة نجاح
            messages.success(request, f"تم رفع المستند '{title}' بنجاح")
            
            # إعادة التوجيه حسب المجلد
            if folder_id:
                return redirect(reverse('admin_archive_folder', kwargs={'folder_id': folder_id}))
            else:
                return redirect('admin_archive')
            
        except Exception as e:
            print(f"❌ خطأ في قاعدة البيانات: {str(e)}")
            print(traceback.format_exc())
            messages.error(request, f"خطأ في قاعدة البيانات: {str(e)[:100]}")
            return redirect(request.path)
    
    # إذا لم يكن الطلب POST، قم بجلب بيانات المجلدات
    else:
        try:
            # الاتصال بقاعدة البيانات
            db_url = os.environ.get('DATABASE_URL')
            conn = psycopg2.connect(db_url)
            cursor = conn.cursor()
            
            # الحصول على المجلدات
            cursor.execute("SELECT id, name FROM rental_archivefolder ORDER BY name")
            all_folders = [{'id': row[0], 'name': row[1]} for row in cursor.fetchall()]
            
            # الحصول على معلومات المجلد الحالي إذا كان موجود
            if folder_id:
                cursor.execute("SELECT id, name FROM rental_archivefolder WHERE id = %s", (folder_id,))
                folder_row = cursor.fetchone()
                if folder_row:
                    current_folder = {'id': folder_row[0], 'name': folder_row[1]}
            
            # إغلاق الاتصال
            cursor.close()
            conn.close()
            
        except Exception as e:
            print(f"❌ خطأ في جلب المجلدات: {str(e)}")
            messages.error(request, "حدث خطأ في تحميل بيانات المجلدات")
    
    # تحضير سياق العرض
    context = {
        'current_folder': current_folder,
        'folders': all_folders,
        'folder_id': folder_id
    }
    
    # عرض صفحة الرفع
    return render(request, 'admin/archive/raw_upload.html', context)