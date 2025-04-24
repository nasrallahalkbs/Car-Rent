"""
منع إنشاء المستندات التلقائية عند إنشاء المجلدات

هذا السكريبت يقوم بالتعديل على نموذج ArchiveFolder ليمنع إنشاء المستندات التلقائية
"""
import os
import django

# إعداد Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'car_rental_project.settings')
django.setup()

from django.db import connection
from django.db import transaction

def disable_auto_document_creation():
    """تعطيل آلية إنشاء المستندات التلقائية عند إنشاء المجلدات"""
    print("\n" + "="*50)
    print("🔄 بدء تعطيل إنشاء المستندات التلقائية...")
    print("="*50 + "\n")
    
    # التحقق مما إذا كان العمود موجودًا في قاعدة البيانات
    with transaction.atomic():
        cursor = connection.cursor()
        
        # التحقق من وجود عمود is_auto_document_disabled
        cursor.execute("SELECT COUNT(*) FROM information_schema.columns WHERE table_name = 'rental_archivefolder' AND column_name = 'is_auto_document_disabled';")
        has_column = cursor.fetchone()[0]
        
        if has_column == 0:
            print("👉 إضافة عمود is_auto_document_disabled إلى جدول ArchiveFolder...")
            # إضافة العمود مع القيمة الافتراضية True
            cursor.execute("ALTER TABLE rental_archivefolder ADD COLUMN is_auto_document_disabled BOOLEAN DEFAULT TRUE;")
            print("✓ تمت إضافة العمود بنجاح!")
        else:
            print("👉 العمود is_auto_document_disabled موجود بالفعل، تحديث القيم...")
            
        # تحديث جميع السجلات لتعطيل إنشاء المستندات التلقائية
        cursor.execute("UPDATE rental_archivefolder SET is_auto_document_disabled = TRUE;")
        print("✓ تم تحديث جميع المجلدات لتعطيل إنشاء المستندات التلقائية!")
    
    print("\n" + "="*50)
    print("✓ اكتملت عملية تعطيل إنشاء المستندات التلقائية بنجاح!")
    print("="*50 + "\n")
    
    print("⚠️ ملاحظة هامة: تأكد من تحديث نموذج ArchiveFolder في ملف models.py")
    print("⚠️ لإضافة العمود is_auto_document_disabled في تعريف النموذج")
    print("⚠️ وتعديل دالة save ليتم التحقق من هذا الحقل عند إنشاء المستندات التلقائية")

if __name__ == "__main__":
    disable_auto_document_creation()