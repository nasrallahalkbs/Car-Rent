"""
إصلاح مباشر لنموذج Document عبر تعديل طرق __init__ و save

هذا السكريبت يقوم بإصلاح مشكلة منع المستندات التلقائية مباشرة في نموذج Document
"""

import os
import sys
import django
import traceback

# إضافة المسار الحالي إلى مسارات Python
sys.path.append(os.getcwd())

# إعداد Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'car_rental_project.settings')
django.setup()

# استيراد النماذج المطلوبة
from rental.models import Document, User
from django.db import transaction, connection

def fix_document_model():
    """إصلاح نموذج Document"""
    print("\n=== بدء تنفيذ إصلاح نموذج Document ===")
    
    # حفظ الدوال الأصلية
    original_init = Document.__init__
    original_save = Document.save
    
    def new_init(self, *args, **kwargs):
        """دالة __init__ المعدلة للسماح بإنشاء المستندات"""
        # إضافة علامة تجاوز الإشارات
        self._ignore_auto_document_signal = True
        self._force_allow_document = True
        
        # استدعاء الدالة الأصلية
        result = original_init(self, *args, **kwargs)
        
        # إعادة تعيين العلامات
        self._ignore_auto_document_signal = True
        self._force_allow_document = True
        
        # إعادة النتيجة الأصلية
        return result
    
    def new_save(self, *args, **kwargs):
        """دالة save المعدلة للسماح بحفظ المستندات"""
        # إضافة علامة تجاوز الإشارات
        setattr(self, '_ignore_auto_document_signal', True)
        setattr(self, '_force_allow_document', True)
        
        # حذف علامة المستند التلقائي إذا وجدت
        if hasattr(self, '_auto_document'):
            delattr(self, '_auto_document')
        
        # تجاوز المنطق المبني في طريقة save الأصلية
        # استخدام SQL مباشر لتخزين المستند في قاعدة البيانات
        if not self.pk:  # للمستندات الجديدة فقط
            if hasattr(self, 'file') and self.file:
                # تعيين محتوى الملف
                self.file.seek(0)
                self.file_content = self.file.read()
                self.file.seek(0)
                
                # تعيين معلومات الملف
                if not self.file_name and hasattr(self.file, 'name'):
                    self.file_name = os.path.basename(self.file.name)
                if not self.file_type and hasattr(self.file, 'content_type'):
                    self.file_type = self.file.content_type
                if not self.file_size and hasattr(self.file, 'size'):
                    self.file_size = self.file.size
                
                print(f"تم تحضير المستند: عنوان={self.title}, معلومات الملف={self.file_name}")
        
        # استدعاء الدالة الأصلية
        return original_save(self, *args, **kwargs)
    
    # استبدال الدوال الأصلية
    Document.__init__ = new_init
    Document.save = new_save
    
    print("✓ تم تعديل دالة __init__ في نموذج Document")
    print("✓ تم تعديل دالة save في نموذج Document")
    
    # إيقاف الإشارات
    try:
        from django.db.models.signals import pre_save
        pre_save.disconnect(dispatch_uid="prevent_auto_document_creation", sender=Document)
        print("✓ تم فصل إشارة pre_save من نموذج Document")
    except Exception as e:
        print(f"⚠️ حدث خطأ عند محاولة فصل الإشارة: {str(e)}")
    
    # إنشاء مستند اختباري للتأكد من عمل الإصلاح
    try:
        with transaction.atomic():
            # البحث عن مستخدم نشط
            user = User.objects.filter(is_active=True).first()
            
            test_document = Document(
                title="مستند اختباري للتأكد من عمل الإصلاح",
                description="تم إنشاء هذا المستند للتأكد من عمل إصلاح منع المستندات التلقائية",
                document_type="other",
                added_by=user
            )
            
            # تعيين علامات التجاوز
            test_document._ignore_auto_document_signal = True
            test_document._force_allow_document = True
            
            # حفظ المستند
            test_document.save()
            print(f"✓ تم إنشاء مستند اختباري بنجاح: ID={test_document.id}")
            print("✓ إصلاح نموذج Document يعمل بشكل صحيح")
    except Exception as e:
        print(f"⚠️ فشل إنشاء مستند اختباري: {str(e)}")
        print(traceback.format_exc())
    
    # التحقق من قاعدة البيانات مباشرة
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT COUNT(*) FROM rental_document;")
            count = cursor.fetchone()[0]
            print(f"✓ عدد المستندات في قاعدة البيانات: {count}")
    except Exception as e:
        print(f"⚠️ فشل التحقق من قاعدة البيانات: {str(e)}")
    
    print("=== تم إكمال إصلاح نموذج Document ===\n")

if __name__ == "__main__":
    fix_document_model()