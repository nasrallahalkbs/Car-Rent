"""
تنظيف المستندات الفارغة من قاعدة البيانات
"""
import os
import sys
import django

# إعداد بيئة Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'car_rental_project.settings')
django.setup()

# استيراد النماذج
from rental.models import Document, ArchiveFolder

def clean_empty_documents():
    """حذف المستندات الفارغة من قاعدة البيانات"""
    # المستندات التي لا تحتوي على محتوى ملف
    empty_content_docs = Document.objects.filter(file_content__isnull=True)
    print(f"عدد المستندات بدون محتوى ملف: {empty_content_docs.count()}")
    
    # المستندات التي لها محتوى فارغ (0 بايت)
    zero_size_docs = Document.objects.filter(file_size=0)
    print(f"عدد المستندات بحجم 0 بايت: {zero_size_docs.count()}")
    
    # طباعة معلومات عن المستندات الفارغة
    for doc in empty_content_docs:
        print(f"مستند فارغ ID={doc.id}, العنوان={doc.title}, المجلد={doc.folder.name if doc.folder else 'لا يوجد'}")
    
    # طباعة معلومات عن المستندات بحجم 0 بايت
    for doc in zero_size_docs:
        print(f"مستند بحجم 0 بايت ID={doc.id}, العنوان={doc.title}, المجلد={doc.folder.name if doc.folder else 'لا يوجد'}")
    
    # حذف المستندات الفارغة تلقائيًا
    print("\nجاري حذف المستندات الفارغة...")
    empty_content_docs.delete()
    zero_size_docs.delete()
    print("✅ تم حذف المستندات الفارغة بنجاح")

if __name__ == "__main__":
    clean_empty_documents()