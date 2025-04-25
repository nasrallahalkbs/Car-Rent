"""
حل نهائي لإنشاء ورفع مستند باستخدام Django مباشرة
"""
import os
import sys
import django
from django.utils import timezone

# إعداد بيئة Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'car_rental_project.settings')
django.setup()

# استيراد النماذج
from rental.models import ArchiveFolder, Document

def create_test_document():
    """إنشاء مستند اختباري للتأكد من عمل العرض"""
    # إنشاء مجلد اختبار جديد
    folder_name = f"مجلد_اختبار_{int(timezone.now().timestamp())}"
    
    try:
        folder = ArchiveFolder.objects.create(
            name=folder_name,
            description="مجلد اختبار للحل النهائي",
            is_system_folder=False
        )
        print(f"✅ تم إنشاء مجلد اختبار جديد: {folder.name} (ID: {folder.id})")
        
        # إنشاء محتوى الملف
        file_content = "هذا محتوى ملف اختباري للحل النهائي".encode('utf-8')
        
        # إنشاء المستند
        document_title = f"مستند_اختبار_{int(timezone.now().timestamp())}"
        
        # محاولة إنشاء المستند باستخدام Django ORM
        try:
            # إنشاء المستند باستخدام Django ORM
            document = Document(
                title=document_title,
                description="مستند اختبار للحل النهائي",
                document_type="other",
                folder=folder,
                file_name="test_file.txt",
                file_type="text/plain",
                file_size=len(file_content),
                file_content=file_content,
                is_auto_created=False
            )
            
            # إيقاف إشارات منع المستندات التلقائية مؤقتًا
            setattr(document, '_ignore_auto_document_signal', True)
            
            # تخزين المستند
            document.save()
            
            print(f"✅ تم إنشاء المستند باستخدام Django ORM: {document.title} (ID: {document.id})")
            
            # اختبار استرجاع المستند
            loaded_document = Document.objects.get(id=document.id)
            
            print(f"✅ تم استرجاع المستند: {loaded_document.title}")
            print(f"  - حجم الملف: {loaded_document.file_size} بايت")
            print(f"  - حجم المحتوى: {len(loaded_document.file_content)} بايت")
            
            # الحصول على جميع المستندات في المجلد والتأكد من وجود المستند الجديد
            folder_documents = Document.objects.filter(folder=folder)
            print(f"✅ عدد المستندات في المجلد: {folder_documents.count()}")
            
            for doc in folder_documents:
                print(f"  - مستند: {doc.title} (ID: {doc.id})")
                
            return folder, document
        except Exception as e:
            print(f"❌ فشل إنشاء المستند باستخدام Django ORM: {str(e)}")
            
            # محاولة إنشاء المستند باستخدام SQL المباشر
            try:
                from django.db import connection
                cursor = connection.cursor()
                
                # التحقق من وجود حقل is_auto_created
                cursor.execute("SELECT column_name FROM information_schema.columns WHERE table_name = 'rental_document' AND column_name = 'is_auto_created';")
                is_auto_created_exists = cursor.fetchone() is not None
                
                print(f"حقل is_auto_created {'موجود' if is_auto_created_exists else 'غير موجود'} في جدول المستندات")
                
                if is_auto_created_exists:
                    query = """
                        INSERT INTO rental_document (
                            title, description, document_type, folder_id, 
                            file_name, file_type, file_size, file_content,
                            created_at, updated_at, is_auto_created
                        ) 
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, NOW(), NOW(), %s)
                        RETURNING id;
                    """
                    cursor.execute(query, [
                        document_title, 
                        "مستند اختبار تم إنشاؤه باستخدام SQL المباشر",
                        "other",
                        folder.id, 
                        "test_file.txt",
                        "text/plain",
                        len(file_content),
                        file_content,
                        False
                    ])
                else:
                    query = """
                        INSERT INTO rental_document (
                            title, description, document_type, folder_id, 
                            file_name, file_type, file_size, file_content,
                            created_at, updated_at
                        ) 
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, NOW(), NOW())
                        RETURNING id;
                    """
                    cursor.execute(query, [
                        document_title, 
                        "مستند اختبار تم إنشاؤه باستخدام SQL المباشر",
                        "other",
                        folder.id, 
                        "test_file.txt",
                        "text/plain",
                        len(file_content),
                        file_content
                    ])
                
                document_id = cursor.fetchone()[0]
                connection.commit()
                
                print(f"✅ تم إنشاء المستند باستخدام SQL المباشر: ID: {document_id}")
                
                # استرجاع المستند
                loaded_document = Document.objects.get(id=document_id)
                
                print(f"✅ تم استرجاع المستند: {loaded_document.title}")
                print(f"  - حجم الملف: {loaded_document.file_size} بايت")
                print(f"  - حجم المحتوى: {len(loaded_document.file_content)} بايت")
                
                # الحصول على جميع المستندات في المجلد والتأكد من وجود المستند الجديد
                folder_documents = Document.objects.filter(folder=folder)
                print(f"✅ عدد المستندات في المجلد: {folder_documents.count()}")
                
                for doc in folder_documents:
                    print(f"  - مستند: {doc.title} (ID: {doc.id})")
                    
                return folder, loaded_document
            except Exception as sql_error:
                print(f"❌ فشل إنشاء المستند باستخدام SQL المباشر: {str(sql_error)}")
                return folder, None
    except Exception as e:
        print(f"❌ فشل إنشاء مجلد الاختبار: {str(e)}")
        return None, None

def fix_document_display_in_windows_explorer():
    """إصلاح طريقة عرض المستندات في قالب windows_explorer_enhanced.html"""
    template_path = 'templates/admin/archive/windows_explorer_enhanced.html'
    
    try:
        # قراءة محتوى القالب
        with open(template_path, 'r', encoding='utf-8') as file:
            content = file.read()
        
        # البحث عن جزء عرض المستندات
        documents_pattern = """{% for document in documents %}
                    <div class="file-box">
                        <div class="file" onclick="showDocumentDetails('{{ document.id }}', '{{ document.title }}')">
                            <a>
                                <span class="corner"></span>
                                <div class="icon">
                                    <i class="fa fa-file"></i>
                                </div>
                                <div class="file-name">
                                    {{ document.title }}
                                    <br>
                                    <small>{{ document.created_at|date:"Y-m-d H:i" }}</small>
                                </div>
                            </a>
                        </div>
                    </div>
                {% empty %}"""
        
        # البحث عن الجزء في محتوى القالب
        if documents_pattern in content:
            # عرض معلومات تشخيصية
            print("✅ تم العثور على جزء عرض المستندات في القالب")
            print("محتوى القالب يبدو صحيحًا")
        else:
            print("❌ لم يتم العثور على جزء عرض المستندات في القالب")
            print("قد يكون هناك خطأ في القالب")
        
        # التحقق من متغير files
        if "{% for document in files %}" in content:
            print("⚠️ يستخدم القالب متغير 'files' بدلاً من 'documents'")
            
            # إذا كان القالب يستخدم متغير 'files'، نتأكد من أن دالة admin_archive تقوم بتعيين متغير 'files'
            admin_views_path = 'rental/admin_views.py'
            
            with open(admin_views_path, 'r', encoding='utf-8') as file:
                admin_views_content = file.read()
            
            if "'files': documents," in admin_views_content:
                print("✅ يتم تعيين متغير 'files' في سياق القالب")
            else:
                print("❌ لا يتم تعيين متغير 'files' في سياق القالب")
                
                # إضافة متغير 'files' إلى سياق القالب
                context_pattern = "    context = {\n        'current_folder': current_folder,\n        'folders': subfolders,\n        'documents': documents,"
                new_context = "    context = {\n        'current_folder': current_folder,\n        'folders': subfolders,\n        'documents': documents,\n        'files': documents,"
                
                modified_content = admin_views_content.replace(context_pattern, new_context)
                
                if modified_content != admin_views_content:
                    with open(admin_views_path, 'w', encoding='utf-8') as file:
                        file.write(modified_content)
                    print("✅ تم إضافة متغير 'files' إلى سياق القالب بنجاح")
                else:
                    print("❌ فشل إضافة متغير 'files' إلى سياق القالب")
    except Exception as e:
        print(f"❌ حدث خطأ أثناء إصلاح طريقة عرض المستندات: {str(e)}")

if __name__ == "__main__":
    print("🛠️ بدء تنفيذ الحل النهائي لمشكلة رفع وعرض المستندات...")
    
    # إصلاح طريقة عرض المستندات
    fix_document_display_in_windows_explorer()
    
    # إنشاء مستند اختباري
    folder, document = create_test_document()
    
    if folder and document:
        print(f"\n✅ تم تنفيذ الحل النهائي بنجاح!")
        print(f"الآن يجب أن تظهر المستندات في المجلد {folder.name} (ID: {folder.id})")
        print(f"يرجى زيارة الرابط التالي للتحقق: /ar/dashboard/archive/?folder={folder.id}")
    else:
        print("\n❌ فشل تنفيذ الحل النهائي")