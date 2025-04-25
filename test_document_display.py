"""
اختبار عرض المستندات المرتبطة بمجلد معين
"""
import os
import sys
import django

# إعداد بيئة Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'car_rental_project.settings')
django.setup()

# استيراد النماذج
from rental.models import Document, ArchiveFolder

def test_folder_documents():
    """اختبار استرجاع المستندات المرتبطة بمجلد معين"""
    # عرض قائمة بالمجلدات التي لديها مستندات
    folder_docs = Document.objects.exclude(folder__isnull=True).values_list('folder_id', flat=True).distinct()
    
    print(f"المجلدات التي تحتوي على مستندات: {list(folder_docs)}")
    
    # التحقق من المستندات الموجودة في كل مجلد
    for folder_id in folder_docs:
        folder = ArchiveFolder.objects.get(id=folder_id)
        docs = Document.objects.filter(folder_id=folder_id)
        
        print(f"\nمجلد: {folder.name} (ID: {folder_id})")
        for doc in docs:
            print(f"  - مستند: {doc.title} (ID: {doc.id})")
    
    # التحقق من طريقة استرجاع المستندات في وظيفة عرض الأرشيف
    print("\nالتحقق من طريقة استرجاع المستندات من مجلد محدد...")
    for folder_id in folder_docs:
        folder = ArchiveFolder.objects.get(id=folder_id)
        
        # هذا هو الكود المستخدم في windows_explorer_view.py
        docs_from_model = Document.objects.filter(folder=folder).order_by('-created_at')
        
        print(f"\nمجلد: {folder.name} (ID: {folder_id})")
        print(f"عدد المستندات من استعلام المجلد: {docs_from_model.count()}")
        for doc in docs_from_model:
            print(f"  - مستند: {doc.title} (ID: {doc.id}, حجم: {doc.file_size} بايت)")

if __name__ == "__main__":
    test_folder_documents()