"""
التحقق من مستندات المجلد 92
"""
import os
import django

# إعداد بيئة Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'car_rental_project.settings')
django.setup()

from rental.models import ArchiveFolder, Document

def check_folder_92():
    try:
        folder = ArchiveFolder.objects.get(id=92)
        print(f'المجلد: {folder.name}, عدد المستندات: {folder.documents.count()}')
        
        for doc in folder.documents.all():
            print(f' - مستند: {doc.id} | {doc.title or "بدون عنوان"}')
    except ArchiveFolder.DoesNotExist:
        print("لا يوجد مجلد بالمعرف 92")

if __name__ == "__main__":
    check_folder_92()