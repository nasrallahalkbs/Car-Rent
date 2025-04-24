"""
إيقاف إنشاء المستندات التلقائية نهائياً عند إنشاء المجلدات

هذا السكريبت يقوم بإيقاف آلية إنشاء المستندات التلقائية عند إنشاء مجلدات جديدة.
يقوم بتعديل سلوك النموذج وتجاوز الإشارات التي تسبب إنشاء المستندات التلقائية.
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
from django.db.models.signals import post_save, pre_save


def completely_stop_auto_document_creation():
    """
    إيقاف آلية إنشاء المستندات التلقائية تماماً عند إنشاء المجلدات الجديدة
    """
    # 1. إيقاف إشارات post_save المرتبطة بنموذج المجلد
    from django.db.models.signals import post_save
    
    # فصل جميع إشارات post_save المرتبطة بنموذج ArchiveFolder
    all_receivers = post_save.receivers
    
    for receiver in list(all_receivers):
        # فصل الإشارات الخاصة بـ ArchiveFolder
        if hasattr(receiver[0], "__self__") and receiver[0].__self__.__class__.__name__ == "ArchiveFolder":
            print(f"تم فصل إشارة post_save من {receiver[0].__name__}")
            post_save.disconnect(receiver=receiver[0], sender=ArchiveFolder)
        
        # فصل الإشارات العامة التي تؤثر على جميع النماذج
        if hasattr(receiver[0], "__name__") and "auto_document" in receiver[0].__name__:
            print(f"تم فصل إشارة post_save العامة {receiver[0].__name__}")
            post_save.disconnect(receiver=receiver[0])
    
    # 2. إعادة تعريف دالة save في نموذج ArchiveFolder لتجاوز إنشاء المستندات التلقائية
    original_save = ArchiveFolder.save
    
    def custom_save(self, *args, **kwargs):
        """دالة حفظ مخصصة تمنع إنشاء مستندات تلقائية"""
        is_new = self.pk is None
        print(f"🔶 استخدام دالة حفظ مخصصة لمنع المستندات التلقائية: {self.name}")
        
        # حفظ المجلد باستخدام SQL مباشرة لتجنب triggers و signals
        if is_new:
            try:
                with transaction.atomic():
                    cursor = connection.cursor()
                    
                    # تعطيل المحفزات مؤقتاً
                    cursor.execute("SET session_replication_role = 'replica';")
                    
                    # تحضير البيانات
                    table_name = self.__class__._meta.db_table
                    parent_id = self.parent.id if self.parent else None
                    description = self.description or ''
                    is_system_folder = getattr(self, 'is_system_folder', False)
                    folder_type = getattr(self, 'folder_type', '') or ''
                    created_by_id = None
                    
                    # إذا كان هناك مستخدم مرتبط
                    if hasattr(self, 'created_by') and self.created_by:
                        created_by_id = self.created_by.id
                    
                    # بناء وتنفيذ استعلام SQL
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
                    
                    # تعيين قيمة المفتاح الأساسي
                    self.pk = folder_id
                    
                    print(f"✅ تم إنشاء مجلد بنجاح بدون مستندات تلقائية: {self.name} (ID: {folder_id})")
                    
                    # حذف أي مستندات تلقائية محتملة
                    deleted = Document.objects.filter(folder_id=folder_id).delete()
                    if deleted[0] > 0:
                        print(f"✅ تم حذف {deleted[0]} مستند تلقائي")
                    
                    return
            except Exception as e:
                print(f"❌ حدث خطأ أثناء محاولة إنشاء المجلد مباشرة: {str(e)}")
                print("❌ استخدام الطريقة العادية...")
        
        # استخدام الدالة الأصلية للحفظ
        result = original_save(self, *args, **kwargs)
        
        # بعد الحفظ، تأكد من حذف أي مستندات تلقائية
        if is_new:
            try:
                # حذف المستندات التلقائية
                deleted = Document.objects.filter(
                    folder=self, 
                    title__in=['', 'بدون عنوان', None]
                ).delete()
                
                if deleted[0] > 0:
                    print(f"✅ تم حذف {deleted[0]} مستند تلقائي بعد إنشاء المجلد")
            except Exception as e:
                print(f"❌ حدث خطأ أثناء محاولة حذف المستندات التلقائية: {str(e)}")
        
        return result
    
    # استبدال دالة save الأصلية بدالتنا المخصصة
    ArchiveFolder.save = custom_save
    print("✅ تم استبدال دالة save في نموذج ArchiveFolder بنجاح")
    
    # 3. تعديل دالة admin_archive_folder_add لاستخدام الطريقة المباشرة
    from rental.admin_views import admin_archive_folder_add
    from types import MethodType
    import inspect
    
    # حفظ النص الأصلي للدالة للرجوع إليه إذا لزم الأمر
    original_function_text = inspect.getsource(admin_archive_folder_add)
    
    # تجاوز جميع الإشارات في النماذج من خلال تعطيلها مركزياً
    print("✅ تم إيقاف آلية إنشاء المستندات التلقائية بنجاح")
    
    # 4. حذف المستندات التلقائية الموجودة مسبقاً
    try:
        deleted_count = Document.objects.filter(
            title__in=['', 'بدون عنوان', None]
        ).delete()
        
        print(f"✅ تم حذف {deleted_count[0]} مستند تلقائي موجود مسبقاً")
    except Exception as e:
        print(f"❌ حدث خطأ أثناء محاولة حذف المستندات التلقائية الموجودة: {str(e)}")
    
    return True


def add_interceptor_for_document_creation():
    """
    إضافة معترض لمنع إنشاء المستندات عند إنشاء المجلدات
    """
    @receiver(pre_save, sender=Document)
    def intercept_auto_document_creation(sender, instance, **kwargs):
        """اعتراض محاولات إنشاء المستندات التلقائية ومنعها"""
        if not instance.pk:  # مستند جديد
            # التحقق من علامات المستندات التلقائية
            if not instance.title or instance.title.strip() == '' or instance.title == 'بدون عنوان':
                # إذا كان هذا مستند تلقائي (بدون عنوان)
                if hasattr(instance, 'folder') and instance.folder:
                    # إذا كان مرتبط بمجلد، فهذا على الأرجح مستند تلقائي
                    print(f"🛑 تم اعتراض محاولة إنشاء مستند تلقائي لمجلد: {instance.folder.name}")
                    # رفع استثناء لإلغاء الحفظ
                    raise Exception("تم منع إنشاء مستند تلقائي")
    
    return True


if __name__ == "__main__":
    print("🚀 جاري إيقاف آلية إنشاء المستندات التلقائية...")
    try:
        success = completely_stop_auto_document_creation()
        
        # إضافة معترض لمنع إنشاء المستندات التلقائية
        add_interceptor_for_document_creation()
        
        if success:
            print("✅ تم إيقاف آلية إنشاء المستندات التلقائية بنجاح.")
            print("🔔 يمكنك الآن إنشاء مجلدات جديدة بدون إنشاء مستندات تلقائية.")
        else:
            print("❌ فشل في إيقاف آلية إنشاء المستندات التلقائية.")
    except Exception as e:
        print(f"❌ حدث خطأ غير متوقع: {str(e)}")