"""
حل نهائي أقصى التبسيط لمشكلة رفع الملفات في الأرشيف
استخدام SQL مباشر فقط بدون ORM نهائياً
"""

import os
import psycopg2
import secrets
import time
import traceback
from datetime import datetime

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import render, redirect

# استدعاء ديكوريتور admin_required
from rental.decorators import admin_required


@login_required
@admin_required
def pure_sql_upload(request):
    """
    رفع ملفات باستخدام SQL المباشر دون استخدام ORM بتاتاً
    أبسط طريقة ممكنة، تتجاوز جميع آليات Django
    """
    # طباعة رسالة تصحيح
    print("\n======== بدء عملية رفع ملف بطريقة SQL المباشر ========")
    
    # تحضير البيانات للقالب
    context = {
        "folders": [],  # سيتم ملؤها لاحقاً
        "current_folder": None,
        "folder_id": None
    }
    
    # الحصول على معلمات URL
    folder_id = request.GET.get('folder', None)
    
    # إعداد اتصال قاعدة البيانات
    db_url = os.environ.get('DATABASE_URL')
    if not db_url:
        messages.error(request, "لم يتم العثور على معلومات قاعدة البيانات")
        return render(request, 'admin/archive/super_basic_upload.html', context)
    
    # إنشاء اتصال قاعدة البيانات
    try:
        conn = psycopg2.connect(db_url)
        cursor = conn.cursor()
        
        # استعلام للحصول على قائمة المجلدات
        cursor.execute("SELECT id, name FROM rental_archivefolder ORDER BY name")
        folders_data = cursor.fetchall()
        folders = [{"id": folder[0], "name": folder[1]} for folder in folders_data]
        context["folders"] = folders
        
        # الحصول على معلومات المجلد الحالي إذا تم تحديده
        if folder_id:
            try:
                folder_id = int(folder_id)
                cursor.execute("SELECT id, name FROM rental_archivefolder WHERE id = %s", (folder_id,))
                folder_data = cursor.fetchone()
                if folder_data:
                    context["current_folder"] = {"id": folder_data[0], "name": folder_data[1]}
                    context["folder_id"] = folder_data[0]
                    print(f"المجلد المحدد: {folder_data[1]} (ID: {folder_data[0]})")
            except (ValueError, TypeError):
                messages.error(request, "معرف المجلد غير صالح")
    
    except Exception as e:
        print(f"خطأ في الاتصال بقاعدة البيانات: {str(e)}")
        messages.error(request, "حدث خطأ في الاتصال بقاعدة البيانات")
        return render(request, 'admin/archive/super_basic_upload.html', context)
    
    # معالجة طلب POST لرفع الملف
    if request.method == 'POST':
        # طباعة معلومات الطلب
        print(f"تم استلام طلب POST: {request.POST}")
        print(f"الملفات: {request.FILES}")
        
        # استخراج البيانات المرسلة
        title = request.POST.get('title', '').strip()
        description = request.POST.get('description', '')
        document_type = request.POST.get('document_type', 'other')
        folder_id = request.POST.get('folder', None)
        
        # التحقق من عنوان المستند
        if not title:
            messages.error(request, "يرجى إدخال عنوان للمستند")
            return render(request, 'admin/archive/super_basic_upload.html', context)
        
        # التحقق من وجود ملف
        if 'file' not in request.FILES:
            messages.error(request, "يرجى تحديد ملف للرفع")
            return render(request, 'admin/archive/super_basic_upload.html', context)
        
        # معالجة الملف المرفوع
        uploaded_file = request.FILES['file']
        file_name = uploaded_file.name
        file_type = uploaded_file.content_type
        file_size = uploaded_file.size
        
        print(f"معلومات الملف: الاسم={file_name}, النوع={file_type}, الحجم={file_size}")
        
        try:
            # إنشاء اسم ملف فريد لتجنب التعارض
            unique_filename = f"{int(time.time())}_{secrets.token_hex(4)}_{file_name}"
            
            # إنشاء مسار للملف
            file_path = os.path.join('documents', unique_filename)
            absolute_path = os.path.join(settings.MEDIA_ROOT, file_path)
            
            # التأكد من وجود المجلد
            os.makedirs(os.path.dirname(absolute_path), exist_ok=True)
            
            # حفظ الملف على القرص
            with open(absolute_path, 'wb') as destination:
                for chunk in uploaded_file.chunks():
                    destination.write(chunk)
            
            print(f"✅ تم حفظ الملف في: {absolute_path}")
            
            # حفظ في قاعدة البيانات
            now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            user_id = request.user.id
            
            # استعلام SQL مباشر لإدخال المستند
            sql = """
            INSERT INTO rental_document 
            (title, description, document_type, folder_id, 
            file, file_name, file_type, file_size, 
            created_at, updated_at, created_by_id, added_by_id, 
            is_auto_created, document_date)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING id;
            """
            
            # تنفيذ الاستعلام
            folder_id_val = int(folder_id) if folder_id and folder_id.isdigit() else None
            
            cursor.execute(sql, [
                title,
                description,
                document_type,
                folder_id_val,
                file_path,  # مسار الملف
                file_name,
                file_type,
                file_size,
                now,  # created_at
                now,  # updated_at
                user_id,  # created_by_id
                user_id,  # added_by_id
                False,  # is_auto_created
                now,    # document_date
            ])
            
            # الحصول على معرف المستند
            document_id = cursor.fetchone()[0]
            
            # تنفيذ التغييرات
            conn.commit()
            
            print(f"✅ تم إدراج المستند في قاعدة البيانات بمعرف: {document_id}")
            
            # إظهار رسالة نجاح
            messages.success(request, f"تم رفع المستند '{title}' بنجاح (عملية مباشرة)")
            
            # إعادة التوجيه إلى صفحة الأرشيف
            if folder_id_val:
                return redirect(f"/ar/dashboard/archive/{folder_id_val}/")
            else:
                return redirect("/ar/dashboard/archive/")
            
        except Exception as e:
            # التراجع عن التغييرات في حالة وجود خطأ
            if 'conn' in locals() and conn:
                conn.rollback()
            
            # طباعة تفاصيل الخطأ
            print(f"❌ خطأ في رفع المستند: {str(e)}")
            print(traceback.format_exc())
            
            # إظهار رسالة خطأ
            messages.error(request, f"فشل في رفع المستند: {str(e)[:100]}")
            
            return render(request, 'admin/archive/super_basic_upload.html', context)
        
        finally:
            # إغلاق الاتصال بقاعدة البيانات
            if 'cursor' in locals() and cursor:
                cursor.close()
            if 'conn' in locals() and conn:
                conn.close()
    
    # إغلاق الاتصال بقاعدة البيانات
    if 'cursor' in locals() and cursor:
        cursor.close()
    if 'conn' in locals() and conn:
        conn.close()
    
    # عرض صفحة الرفع
    return render(request, 'admin/archive/super_basic_upload.html', context)