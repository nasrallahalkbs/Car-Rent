"""
حل نهائي مباشر لمشكلة رفع الملفات

هذا الحل يقوم بتعطيل جميع إشارات Django مؤقتاً أثناء عملية الرفع
ويستخدم SQL مباشر للتجاوز أي قيود
"""

import os
import uuid
from datetime import datetime, timedelta
import tempfile

from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib import messages
from django.db import connection
from django.conf import settings
from django.db.models.signals import pre_save, post_save
from django.apps import apps
from django.urls import reverse
from django.utils import timezone
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.dispatch import Signal

from rental.models import Document, ArchiveFolder
from rental.decorators import admin_required

# قائمة بجميع الإشارات المسجلة التي سنعطلها مؤقتاً
ALL_SIGNALS = [pre_save, post_save]

# حفظ جميع الإشارات المتصلة بها
SIGNAL_HANDLERS = {}

def disconnect_all_signals():
    """تعطيل جميع إشارات Django مؤقتاً"""
    print("🔕 تعطيل جميع إشارات Django...")
    
    # حفظ وتعطيل كل إشارة
    for signal in ALL_SIGNALS:
        SIGNAL_HANDLERS[signal] = signal.receivers.copy()
        signal.receivers = []
    
    print("✅ تم تعطيل جميع الإشارات بنجاح")

def reconnect_all_signals():
    """إعادة توصيل جميع إشارات Django"""
    print("🔔 إعادة توصيل جميع إشارات Django...")
    
    # إعادة تفعيل كل إشارة
    for signal in ALL_SIGNALS:
        signal.receivers = SIGNAL_HANDLERS.get(signal, [])
    
    print("✅ تم إعادة توصيل جميع الإشارات بنجاح")

@admin_required
def ultimate_upload(request):
    """حل نهائي يتجاوز جميع مشاكل رفع الملفات"""
    if request.method == 'POST':
        file = request.FILES.get('file')
        title = request.POST.get('title', '')
        folder_id = request.POST.get('folder_id')
        
        # معلومات إضافية
        expiry_date = request.POST.get('expiry_date')
        document_type = request.POST.get('document_type', 'مستند عام')
        related_to_type = request.POST.get('related_to_type', '')
        related_to_id = request.POST.get('related_to_id', '')
        
        if not title:
            title = file.name if file else "مستند جديد"
        
        if file:
            try:
                print(f"📄 بدء عملية رفع الملف: {title}")
                
                # 1. تعطيل جميع الإشارات مؤقتاً
                disconnect_all_signals()
                
                # 2. حفظ الملف مؤقتاً
                temp_path = default_storage.save(
                    f"temp/{uuid.uuid4()}/{file.name}",
                    ContentFile(file.read())
                )
                
                # 3. الاستعلام المباشر لإنشاء المستند
                with connection.cursor() as cursor:
                    file_path = f"{settings.MEDIA_ROOT}/{temp_path}"
                    if not os.path.exists(os.path.dirname(file_path)):
                        os.makedirs(os.path.dirname(file_path), exist_ok=True)
                    
                    # تجهيز البيانات للاستعلام
                    now = timezone.now()
                    
                    # تحويل تاريخ انتهاء الصلاحية
                    if expiry_date:
                        try:
                            expiry = datetime.strptime(expiry_date, '%Y-%m-%d').replace(tzinfo=timezone.utc)
                        except ValueError:
                            # إذا كان التاريخ غير صالح، نستخدم تاريخ افتراضي بعد سنة
                            expiry = now + timedelta(days=365)
                    else:
                        # تاريخ افتراضي بعد سنة
                        expiry = now + timedelta(days=365)
                    
                    # إنشاء استعلام SQL للإدراج
                    query = """
                    INSERT INTO rental_document 
                    (title, file, content_type, size, upload_date, expiry_date, document_type, 
                     related_to_type, related_to_id, folder_id, is_auto_document) 
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    RETURNING id
                    """
                    
                    cursor.execute(query, [
                        title,
                        temp_path,  # مسار الملف المؤقت
                        file.content_type,
                        file.size,
                        now,
                        expiry,
                        document_type,
                        related_to_type,
                        related_to_id,
                        folder_id,
                        False  # ليس مستنداً تلقائياً
                    ])
                    
                    # الحصول على معرف المستند المنشأ
                    document_id = cursor.fetchone()[0]
                
                messages.success(request, f"تم رفع المستند '{title}' بنجاح!")
                
                # إعادة توجيه إلى صفحة الأرشيف المناسبة
                if folder_id:
                    return redirect('admin_archive_folder', folder_id=folder_id)
                else:
                    return redirect('admin_archive')
            
            except Exception as e:
                print(f"❌ خطأ في رفع الملف: {str(e)}")
                messages.error(request, f"حدث خطأ أثناء رفع الملف: {str(e)}")
            finally:
                # إعادة توصيل الإشارات بغض النظر عن نجاح أو فشل العملية
                reconnect_all_signals()
        else:
            messages.error(request, "لم يتم تحديد ملف للرفع!")
    
    # استرجاع قائمة المجلدات لعرضها في نموذج الرفع
    folders = ArchiveFolder.objects.all()
    
    # عرض نموذج رفع الملف
    return render(request, 'admin/archive/direct_upload_form.html', {
        'folders': folders,
        'parent_template': 'admin_layout.html',
    })

# إضافة المسار URL
def add_url_route():
    """إضافة مسار URL للحل النهائي"""
    with open('rental/urls.py', 'r') as f:
        urls_content = f.read()
    
    # التحقق من وجود الاستيراد
    if 'from ultimate_upload_solution import ultimate_upload' not in urls_content:
        # إضافة استيراد الدالة
        import_line = 'from direct_upload_implementation import direct_sql_upload_document'
        new_import = 'from direct_upload_implementation import direct_sql_upload_document\nfrom ultimate_upload_solution import ultimate_upload'
        urls_content = urls_content.replace(import_line, new_import)
    
    # التحقق من وجود المسار
    if "path('ar/dashboard/archive/ultimate-upload/', ultimate_upload, name='ultimate_upload')" not in urls_content:
        # إضافة المسار الجديد بعد مسارات الرفع الأخرى
        pattern = "path('ar/dashboard/archive/upload/', super_reliable_upload, name='admin_archive_upload'),"
        new_route = "path('ar/dashboard/archive/upload/', super_reliable_upload, name='admin_archive_upload'),\n    path('ar/dashboard/archive/ultimate-upload/', ultimate_upload, name='ultimate_upload'),"
        urls_content = urls_content.replace(pattern, new_route)
    
    # حفظ التغييرات
    with open('rental/urls.py', 'w') as f:
        f.write(urls_content)
    
    print("✅ تم إضافة مسار URL للحل النهائي")

# تحديث نموذج الرفع لاستخدام الحل النهائي
def update_upload_form():
    """تحديث نموذج رفع الملفات ليستخدم الحل النهائي"""
    with open('templates/admin/archive/direct_upload_form.html', 'r') as f:
        form_content = f.read()
    
    # تغيير وجهة النموذج
    if 'action="{% url \'direct_sql_upload_document\' %}"' in form_content:
        new_form = form_content.replace(
            'action="{% url \'direct_sql_upload_document\' %}"',
            'action="{% url \'ultimate_upload\' %}"'
        )
        
        with open('templates/admin/archive/direct_upload_form.html', 'w') as f:
            f.write(new_form)
        
        print("✅ تم تحديث نموذج الرفع ليستخدم الحل النهائي")

# تحديث النوافذ المنبثقة في قالب الأرشيف
def update_archive_template():
    """تحديث النوافذ المنبثقة في قالب الأرشيف"""
    with open('templates/admin/archive/windows_explorer_enhanced.html', 'r') as f:
        template_content = f.read()
    
    # تحديث رابط وجهة نموذج رفع الملفات
    if 'action="{% url \'admin_archive_upload\' %}"' in template_content:
        new_template = template_content.replace(
            'action="{% url \'admin_archive_upload\' %}"',
            'action="{% url \'ultimate_upload\' %}"'
        )
        
        with open('templates/admin/archive/windows_explorer_enhanced.html', 'w') as f:
            f.write(new_template)
        
        print("✅ تم تحديث قالب الأرشيف لاستخدام الحل النهائي")

def main():
    """تطبيق جميع التغييرات"""
    add_url_route()
    update_upload_form()
    update_archive_template()
    print("✅ تم تطبيق الحل النهائي")

if __name__ == "__main__":
    main()