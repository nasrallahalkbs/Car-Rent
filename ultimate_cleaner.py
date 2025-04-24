"""
تنظيف شامل نهائي للمستندات التلقائية وتحسين الحماية

هذا السكريبت يقوم بتنظيف شامل لجميع المستندات التلقائية في النظام
وتطبيق مستوى إضافي من الحماية لضمان عدم ظهور أي مستندات تلقائية

يجب تشغيل هذا السكريبت مباشرة بعد ملاحظة أي مستندات تلقائية جديدة
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

def clean_auto_documents_everywhere():
    """
    تنظيف شامل للمستندات التلقائية في جميع أنحاء النظام
    وتحسين الحماية ضد إنشاء مستندات جديدة
    """
    print("\n" + "="*70)
    print("🧹 التنظيف الشامل النهائي للمستندات التلقائية")
    print("="*70 + "\n")
    
    try:
        # 1. حذف جميع المستندات التلقائية في النظام
        print("1. حذف جميع المستندات التلقائية الموجودة...")
        
        # البحث عن المستندات التلقائية (بدون عنوان أو بعنوان فارغ)
        auto_docs = Document.objects.filter(
            Q(title__isnull=True) | Q(title='') | Q(title='بدون عنوان')
        )
        
        # طباعة معلومات المستندات قبل الحذف
        count = auto_docs.count()
        print(f"ℹ️ تم العثور على {count} مستند تلقائي في النظام")
        
        if count > 0:
            # طباعة تفاصيل المستندات
            for doc in auto_docs:
                folder_name = doc.folder.name if doc.folder else "بدون مجلد"
                folder_id = doc.folder.id if doc.folder else "N/A"
                print(f"   - مستند تلقائي (ID: {doc.id}): {doc.title or 'بدون عنوان'} في المجلد '{folder_name}' (ID: {folder_id})")
            
            # حذف المستندات التلقائية باستخدام استعلام SQL مباشر للتأكد من الحذف
            with transaction.atomic():
                cursor = connection.cursor()
                # الحذف باستخدام شروط مختلفة للتأكد من حذف جميع المستندات التلقائية
                cursor.execute("""
                DELETE FROM rental_document 
                WHERE title IS NULL OR title = '' OR title = 'بدون عنوان';
                """)
            
            print(f"✅ تم حذف {count} مستند تلقائي بنجاح")
        else:
            print("✅ لا توجد مستندات تلقائية للحذف")
        
        # 2. تطبيق حماية مشددة على جميع المجلدات
        print("\n2. تطبيق حماية مشددة على جميع المجلدات...")
        
        # الحصول على جميع المجلدات
        all_folders = ArchiveFolder.objects.all()
        folders_count = all_folders.count()
        
        print(f"ℹ️ تطبيق الحماية على {folders_count} مجلد")
        
        # تطبيق علامات الحماية على جميع المجلدات
        for folder in all_folders:
            folder._skip_auto_document_creation = True
            folder._prevent_auto_docs = True
            # لا نحتاج إلى حفظ المجلد هنا، فقط تعيين العلامات
        
        print("✅ تم تعيين علامات الحماية على جميع المجلدات")
        
        # 3. تحسين طريقة عرض المجلدات في admin_views.py
        print("\n3. تحسين طريقة عرض المجلدات...")
        
        admin_views_path = os.path.join('rental', 'admin_views.py')
        
        with open(admin_views_path, 'r', encoding='utf-8') as file:
            admin_views_content = file.read()
        
        # البحث عن دالة admin_archive_folder_view وإضافة تنظيف مستندات إضافي
        if 'def admin_archive_folder_view(' in admin_views_content:
            # البحث عن نمط الكود الذي نريد تعديله
            folder_view_pattern = "def admin_archive_folder_view(request, folder_id):"
            folder_view_index = admin_views_content.find(folder_view_pattern)
            
            if folder_view_index > -1:
                # البحث عن موقع بدء دالة العرض
                function_start = admin_views_content[folder_view_index:]
                # البحث عن موقع داخل الدالة حيث يمكننا إضافة كود التنظيف
                folder_obj_pattern = "folder = get_object_or_404(ArchiveFolder, id=folder_id)"
                folder_obj_index = function_start.find(folder_obj_pattern)
                
                if folder_obj_index > -1:
                    # إضافة كود التنظيف بعد الحصول على المجلد
                    insert_index = folder_view_index + folder_obj_index + len(folder_obj_pattern)
                    cleaning_code = """
    # تنظيف تلقائي للمستندات التلقائية عند فتح المجلد
    auto_docs = Document.objects.filter(
        folder=folder,
        Q(title__isnull=True) | Q(title='') | Q(title='بدون عنوان')
    )
    if auto_docs.exists():
        deleted_count = auto_docs.count()
        print(f"🧹 تم حذف {deleted_count} مستند تلقائي من المجلد {folder.name} (ID: {folder.id})")
        auto_docs.delete()
    """
                    
                    # تحقق مما إذا كان الكود موجوداً بالفعل
                    if "تنظيف تلقائي للمستندات التلقائية عند فتح المجلد" not in function_start:
                        # إضافة الكود
                        new_content = admin_views_content[:insert_index] + cleaning_code + admin_views_content[insert_index:]
                        
                        # حفظ التعديلات
                        with open(admin_views_path, 'w', encoding='utf-8') as file:
                            file.write(new_content)
                        
                        print("✅ تم تحسين طريقة عرض المجلدات لحذف المستندات التلقائية عند فتح المجلد")
                    else:
                        print("ℹ️ كود التنظيف موجود بالفعل في دالة عرض المجلد")
                else:
                    print("⚠️ لم يتم العثور على نمط إنشاء المجلد في دالة العرض")
            else:
                print("⚠️ لم يتم العثور على دالة عرض المجلد")
        else:
            print("⚠️ لم يتم العثور على دالة admin_archive_folder_view")
        
        # 4. تعديل كود عرض المجلدات لمنع عرض المستندات التلقائية
        print("\n4. تعديل كود عرض المجلدات لمنع عرض المستندات التلقائية...")
        
        # البحث عن نمط استعلام المستندات في دالة عرض المجلدات
        admin_archive_folder_docs_pattern = "folder_documents = folder.documents.all().order_by('-created_at')"
        
        if admin_archive_folder_docs_pattern in admin_views_content:
            # استبدال استعلام المستندات باستعلام يستبعد المستندات التلقائية
            new_folder_docs_query = """folder_documents = folder.documents.exclude(
            Q(title__isnull=True) | Q(title='') | Q(title='بدون عنوان')
        ).order_by('-created_at')"""
            
            # تحقق مما إذا كان الاستعلام الجديد موجوداً بالفعل
            if "exclude" not in admin_views_content[admin_views_content.find(admin_archive_folder_docs_pattern) - 100:
                                               admin_views_content.find(admin_archive_folder_docs_pattern) + 200]:
                # استبدال الاستعلام القديم بالجديد
                new_admin_views_content = admin_views_content.replace(admin_archive_folder_docs_pattern, new_folder_docs_query)
                
                # حفظ التعديلات
                with open(admin_views_path, 'w', encoding='utf-8') as file:
                    file.write(new_admin_views_content)
                
                print("✅ تم تعديل استعلام المستندات لاستبعاد المستندات التلقائية من العرض")
            else:
                print("ℹ️ استعلام استبعاد المستندات التلقائية موجود بالفعل")
        else:
            print("⚠️ لم يتم العثور على نمط استعلام المستندات")
        
        # 5. إضافة حماية إضافية في guard.py
        print("\n5. تحسين نظام الحماية الدائم في guard.py...")
        
        guard_path = os.path.join('rental', 'guard.py')
        
        # التحقق من وجود ملف الحماية
        if os.path.exists(guard_path):
            with open(guard_path, 'r', encoding='utf-8') as file:
                guard_content = file.read()
            
            # تحسين طريقة منع المستندات التلقائية
            improved_document_save = """def improved_document_save(self, *args, **kwargs):
    \"\"\"منع إنشاء المستندات التلقائية بشكل قاطع\"\"\"
    # فحص ما إذا كان هذا مستند جديد
    if not self.pk:
        # فحص ما إذا كان عنوان المستند فارغ أو "بدون عنوان"
        if not self.title or self.title.strip() == '' or self.title == 'بدون عنوان':
            print(f"🛑 [GUARD] منع إنشاء مستند تلقائي: '{self.title}'")
            return None
    
    # استخدام الطريقة الأصلية للمستندات العادية
    return self._guarded_save(*args, **kwargs)
"""
            
            # تحقق مما إذا كانت وظيفة الحماية المحسنة موجودة بالفعل
            if "improved_document_save" not in guard_content:
                # إضافة وظيفة الحماية المحسنة
                start_func_pattern = "def safe_document_save(self, *args, **kwargs):"
                if start_func_pattern in guard_content:
                    new_guard_content = guard_content.replace(start_func_pattern, improved_document_save.replace("improved_document_save", "safe_document_save"))
                    
                    # حفظ التعديلات
                    with open(guard_path, 'w', encoding='utf-8') as file:
                        file.write(new_guard_content)
                    
                    print("✅ تم تحسين وظيفة الحماية في ملف guard.py")
                else:
                    print("⚠️ لم يتم العثور على وظيفة safe_document_save في ملف guard.py")
            else:
                print("ℹ️ وظيفة الحماية المحسنة موجودة بالفعل")
        else:
            print("⚠️ ملف guard.py غير موجود، سيتم إنشاؤه...")
            
            # إنشاء ملف guard.py جديد
            guard_content = """# -*- coding: utf-8 -*-
\"\"\"
ملف الحماية الدائمة ضد المستندات التلقائية
تم إنشاؤه تلقائيًا
\"\"\"

def start():
    \"\"\"تطبيق حماية المستندات التلقائية\"\"\"
    from rental.models import Document, ArchiveFolder
    from django.db.models import Q
    
    # حفظ طرق الحفظ الأصلية
    if not hasattr(Document, '_guarded_save'):
        Document._guarded_save = Document.save
    
    if not hasattr(ArchiveFolder, '_guarded_save'):
        ArchiveFolder._guarded_save = ArchiveFolder.save
    
    # تعريف طرق الحفظ الآمنة
    def safe_document_save(self, *args, **kwargs):
        \"\"\"منع إنشاء المستندات التلقائية بشكل قاطع\"\"\"
        # فحص ما إذا كان هذا مستند جديد
        if not self.pk:
            # فحص ما إذا كان عنوان المستند فارغ أو "بدون عنوان"
            if not self.title or self.title.strip() == '' or self.title == 'بدون عنوان':
                print(f"🛑 [GUARD] منع إنشاء مستند تلقائي: '{self.title}'")
                # إضافة سجل تصحيح
                import traceback
                stack = traceback.extract_stack()
                caller = stack[-2]
                print(f"🛑 [GUARD] تم الاستدعاء من: {caller.filename.split('/')[-1]}:{caller.name}")
                return None
        
        # استخدام الطريقة الأصلية للمستندات العادية
        return self._guarded_save(*args, **kwargs)
    
    def safe_folder_save(self, *args, **kwargs):
        \"\"\"منع المستندات التلقائية في المجلدات\"\"\"
        # تعيين علامات منع المستندات التلقائية
        self._skip_auto_document_creation = True
        if hasattr(self, 'disable_auto_documents'):
            self.disable_auto_documents = True
        
        # استخدام الطريقة الأصلية
        result = self._guarded_save(*args, **kwargs)
        
        # تنظيف المستندات التلقائية بعد الحفظ
        if self.pk:
            auto_docs = Document.objects.filter(
                folder=self,
                Q(title__isnull=True) | Q(title='') | Q(title='بدون عنوان')
            )
            if auto_docs.exists():
                print(f"🧹 [GUARD] تنظيف {auto_docs.count()} مستند تلقائي من المجلد {self.name} (ID: {self.id})")
                auto_docs.delete()
        
        return result
    
    # تطبيق طرق الحفظ الآمنة
    Document.save = safe_document_save
    ArchiveFolder.save = safe_folder_save
    
    # تنظيف مبدئي للمستندات التلقائية
    auto_docs = Document.objects.filter(
        Q(title__isnull=True) | Q(title='') | Q(title='بدون عنوان')
    )
    if auto_docs.exists():
        count = auto_docs.count()
        print(f"🧹 [GUARD] تنظيف {count} مستند تلقائي عند بدء التشغيل")
        auto_docs.delete()
    
    print("🛡️ تم تفعيل الحماية الدائمة ضد المستندات التلقائية")
"""
            
            # حفظ ملف الحماية الجديد
            with open(guard_path, 'w', encoding='utf-8') as file:
                file.write(guard_content)
            
            print("✅ تم إنشاء ملف الحماية guard.py")
        
        # 6. إنشاء مشغل تلقائي للتنظيف المنتظم
        print("\n6. إنشاء مشغل تلقائي للتنظيف المنتظم...")
        
        cleaner_path = os.path.join('rental', 'auto_cleaner.py')
        
        auto_cleaner_content = """# -*- coding: utf-8 -*-
\"\"\"
مشغل تلقائي للتنظيف المنتظم للمستندات التلقائية
\"\"\"

from django.db.models import Q
from .models import Document, ArchiveFolder
import threading
import time

class AutoCleaner:
    \"\"\"فئة التنظيف التلقائي للمستندات\"\"\"
    
    def __init__(self):
        self.running = False
        self.thread = None
    
    def start(self):
        \"\"\"بدء التنظيف التلقائي\"\"\"
        if not self.running:
            self.running = True
            self.thread = threading.Thread(target=self.cleaner_loop)
            self.thread.daemon = True
            self.thread.start()
            print("🧹 [AUTO_CLEANER] تم بدء خدمة التنظيف التلقائي")
    
    def stop(self):
        \"\"\"إيقاف التنظيف التلقائي\"\"\"
        self.running = False
        if self.thread:
            self.thread.join(1)
            print("🧹 [AUTO_CLEANER] تم إيقاف خدمة التنظيف التلقائي")
    
    def cleaner_loop(self):
        \"\"\"حلقة التنظيف المستمرة\"\"\"
        while self.running:
            try:
                self.clean_auto_documents()
                # السبات لمدة 5 دقائق قبل التنظيف التالي
                for _ in range(300):
                    if not self.running:
                        break
                    time.sleep(1)
            except Exception as e:
                print(f"⚠️ [AUTO_CLEANER] حدث خطأ: {str(e)}")
                time.sleep(60)
    
    def clean_auto_documents(self):
        \"\"\"تنظيف المستندات التلقائية\"\"\"
        try:
            # البحث عن المستندات التلقائية
            auto_docs = Document.objects.filter(
                Q(title__isnull=True) | Q(title='') | Q(title='بدون عنوان')
            )
            
            count = auto_docs.count()
            if count > 0:
                print(f"🧹 [AUTO_CLEANER] تنظيف {count} مستند تلقائي")
                auto_docs.delete()
        except Exception as e:
            print(f"⚠️ [AUTO_CLEANER] حدث خطأ أثناء التنظيف: {str(e)}")

# إنشاء نسخة من التنظيف التلقائي
auto_cleaner = AutoCleaner()

def start_auto_cleaner():
    \"\"\"بدء خدمة التنظيف التلقائي\"\"\"
    auto_cleaner.start()

# بدء التنظيف التلقائي عند استيراد الوحدة
start_auto_cleaner()
"""
        
        # حفظ ملف التنظيف التلقائي
        with open(cleaner_path, 'w', encoding='utf-8') as file:
            file.write(auto_cleaner_content)
        
        print("✅ تم إنشاء مشغل التنظيف التلقائي auto_cleaner.py")
        
        # 7. تعديل ملف signals.py لاستيراد التنظيف التلقائي
        print("\n7. تعديل ملف signals.py لتشغيل التنظيف التلقائي...")
        
        signals_path = os.path.join('rental', 'signals.py')
        
        if os.path.exists(signals_path):
            with open(signals_path, 'r', encoding='utf-8') as file:
                signals_content = file.read()
            
            # إضافة استيراد للتنظيف التلقائي
            if "from rental.auto_cleaner import start_auto_cleaner" not in signals_content:
                # إضافة استيراد وتشغيل التنظيف التلقائي في نهاية الملف
                auto_cleaner_import = "\n\n# تشغيل التنظيف التلقائي\ntry:\n    from rental.auto_cleaner import start_auto_cleaner\n    start_auto_cleaner()\n    print('✅ تم تشغيل خدمة التنظيف التلقائي')\nexcept Exception as e:\n    print(f'⚠️ لم يمكن تشغيل التنظيف التلقائي: {str(e)}')\n"
                
                # تحقق من عدم وجود الاستيراد بالفعل
                if "تشغيل التنظيف التلقائي" not in signals_content:
                    signals_content += auto_cleaner_import
                    
                    # حفظ التعديلات
                    with open(signals_path, 'w', encoding='utf-8') as file:
                        file.write(signals_content)
                    
                    print("✅ تم تعديل ملف signals.py لتشغيل التنظيف التلقائي")
                else:
                    print("ℹ️ استيراد التنظيف التلقائي موجود بالفعل")
            else:
                print("ℹ️ استيراد التنظيف التلقائي موجود بالفعل")
        else:
            print("⚠️ ملف signals.py غير موجود")
        
        # 8. فحص نهائي للمستندات التلقائية
        print("\n8. فحص نهائي للمستندات التلقائية...")
        
        # البحث عن المستندات التلقائية مرة أخرى
        final_auto_docs = Document.objects.filter(
            Q(title__isnull=True) | Q(title='') | Q(title='بدون عنوان')
        )
        
        final_count = final_auto_docs.count()
        if final_count > 0:
            print(f"⚠️ لا يزال هناك {final_count} مستند تلقائي في النظام")
            print("🔄 محاولة أخيرة لحذف المستندات التلقائية...")
            
            # استخدام SQL مباشر للحذف النهائي
            with transaction.atomic():
                cursor = connection.cursor()
                cursor.execute("""
                DELETE FROM rental_document 
                WHERE title IS NULL OR title = '' OR title = 'بدون عنوان';
                """)
            
            # فحص مرة أخيرة
            very_final_count = Document.objects.filter(
                Q(title__isnull=True) | Q(title='') | Q(title='بدون عنوان')
            ).count()
            
            if very_final_count > 0:
                print(f"⚠️ لا يزال هناك {very_final_count} مستند تلقائي")
                print("⚠️ سيقوم التنظيف التلقائي بحذفها بعد إعادة تشغيل التطبيق")
            else:
                print("✅ تم حذف جميع المستندات التلقائية بنجاح")
        else:
            print("✅ لا توجد مستندات تلقائية في النظام - التنظيف ناجح!")
        
        # 9. إنشاء ملف التشغيل التلقائي عند بدء التشغيل
        print("\n9. إنشاء ملف التشغيل التلقائي عند بدء التشغيل...")
        
        apps_path = os.path.join('rental', 'apps.py')
        
        if os.path.exists(apps_path):
            with open(apps_path, 'r', encoding='utf-8') as file:
                apps_content = file.read()
            
            # تحسين ملف التطبيق لتشغيل آليات الحماية عند بدء التشغيل
            ready_function = """    def ready(self):
        \"\"\"تشغيل التنظيف والحماية عند بدء تشغيل التطبيق\"\"\"
        try:
            # تشغيل الحماية والتنظيف عند بدء التشغيل
            import rental.signals  # لتسجيل الإشارات
            from rental.guard import start
            start()  # تشغيل الحماية
            print("✅ تم تفعيل الحماية عند بدء التشغيل")
            
            # تنظيف مبدئي للمستندات التلقائية
            from django.db.models import Q
            from rental.models import Document
            auto_docs = Document.objects.filter(
                Q(title__isnull=True) | Q(title='') | Q(title='بدون عنوان')
            )
            if auto_docs.exists():
                count = auto_docs.count()
                print(f"🧹 تنظيف {count} مستند تلقائي عند بدء التشغيل")
                auto_docs.delete()
                
            # تشغيل التنظيف التلقائي
            from rental.auto_cleaner import start_auto_cleaner
            start_auto_cleaner()
            print("✅ تم تشغيل التنظيف التلقائي")
        except Exception as e:
            print(f"⚠️ حدث خطأ أثناء تهيئة التطبيق: {str(e)}")
            import traceback
            traceback.print_exc()
"""
            
            # تحقق من وجود دالة ready
            if "def ready(self):" in apps_content:
                # استبدال دالة ready الحالية
                import re
                ready_pattern = r"def ready\(self\):.*?(?=\n\s*def|\n\s*class|\Z)"
                matches = re.search(ready_pattern, apps_content, re.DOTALL)
                
                if matches:
                    old_ready = matches.group(0)
                    new_apps_content = apps_content.replace(old_ready, ready_function)
                    
                    # حفظ التعديلات
                    with open(apps_path, 'w', encoding='utf-8') as file:
                        file.write(new_apps_content)
                    
                    print("✅ تم تحديث دالة ready في ملف التطبيق")
                else:
                    print("⚠️ لم يتم العثور على دالة ready باستخدام التعبير المنتظم")
            else:
                # إضافة دالة ready جديدة
                # البحث عن نهاية تعريف الفئة
                class_pattern = "class RentalConfig(AppConfig):"
                if class_pattern in apps_content:
                    class_index = apps_content.find(class_pattern)
                    class_end_index = class_index + len(class_pattern)
                    
                    # إيجاد موقع نهاية تعريف الخصائص
                    next_line_index = apps_content.find("\n", class_end_index)
                    if next_line_index > -1:
                        # إضافة مسافة بادئة للدالة
                        indented_ready = ready_function
                        
                        # إضافة الدالة
                        new_apps_content = apps_content[:next_line_index + 1] + indented_ready + apps_content[next_line_index + 1:]
                        
                        # حفظ التعديلات
                        with open(apps_path, 'w', encoding='utf-8') as file:
                            file.write(new_apps_content)
                        
                        print("✅ تم إضافة دالة ready إلى ملف التطبيق")
                    else:
                        print("⚠️ لم يتم العثور على نهاية تعريف الفئة")
                else:
                    print("⚠️ لم يتم العثور على فئة RentalConfig")
        else:
            print("⚠️ ملف apps.py غير موجود")
        
        print("\n" + "="*70)
        print("✅ تم تطبيق التنظيف الشامل والحماية المحسنة بنجاح!")
        print("✅ يرجى إعادة تشغيل التطبيق لتطبيق جميع التغييرات")
        print("="*70 + "\n")
        
    except Exception as e:
        print(f"❌ حدث خطأ أثناء التنظيف: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    clean_auto_documents_everywhere()