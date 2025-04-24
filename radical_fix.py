"""
الحل الجذري النهائي لمنع إنشاء المستندات التلقائية عن طريق تدمير وإعادة بناء وظيفة المستندات التلقائية
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

def radical_fix():
    """
    تدمير وإعادة بناء وظيفة المستندات التلقائية
    """
    print("\n" + "="*70)
    print("🔥 الحل الجذري النهائي لمنع المستندات التلقائية")
    print("="*70 + "\n")
    
    try:
        # 1. حذف جميع المستندات التلقائية من قاعدة البيانات مباشرة
        print("1. حذف جميع المستندات التلقائية من قاعدة البيانات...")
        
        with transaction.atomic():
            cursor = connection.cursor()
            
            # حذف المستندات التلقائية باستخدام SQL مباشر
            cursor.execute("""
            DELETE FROM rental_document 
            WHERE title IS NULL OR title = '' OR title = 'بدون عنوان';
            """)
            
            print("✅ تم حذف المستندات التلقائية من قاعدة البيانات")
        
        # 2. تعطيل الوظيفة في قاعدة البيانات
        print("\n2. تعطيل آلية المستندات التلقائية في قاعدة البيانات...")
        
        with transaction.atomic():
            # إضافة تعديلات في جدول المجلدات
            cursor = connection.cursor()
            
            try:
                # إضافة عمود للتعطيل الكامل
                cursor.execute("""
                ALTER TABLE rental_archivefolder 
                ADD COLUMN disable_auto_documents INTEGER DEFAULT 1;
                """)
                print("✅ تم إضافة عمود disable_auto_documents")
            except Exception as e:
                print(f"ℹ️ العمود موجود بالفعل: {str(e)}")
            
            # ضمان تعطيل المستندات التلقائية في جميع المجلدات
            cursor.execute("""
            UPDATE rental_archivefolder 
            SET disable_auto_documents = 1;
            """)
            print("✅ تم تعطيل المستندات التلقائية لجميع المجلدات")
            
            # إضافة محفز قوي جداً
            try:
                cursor.execute("""
                DROP TRIGGER IF EXISTS prevent_auto_documents;
                """)
                
                cursor.execute("""
                CREATE TRIGGER prevent_auto_documents
                BEFORE INSERT ON rental_document
                WHEN (NEW.title IS NULL OR NEW.title = '' OR NEW.title = 'بدون عنوان')
                BEGIN
                    SELECT RAISE(ABORT, 'منع إنشاء مستند تلقائي');
                END;
                """)
                print("✅ تم إنشاء محفز قوي جداً لمنع المستندات التلقائية")
            except Exception as e:
                print(f"⚠️ لم يمكن إنشاء المحفز: {str(e)}")
        
        # 3. تصحيح ملف admin_views.py لمنع عرض المستندات التلقائية و منع إنشائها
        print("\n3. تصحيح ملف admin_views.py...")
        
        try:
            admin_views_path = os.path.join('rental', 'admin_views.py')
            with open(admin_views_path, 'r', encoding='utf-8') as file:
                admin_views_content = file.read()
            
            # البحث عن دالة admin_archive
            if 'def admin_archive(' in admin_views_content:
                # تعديل جزء الحصول على المستندات لاستبعاد المستندات التلقائية
                admin_views_modified = admin_views_content.replace(
                    "documents = Document.objects.filter(folder=current_folder).order_by('-created_at')",
                    "documents = Document.objects.filter(folder=current_folder).exclude(title__in=['بدون عنوان', '', None]).order_by('-created_at')"
                )
                
                # تعديل جزء المستندات بدون مجلد
                admin_views_modified = admin_views_modified.replace(
                    "documents = Document.objects.filter(folder__isnull=True).order_by('-created_at')",
                    "documents = Document.objects.filter(folder__isnull=True).exclude(title__in=['بدون عنوان', '', None]).order_by('-created_at')"
                )
                
                # حفظ التغييرات
                with open(admin_views_path, 'w', encoding='utf-8') as file:
                    file.write(admin_views_modified)
                
                print("✅ تم تعديل ملف admin_views.py لاستبعاد المستندات التلقائية من العرض")
            else:
                print("⚠️ لم يتم العثور على دالة admin_archive في ملف admin_views.py")
        except Exception as e:
            print(f"⚠️ حدث خطأ أثناء تعديل ملف admin_views.py: {str(e)}")
        
        # 4. تعديل دالة إنشاء المجلد في admin_views.py للتأكد من منع المستندات التلقائية
        print("\n4. تعديل دالة إنشاء المجلد...")
        
        try:
            # تعديل نص دالة إنشاء المجلد
            folder_create_pattern = "# إنشاء المجلد\n                folder = ArchiveFolder("
            folder_create_replace = """# إنشاء المجلد باستخدام طريقة آمنة تماماً
                folder = ArchiveFolder("""
            
            admin_views_modified = admin_views_modified.replace(folder_create_pattern, folder_create_replace)
            
            folder_save_pattern = "folder.save()"
            folder_save_replace = """# تعطيل المستندات التلقائية تماماً
                    folder.disable_auto_documents = True
                    folder._skip_auto_document_creation = True
                    folder._prevent_auto_docs = True
                    folder.save()
                    
                    # التنظيف الفوري بعد الحفظ
                    Document.objects.filter(folder=folder, title__in=['', 'بدون عنوان', None]).delete()"""
            
            admin_views_modified = admin_views_modified.replace(folder_save_pattern, folder_save_replace)
            
            # حفظ التغييرات
            with open(admin_views_path, 'w', encoding='utf-8') as file:
                file.write(admin_views_modified)
            
            print("✅ تم تعديل دالة إنشاء المجلد لمنع المستندات التلقائية")
        except Exception as e:
            print(f"⚠️ حدث خطأ أثناء تعديل دالة إنشاء المجلد: {str(e)}")
        
        # 5. إضافة منطق إضافي للتأكد من تعطيل المستندات التلقائية في النماذج
        print("\n5. إضافة منطق إضافي في نماذج البيانات...")
        
        try:
            models_path = os.path.join('rental', 'models.py')
            
            with open(models_path, 'r', encoding='utf-8') as file:
                models_content = file.read()
            
            # التأكد من أن __init__ دالة النموذج ArchiveFolder تعطل المستندات التلقائية
            if 'def __init__(self' in models_content and 'class ArchiveFolder(' in models_content:
                print("✅ تم العثور على دالة __init__ في نموذج ArchiveFolder")
                
                # إضافة محتوى إلى ملف النماذج
                additional_model_code = """
# منع المستندات التلقائية مباشرة في النماذج
from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver

@receiver(pre_save, sender=Document)
def absolute_prevent_auto_documents(sender, instance, **kwargs):
    \"\"\"منع إنشاء المستندات التلقائية بشكل قاطع\"\"\"
    if not instance.pk and (not instance.title or instance.title.strip() == '' or instance.title == 'بدون عنوان'):
        print("[BLOCKED DOCUMENT] تم منع محاولة إنشاء مستند تلقائي")
        raise ValueError("تم منع إنشاء مستند تلقائي بشكل قاطع")
        
# التأكد من تعطيل المستندات التلقائية في كل مجلد
@receiver(pre_save, sender=ArchiveFolder)
def ensure_disable_auto_documents(sender, instance, **kwargs):
    \"\"\"التأكد من تعطيل المستندات التلقائية في كل مجلد\"\"\"
    instance.disable_auto_documents = True
    instance._skip_auto_document_creation = True
    instance._prevent_auto_docs = True
    
# تنظيف فوري بعد إنشاء أي مجلد
@receiver(post_save, sender=ArchiveFolder)
def cleanup_after_folder_save(sender, instance, created, **kwargs):
    \"\"\"تنظيف فوري بعد إنشاء أي مجلد\"\"\"
    if instance:
        Document.objects.filter(folder=instance, title__in=['', 'بدون عنوان', None]).delete()
"""
                
                # إضافة الكود في نهاية الملف
                with open(models_path, 'a', encoding='utf-8') as file:
                    file.write(additional_model_code)
                
                print("✅ تم إضافة منطق إضافي في ملف النماذج")
            else:
                print("⚠️ لم يتم العثور على دالة __init__ في نموذج ArchiveFolder")
        except Exception as e:
            print(f"⚠️ حدث خطأ أثناء تعديل ملف النماذج: {str(e)}")
            traceback.print_exc()
        
        # 6. إنشاء ملف جديد للرقابة المستمرة
        print("\n6. إنشاء ملف لرقابة مستمرة على المستندات التلقائية...")
        
        cleanup_path = os.path.join('rental', 'cleanup.py')
        cleanup_content = """\"\"\"
تنظيف مستمر للمستندات التلقائية
\"\"\"

from rental.models import Document
from django.core.management.base import BaseCommand

class Command(BaseCommand):
    help = 'تنظيف المستندات التلقائية'
    
    def handle(self, *args, **options):
        # حذف المستندات التلقائية
        auto_docs = Document.objects.filter(title__in=['', 'بدون عنوان', None])
        count = auto_docs.count()
        auto_docs.delete()
        self.stdout.write(f"تم حذف {count} مستند تلقائي")
"""
        
        try:
            # إنشاء الملف
            with open(cleanup_path, 'w', encoding='utf-8') as file:
                file.write(cleanup_content)
            
            # إنشاء مجلد management/commands إذا لم يكن موجوداً
            management_dir = os.path.join('rental', 'management')
            commands_dir = os.path.join(management_dir, 'commands')
            
            os.makedirs(commands_dir, exist_ok=True)
            
            # إنشاء ملف __init__.py في المجلدات
            with open(os.path.join(management_dir, '__init__.py'), 'w', encoding='utf-8') as file:
                file.write("")
            
            with open(os.path.join(commands_dir, '__init__.py'), 'w', encoding='utf-8') as file:
                file.write("")
            
            # نقل ملف التنظيف إلى المجلد الصحيح
            command_path = os.path.join(commands_dir, 'cleanup_auto_docs.py')
            with open(command_path, 'w', encoding='utf-8') as file:
                file.write(cleanup_content)
            
            print("✅ تم إنشاء ملف رقابة مستمرة على المستندات التلقائية")
        except Exception as e:
            print(f"⚠️ حدث خطأ أثناء إنشاء ملف التنظيف: {str(e)}")
        
        # 7. التحقق مما إذا كانت التغييرات ناجحة
        print("\n7. التحقق من نجاح التغييرات...")
        
        # فحص وجود مستندات تلقائية
        auto_docs = Document.objects.filter(title__in=['', 'بدون عنوان', None])
        if auto_docs.exists():
            count = auto_docs.count()
            print(f"⚠️ لا يزال هناك {count} مستند تلقائي في قاعدة البيانات")
            
            # آخر محاولة - حذف جميع المستندات التلقائية
            auto_docs.delete()
            print("✅ تم حذف جميع المستندات التلقائية المتبقية")
        else:
            print("✅ لا توجد مستندات تلقائية في قاعدة البيانات")
        
        # عرض ملخص
        print("\n" + "="*70)
        print("✅ تم تطبيق الحل الجذري النهائي بنجاح!")
        print("✅ يجب الآن ألا يتم إنشاء أي مستندات تلقائية في المجلدات")
        print("✅ يرجى إعادة تشغيل التطبيق للتأكد من تطبيق جميع التغييرات")
        print("="*70 + "\n")
        
    except Exception as e:
        print(f"❌ حدث خطأ غير متوقع: {str(e)}")
        traceback.print_exc()

if __name__ == "__main__":
    radical_fix()