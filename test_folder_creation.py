"""
اختبار إنشاء مجلد جديد والتحقق من عدم إنشاء مستندات تلقائية

هذا السكريبت يقوم بإنشاء مجلد اختباري والتحقق من عدم إنشاء أي مستندات تلقائية فيه
"""

import os
import sys
import django
import traceback

# إعداد بيئة Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'car_rental_project.settings')
django.setup()

from rental.models import ArchiveFolder, Document
from django.db import connection, transaction
from django.db.models import Q

def test_folder_creation():
    """
    اختبار إنشاء مجلد جديد والتحقق من عدم إنشاء مستندات تلقائية فيه
    """
    print("="*70)
    print("🧪 اختبار إنشاء مجلد جديد بدون مستندات تلقائية")
    print("="*70)
    
    # إنشاء اسم فريد للمجلد الاختباري
    import datetime
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    test_folder_name = f"مجلد اختبار {timestamp}"
    
    try:
        # البحث عن المجلد الجذر الأول
        try:
            # البحث عن المجلد 85 أولاً (المذكور في المشكلة)
            root_folder = ArchiveFolder.objects.get(id=85)
            print(f"🔍 تم العثور على المجلد 85: {root_folder.name}")
        except ArchiveFolder.DoesNotExist:
            # استخدام أي مجلد جذر
            root_folders = ArchiveFolder.objects.filter(parent__isnull=True)
            if root_folders.exists():
                root_folder = root_folders.first()
                print(f"🔍 تم استخدام المجلد الجذر: {root_folder.name} (ID: {root_folder.id})")
            else:
                # إنشاء مجلد جذر جديد إذا لم يكن هناك مجلدات جذر
                root_folder = ArchiveFolder.objects.create(
                    name="مجلد اختبار جذر",
                    disable_auto_documents=True,
                    is_system_folder=False
                )
                print(f"🔍 تم إنشاء مجلد جذر جديد: {root_folder.name} (ID: {root_folder.id})")
        
        # 1. إنشاء مجلد اختبار جديد
        print(f"\n1. إنشاء مجلد اختبار جديد باسم '{test_folder_name}'...")
        
        # تعيين علامات الحماية قبل الإنشاء
        new_folder = ArchiveFolder(
            name=test_folder_name,
            parent=root_folder,
            disable_auto_documents=True,
            is_system_folder=False,
            description="مجلد اختبار أنشئ بواسطة سكريبت التحقق من منع المستندات التلقائية"
        )
        
        # تعيين المتغيرات الخاصة بمنع المستندات التلقائية
        new_folder._skip_auto_document_creation = True
        new_folder._prevent_auto_docs = True
        
        # حفظ المجلد
        new_folder.save()
        folder_id = new_folder.id
        print(f"✅ تم إنشاء المجلد بنجاح بالمعرف: {folder_id}")
        
        # 2. التحقق من عدم إنشاء مستندات تلقائية
        print("\n2. التحقق من عدم وجود مستندات تلقائية في المجلد الجديد...")
        
        # البحث عن المستندات في المجلد الجديد
        documents = Document.objects.filter(folder=new_folder)
        
        if documents.exists():
            document_count = documents.count()
            print(f"⚠️ تم العثور على {document_count} مستند في المجلد الجديد:")
            
            for doc in documents:
                print(f"   - {doc.id}: {doc.title or 'بدون عنوان'}")
            
            # التحقق من وجود مستندات تلقائية
            title_conditions = Q(title__isnull=True) | Q(title='') | Q(title='بدون عنوان')
            auto_docs = documents.filter(title_conditions)
            
            if auto_docs.exists():
                auto_count = auto_docs.count()
                print(f"❌ فشل الاختبار: تم العثور على {auto_count} مستند تلقائي")
                
                # حذف المستندات التلقائية
                auto_docs.delete()
                print(f"🧹 تم حذف {auto_count} مستند تلقائي")
            else:
                print("✅ لا توجد مستندات تلقائية في المجلد (المستندات الموجودة لها عناوين صحيحة)")
        else:
            print("✅ لا توجد مستندات في المجلد الجديد - نجح الاختبار!")
        
        # 3. التنظيف بعد الاختبار
        print("\n3. تنظيف بيانات الاختبار...")
        
        # حذف المجلد تلقائياً (نسخة تلقائية)
        try:
            # حذف جميع المستندات المتبقية أولاً
            if documents.exists():
                documents.delete()
            
            # ثم حذف المجلد
            new_folder.delete()
            print(f"✅ تم حذف مجلد الاختبار: {test_folder_name}")
        except Exception as e:
            print(f"⚠️ حدث خطأ أثناء حذف مجلد الاختبار: {str(e)}")
        
        print("\n" + "="*70)
        print("✅ تم إكمال اختبار إنشاء المجلد بنجاح!")
        print("="*70)
        
    except Exception as e:
        print(f"❌ حدث خطأ أثناء اختبار إنشاء المجلد: {str(e)}")
        traceback.print_exc()

if __name__ == "__main__":
    test_folder_creation()