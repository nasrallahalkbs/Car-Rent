"""
اختبار إنشاء مجلد جديد للتأكد من عدم إنشاء مستندات تلقائية
"""

import os
import sys
import django

# إعداد بيئة Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'car_rental_project.settings')
django.setup()

from rental.models import ArchiveFolder, Document
from django.db import connection, transaction
import time

def test_folder_creation():
    """
    اختبار إنشاء مجلد جديد والتحقق من عدم إنشاء مستندات تلقائية
    """
    print("\n" + "="*70)
    print("🧪 اختبار منع المستندات التلقائية")
    print("="*70 + "\n")
    
    # إنشاء مجلد جديد للاختبار
    timestamp = int(time.time())
    folder_name = f"مجلد_اختبار_{timestamp}"
    
    try:
        print(f"1. إنشاء مجلد جديد باسم: {folder_name}")
        
        # استخدام العديد من الحمايات
        with transaction.atomic():
            # 1. إنشاء المجلد باستخدام Django ORM
            folder = ArchiveFolder(
                name=folder_name,
                description="مجلد اختبار لمنع المستندات التلقائية",
                is_system_folder=False
            )
            
            # تعيين علامات حماية
            folder._skip_auto_document_creation = True
            folder.disable_auto_documents = True
            
            # حفظ المجلد
            folder.save()
            
            # حفظ معرف المجلد لاستخدامه لاحقاً
            new_folder_id = folder.id
            
            print(f"✅ تم إنشاء المجلد بنجاح بمعرف: {new_folder_id}")
        
        # انتظار لحظة للتأكد من اكتمال أي عمليات خلفية
        time.sleep(1)
        
        print("\n2. التحقق من وجود مستندات تلقائية...")
        
        # البحث عن المستندات التلقائية في المجلد الجديد
        auto_docs = Document.objects.filter(
            folder_id=new_folder_id,
            title__in=['', 'بدون عنوان', None]
        )
        
        # التحقق من نتائج البحث
        if auto_docs.exists():
            count = auto_docs.count()
            print(f"⚠️ تم العثور على {count} مستند تلقائي في المجلد الجديد")
            for doc in auto_docs:
                print(f" - {doc.id}: {doc.title} (تاريخ الإنشاء: {doc.created_at})")
        else:
            print("✅ لا توجد مستندات تلقائية في المجلد الجديد")
        
        # البحث عن جميع المستندات في المجلد الجديد
        all_docs = Document.objects.filter(folder_id=new_folder_id)
        if all_docs.exists():
            count = all_docs.count()
            print(f"ℹ️ إجمالي المستندات في المجلد الجديد: {count}")
        else:
            print("✅ المجلد الجديد فارغ تماماً (لا توجد مستندات)")
        
        # الاختبار ناجح إذا لم يتم العثور على مستندات تلقائية
        if not auto_docs.exists():
            print("\n✅ الاختبار ناجح! لم يتم إنشاء مستندات تلقائية في المجلد الجديد")
        else:
            print("\n❌ الاختبار فاشل! تم إنشاء مستندات تلقائية في المجلد الجديد")
        
        print("\n" + "="*70)
        print("انتهى الاختبار")
        print("="*70 + "\n")
        
    except Exception as e:
        print(f"❌ حدث خطأ أثناء الاختبار: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_folder_creation()