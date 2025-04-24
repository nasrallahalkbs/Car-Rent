"""
التحقق من معلومات المجلد رقم 85 وكيفية إنشاء المستندات التلقائية
"""

import os
import sys
import django

# إعداد بيئة Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'car_rental_project.settings')
django.setup()

from rental.models import ArchiveFolder, Document
from django.db import connection

def check_auto_documents():
    """
    التحقق من المستندات التلقائية للمجلد 85
    """
    try:
        # البحث عن المجلد رقم 85
        folder = ArchiveFolder.objects.filter(id=85).first()
        
        if folder:
            print(f"\n==== معلومات المجلد {folder.id} ====")
            print(f"الاسم: {folder.name}")
            print(f"الوصف: {folder.description}")
            print(f"المجلد الأب: {folder.parent.name if folder.parent else 'بدون مجلد أب'}")
            print(f"تاريخ الإنشاء: {folder.created_at}")
            
            # التحقق من خاصية disable_auto_documents
            has_disable_flag = hasattr(folder, 'disable_auto_documents')
            print(f"يحتوي على علامة disable_auto_documents: {has_disable_flag}")
            if has_disable_flag:
                print(f"قيمة disable_auto_documents: {folder.disable_auto_documents}")
            
            # البحث عن المستندات المرتبطة بهذا المجلد
            documents = Document.objects.filter(folder=folder)
            print(f"\n==== المستندات في المجلد (العدد: {documents.count()}) ====")
            for doc in documents:
                print(f" - {doc.id}: {doc.title} (تاريخ الإنشاء: {doc.created_at})")
            
            # البحث عن المستندات التلقائية (بدون عنوان)
            auto_docs = Document.objects.filter(folder=folder, title__in=['', 'بدون عنوان', None])
            print(f"\n==== المستندات التلقائية (العدد: {auto_docs.count()}) ====")
            for doc in auto_docs:
                print(f" - {doc.id}: '{doc.title}' (تاريخ الإنشاء: {doc.created_at})")
        else:
            print(f"المجلد رقم 85 غير موجود!")
        
        # البحث عن جميع الأعمدة في جدول المجلدات
        print("\n==== هيكل جدول المجلدات ====")
        cursor = connection.cursor()
        cursor.execute("PRAGMA table_info(rental_archivefolder);")
        columns = cursor.fetchall()
        for col in columns:
            print(f" - {col}")
    
    except Exception as e:
        print(f"حدث خطأ: {str(e)}")

if __name__ == "__main__":
    check_auto_documents()