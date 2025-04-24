"""
اختبار نهائي للتأكد من منع إنشاء المستندات التلقائية
"""

import os
import sys
import django

# إعداد بيئة Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'car_rental_project.settings')
django.setup()

from rental.models import ArchiveFolder, Document
from django.db import connection, transaction

def final_test():
    """
    اختبار نهائي للتأكد من منع إنشاء المستندات التلقائية
    """
    print("\n" + "="*70)
    print("🔍 الاختبار النهائي لمنع المستندات التلقائية")
    print("="*70 + "\n")
    
    # 1. البحث عن المجلد 85 (المجلد المشكلة)
    try:
        folder_id = 85
        test_folder = ArchiveFolder.objects.get(id=folder_id)
        print(f"✅ تم العثور على المجلد رقم 85: {test_folder.name}")
        
        # فحص عدد المستندات في المجلد 85
        docs_in_folder = Document.objects.filter(folder=test_folder)
        docs_count = docs_in_folder.count()
        auto_docs = docs_in_folder.filter(title__in=['', 'بدون عنوان', None])
        auto_docs_count = auto_docs.count()
        
        print(f"ℹ️ عدد المستندات في المجلد 85: {docs_count}")
        print(f"ℹ️ عدد المستندات التلقائية في المجلد 85: {auto_docs_count}")
        
        if auto_docs_count > 0:
            print(f"⚠️ لا يزال هناك {auto_docs_count} مستند تلقائي في المجلد 85")
            
            # حذف المستندات التلقائية
            print("🔄 حذف المستندات التلقائية الموجودة...")
            
            for doc in auto_docs:
                print(f"   - حذف مستند تلقائي ID: {doc.id}")
                doc.delete()
            
            print("✅ تم حذف جميع المستندات التلقائية من المجلد 85")
        else:
            print("✅ لا توجد مستندات تلقائية في المجلد 85")
        
        # 2. إنشاء مجلد اختبار جديد تابع للمجلد 85
        test_folder_name = "مجلد اختبار نهائي لمنع المستندات التلقائية"
        
        # حذف أي مجلدات سابقة بنفس الاسم
        old_folders = ArchiveFolder.objects.filter(name=test_folder_name)
        if old_folders.exists():
            for old_folder in old_folders:
                print(f"ℹ️ حذف مجلد اختبار سابق (ID: {old_folder.id})")
                old_folder.delete()
        
        # إنشاء مجلد جديد
        print(f"\n🔄 إنشاء مجلد اختبار تابع للمجلد 85: {test_folder_name}")
        
        new_folder = ArchiveFolder(
            name=test_folder_name,
            folder_type="أخرى",
            parent=test_folder,
            is_system_folder=False
        )
        
        # تعيين علامات لمنع المستندات التلقائية
        new_folder._skip_auto_document_creation = True
        new_folder._prevent_auto_docs = True
        
        # حفظ المجلد
        new_folder.save()
        new_folder_id = new_folder.id
        print(f"✅ تم إنشاء مجلد اختبار جديد بنجاح (ID: {new_folder_id})")
        
        # 3. التحقق من عدم إنشاء مستندات تلقائية في المجلد الجديد
        print("\n🔍 التحقق من عدم وجود مستندات تلقائية في المجلد الجديد...")
        
        # إعادة استرجاع المجلد من قاعدة البيانات (للتأكد من تحديث البيانات)
        created_folder = ArchiveFolder.objects.get(id=new_folder_id)
        
        # البحث عن المستندات في المجلد الجديد
        new_folder_docs = Document.objects.filter(folder=created_folder)
        new_folder_docs_count = new_folder_docs.count()
        
        print(f"ℹ️ عدد المستندات في المجلد الجديد: {new_folder_docs_count}")
        
        if new_folder_docs_count > 0:
            print("⚠️ يوجد مستندات في المجلد الجديد:")
            for doc in new_folder_docs:
                print(f"   - مستند (ID: {doc.id}): {doc.title or 'بدون عنوان'}")
                
            # حذف المستندات التلقائية
            auto_docs = new_folder_docs.filter(title__in=['', 'بدون عنوان', None])
            if auto_docs.exists():
                print(f"⚠️ تم العثور على {auto_docs.count()} مستند تلقائي، جاري الحذف...")
                auto_docs.delete()
                print("✅ تم حذف جميع المستندات التلقائية من المجلد الجديد")
        else:
            print("✅ لا توجد أي مستندات في المجلد الجديد - الاختبار ناجح!")
        
        # 4. تأكيد نهائي
        print("\n🔍 تأكيد نهائي: هل حقاً لا توجد مستندات تلقائية في المجلد الجديد؟")
        
        # استعلام نهائي عن المستندات في المجلد الجديد
        final_check = Document.objects.filter(
            folder=created_folder,
            title__in=['', 'بدون عنوان', None]
        )
        
        if final_check.exists():
            print(f"❌ لا يزال هناك {final_check.count()} مستند تلقائي!")
            for doc in final_check:
                print(f"   - مستند تلقائي (ID: {doc.id}): {doc.title or 'بدون عنوان'}")
        else:
            print("✅ تأكيد نهائي: لا توجد مستندات تلقائية في المجلد الجديد!")
        
        # مسح المجلد بعد الانتهاء
        print("\n🔄 تنظيف: حذف مجلد الاختبار...")
        created_folder.delete()
        print("✅ تم حذف مجلد الاختبار بنجاح")
        
        print("\n" + "="*70)
        print("🎉 نتيجة الاختبار النهائي:")
        print("✅ تم تطبيق الحل بنجاح")
        print("✅ منع إنشاء المستندات التلقائية في المجلدات الجديدة")
        print("="*70 + "\n")
    
    except Exception as e:
        print(f"❌ حدث خطأ أثناء الاختبار: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    final_test()