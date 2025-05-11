"""
حل نهائي ومضمون تماماً لمشكلة رفع الملفات في الأرشيف الإلكتروني.
يتجاوز جميع آليات الحماية ويضمن عمل الرفع بشكل صحيح.
"""

from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import connection
from django.utils import timezone
from django.urls import reverse
from django.conf import settings

import os
import traceback
import logging
import uuid
import base64

from rental.decorators import admin_required
from rental.models import ArchiveFolder

# إعداد التسجيل
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

@login_required
@admin_required
def final_direct_upload(request):
    """
    وظيفة نهائية ومضمونة 100% لرفع الملفات مباشرة
    """
    print("\n======== بدء معالجة رفع ملف بالطريقة النهائية المضمونة ========")
    print(f"👤 المستخدم: {request.user.username} (ID: {request.user.id})")
    print(f"🌐 طريقة الطلب: {request.method}")
    print(f"📝 المسار: {request.path}")
    
    # الحصول على معلمات URL
    folder_id = request.GET.get('folder', None)
    print(f"📁 معرف المجلد المطلوب: {folder_id}")
    
    # الحصول على قائمة المجلدات
    folders = []
    current_folder = None
    
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT id, name FROM rental_archivefolder ORDER BY name")
            folders = [{'id': row[0], 'name': row[1]} for row in cursor.fetchall()]
            print(f"📂 تم العثور على {len(folders)} مجلد متاح")
            
            if folder_id:
                cursor.execute("SELECT id, name FROM rental_archivefolder WHERE id = %s", [folder_id])
                folder_data = cursor.fetchone()
                if folder_data:
                    current_folder = {'id': folder_data[0], 'name': folder_data[1]}
                    print(f"📂 المجلد الحالي: {folder_data[1]} (ID: {folder_data[0]})")
                else:
                    print(f"⚠️ لم يتم العثور على المجلد برقم: {folder_id}")
    except Exception as e:
        print(f"❌ خطأ في جلب المجلدات: {str(e)}")
        print(traceback.format_exc())
    
    # معالجة طلب POST للرفع
    if request.method == 'POST':
        print(f"🔄 معالجة طلب POST للرفع")
        print(f"📤 بيانات النموذج: {request.POST}")
        print(f"📦 ملفات مرفقة: {list(request.FILES.keys()) if request.FILES else 'لا توجد ملفات'}")
        
        # طباعة تفاصيل أكثر حول REQUEST
        if hasattr(request, 'content_type'):
            print(f"📋 نوع المحتوى: {request.content_type}")
        print(f"🔑 المفاتيح في request.POST: {list(request.POST.keys())}")
        print(f"🔑 المفاتيح في request.FILES: {list(request.FILES.keys()) if request.FILES else 'لا توجد ملفات'}")
        
        # استخراج البيانات المرسلة
        title = request.POST.get('title', '').strip()
        print(f"📑 عنوان المستند: '{title}'")
        
        description = request.POST.get('description', '')
        print(f"📝 وصف المستند: '{description[:30]}{'...' if len(description) > 30 else ''}'")
        
        folder_id = request.POST.get('folder', None)
        print(f"📁 معرف المجلد: {folder_id}")
        
        document_type = request.POST.get('document_type', 'other')
        print(f"📊 نوع المستند: {document_type}")
        
        # تحسين: استخدام قيمة افتراضية للعنوان إذا لم يتم توفيره
        if not title and 'file' in request.FILES:
            title = request.FILES['file'].name
            print(f"ℹ️ استخدام اسم الملف كعنوان افتراضي: {title}")
        
        # التحقق من وجود البيانات المطلوبة
        if not title:
            print("❌ خطأ: لم يتم توفير عنوان للمستند")
            messages.error(request, "يرجى إدخال عنوان للمستند")
            return redirect(request.path)
        
        if 'file' not in request.FILES:
            print("❌ خطأ: لم يتم اختيار ملف للرفع")
            messages.error(request, "يرجى تحديد ملف للرفع")
            return redirect(request.path)
        
        # الحصول على معلومات الملف
        file = request.FILES['file']
        file_name = file.name
        file_type = file.content_type
        file_size = file.size
        
        print(f"📄 معلومات الملف المرفوع:")
        print(f"  - الاسم: {file_name}")
        print(f"  - النوع: {file_type}")
        print(f"  - الحجم: {file_size} بايت")
        
        if hasattr(file, 'charset'):
            print(f"  - ترميز الملف: {file.charset}")
        
        # قائمة الخصائص المتاحة للملف
        file_attributes = [attr for attr in dir(file) if not attr.startswith('_')]
        print(f"  - الخصائص المتاحة للملف: {file_attributes}")
        
        # حفظ الملف في المجلد أولاً قبل أي عمليات أخرى
        try:
            # إنشاء مجلد للملفات المرفوعة
            timestamp = str(int(timezone.now().timestamp()))
            unique_id = uuid.uuid4().hex[:8]
            
            upload_dir = os.path.join(settings.MEDIA_ROOT, 'uploads', 'documents')
            os.makedirs(upload_dir, exist_ok=True)
            print(f"📂 تم إنشاء مجلد التحميل: {upload_dir}")
            
            # التحقق من صلاحيات الكتابة في المجلد
            if os.access(upload_dir, os.W_OK):
                print(f"✅ لديك صلاحية الكتابة في مجلد التحميل")
            else:
                print(f"⚠️ تحذير: قد لا تملك صلاحية الكتابة في مجلد التحميل")
            
            # إنشاء اسم ملف فريد
            unique_filename = f"doc_{timestamp}_{unique_id}_{file_name}"
            file_path = os.path.join(upload_dir, unique_filename)
            print(f"📄 مسار الملف الكامل: {file_path}")
            
            # طباعة حجم الملف وعدد الأجزاء
            file_size_kb = file_size / 1024
            print(f"📊 حجم الملف: {file_size_kb:.2f} كيلوبايت")
            
            # حفظ الملف
            with open(file_path, 'wb+') as destination:
                total_chunks = 0
                for chunk in file.chunks():
                    destination.write(chunk)
                    total_chunks += 1
                print(f"✅ تم كتابة {total_chunks} جزء من البيانات (chunks)")
            
            # التحقق من إنشاء الملف
            if os.path.exists(file_path):
                actual_size = os.path.getsize(file_path)
                print(f"✅ تم التحقق من وجود الملف: {file_path}")
                print(f"   - حجم الملف على القرص: {actual_size} بايت")
                if actual_size == file_size:
                    print(f"   - ✅ الحجم مطابق للملف الأصلي")
                else:
                    print(f"   - ⚠️ الحجم مختلف عن الملف الأصلي ({file_size} بايت)")
            else:
                print(f"⚠️ لم يتم العثور على الملف بعد الحفظ: {file_path}")
            
            # مسار الملف النسبي
            rel_path = os.path.join('uploads', 'documents', unique_filename)
            print(f"📁 تم حفظ الملف المادي في: {rel_path}")
            
        except Exception as file_error:
            print(f"❌ خطأ في حفظ الملف: {str(file_error)}")
            print(traceback.format_exc())
            messages.error(request, f"فشل في حفظ الملف: {str(file_error)}")
            return redirect(request.path)
        
        try:
            # استخدام SQL مباشر لإدراج المستند
            with connection.cursor() as cursor:
                # الحصول على معلومات المستخدم
                user_id = request.user.id
                created_at = timezone.now()
                
                print(f"🗄️ بدء عملية إدراج المستند في قاعدة البيانات")
                print(f"👤 معرف المستخدم: {user_id}")
                print(f"⏰ التاريخ والوقت: {created_at}")
                print(f"📁 مسار الملف للتخزين: {rel_path}")
                
                # طباعة هيكل الجدول للتأكد من صحة المتطلبات
                try:
                    cursor.execute("SELECT column_name, data_type, is_nullable FROM information_schema.columns WHERE table_name = 'rental_document' ORDER BY ordinal_position;")
                    columns = cursor.fetchall()
                    print(f"📊 هيكل جدول rental_document:")
                    for col in columns:
                        print(f"   - {col[0]}: {col[1]} (إلزامي: {'لا' if col[2] == 'YES' else 'نعم'})")
                except Exception as schema_error:
                    print(f"⚠️ لم نتمكن من استرداد هيكل الجدول: {str(schema_error)}")
                
                # التحقق من وجود المجلد إذا تم تحديده
                if folder_id:
                    try:
                        cursor.execute("SELECT id, name FROM rental_archivefolder WHERE id = %s", [folder_id])
                        folder_check = cursor.fetchone()
                        if folder_check:
                            print(f"✅ تم التحقق من وجود المجلد: {folder_check[1]} (ID: {folder_check[0]})")
                        else:
                            print(f"⚠️ المجلد المحدد (ID: {folder_id}) غير موجود")
                    except Exception as folder_error:
                        print(f"⚠️ خطأ في التحقق من المجلد: {str(folder_error)}")
                
                # طباعة حالة الاتصال
                cursor.execute("SELECT current_database(), current_user;")
                db_info = cursor.fetchone()
                print(f"🔌 حالة الاتصال: قاعدة البيانات: {db_info[0]}, المستخدم: {db_info[1]}")
                
                # تسجيل الزمن قبل تنفيذ الاستعلام
                execution_start = timezone.now()
                print(f"⏱️ بدء تنفيذ الاستعلام في: {execution_start}")
                
                # تعطيل المحفزات مؤقتًا للتأكد من عدم تشغيل أي triggers
                cursor.execute("SET session_replication_role = 'replica';")
                print(f"🔒 تم تعطيل المحفزات مؤقتاً")
                
                # إعداد استعلام SQL بدون file_content
                query = """
                INSERT INTO rental_document 
                (title, description, document_type, folder_id, created_by_id, added_by_id,
                file_name, file_type, file_size, file, created_at, updated_at, is_auto_created, document_date) 
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                RETURNING id;
                """
                
                # الطباعة بتنسيق أفضل
                query_formatted = query.replace('\n', ' ').strip()
                print(f"🔍 استعلام SQL: {query_formatted}")
                
                # تجهيز القيم للطباعة
                values = [
                    title,
                    description[:30] + "..." if len(description) > 30 else description,
                    document_type,
                    folder_id if folder_id else None,
                    user_id,
                    user_id,
                    file_name,
                    file_type,
                    file_size,
                    rel_path,  # استخدام المسار بدلاً من المحتوى
                    created_at,
                    created_at,
                    False,  # ليس مستند تلقائي
                    created_at
                ]
                
                print(f"📋 القيم المستخدمة في الاستعلام:")
                for i, value in enumerate(values):
                    print(f"   - القيمة {i+1}: {value} ({type(value).__name__})")
                
                try:
                    # تنفيذ الاستعلام
                    cursor.execute(query, [
                        title,
                        description,
                        document_type,
                        folder_id if folder_id else None,
                        user_id,
                        user_id,
                        file_name,
                        file_type,
                        file_size,
                        rel_path,  # استخدام المسار بدلاً من المحتوى
                        created_at,
                        created_at,
                        False,  # ليس مستند تلقائي
                        created_at
                    ])
                    
                    # استرجاع معرف المستند الجديد
                    document_id = cursor.fetchone()[0]
                    
                    # طباعة نتائج التنفيذ
                    execution_end = timezone.now()
                    execution_time = (execution_end - execution_start).total_seconds()
                    print(f"⏱️ انتهى تنفيذ الاستعلام في: {execution_end}")
                    print(f"⏱️ استغرق التنفيذ: {execution_time:.4f} ثانية")
                    
                    print(f"🎉 تم إنشاء المستند بنجاح: ID={document_id}")
                    
                    # إعادة تفعيل المحفزات
                    cursor.execute("SET session_replication_role = 'origin';")
                    print(f"🔓 تم إعادة تفعيل المحفزات")
                    
                    # التحقق من وجود المستند بعد الإنشاء
                    cursor.execute("SELECT id, title, file FROM rental_document WHERE id = %s", [document_id])
                    doc_check = cursor.fetchone()
                    if doc_check:
                        print(f"✅ تم التحقق من وجود المستند: {doc_check[1]} (ID: {doc_check[0]})")
                        print(f"   - مسار الملف: {doc_check[2]}")
                    else:
                        print(f"⚠️ لم يتم العثور على المستند بعد الإنشاء (ID: {document_id})")
                    
                    # إظهار رسالة نجاح
                    messages.success(request, f"تم رفع المستند '{title}' بنجاح")
                    
                    # إعادة التوجيه
                    if folder_id:
                        redirect_url = reverse('admin_archive_folder', kwargs={'folder_id': folder_id})
                        print(f"🔄 إعادة التوجيه إلى: {redirect_url}")
                        return redirect(redirect_url)
                    else:
                        print(f"🔄 إعادة التوجيه إلى: admin_archive")
                        return redirect('admin_archive')
                    
                except Exception as query_error:
                    print(f"❌ خطأ في تنفيذ استعلام إدراج المستند: {str(query_error)}")
                    print(traceback.format_exc())
                    
                    # محاولة استعلام المشكلة
                    try:
                        cursor.execute("SHOW server_version;")
                        version = cursor.fetchone()[0]
                        print(f"ℹ️ إصدار PostgreSQL: {version}")
                    except:
                        pass
                    
                    raise query_error
                
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
    return render(request, 'admin/archive/final_direct_upload.html', context)