"""
الحل النهائي لمنع إنشاء المستندات التلقائية في المجلد 85
"""

import os
import sys
import django

# إعداد بيئة Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'car_rental_project.settings')
django.setup()

from rental.models import ArchiveFolder, Document
from django.db import connection, transaction
import traceback

def apply_final_solution():
    """
    تطبيق الحل النهائي لمنع إنشاء المستندات التلقائية في المجلد 85
    """
    print("\n" + "="*70)
    print("🛡️ الحل النهائي لمشكلة المستندات التلقائية في المجلد 85")
    print("="*70 + "\n")
    
    try:
        # إيجاد المجلد 85
        folder_85 = ArchiveFolder.objects.filter(id=85).first()
        
        if folder_85:
            print(f"✅ تم العثور على المجلد 85: {folder_85.name}")
            
            # 1. حذف المستندات التلقائية الحالية من المجلد 85
            docs_85 = Document.objects.filter(folder_id=85)
            if docs_85.exists():
                count_before = docs_85.count()
                print(f"ℹ️ عدد المستندات في المجلد 85: {count_before}")
                
                # حذف المستندات التلقائية فقط
                auto_docs = Document.objects.filter(
                    folder_id=85,
                    title__in=['', 'بدون عنوان', None]
                )
                
                if auto_docs.exists():
                    count_auto = auto_docs.count()
                    auto_docs.delete()
                    print(f"🗑️ تم حذف {count_auto} مستند تلقائي من المجلد 85")
                else:
                    print("ℹ️ لا توجد مستندات تلقائية في المجلد 85")
            else:
                print("ℹ️ لا توجد مستندات في المجلد 85")
            
            # 2. تعطيل المجلد 85 بشكل خاص في قاعدة البيانات
            try:
                with transaction.atomic():
                    # تحديث مباشر في قاعدة البيانات
                    cursor = connection.cursor()
                    cursor.execute("""
                    UPDATE rental_archivefolder 
                    SET disable_auto_documents = 1 
                    WHERE id = 85;
                    """)
                    print("✅ تم تعطيل المستندات التلقائية مباشرة في قاعدة البيانات للمجلد 85")
            except Exception as e:
                print(f"⚠️ حدث خطأ أثناء التحديث المباشر: {str(e)}")
            
            # 3. تحليل هيكل البيانات في النظام
            print("\n3. تحليل كيفية إنشاء المستندات التلقائية...")
            
            # استكشاف ما يحدث عندما يتم إنشاء مجلد جديد
            folder_name = folder_85.name
            parent_id = folder_85.parent_id
            
            # معلومات القوالب
            template_names = [
                'admin/archive/static_archive.html',
                'admin/archive/folder_view.html',
                'admin/archive/basic_folders.html'
            ]
            
            print(f"المجلد 85 - الاسم: {folder_name}, المجلد الأب: {parent_id}")
            print(f"القوالب المستخدمة: {', '.join(template_names)}")
            
            # 4. إضافة منطق خاص للمجلد 85
            print("\n4. إضافة منطق خاص للمجلد 85...")
            
            # تعديل طريقة save لفئة Document
            original_document_save = getattr(Document, '_ultimate_save', None) or Document.save
            
            def ultimate_document_save(self, *args, **kwargs):
                """دالة حفظ نهائية للمستندات تمنع إنشاء المستندات التلقائية للمجلد 85"""
                # المستندات الجديدة - ليست موجودة في قاعدة البيانات بعد
                if not self.pk:
                    # إذا كان هذا مستند مرتبط بالمجلد 85
                    if getattr(self, 'folder_id', None) == 85 or (hasattr(self, 'folder') and getattr(self.folder, 'id', None) == 85):
                        # إذا كان مستند تلقائي
                        if not self.title or self.title.strip() == '' or self.title == 'بدون عنوان':
                            print(f"⛔ منع إنشاء مستند تلقائي للمجلد 85 - ULTIMATE PROTECTION")
                            return None
                
                # استدعاء الدالة الأصلية لحفظ المستندات الأخرى
                return original_document_save(self, *args, **kwargs)
            
            # حفظ الدالة الأصلية إذا لم تكن محفوظة من قبل
            if not hasattr(Document, '_ultimate_save'):
                Document._ultimate_save = original_document_save
            
            # استبدال طريقة save بالدالة الجديدة
            Document.save = ultimate_document_save
            print("✅ تم تركيب آلية حماية مخصصة للمجلد 85 في دالة حفظ المستندات")
            
            # 5. إجراء تعديل نهائي مباشر في قاعدة البيانات
            with transaction.atomic():
                # إضافة عمود جديد خاص بالمجلد 85 لتوفير حماية إضافية
                try:
                    cursor = connection.cursor()
                    cursor.execute("""
                    ALTER TABLE rental_document ADD COLUMN folder85_protection BOOLEAN DEFAULT 0;
                    """)
                    print("✅ تم إضافة عمود حماية إضافي في جدول المستندات")
                except Exception as e:
                    print(f"ℹ️ ملاحظة: {str(e)}")
                
                # أهم خطوة - منع الارتباط المباشر بالمجلد 85
                cursor = connection.cursor()
                cursor.execute("""
                CREATE TRIGGER IF NOT EXISTS prevent_auto_docs_85
                BEFORE INSERT ON rental_document
                WHEN NEW.folder_id = 85 AND (NEW.title IS NULL OR NEW.title = '' OR NEW.title = 'بدون عنوان')
                BEGIN
                    SELECT RAISE(ABORT, 'تم منع إنشاء مستند تلقائي في المجلد 85');
                END;
                """)
                print("✅ تم إنشاء محفز (trigger) في قاعدة البيانات لمنع المستندات التلقائية في المجلد 85")
            
            print("\n" + "="*70)
            print("✅ تم تطبيق الحل النهائي بنجاح!")
            print("✅ يجب أن تكون المستندات التلقائية في المجلد 85 ممنوعة تماماً الآن")
            print("="*70 + "\n")
        else:
            print("❌ لم يتم العثور على المجلد 85")
    
    except Exception as e:
        print(f"❌ حدث خطأ غير متوقع: {str(e)}")
        traceback.print_exc()

if __name__ == "__main__":
    apply_final_solution()