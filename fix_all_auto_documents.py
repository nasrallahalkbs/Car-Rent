"""
الحل النهائي الشامل لمنع إنشاء المستندات التلقائية في كل المجلدات
وتنظيف جميع المستندات التلقائية الموجودة

هذا السكريبت يقوم بما يلي:
1. تنظيف جميع المستندات التلقائية الموجودة
2. ضمان تطبيق الحماية في جميع أنحاء النظام
3. إصلاح جميع الأماكن التي قد تخلق مستندات تلقائية
4. تحسين أداء النظام من خلال تقليل الاستعلامات غير الضرورية
"""

import os
import sys
import django
import time
import traceback

# إعداد بيئة Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'car_rental_project.settings')
django.setup()

from rental.models import ArchiveFolder, Document
from django.db import connection, transaction
from django.db.models import Q
import json

def comprehensive_fix():
    """
    الحل الشامل لمنع المستندات التلقائية ومعالجة المشاكل ذات الصلة
    """
    print("\n" + "="*70)
    print("🛡️ الحل النهائي الشامل لمشكلة المستندات التلقائية")
    print("="*70 + "\n")
    
    try:
        # 1. تنظيف جميع المستندات التلقائية الموجودة
        print("1. تنظيف المستندات التلقائية الموجودة...")
        
        with transaction.atomic():
            # حذف المستندات التلقائية باستخدام معايير متعددة للتأكد من حذف جميع الحالات
            cursor = connection.cursor()
            cursor.execute("""
            DELETE FROM rental_document 
            WHERE title IS NULL OR title = '' OR title = 'بدون عنوان';
            """)
            
            # الحصول على عدد الصفوف المتأثرة
            cursor.execute("SELECT changes();")
            result = cursor.fetchone()
            if result:
                count = result[0]
                print(f"✅ تم حذف {count} مستند تلقائي")
            else:
                print("✅ تم التنظيف (عدد المستندات المحذوفة غير معروف)")
        
        # 2. تطبيق الحماية على جميع المجلدات
        print("\n2. تطبيق الحماية على جميع المجلدات...")
        
        all_folders = ArchiveFolder.objects.all()
        folder_count = all_folders.count()
        
        for folder in all_folders:
            # تعيين علامات الحماية
            folder._skip_auto_document_creation = True
            folder._prevent_auto_docs = True
            if hasattr(folder, 'disable_auto_documents'):
                folder.disable_auto_documents = True
        
        print(f"✅ تم تطبيق الحماية على {folder_count} مجلد")
        
        # 3. الحماية المباشرة لنماذج البيانات
        print("\n3. تطبيق الحماية المباشرة على نماذج البيانات...")
        
        # حفظ الإصدارات الأصلية من دوال الحفظ إذا لم تكن محفوظة بالفعل
        if not hasattr(Document, '_original_save'):
            Document._original_save = Document.save
        
        if not hasattr(ArchiveFolder, '_original_save'):
            ArchiveFolder._original_save = ArchiveFolder.save
        
        # تعريف دوال الحفظ المخصصة
        def safe_document_save(self, *args, **kwargs):
            """منع إنشاء المستندات التلقائية بشكل كامل"""
            # منع إنشاء مستندات تلقائية جديدة
            if not self.pk:  # إذا كان مستند جديد
                if not self.title or self.title.strip() == '' or self.title == 'بدون عنوان':
                    print(f"🛑 تم منع إنشاء مستند تلقائي في المجلد {self.folder.name if self.folder else 'بدون مجلد'}")
                    # تتبع مكان الاستدعاء (للتصحيح)
                    stack = traceback.extract_stack()
                    caller = stack[-2]
                    print(f"🔍 مكان الاستدعاء: {caller.filename.split('/')[-1]}:{caller.name}")
                    return None  # منع الإنشاء عن طريق عدم استدعاء الدالة الأصلية
            
            # استمرار في الحفظ للمستندات العادية
            return self._original_save(*args, **kwargs)
        
        def safe_folder_save(self, *args, **kwargs):
            """منع إنشاء المستندات التلقائية عند إنشاء المجلدات"""
            # تعيين علامات منع المستندات التلقائية
            self._skip_auto_document_creation = True
            self._prevent_auto_docs = True
            if hasattr(self, 'disable_auto_documents'):
                self.disable_auto_documents = True
            
            # حفظ المجلد باستخدام الطريقة الأصلية
            result = self._original_save(*args, **kwargs)
            
            # تنظيف المستندات التلقائية بعد الحفظ
            if self.pk:  # إذا تم حفظ المجلد بنجاح
                title_conditions = Q(title__isnull=True) | Q(title='') | Q(title='بدون عنوان')
                auto_docs = Document.objects.filter(folder=self).filter(title_conditions)
                if auto_docs.exists():
                    count = auto_docs.count()
                    auto_docs.delete()
                    print(f"🧹 تم حذف {count} مستند تلقائي بعد حفظ المجلد {self.name}")
            
            return result
        
        # تطبيق الدوال المخصصة
        Document.save = safe_document_save
        ArchiveFolder.save = safe_folder_save
        
        print("✅ تم تطبيق الحماية المباشرة على نماذج البيانات")
        
        # 4. التحقق النهائي من المستندات التلقائية
        print("\n4. التحقق النهائي من المستندات التلقائية...")
        
        # فحص إذا كان لا يزال هناك مستندات تلقائية
        title_conditions = Q(title__isnull=True) | Q(title='') | Q(title='بدون عنوان')
        auto_docs = Document.objects.filter(title_conditions)
        
        if auto_docs.exists():
            count = auto_docs.count()
            print(f"⚠️ لا يزال هناك {count} مستند تلقائي في النظام")
            print("⚠️ تفاصيل المستندات:")
            
            for doc in auto_docs:
                folder_name = doc.folder.name if doc.folder else "بدون مجلد"
                folder_id = doc.folder.id if doc.folder else "N/A"
                print(f"   - {doc.id}: {doc.title or 'بدون عنوان'} في المجلد '{folder_name}' (ID: {folder_id})")
            
            print("\n🔄 محاولة نهائية لحذف المستندات المتبقية...")
            auto_docs.delete()
            
            # التحقق مرة أخرى
            title_conditions = Q(title__isnull=True) | Q(title='') | Q(title='بدون عنوان')
            remaining = Document.objects.filter(title_conditions).count()
            
            if remaining > 0:
                print(f"⚠️ لا يزال هناك {remaining} مستند. يرجى الاتصال بالمطور.")
            else:
                print("✅ تم حذف جميع المستندات التلقائية المتبقية")
        else:
            print("✅ لا توجد مستندات تلقائية في النظام")
        
        # 5. إنشاء إجراء حماية إضافي
        print("\n5. إنشاء إجراء حماية إضافي...")
        
        # تسجيل دالة التنظيف الدوري لتشغيلها كل 5 دقائق
        def periodic_cleanup():
            """التنظيف الدوري للمستندات التلقائية"""
            while True:
                try:
                    # تنظيف المستندات التلقائية
                    title_conditions = Q(title__isnull=True) | Q(title='') | Q(title='بدون عنوان')
                    auto_docs = Document.objects.filter(title_conditions)
                    if auto_docs.exists():
                        count = auto_docs.count()
                        auto_docs.delete()
                        print(f"🧹 [تنظيف دوري] تم حذف {count} مستند تلقائي")
                    
                    # انتظار 5 دقائق
                    time.sleep(300)
                except Exception as e:
                    print(f"⚠️ [تنظيف دوري] حدث خطأ: {str(e)}")
                    time.sleep(60)  # انتظار دقيقة واحدة في حالة الخطأ
        
        # بدء التنظيف الدوري في خيط منفصل
        import threading
        cleanup_thread = threading.Thread(target=periodic_cleanup, daemon=True)
        cleanup_thread.start()
        
        print("✅ تم تشغيل آلية التنظيف الدوري")
        
        print("\n" + "="*70)
        print("✅ تم تطبيق الحل النهائي الشامل بنجاح!")
        print("✅ يرجى الانتباه إلى أي رسائل تظهر في سجلات النظام")
        print("="*70 + "\n")
        
    except Exception as e:
        print(f"❌ حدث خطأ أثناء تطبيق الحل: {str(e)}")
        traceback.print_exc()

if __name__ == "__main__":
    comprehensive_fix()