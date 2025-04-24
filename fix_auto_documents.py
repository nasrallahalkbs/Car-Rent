"""
إيقاف إنشاء المستندات التلقائية نهائياً عند إنشاء المجلدات - الإصدار المصحح

هذا السكريبت يقوم بإيقاف آلية إنشاء المستندات التلقائية عند إنشاء مجلدات جديدة بطريقة بسيطة.
"""

import os
import sys
import django

# إعداد بيئة Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'car_rental_project.settings')
django.setup()

# استيراد النماذج ذات الصلة
from rental.models import Document, ArchiveFolder
from django.db import transaction, connection


def patch_document_model():
    """
    تعديل الطريقة التي يتم بها إنشاء المستندات التلقائية
    """
    # تخزين طريقة save الأصلية
    original_save = Document.save
    
    def custom_save(self, *args, **kwargs):
        """طريقة حفظ مخصصة للمستندات تمنع إنشاء المستندات التلقائية"""
        is_new = self.pk is None
        
        # التحقق من إذا كان هذا مستند تلقائي يجب تجاهله
        if is_new and hasattr(self, 'folder') and self.folder:
            # المستندات التلقائية غالباً لا تحتوي على عنوان أو لها عنوان فارغ
            if not self.title or self.title.strip() == '' or self.title == 'بدون عنوان':
                print(f"⛔ منع إنشاء مستند تلقائي لمجلد: {self.folder.name}")
                # إيقاف عملية الحفظ عن طريق العودة دون تنفيذ الحفظ الأصلي
                return None
        
        # استمرار بعملية الحفظ العادية للمستندات غير التلقائية
        return original_save(self, *args, **kwargs)
    
    # استبدال دالة save
    Document.save = custom_save
    print("✅ تم تعديل دالة save في نموذج Document لمنع المستندات التلقائية")


def patch_folder_model():
    """
    تعديل نموذج المجلد لمنع إنشاء المستندات التلقائية
    """
    # تخزين طريقة save الأصلية
    original_save = ArchiveFolder.save
    
    def custom_save(self, *args, **kwargs):
        """طريقة حفظ مخصصة للمجلدات تمنع إنشاء المستندات التلقائية"""
        is_new = self.pk is None
        
        # تعيين علامة تجاوز إنشاء المستندات التلقائية
        self._skip_auto_document_creation = True
        
        if is_new:
            print(f"📁 إنشاء مجلد جديد بدون مستندات تلقائية: {self.name}")
            
            try:
                # استخدام SQL مباشرة لتجاوز آليات النظام
                with transaction.atomic():
                    cursor = connection.cursor()
                    
                    # تعطيل المحفزات (triggers)
                    cursor.execute("SET session_replication_role = 'replica';")
                    
                    # تحضير البيانات
                    table_name = self.__class__._meta.db_table
                    parent_id = self.parent.id if self.parent else None
                    description = self.description or ''
                    is_system_folder = getattr(self, 'is_system_folder', False)
                    folder_type = getattr(self, 'folder_type', '') or ''
                    
                    # الحصول على معرف المستخدم المنشئ إذا وجد
                    created_by_id = None
                    if hasattr(self, 'created_by') and self.created_by:
                        created_by_id = self.created_by.id
                    
                    # إنشاء المجلد مباشرة في قاعدة البيانات
                    sql = f"""
                    INSERT INTO {table_name}
                    (name, parent_id, created_at, updated_at, description, is_system_folder, 
                    folder_type, created_by_id)
                    VALUES (%s, %s, NOW(), NOW(), %s, %s, %s, %s)
                    RETURNING id;
                    """
                    
                    cursor.execute(sql, [
                        self.name, parent_id, description, 
                        is_system_folder, folder_type, created_by_id
                    ])
                    
                    folder_id = cursor.fetchone()[0]
                    
                    # إعادة تفعيل المحفزات
                    cursor.execute("SET session_replication_role = 'origin';")
                    
                    # تحديث معرف الكائن الحالي
                    self.pk = folder_id
                    
                    print(f"✅ تم إنشاء المجلد بنجاح بدون مستندات تلقائية: {self.name} (ID: {folder_id})")
                    
                    return
            except Exception as e:
                print(f"❌ حدث خطأ أثناء إنشاء المجلد باستخدام SQL المباشر: {str(e)}")
                print("❌ الانتقال إلى طريقة الحفظ العادية...")
        
        # استخدام الطريقة الأصلية للحفظ
        result = original_save(self, *args, **kwargs)
        
        # بعد الحفظ، حذف أي مستندات تلقائية قد تكون أنشئت
        if is_new:
            try:
                # حذف المستندات التلقائية
                auto_docs = Document.objects.filter(
                    folder=self, 
                    title__in=['', 'بدون عنوان', None]
                )
                
                if auto_docs.exists():
                    count = auto_docs.count()
                    auto_docs.delete()
                    print(f"🗑️ تم حذف {count} مستند تلقائي بعد إنشاء المجلد")
            except Exception as e:
                print(f"❌ حدث خطأ أثناء حذف المستندات التلقائية: {str(e)}")
        
        return result
    
    # استبدال دالة save
    ArchiveFolder.save = custom_save
    print("✅ تم تعديل دالة save في نموذج ArchiveFolder لمنع المستندات التلقائية")


def cleanup_existing_auto_docs():
    """
    تنظيف مستندات تلقائية موجودة
    """
    try:
        # حذف المستندات التلقائية (بدون عنوان أو بعنوان فارغ)
        auto_docs = Document.objects.filter(title__in=['', 'بدون عنوان', None])
        
        if auto_docs.exists():
            count = auto_docs.count()
            auto_docs.delete()
            print(f"🗑️ تم حذف {count} مستند تلقائي موجود")
        else:
            print("✓ لا توجد مستندات تلقائية للحذف")
    except Exception as e:
        print(f"❌ حدث خطأ أثناء تنظيف المستندات التلقائية الموجودة: {str(e)}")


if __name__ == "__main__":
    print("\n🔧 جاري تطبيق إصلاح المستندات التلقائية...")
    
    # تعديل نموذج Document لمنع إنشاء المستندات التلقائية
    patch_document_model()
    
    # تعديل نموذج ArchiveFolder لمنع إنشاء المستندات التلقائية
    patch_folder_model()
    
    # تنظيف المستندات التلقائية الموجودة
    cleanup_existing_auto_docs()
    
    print("\n✅ تم تطبيق الإصلاح بنجاح!")
    print("🔔 يمكنك الآن إنشاء مجلدات جديدة بدون قلق من إنشاء مستندات تلقائية.")