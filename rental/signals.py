from django.db.models.signals import pre_save, post_save, pre_delete
from django.dispatch import receiver
from .models import ArchiveFolder, Document

# ملف إشارات Django المنفصل - للتحكم في إشارات النماذج
# هذا الملف يتم استدعاؤه في apps.py

# عجموعة لتخزين المجلدات التي تم إنشاؤها حديثًا
_new_folders = set()

@receiver(pre_save, sender=ArchiveFolder)
def prevent_auto_document_creation_on_folder_creation(sender, instance, **kwargs):
    """تمييز المجلدات الجديدة لمنع إنشاء مستندات تلقائية"""
    if not instance.pk:  # إذا كان هذا مجلد جديد
        if hasattr(instance, 'name') and instance.name:
            _new_folders.add(instance.name)
            print(f"DEBUG [signals]: تم تمييز المجلد الجديد '{instance.name}' لمنع المستندات التلقائية")
            # إضافة علامة خاصة على المجلد نفسه
            instance._skip_auto_document_creation = True
            # طباعة كل المجلدات المميزة الآن
            print(f"DEBUG [signals]: قائمة المجلدات المميزة حاليًا: {_new_folders}")

@receiver(pre_save, sender=Document)
def prevent_auto_document_creation(sender, instance, **kwargs):
    """منع إنشاء المستندات التلقائية المرتبطة بمجلدات جديدة"""
    global _new_folders
    
    # حالة المستند الجديد
    if not instance.pk:
        # تحقق مما إذا كان هذا المستند مرتبط بمجلد
        if instance.folder:
            # تحقق مما إذا كان المجلد مميزًا كمجلد جديد
            if hasattr(instance.folder, 'name') and instance.folder.name in _new_folders:
                print(f"DEBUG [signals]: تم اكتشاف محاولة إنشاء مستند تلقائي للمجلد '{instance.folder.name}'")
                
                # التحقق من أن هذا مستند تلقائي (بدون عنوان عادة)
                if not instance.title or not instance.title.strip():
                    print(f"DEBUG [signals]: تم منع إنشاء مستند تلقائي للمجلد '{instance.folder.name}'")
                    # إلغاء الحفظ عن طريق رفع استثناء
                    raise Exception("تم منع إنشاء المستند التلقائي")
                else:
                    print(f"DEBUG [signals]: السماح بإنشاء مستند يدوي للمجلد '{instance.folder.name}'")
            
            # تحقق من العلامة الخاصة على المجلد (طريقة بديلة)
            elif hasattr(instance.folder, '_skip_auto_document_creation') and instance.folder._skip_auto_document_creation:
                if not instance.title or not instance.title.strip():
                    print(f"DEBUG [signals]: تم منع إنشاء مستند تلقائي باستخدام العلامة الخاصة")
                    # إلغاء الحفظ عن طريق رفع استثناء
                    raise Exception("تم منع إنشاء المستند التلقائي")

@receiver(post_save, sender=ArchiveFolder)
def cleanup_after_folder_creation(sender, instance, created, **kwargs):
    """تنظيف الإشارات بعد إنشاء المجلد وحذف أي مستندات تلقائية"""
    global _new_folders
    
    if created:
        # محاولة حذف المستندات التلقائية
        try:
            # الطباعة قبل عملية الحذف
            doc_count = Document.objects.filter(folder=instance).count()
            print(f"DEBUG [signals]: تم العثور على {doc_count} مستند تلقائي للمجلد '{instance.name}'")
            
            # حذف أي مستندات تلقائية
            Document.objects.filter(folder=instance).delete()
            
            print(f"DEBUG [signals]: تم تنظيف المستندات التلقائية بعد إنشاء المجلد '{instance.name}'")
        except Exception as e:
            print(f"DEBUG [signals]: خطأ أثناء تنظيف المستندات التلقائية: {str(e)}")
        
        # إزالة المجلد من قائمة المجلدات المميزة
        if hasattr(instance, 'name') and instance.name in _new_folders:
            _new_folders.remove(instance.name)
            print(f"DEBUG [signals]: تمت إزالة المجلد '{instance.name}' من قائمة المجلدات المميزة")

# للتأكد من تسجيل الإشارات
print("DEBUG [signals]: تم تسجيل إشارات منع المستندات التلقائية")