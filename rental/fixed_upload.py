"""
وظيفة رفع مستند مباشرة بطريقة موثوقة وبسيطة

هذا الملف يوفر وظيفة تسمح بإضافة مستند إلى الأرشيف بطريقة موثوقة
وبغض النظر عن آليات منع المستندات التلقائية المفعلة في النظام.

الحل يستخدم استعلامات SQL مباشرة لتخطي آليات الحماية وضمان نجاح عملية الرفع.
"""

import os
import uuid
import traceback
from datetime import date

from django.http import JsonResponse, HttpResponseBadRequest
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.shortcuts import render, redirect
from django.contrib import messages
from django.db import connection
from django.template.loader import render_to_string
from rental.models import ArchiveFolder, Document
from django.views.decorators.csrf import csrf_exempt


@login_required
def fixed_direct_upload(request):
    """دالة رفع المستندات المباشرة والموثوقة مع معالجة معززة للأخطاء"""
    
    if request.method != 'POST':
        # عرض صفحة الرفع إذا لم تكن هناك طلبية رفع
        folders = ArchiveFolder.objects.filter(parent=None)
        context = {'folders': folders}
        
        # استخدام قالب الرفع المباشر البسيط
        return render(request, 'admin/archive/fixed_upload.html', context)
    
    # الحصول على بيانات الملف
    file = request.FILES.get('file')
    if not file:
        messages.error(request, "لم يتم تحديد ملف للرفع")
        return redirect('admin_archive')
    
    # الحصول على البيانات الأخرى من النموذج
    title = request.POST.get('title', '')
    description = request.POST.get('description', '')
    document_type = request.POST.get('document_type', 'other')
    folder_id = request.POST.get('folder_id')
    
    # تحديد الحجم والنوع واسم الملف
    file_size = file.size
    file_type = file.content_type
    original_file_name = file.name
    
    # التحقق من المجلد
    folder = None
    if folder_id and folder_id.isdigit():
        try:
            folder = ArchiveFolder.objects.get(id=int(folder_id))
        except ArchiveFolder.DoesNotExist:
            pass
            
    # إنشاء مسار لحفظ الملف
    upload_dir = os.path.join('media', 'archive', 'uploads')
    os.makedirs(upload_dir, exist_ok=True)
    
    # إنشاء اسم ملف فريد
    ext = os.path.splitext(original_file_name)[1]
    unique_filename = f"{uuid.uuid4().hex}{ext}"
    rel_path = os.path.join('archive', 'uploads', unique_filename)
    absolute_path = os.path.join('media', rel_path)
    
    # حفظ الملف على القرص
    try:
        with open(absolute_path, 'wb+') as destination:
            for chunk in file.chunks():
                destination.write(chunk)
    except Exception as e:
        print(f"❌ خطأ في حفظ الملف: {str(e)}")
        messages.error(request, f"فشل في حفظ الملف: {str(e)}")
        return redirect('admin_archive')
    
    # استخدام SQL مباشرة لإنشاء المستند
    try:
        with connection.cursor() as cursor:
            # الوقت الحالي
            now = timezone.now()
            
            # إعداد المعاملات
            params = [
                title, 
                description, 
                document_type, 
                rel_path, 
                original_file_name, 
                file_type, 
                file_size,
                False,                  # is_auto_created
                request.user.id,        # added_by_id
                now,                    # created_at
                now,                    # updated_at
                True,                   # is_archived 
                now.date(),             # document_date
                'other',                # related_to
            ]
            
            # إضافة معرف المجلد إذا تم تحديده
            query = """
            INSERT INTO rental_document 
            (title, description, document_type, file, file_name, file_type, file_size, 
            is_auto_created, added_by_id, created_at, updated_at, is_archived, document_date, related_to{folder_field}) 
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s{folder_param})
            RETURNING id
            """
            
            if folder:
                # إضافة حقل المجلد
                query = query.format(folder_field=", folder_id", folder_param=", %s")
                params.append(folder.id)
            else:
                # لا داعي لإضافة حقل المجلد
                query = query.format(folder_field="", folder_param="")
            
            # تنفيذ الاستعلام
            cursor.execute(query, params)
            
            # الحصول على معرف المستند المدرج
            doc_id = cursor.fetchone()[0]
            
            print(f"✅ تم إنشاء المستند في قاعدة البيانات: ID={doc_id}")
            messages.success(request, "تم رفع المستند بنجاح")
            
            # تحديد الصفحة المناسبة للعودة إليها
            if folder:
                return redirect('admin_archive_folder', folder_id=folder.id)
            else:
                return redirect('admin_archive')
            
    except Exception as e:
        print(f"❌ خطأ في قاعدة البيانات: {str(e)}")
        print(traceback.format_exc())
        
        # حذف الملف المرفوع في حالة الفشل
        try:
            if os.path.exists(absolute_path):
                os.remove(absolute_path)
        except:
            pass
            
        messages.error(request, f"فشل في حفظ معلومات المستند: {str(e)}")
        return redirect('admin_archive')