from django.db.models.signals import pre_save, post_save, pre_delete
from django.dispatch import receiver
from .models import ArchiveFolder, Document

# ملف إشارات Django المنفصل - للتحكم في إشارات النماذج
# هذا الملف يتم استدعاؤه في apps.py

# استهداف المشكلة الفعلية: طريقة ربط المستندات التلقائية بالمجلدات
# دعنا نبحث عن المشكلة الحقيقية ونوثقها

print("⚠️ تحميل إشارات منع المستندات التلقائية")

# نقوم بتعطيل التشغيل التلقائي للإشارات لأنها قد تكون مصدر المشكلة
import django.dispatch
original_connect = django.dispatch.Signal.connect

# نقوم بتخزين كل الإشارات المسجلة للفحص
all_signals = []

def debug_connect(self, receiver, sender=None, weak=True, dispatch_uid=None):
    """دالة مخصصة للتحقق من إشارات Django"""
    print(f"⚠️ تسجيل إشارة: {self} -> {receiver.__name__} من {sender}")
    all_signals.append((self, receiver, sender))
    return original_connect(self, receiver, sender, weak, dispatch_uid)

# تعديل الدالة connect في Django لتسجيل جميع الإشارات
django.dispatch.Signal.connect = debug_connect

# مجموعة لتخزين المجلدات التي تم إنشاؤها حديثًا
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
            print(f"🔶 [signals]: محاولة إنشاء مستند جديد مرتبط بالمجلد '{instance.folder.name}'")
            print(f"🔶 [signals]: عنوان المستند: '{instance.title}'")
            
            # #1: تحقق من خاصية skip_auto_document_creation على المجلد
            if hasattr(instance.folder, '_skip_auto_document_creation') and instance.folder._skip_auto_document_creation:
                # المستندات التلقائية عادة لا تحتوي على عنوان أو لها عنوان فارغ
                if not instance.title or not instance.title.strip():
                    print(f"🔶 [signals]: منع مستند تلقائي - العلامة _skip_auto_document_creation موجودة")
                    # إلغاء الحفظ بإثارة استثناء
                    raise Exception("تم منع إنشاء المستند التلقائي - طريقة 1")
                else:
                    print(f"🔶 [signals]: السماح بمستند يدوي رغم علامة المنع - له عنوان: {instance.title}")
            
            # #2: تحقق من وجود المجلد في قائمة المجلدات الجديدة
            elif hasattr(instance.folder, 'name') and instance.folder.name in _new_folders:
                print(f"🔶 [signals]: تم اكتشاف محاولة إنشاء مستند تلقائي للمجلد '{instance.folder.name}'")
                
                # التحقق من أن هذا مستند تلقائي (بدون عنوان عادة)
                if not instance.title or not instance.title.strip():
                    print(f"🔶 [signals]: منع مستند تلقائي للمجلد '{instance.folder.name}' - في قائمة المجلدات الجديدة")
                    # إلغاء الحفظ عن طريق رفع استثناء
                    raise Exception("تم منع إنشاء المستند التلقائي - طريقة 2")
                else:
                    print(f"🔶 [signals]: السماح بإنشاء مستند يدوي للمجلد '{instance.folder.name}'")
            
            # #3: طريقة إضافية للتأكد - للمستندات بدون عناوين
            elif not instance.title or not instance.title.strip():
                print(f"🔶 [signals]: الاشتباه بمستند تلقائي بدون عنوان حتى بدون علامات")
                if 'djangotest' in str(instance.file) or not instance.file:
                    print(f"🔶 [signals]: منع مستند تلقائي بدون عنوان وبدون ملف حقيقي")
                    raise Exception("تم منع إنشاء المستند التلقائي - طريقة 3")
                else:
                    print(f"🔶 [signals]: السماح بمستند بدون عنوان لكن له ملف: {instance.file}")
            
            else:
                print(f"🔶 [signals]: السماح بمستند جديد طبيعي للمجلد '{instance.folder.name}'")

@receiver(post_save, sender=ArchiveFolder)
def cleanup_after_folder_creation(sender, instance, created, **kwargs):
    """تنظيف الإشارات بعد إنشاء المجلد وحذف أي مستندات تلقائية"""
    global _new_folders
    
    if created:
        print(f"🔷 [signals]: تم إنشاء مجلد جديد: {instance.name} بمعرف {instance.pk}")
        
        # استخدام transaction للتأكد من حذف المستندات التلقائية بشكل آمن
        try:
            from django.db import transaction
            with transaction.atomic():
                # الطباعة قبل عملية الحذف
                doc_count = Document.objects.filter(folder=instance).count()
                print(f"🔷 [signals]: وجدنا {doc_count} مستند تلقائي للمجلد '{instance.name}'")
                
                if doc_count > 0:
                    # حذف أي مستندات تلقائية بشكل آمن
                    deleted_count = Document.objects.filter(folder=instance).delete()
                    print(f"🔷 [signals]: تم حذف {deleted_count} مستند تلقائي للمجلد '{instance.name}'")
                else:
                    print(f"🔷 [signals]: لا توجد مستندات تلقائية للمجلد '{instance.name}'")
        except Exception as e:
            print(f"🔷 [signals]: خطأ أثناء تنظيف المستندات التلقائية: {str(e)}")
        
        # تأكد من عدم وجود مستندات مرة أخرى
        doc_count = Document.objects.filter(folder=instance).count()
        if doc_count > 0:
            print(f"🔷 [signals]: لا تزال هناك {doc_count} مستندات تلقائية! محاولة الحذف مرة أخرى...")
            try:
                Document.objects.filter(folder=instance).delete()
                print(f"🔷 [signals]: تم حذف المستندات المتبقية في المحاولة الثانية")
            except Exception as e:
                print(f"🔷 [signals]: فشل في حذف المستندات المتبقية: {str(e)}")
        
        # إزالة المجلد من قائمة المجلدات المميزة
        if hasattr(instance, 'name') and instance.name in _new_folders:
            _new_folders.remove(instance.name)
            print(f"🔷 [signals]: تمت إزالة المجلد '{instance.name}' من قائمة المجلدات المميزة")

# للتأكد من تسجيل الإشارات
print("DEBUG [signals]: تم تسجيل إشارات منع المستندات التلقائية")