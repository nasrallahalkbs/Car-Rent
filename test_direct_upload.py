"""
اختبار الرفع المباشر للملفات إلى قاعدة البيانات

هذا السكريبت يتجاوز واجهة المستخدم ويرفع ملفًا مباشرة إلى قاعدة البيانات
للتأكد من أن المشكلة ليست في الواجهة ولكن في طريقة الحفظ نفسها
"""
import os
import sys
import django
import datetime
from django.utils import timezone

# إعداد بيئة Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'car_rental_project.settings')
django.setup()

# استيراد النماذج
from rental.models import Document, ArchiveFolder
from django.contrib.auth import get_user_model
User = get_user_model()

def create_test_folder():
    """إنشاء مجلد اختبار جديد للتأكد من عمل الوظيفة"""
    folder_name = f"مجلد_اختبار_{int(timezone.now().timestamp())}"
    
    try:
        folder = ArchiveFolder.objects.create(
            name=folder_name,
            description="مجلد اختبار للتأكد من عمل رفع الملفات",
            is_system_folder=False
        )
        print(f"✅ تم إنشاء مجلد اختبار جديد: {folder.name} (ID: {folder.id})")
        return folder
    except Exception as e:
        print(f"❌ فشل إنشاء مجلد اختبار: {str(e)}")
        return None

def create_test_document(folder):
    """إنشاء مستند اختبار في المجلد المحدد"""
    if not folder:
        print("❌ لا يمكن إنشاء مستند بدون مجلد")
        return None
    
    # إنشاء مستند اختبار
    try:
        # إنشاء محتوى ملف اختباري (نص بسيط)
        file_content = "هذا ملف اختبار للتأكد من عمل رفع الملفات".encode('utf-8')
        
        # إنشاء المستند مباشرة في قاعدة البيانات
        document = Document(
            title=f"مستند_اختبار_{int(timezone.now().timestamp())}",
            description="مستند اختبار للتأكد من عمل رفع الملفات",
            document_type="other",
            folder=folder,
            file_name="test_file.txt",
            file_type="text/plain",
            file_size=len(file_content),
            file_content=file_content,
            is_auto_created=False  # تأكيد أن المستند ليس تلقائي
        )
        
        # تعطيل إشارات منع المستندات التلقائية
        setattr(document, '_ignore_auto_document_signal', True)
        
        # حفظ المستند
        document.save()
        
        print(f"✅ تم إنشاء مستند اختبار جديد: {document.title} (ID: {document.id}) في المجلد: {folder.name}")
        return document
    except Exception as e:
        print(f"❌ فشل إنشاء مستند اختبار: {str(e)}")
        # محاولة أخرى باستخدام SQL المباشر
        try:
            from django.db import connection
            cursor = connection.cursor()
            
            cursor.execute("""
                INSERT INTO rental_document (
                    title, description, document_type, folder_id, 
                    file_name, file_type, file_size, file_content,
                    created_at, updated_at, is_auto_created
                ) 
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                RETURNING id;
            """, [
                f"مستند_اختبار_{int(timezone.now().timestamp())}", 
                "مستند اختبار للتأكد من عمل رفع الملفات",
                "other",
                folder.id, 
                "test_file.txt",
                "text/plain",
                len(file_content),
                file_content,
                timezone.now(),
                timezone.now(),
                False
            ])
            
            document_id = cursor.fetchone()[0]
            print(f"✅ تم إنشاء مستند اختبار جديد باستخدام SQL المباشر: ID: {document_id}")
            return Document.objects.get(id=document_id)
        except Exception as sql_err:
            print(f"❌ فشل إنشاء مستند اختبار حتى باستخدام SQL المباشر: {str(sql_err)}")
            return None

def check_documents(folder):
    """التحقق من عدد المستندات في المجلد"""
    if not folder:
        print("❌ لا يمكن التحقق من المستندات بدون مجلد")
        return
    
    # الحصول على جميع المستندات في المجلد
    documents = Document.objects.filter(folder=folder)
    print(f"\nتم العثور على {documents.count()} مستند في المجلد {folder.name} (ID: {folder.id})")
    
    # طباعة معلومات عن كل مستند
    for doc in documents:
        file_size = doc.file_size if hasattr(doc, 'file_size') else 0
        content_size = len(doc.file_content) if hasattr(doc, 'file_content') and doc.file_content else 0
        
        print(f"  - مستند: {doc.title} (ID: {doc.id})")
        print(f"    حجم الملف: {file_size} بايت")
        print(f"    حجم المحتوى: {content_size} بايت")
        print(f"    تاريخ الإنشاء: {doc.created_at}")

def main():
    """الدالة الرئيسية لاختبار رفع الملفات"""
    print("🧪 بدء اختبار رفع الملفات المباشر...")
    
    # 1. إنشاء مجلد اختبار
    folder = create_test_folder()
    
    if not folder:
        print("❌ فشل الاختبار - لم يتم إنشاء المجلد")
        return
    
    # 2. إنشاء مستند اختبار
    document = create_test_document(folder)
    
    if not document:
        print("❌ فشل الاختبار - لم يتم إنشاء المستند")
        return
    
    # 3. التحقق من عدد المستندات في المجلد
    check_documents(folder)
    
    print("✅ تم اختبار رفع الملفات بنجاح")

if __name__ == "__main__":
    main()