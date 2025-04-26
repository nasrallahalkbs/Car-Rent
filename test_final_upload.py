"""
اختبار نهائي لرفع المستند مباشرة إلى قاعدة البيانات
"""
import os
import sys
import django

# إعداد بيئة Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'car_rental_project.settings')
django.setup()

# استدعاء النماذج
from rental.models import ArchiveFolder, Document, User
from django.core.files.uploadedfile import SimpleUploadedFile
from django.utils import timezone

def create_test_folder():
    """إنشاء مجلد اختبار جديد"""
    # البحث عن مستخدم إداري
    admin_user = User.objects.filter(is_staff=True).first()
    if not admin_user:
        print("No admin user found")
        return None
    
    folder_name = f"Test Final Folder {timezone.now().strftime('%Y-%m-%d %H:%M:%S')}"
    
    # إنشاء المجلد
    folder = ArchiveFolder(
        name=folder_name,
        description="Folder for final upload test",
        created_by=admin_user
    )
    
    # تعيين الخصائص بعد الإنشاء
    setattr(folder, '_prevent_auto_docs', True)
    
    folder.save()
    print(f"Created test folder: {folder.name} (ID: {folder.id})")
    return folder

def create_test_document(folder):
    """إنشاء مستند اختبار في المجلد المحدد"""
    if not folder:
        print("No folder specified")
        return None
    
    # البحث عن مستخدم إداري
    admin_user = User.objects.filter(is_staff=True).first()
    if not admin_user:
        print("No admin user found")
        return None
    
    document_title = f"Final Test Document {timezone.now().strftime('%Y-%m-%d %H:%M:%S')}"
    
    # إنشاء ملف اختبار بسيط
    file_content = b"This is a test file content for final test"
    uploaded_file = SimpleUploadedFile("test_file_final.txt", file_content, content_type="text/plain")
    
    # إنشاء المستند
    document = Document(
        title=document_title,
        description="Document for final upload test",
        document_type="other",
        folder=folder,
        added_by=admin_user,
        file=uploaded_file,
        is_auto_created=False
    )
    
    # تعطيل إشارات منع المستندات التلقائية بشكل صريح
    setattr(document, '_ignore_auto_document_signal', True)
    
    # حفظ المستند
    document.save()
    
    print(f"Created test document: {document.title} (ID: {document.id})")
    print(f"   - Folder: {folder.name} (ID: {folder.id})")
    print(f"   - File content size: {len(file_content)} bytes")
    
    # التأكد من حفظ محتوى الملف في قاعدة البيانات
    if document.file_content:
        print(f"   - File content saved in database: {len(document.file_content)} bytes")
    else:
        print("   - File content NOT saved in database")
    
    return document

def check_documents(folder):
    """التحقق من عدد المستندات في المجلد"""
    if not folder:
        print("No folder specified")
        return
    
    documents = Document.objects.filter(folder=folder)
    print(f"Documents in folder '{folder.name}': {documents.count()}")
    
    for idx, doc in enumerate(documents):
        has_file_content = hasattr(doc, 'file_content') and doc.file_content is not None
        has_file = hasattr(doc, 'file') and doc.file is not None
        
        print(f"   {idx+1}. ID: {doc.id}, Title: {doc.title}")
        print(f"      - file_content: {'exists' if has_file_content else 'not exists'}")
        print(f"      - file: {'exists' if has_file else 'not exists'}")
        print(f"      - file_name: {doc.file_name if hasattr(doc, 'file_name') else 'not exists'}")
        print(f"      - file_type: {doc.file_type if hasattr(doc, 'file_type') else 'not exists'}")

def main():
    """الدالة الرئيسية لاختبار رفع المستندات"""
    print("\n=== STARTING FINAL UPLOAD TEST ===\n")
    
    # إنشاء مجلد اختبار جديد
    folder = create_test_folder()
    
    # التحقق من المجلد قبل إنشاء المستند
    check_documents(folder)
    
    # إنشاء مستند اختبار
    document = create_test_document(folder)
    
    # التحقق من المستندات في المجلد بعد إنشاء المستند
    print("\n=== UPLOAD TEST RESULTS ===\n")
    check_documents(folder)
    
    # التأكد من حفظ المستند بنجاح
    if document and document.pk:
        print("\nDOCUMENT UPLOAD SUCCESSFUL")
    else:
        print("\nDOCUMENT UPLOAD FAILED")
    
    print("\n=== FINAL UPLOAD TEST COMPLETED ===\n")

if __name__ == "__main__":
    main()
