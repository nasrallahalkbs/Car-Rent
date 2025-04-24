"""
ازالة جميع المستندات التلقائية التي تم إنشاؤها مع المجلدات
"""
import os
import django

# إعداد Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'car_rental_project.settings')
django.setup()

from rental.models import Document, ArchiveFolder
from django.db import transaction

def delete_auto_documents():
    """حذف جميع المستندات التلقائية باستخدام SQL المباشر"""
    print("👉 بدء تنظيف المستندات التلقائية...")
    
    from django.db import connection
    
    # إحصائيات قبل الحذف
    total_documents = Document.objects.count()
    total_folders = ArchiveFolder.objects.count()
    print(f"👉 إجمالي المستندات قبل التنظيف: {total_documents}")
    print(f"👉 إجمالي المجلدات: {total_folders}")
    
    with transaction.atomic():
        cursor = connection.cursor()
        # تعطيل المحفزات
        cursor.execute("SET session_replication_role = 'replica';")
        
        # عد المستندات التلقائية
        cursor.execute("SELECT COUNT(*) FROM rental_document WHERE title = '' OR title = 'بدون عنوان' OR title IS NULL;")
        count_1 = cursor.fetchone()[0]
        print(f"👉 عدد المستندات بدون عنوان: {count_1}")
        
        # عد المستندات بدون ملف
        cursor.execute("SELECT COUNT(*) FROM rental_document WHERE file = '';")
        count_2 = cursor.fetchone()[0]
        print(f"👉 عدد المستندات بدون ملف: {count_2}")
        
        # عد المستندات المميزة كتلقائية
        # تحقق من وجود العمود قبل الاستعلام
        cursor.execute("SELECT COUNT(*) FROM information_schema.columns WHERE table_name = 'rental_document' AND column_name = 'is_auto_created';")
        has_column = cursor.fetchone()[0]
        
        count_3 = 0
        if has_column > 0:
            cursor.execute("SELECT COUNT(*) FROM rental_document WHERE is_auto_created = TRUE;")
            count_3 = cursor.fetchone()[0]
        
        print(f"👉 عدد المستندات المميزة كتلقائية: {count_3}")
        
        # عد المستندات بملفات اختبارية
        cursor.execute("SELECT COUNT(*) FROM rental_document WHERE file LIKE '%djangotest%';")
        count_4 = cursor.fetchone()[0]
        print(f"👉 عدد المستندات بملفات اختبارية: {count_4}")
        
        # حذف جميع أنواع المستندات التلقائية في عملية واحدة
        cursor.execute("DELETE FROM rental_document WHERE title = '' OR title = 'بدون عنوان' OR title IS NULL OR file = '' OR file LIKE '%djangotest%';")
        
        # حذف المستندات المميزة كتلقائية إذا كان العمود موجوداً
        if has_column > 0:
            cursor.execute("DELETE FROM rental_document WHERE is_auto_created = TRUE;")
        
        # إعادة تفعيل المحفزات
        cursor.execute("SET session_replication_role = 'origin';")
    
    # إحصائيات بعد الحذف
    remaining_documents = Document.objects.count()
    total_deleted = total_documents - remaining_documents
    print(f"👉 تم حذف {total_deleted} مستند تلقائي بنجاح")
    print(f"👉 إجمالي المستندات المتبقية: {remaining_documents}")

def cleanup_empty_folders():
    """حذف المجلدات الفارغة والمجلدات بدون اسم"""
    print("\n👉 بدء تنظيف المجلدات الفارغة وبدون اسم...")
    
    # استخدام استعلام SQL مباشر لحذف المجلدات بدون اسم
    from django.db import connection
    
    with transaction.atomic():
        cursor = connection.cursor()
        # تعطيل المحفزات
        cursor.execute("SET session_replication_role = 'replica';")
        
        # عد المجلدات بدون اسم أولاً
        cursor.execute("SELECT COUNT(*) FROM rental_archivefolder WHERE name = 'بدون اسم' OR name = '' OR name IS NULL;")
        empty_name_count = cursor.fetchone()[0]
        print(f"👉 عدد المجلدات بدون اسم: {empty_name_count}")
        
        # حذف المجلدات بدون اسم مباشرة
        cursor.execute("DELETE FROM rental_archivefolder WHERE name = 'بدون اسم' OR name = '' OR name IS NULL;")
        
        # إعادة تفعيل المحفزات
        cursor.execute("SET session_replication_role = 'origin';")
    
    # عدم حذف المجلدات الفارغة الآن، فقط العد
    empty_folders_count = 0
    for folder in ArchiveFolder.objects.all():
        if folder.document_count == 0 and not folder.has_children():
            empty_folders_count += 1
    
    print(f"👉 عدد المجلدات الفارغة (ليس لديها مستندات ولا مجلدات فرعية): {empty_folders_count}")
    
    # إحصائيات نهائية
    remaining_folders = ArchiveFolder.objects.count()
    print(f"👉 إجمالي المجلدات المتبقية: {remaining_folders}")

if __name__ == "__main__":
    print("\n" + "="*50)
    print("🔄 بدء عملية تنظيف المستندات والمجلدات التلقائية...")
    print("="*50 + "\n")
    
    delete_auto_documents()
    cleanup_empty_folders()
    
    print("\n" + "="*50)
    print("✓ اكتملت عملية التنظيف بنجاح!")
    print("="*50 + "\n")