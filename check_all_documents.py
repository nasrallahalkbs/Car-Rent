"""
التحقق من جميع المستندات في جميع المجلدات
"""
import os
import sys
import django

# إعداد بيئة Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'car_rental_project.settings')
django.setup()

# استيراد النماذج
from rental.models import Document, ArchiveFolder

def check_all_documents():
    """فحص جميع المستندات في جميع المجلدات"""
    # الحصول على جميع المجلدات
    all_folders = ArchiveFolder.objects.all()
    print(f"عدد المجلدات: {all_folders.count()}")
    
    # الحصول على جميع المستندات
    all_documents = Document.objects.all()
    print(f"عدد المستندات: {all_documents.count()}")
    
    # فحص المستندات في كل مجلد
    for folder in all_folders:
        folder_documents = Document.objects.filter(folder=folder)
        print(f"\nمجلد: {folder.name} (ID: {folder.id})")
        print(f"  عدد المستندات: {folder_documents.count()}")
        
        # طباعة معلومات عن كل مستند
        for doc in folder_documents:
            file_size = doc.file_size if hasattr(doc, 'file_size') else 0
            content_size = len(doc.file_content) if hasattr(doc, 'file_content') and doc.file_content else 0
            has_file = hasattr(doc, 'file') and bool(doc.file)
            
            print(f"  - مستند: {doc.title} (ID: {doc.id})")
            print(f"    حجم الملف: {file_size} بايت")
            print(f"    حجم المحتوى: {content_size} بايت")
            print(f"    له ملف: {'نعم' if has_file else 'لا'}")

if __name__ == "__main__":
    check_all_documents()