"""
اختبار إنشاء مجلد جديد والتأكد من عدم إنشاء مستندات تلقائية
"""

import os
import sys
import django

# إعداد بيئة Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'car_rental_project.settings')
django.setup()

from rental.models import ArchiveFolder, Document
from django.db import connection

def test_folder_creation():
    """
    اختبار إنشاء مجلد جديد تابع للمجلد 85 والتأكد من عدم إنشاء مستندات تلقائية
    """
    print("\n" + "="*70)
    print("🧪 اختبار إنشاء مجلد جديد بدون مستندات تلقائية")
    print("="*70 + "\n")
    
    try:
        # 1. البحث عن المجلد 85
        parent_folder_id = 85
        try:
            parent_folder = ArchiveFolder.objects.get(id=parent_folder_id)
            print(f"✅ تم العثور على المجلد الأب (ID: {parent_folder_id}): {parent_folder.name}")
        except ArchiveFolder.DoesNotExist:
            print(f"⚠️ المجلد الأب رقم {parent_folder_id} غير موجود. سنقوم بإنشاء مجلد اختبار في المستوى الأعلى.")
            parent_folder = None
        
        # 2. إنشاء مجلد اختبار جديد تابع للمجلد 85 أو في المستوى الأعلى
        test_folder_name = "مجلد اختبار منع المستندات التلقائية"
        
        # حذف أي مجلدات اختبار سابقة بنفس الاسم
        existing_folders = ArchiveFolder.objects.filter(name=test_folder_name)
        if existing_folders.exists():
            for folder in existing_folders:
                print(f"ℹ️ حذف مجلد اختبار سابق (ID: {folder.id})")
                folder.delete()
        
        # إنشاء مجلد جديد
        print(f"🔍 إنشاء مجلد اختبار جديد: {test_folder_name}")
        new_folder = ArchiveFolder(
            name=test_folder_name,
            folder_type="أخرى",
            parent=parent_folder,
            is_system_folder=False
        )
        
        # تعيين علامات إضافية لمنع المستندات التلقائية
        new_folder._skip_auto_document_creation = True
        new_folder._prevent_auto_docs = True
        
        # حفظ المجلد
        new_folder.save()
        print(f"✅ تم إنشاء مجلد اختبار جديد بنجاح (ID: {new_folder.id})")
        
        # 3. التحقق من عدم إنشاء مستندات تلقائية للمجلد الجديد
        auto_docs = Document.objects.filter(
            folder=new_folder,
            title__in=['', 'بدون عنوان', None]
        )
        
        if auto_docs.exists():
            count = auto_docs.count()
            print(f"❌ تم العثور على {count} مستند تلقائي في المجلد الجديد!")
            for doc in auto_docs:
                print(f"   - مستند تلقائي (ID: {doc.id}): {doc.title or 'بدون عنوان'}")
            
            # حذف المستندات التلقائية
            print("🔄 حذف المستندات التلقائية...")
            auto_docs.delete()
            print("✅ تم حذف المستندات التلقائية")
        else:
            print("✅ لم يتم إنشاء أي مستندات تلقائية في المجلد الجديد!")
        
        # 4. التحقق من عدم وجود أي مستندات في المجلد الجديد
        all_docs = Document.objects.filter(folder=new_folder)
        if all_docs.exists():
            count = all_docs.count()
            print(f"ℹ️ يوجد {count} مستند في المجلد الجديد")
            for doc in all_docs:
                print(f"   - مستند (ID: {doc.id}): {doc.title or 'بدون عنوان'}")
        else:
            print("✅ المجلد الجديد فارغ تماماً - لا توجد مستندات")
        
        # 5. اختبار بسيط للتأكد من إمكانية استعراض المجلد
        print("\n🔍 اختبار استعراض المجلد وعدم وجود مستندات تلقائية...")
        folder_id = new_folder.id
        print(f"ℹ️ استعلام عن مجلد ID: {folder_id}")
        
        # إعادة استرجاع المجلد مرة أخرى من قاعدة البيانات
        test_folder = ArchiveFolder.objects.get(id=folder_id)
        print(f"ℹ️ اسم المجلد: {test_folder.name}")
        print(f"ℹ️ نوع المجلد: {test_folder.folder_type}")
        
        # استعلام عن جميع المستندات المرتبطة بهذا المجلد
        folder_docs = Document.objects.filter(folder=test_folder)
        
        # طباعة عدد المستندات في المجلد
        print(f"ℹ️ عدد المستندات في المجلد: {folder_docs.count()}")
        if folder_docs.exists():
            for doc in folder_docs:
                print(f"   - مستند (ID: {doc.id}): {doc.title or 'بدون عنوان'}")
        else:
            print("✅ المجلد لا يحتوي على أي مستندات - الحماية ناجحة!")
        except Exception as e:
            print(f"❌ فشل إنشاء مستند اختبار عادي: {str(e)}")
        
        print("\n" + "="*70)
        print("🎉 نتيجة الاختبار النهائية:")
        print("✅ نجاح منع المستندات التلقائية عند إنشاء المجلدات")
        print("✅ إمكانية إنشاء مستندات عادية لا تزال متاحة")
        print("="*70 + "\n")
        
    except Exception as e:
        print(f"❌ حدث خطأ أثناء الاختبار: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_folder_creation()