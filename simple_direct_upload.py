"""
حل مباشر لرفع الملفات في صفحة الأرشيف
هذا الملف يوفر حلاً بسيطاً ومباشراً لضمان رفع الملفات بنجاح إلى الأرشيف
"""

import os
import uuid
import traceback
from datetime import datetime
from django.utils import timezone
from django.shortcuts import render, redirect
from django.contrib import messages
from django.db import connection, transaction
from django.urls import path
from django.contrib.auth.decorators import login_required
from rental.admin_views import admin_required

def simple_direct_upload():
    """
    إضافة وظيفة رفع ملفات مباشرة تعمل بشكل مضمون
    """
    print("\n=== تثبيت وظيفة رفع الملفات المباشرة ===")
    
    @login_required
    @admin_required
    def direct_upload_file(request):
        """وظيفة رفع ملفات مباشرة باستخدام SQL وتجاوز القيود"""
        if request.method != 'POST':
            return redirect('admin_archive')
        
        # طباعة بيانات النموذج للتصحيح
        print(f"📑 بيانات النموذج: {request.POST}")
        print(f"📑 الملفات: {request.FILES}")
        
        # استخراج البيانات الأساسية
        title = request.POST.get('title', '').strip()
        description = request.POST.get('description', '')
        folder_id = request.POST.get('folder')
        document_type = request.POST.get('document_type', 'other')
        
        # التحقق من البيانات الأساسية
        if not title:
            messages.error(request, "يرجى إدخال عنوان للملف")
            return redirect('admin_archive')
        
        if 'file' not in request.FILES:
            messages.error(request, "يرجى تحديد ملف للرفع")
            return redirect('admin_archive')
        
        # استخراج معلومات الملف
        uploaded_file = request.FILES['file']
        file_name = uploaded_file.name
        file_type = uploaded_file.content_type
        file_size = uploaded_file.size
        
        print(f"📄 معلومات الملف: {file_name}, النوع: {file_type}, الحجم: {file_size}")
        
        # إنشاء مسار لحفظ نسخة فعلية من الملف
        # تأكد من وجود مجلد لحفظ الملفات
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
    
    # إضافة المسار في urls.py
    from rental import urls as rental_urls
    from django.urls.resolvers import URLPattern
    
    # إضافة المسار إذا لم يكن موجوداً
    path_exists = False
    for pattern in rental_urls.urlpatterns:
        if hasattr(pattern, 'pattern') and 'direct-upload-file' in str(pattern.pattern):
            path_exists = True
            break
    
    if not path_exists:
        # إضافة المسار الجديد
        new_path = path('dashboard/archive/direct-upload-file/', direct_upload_file, name='direct_upload_file')
        rental_urls.urlpatterns.append(new_path)
        print("✅ تم إضافة مسار جديد لرفع الملفات: /dashboard/archive/direct-upload-file/")
    
    # تعديل نموذج الرفع في القالب
    update_upload_form()
    
    return direct_upload_file

def update_upload_form():
    """
    تحديث نموذج رفع الملفات في قالب windows_explorer_enhanced.html
    """
    template_path = 'templates/admin/archive/windows_explorer_enhanced.html'
    
    try:
        with open(template_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # تحديث عنوان النموذج لاستخدام المسار الجديد
        if 'action="{% url \'admin_archive_upload\' %}"' in content:
            content = content.replace(
                'action="{% url \'admin_archive_upload\' %}"',
                'action="{% url \'direct_upload_file\' %}"'
            )
            
            # حفظ التغييرات
            with open(template_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            print(f"✅ تم تحديث نموذج رفع الملفات في {template_path}")
        else:
            print(f"⚠️ لم يتم العثور على نموذج الرفع في {template_path}")
    except Exception as e:
        print(f"❌ حدث خطأ أثناء تحديث نموذج الرفع: {str(e)}")

def main():
    """الدالة الرئيسية"""
    direct_upload_function = simple_direct_upload()
    print("✅ تم تثبيت وظيفة رفع الملفات المباشرة بنجاح")
    
    # إعادة مرجع الوظيفة للاستخدام المباشر
    return direct_upload_function

if __name__ == "__main__":
    main()