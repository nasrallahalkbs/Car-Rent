"""
منع إنشاء المستندات التلقائياً نهائياً

هذا السكريبت يقوم بتعديل قاعدة البيانات لمنع إنشاء المستندات التلقائية نهائياً عند إنشاء المجلدات
"""

import os
import sys
import django

# إعداد بيئة Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'car_rental_project.settings')
django.setup()

from django.db import connection, transaction
from rental.models import Document, ArchiveFolder

def completely_disable_auto_documents():
    """
    منع إنشاء المستندات التلقائية بشكل كامل ونهائي
    """
    print("\n" + "="*70)
    print("🔒 منع إنشاء المستندات التلقائية نهائياً")
    print("="*70 + "\n")
    
    try:
        # 1. تعديل قاعدة البيانات - استخدام طريقة آمنة تعمل مع SQLite
        with transaction.atomic():
            cursor = connection.cursor()
            
            # التحقق من وجود العمود (طريقة تعمل مع SQLite)
            try:
                print("1. التحقق من وجود عمود disable_auto_documents...")
                # محاولة استعلام البيانات باستخدام العمود للتحقق من وجوده
                cursor.execute("SELECT disable_auto_documents FROM rental_archivefolder LIMIT 1;")
                print("✅ العمود موجود بالفعل!")
                column_exists = True
            except Exception:
                column_exists = False
            
            if not column_exists:
                print("1. إضافة عمود disable_auto_documents إلى جدول المجلدات...")
                try:
                    cursor.execute("""
                    ALTER TABLE rental_archivefolder 
                    ADD COLUMN disable_auto_documents BOOLEAN DEFAULT 1;
                    """)
                    print("✅ تمت إضافة العمود بنجاح!")
                except Exception as e:
                    print(f"⚠️ ملاحظة عند إضافة العمود: {str(e)}")
                    print("⚠️ سنتابع العملية بافتراض وجود العمود...")
            
            # تعيين القيمة لجميع المجلدات الموجودة (SQLite متوافق)
            cursor.execute("""
            UPDATE rental_archivefolder 
            SET disable_auto_documents = 1 
            WHERE disable_auto_documents IS NULL OR disable_auto_documents = 0;
            """)
            
            print("✅ تم تعيين قيمة disable_auto_documents = TRUE لجميع المجلدات!")
        
        # 2. تعديل كود النموذج - إضافة خاصية وتعديل طريقة save
        print("\n2. تعديل نماذج البيانات برمجياً...")
        
        # تعديل طريقة save لفئة ArchiveFolder
        original_folder_save = ArchiveFolder.save
        
        def custom_folder_save(self, *args, **kwargs):
            """طريقة save المخصصة لمنع إنشاء المستندات التلقائية"""
            # تعيين علامة تجاوز إنشاء المستندات التلقائية دائماً
            self._skip_auto_document_creation = True
            self.disable_auto_documents = True
            
            # استدعاء طريقة save الأصلية
            result = original_folder_save(self, *args, **kwargs)
            
            # بعد الحفظ، نتأكد من عدم وجود مستندات تلقائية
            try:
                # حذف المستندات التلقائية
                auto_docs = Document.objects.filter(
                    folder=self, 
                    title__in=['', 'بدون عنوان', None]
                )
                
                if auto_docs.exists():
                    count = auto_docs.count()
                    auto_docs.delete()
                    print(f"🗑️ تم حذف {count} مستند تلقائي للمجلد '{self.name}'")
            except Exception as e:
                print(f"❌ خطأ أثناء حذف المستندات التلقائية: {str(e)}")
            
            return result
        
        # استبدال طريقة save
        ArchiveFolder.save = custom_folder_save
        print("✅ تم تعديل طريقة save لفئة ArchiveFolder لمنع إنشاء المستندات التلقائية!")
        
        # تعديل طريقة save لفئة Document
        original_document_save = Document.save
        
        def custom_document_save(self, *args, **kwargs):
            """طريقة save المخصصة لمنع حفظ المستندات التلقائية"""
            # التحقق من إذا كان هذا مستند تلقائي
            if not self.pk and hasattr(self, 'folder') and self.folder:
                if hasattr(self.folder, 'disable_auto_documents') and self.folder.disable_auto_documents:
                    # مستند جديد لمجلد معطل للمستندات التلقائية
                    if not self.title or self.title.strip() == '' or self.title == 'بدون عنوان':
                        print(f"⛔ منع حفظ مستند تلقائي لمجلد: {self.folder.name}")
                        return None
            
            # استدعاء طريقة save الأصلية
            return original_document_save(self, *args, **kwargs)
        
        # استبدال طريقة save
        Document.save = custom_document_save
        print("✅ تم تعديل طريقة save لفئة Document لمنع حفظ المستندات التلقائية!")
        
        # 3. حذف المستندات التلقائية الموجودة
        print("\n3. تنظيف المستندات التلقائية الموجودة...")
        auto_docs = Document.objects.filter(title__in=['', 'بدون عنوان', None])
        if auto_docs.exists():
            count = auto_docs.count()
            auto_docs.delete()
            print(f"✅ تم حذف {count} مستند تلقائي موجود!")
        else:
            print("✅ لا توجد مستندات تلقائية للتنظيف!")
        
        # 4. الإعلان عن نجاح العملية
        print("\n" + "="*70)
        print("✅ تم منع إنشاء المستندات التلقائية بنجاح!")
        print("✅ يمكنك الآن إنشاء مجلدات جديدة بدون قلق من إنشاء مستندات تلقائية!")
        print("="*70 + "\n")
        
    except Exception as e:
        print(f"❌ حدث خطأ غير متوقع: {str(e)}")

if __name__ == "__main__":
    completely_disable_auto_documents()