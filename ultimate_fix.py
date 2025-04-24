"""
الحل النهائي والقاطع لمنع إنشاء المستندات التلقائية
"""

import os
import sys
import django

# إعداد بيئة Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'car_rental_project.settings')
django.setup()

from rental.models import ArchiveFolder, Document
from django.db import connection, transaction
import json

def apply_ultimate_fix():
    """
    تطبيق الحل النهائي والقاطع لمنع إنشاء المستندات التلقائية
    """
    print("\n" + "="*70)
    print("⚡ الحل النهائي والقاطع لمنع المستندات التلقائية")
    print("="*70 + "\n")
    
    try:
        # 1. إيجاد أي مستندات تلقائية موجودة وحذفها
        print("1. حذف جميع المستندات التلقائية الموجودة...")
        
        # البحث عن المستندات التلقائية
        auto_docs = Document.objects.filter(
            title__in=['', 'بدون عنوان', None]
        )
        
        # حذف المستندات التلقائية
        if auto_docs.exists():
            count = auto_docs.count()
            auto_docs_ids = list(auto_docs.values_list('id', flat=True))
            auto_docs_folders = list(auto_docs.values_list('folder_id', flat=True))
            
            # طباعة معلومات المستندات قبل الحذف
            print(f"ℹ️ تم العثور على {count} مستند تلقائي")
            print(f"ℹ️ معرفات المستندات: {auto_docs_ids}")
            print(f"ℹ️ معرفات المجلدات المرتبطة: {auto_docs_folders}")
            
            # حذف المستندات باستخدام القاعدة البيانات مباشرة
            with transaction.atomic():
                cursor = connection.cursor()
                cursor.execute("""
                DELETE FROM rental_document 
                WHERE title IS NULL OR title = '' OR title = 'بدون عنوان';
                """)
            
            print(f"✅ تم حذف {count} مستند تلقائي بنجاح")
        else:
            print("✅ لا توجد مستندات تلقائية للحذف")
        
        # 2. تنفيذ تعديل مباشر في طريقة حفظ المستندات
        print("\n2. تنفيذ تعديل مباشر في طريقة حفظ المستندات...")
        
        # حفظ الطريقة الأصلية
        if not hasattr(Document, '_ultimate_save'):
            Document._ultimate_save = Document.save
        
        # استبدال بطريقة جديدة
        def prevent_auto_document(self, *args, **kwargs):
            """منع إنشاء المستندات التلقائية بشكل قاطع"""
            # إذا كان مستند جديد
            if not self.pk:
                # إذا كان عنوان المستند فارغ أو "بدون عنوان"
                if not self.title or self.title.strip() == '' or self.title == 'بدون عنوان':
                    print(f"🚫 منع إنشاء مستند تلقائي عنوانه: '{self.title}' - الحل النهائي")
                    return None
            
            # لكل المستندات الأخرى، استخدم الطريقة الأصلية
            return self._ultimate_save(*args, **kwargs)
        
        # استبدال طريقة الحفظ
        Document.save = prevent_auto_document
        print("✅ تم تركيب آلية حاسمة لمنع إنشاء المستندات التلقائية")
        
        # 3. التأكد من تعطيل المستندات التلقائية في المجلدات
        print("\n3. تعطيل المستندات التلقائية في جميع المجلدات...")
        
        # حفظ طريقة الأصلية
        if not hasattr(ArchiveFolder, '_ultimate_save'):
            ArchiveFolder._ultimate_save = ArchiveFolder.save
        
        # استبدال بطريقة جديدة
        def prevent_auto_document_folder(self, *args, **kwargs):
            """منع المستندات التلقائية في المجلدات"""
            # تعيين علامات منع المستندات التلقائية
            self._skip_auto_document_creation = True
            self._prevent_auto_docs = True
            if hasattr(self, 'disable_auto_documents'):
                self.disable_auto_documents = True
            
            # استخدام طريقة الحفظ الأصلية
            result = self._ultimate_save(*args, **kwargs)
            
            # تنظيف بعد الحفظ
            if self.pk:
                Document.objects.filter(
                    folder=self,
                    title__in=['', 'بدون عنوان', None]
                ).delete()
            
            return result
        
        # استبدال طريقة الحفظ
        ArchiveFolder.save = prevent_auto_document_folder
        print("✅ تم تركيب آلية حماية في المجلدات")
        
        # 4. إضافة محفز (trigger) ثابت في قاعدة البيانات
        print("\n4. إضافة محفز ثابت في قاعدة البيانات...")
        
        try:
            with transaction.atomic():
                cursor = connection.cursor()
                
                # حذف المحفز إذا كان موجوداً
                cursor.execute("DROP TRIGGER IF EXISTS block_auto_documents;")
                
                # إنشاء محفز جديد
                cursor.execute("""
                CREATE TRIGGER IF NOT EXISTS block_auto_documents
                BEFORE INSERT ON rental_document
                WHEN NEW.title IS NULL OR NEW.title = '' OR NEW.title = 'بدون عنوان'
                BEGIN
                    SELECT RAISE(ABORT, 'منع إنشاء مستند تلقائي بواسطة المحفز');
                END;
                """)
            
            print("✅ تم إنشاء محفز في قاعدة البيانات لمنع المستندات التلقائية")
        except Exception as e:
            print(f"⚠️ لم يمكن إنشاء المحفز: {str(e)}")
            print("⚠️ سنعتمد على طرق الحماية الأخرى")
        
        # 5. التحقق النهائي من عدم وجود مستندات تلقائية
        print("\n5. التحقق النهائي...")
        
        # البحث مرة أخرى
        auto_docs = Document.objects.filter(
            title__in=['', 'بدون عنوان', None]
        )
        
        if auto_docs.exists():
            count = auto_docs.count()
            print(f"⚠️ لا يزال هناك {count} مستند تلقائي")
            print(f"⚠️ سيتم حذفها الآن بشكل نهائي")
            
            # حذف المستندات
            auto_docs.delete()
            print("✅ تم حذف المستندات المتبقية")
        else:
            print("✅ لا توجد مستندات تلقائية - الحماية ناجحة")
        
        # 6. إنشاء ملف دائم للحماية
        print("\n6. إنشاء ملف دائم للحماية...")
        
        guard_file_content = """# -*- coding: utf-8 -*-
\"\"\"
ملف الحماية الدائمة ضد المستندات التلقائية
تم إنشاؤه تلقائيًا
\"\"\"

def start():
    \"\"\"تطبيق حماية المستندات التلقائية\"\"\"
    from rental.models import Document, ArchiveFolder
    
    # حفظ طرق الحفظ الأصلية
    if not hasattr(Document, '_guarded_save'):
        Document._guarded_save = Document.save
    
    if not hasattr(ArchiveFolder, '_guarded_save'):
        ArchiveFolder._guarded_save = ArchiveFolder.save
    
    # تعريف طرق الحفظ الآمنة
    def safe_document_save(self, *args, **kwargs):
        \"\"\"منع إنشاء المستندات التلقائية\"\"\"
        if not self.pk and (not self.title or self.title.strip() == '' or self.title == 'بدون عنوان'):
            print(f"🛡️ منع إنشاء مستند تلقائي: '{self.title}'")
            return None
        return self._guarded_save(*args, **kwargs)
    
    def safe_folder_save(self, *args, **kwargs):
        \"\"\"منع المستندات التلقائية في المجلدات\"\"\"
        self._skip_auto_document_creation = True
        if hasattr(self, 'disable_auto_documents'):
            self.disable_auto_documents = True
        result = self._guarded_save(*args, **kwargs)
        if self.pk:
            Document.objects.filter(folder=self, title__in=['', 'بدون عنوان', None]).delete()
        return result
    
    # تطبيق طرق الحفظ الآمنة
    Document.save = safe_document_save
    ArchiveFolder.save = safe_folder_save
    
    print("🛡️ تم تفعيل الحماية الدائمة ضد المستندات التلقائية")
"""
        
        # إنشاء ملف الحماية
        guard_file = os.path.join('rental', 'guard.py')
        
        with open(guard_file, 'w', encoding='utf-8') as file:
            file.write(guard_file_content)
        
        # تحديث ملف الإشارات لتطبيق الحماية عند بدء تشغيل التطبيق
        signals_file = os.path.join('rental', 'signals.py')
        
        with open(signals_file, 'r', encoding='utf-8') as file:
            signals_content = file.read()
        
        # إضافة استدعاء لملف الحماية في نهاية ملف الإشارات
        if 'from rental.guard import start' not in signals_content:
            signals_content += "\n\n# تطبيق الحماية الدائمة\ntry:\n    from rental.guard import start\n    start()\n    print('✅ تم تفعيل الحماية الدائمة ضد المستندات التلقائية')\nexcept Exception as e:\n    print(f'⚠️ لم يمكن تفعيل الحماية الدائمة: {str(e)}')\n"
            
            with open(signals_file, 'w', encoding='utf-8') as file:
                file.write(signals_content)
        
        print("✅ تم إنشاء وتفعيل نظام الحماية الدائم")
        
        # 7. عرض ملخص نهائي
        print("\n" + "="*70)
        print("✨ تم تطبيق الحل النهائي والقاطع بنجاح!")
        print("✨ يجب الآن ألا يتم إنشاء أي مستندات تلقائية مطلقاً")
        print("✨ تم تفعيل آليات حماية متعددة ودائمة")
        print("✨ يرجى إعادة تشغيل التطبيق لتطبيق جميع التغييرات")
        print("="*70 + "\n")
        
    except Exception as e:
        print(f"❌ حدث خطأ غير متوقع: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    apply_ultimate_fix()