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
from rental.models import ArchiveFolder, Document
from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from django.utils import timezone

def create_test_folder():
    """إنشاء مجلد اختبار جديد"""
    # البحث عن مستخدم إداري
    admin_user = User.objects.filter(is_staff=True).first()
    if not admin_user:
        print("❌ لم يتم العثور على مستخدم إداري")
        return None
    
    folder_name = f"مجلد اختبار النهائي {timezone.now().strftime('%Y-%m-%d %H:%M:%S')}"
    
    # إنشاء المجلد
    folder = ArchiveFolder(
        name=folder_name,
        description="مجلد لاختبار رفع المستندات النهائي",
        created_by=admin_user,
        disable_auto_documents=True,
        _prevent_auto_docs=True,
        _skip_auto_document_creation=True
    )
    
    folder.save()
    print(f"✅ تم إنشاء مجلد اختبار جديد: {folder.name} (ID: {folder.id})")
    return folder

def create_test_document(folder):
    """إنشاء مستند اختبار في المجلد المحدد"""
    if not folder:
        print("❌ لم يتم تحديد مجلد")
        return None
    
    # البحث عن مستخدم إداري
    admin_user = User.objects.filter(is_staff=True).first()
    if not admin_user:
        print("❌ لم يتم العثور على مستخدم إداري")
        return None
    
    document_title = f"مستند اختبار نهائي {timezone.now().strftime('%Y-%m-%d %H:%M:%S')}"
    
    # إنشاء ملف اختبار بسيط
    file_content = b"هذا محتوى ملف اختبار نهائي"
    uploaded_file = SimpleUploadedFile("test_file_final.txt", file_content, content_type="text/plain")
    
    # إنشاء المستند
    document = Document(
        title=document_title,
        description="مستند لاختبار الرفع النهائي",
        document_type="other",
        folder=folder,
        created_by=admin_user,
        file=uploaded_file,
        is_auto_created=False
    )
    
    # تعطيل إشارات منع المستندات التلقائية بشكل صريح
    setattr(document, '_ignore_auto_document_signal', True)
    
    # حفظ المستند
    document.save()
    
    print(f"✅ تم إنشاء مستند اختبار جديد: {document.title} (ID: {document.id})")
    print(f"   - المجلد: {folder.name} (ID: {folder.id})")
    print(f"   - حجم محتوى الملف: {len(file_content)} بايت")
    
    # التأكد من حفظ محتوى الملف في قاعدة البيانات
    if document.file_content:
        print(f"   - تم حفظ محتوى الملف في قاعدة البيانات: {len(document.file_content)} بايت")
    else:
        print("   - ❌ لم يتم حفظ محتوى الملف في قاعدة البيانات")
    
    return document

def check_documents(folder):
    """التحقق من عدد المستندات في المجلد"""
    if not folder:
        print("❌ لم يتم تحديد مجلد")
        return
    
    documents = Document.objects.filter(folder=folder)
    print(f"📊 عدد المستندات في المجلد '{folder.name}': {documents.count()}")
    
    for idx, doc in enumerate(documents):
        has_file_content = hasattr(doc, 'file_content') and doc.file_content is not None
        has_file = hasattr(doc, 'file') and doc.file is not None
        
        print(f"   {idx+1}. معرف: {doc.id}, العنوان: {doc.title}")
        print(f"      - file_content: {'موجود' if has_file_content else 'غير موجود'}")
        print(f"      - file: {'موجود' if has_file else 'غير موجود'}")
        print(f"      - file_name: {doc.file_name if hasattr(doc, 'file_name') else 'غير موجود'}")
        print(f"      - file_type: {doc.file_type if hasattr(doc, 'file_type') else 'غير موجود'}")

def main():
    """الدالة الرئيسية لاختبار رفع المستندات"""
    print("\n=== بدء اختبار رفع المستندات النهائي ===\n")
    
    # إنشاء مجلد اختبار جديد
    folder = create_test_folder()
    
    # التحقق من المجلد قبل إنشاء المستند
    check_documents(folder)
    
    # إنشاء مستند اختبار
    document = create_test_document(folder)
    
    # التحقق من المستندات في المجلد بعد إنشاء المستند
    print("\n=== نتائج اختبار رفع المستندات ===\n")
    check_documents(folder)
    
    # التأكد من حفظ المستند بنجاح
    if document and document.pk:
        print("\n✅ تم رفع المستند بنجاح وتخزينه في قاعدة البيانات")
    else:
        print("\n❌ فشل رفع المستند")
    
    print("\n=== اكتمل اختبار رفع المستندات ===\n")

if __name__ == "__main__":
    main()
