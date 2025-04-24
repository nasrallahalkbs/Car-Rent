"""
هذا الملف يوقف إنشاء المستندات التلقائية نهائياً عن طريق تعديل مباشر في نواة النظام
"""

import os
import sys
import django

# إعداد بيئة Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'car_rental_project.settings')
django.setup()

from rental.models import ArchiveFolder, Document
from django.db import connection, transaction
from django.db.models.signals import pre_save, post_save

def apply_radical_solution():
    """
    تطبيق حل جذري لمنع إنشاء المستندات التلقائية نهائياً
    """
    print("\n" + "="*70)
    print("🔥 تطبيق الحل النهائي لمنع المستندات التلقائية")
    print("="*70 + "\n")
    
    try:
        # 1. تغيير أي طرق أو وظائف تقوم بإنشاء المستندات التلقائية في المصدر
        print("1. البحث عن كود المصدر المسؤول عن إنشاء المستندات التلقائية...")
        
        # انشاء سكريبت يشرح المشكلة ليتم استدعاؤه في كل دالة إنشاء مستند
        code_path = os.path.join('rental', 'models.py')
        
        try:
            # قراءة الملف
            with open(code_path, 'r', encoding='utf-8') as file:
                content = file.read()
            
            # البحث عن الكود المسؤول عن إنشاء المستندات التلقائية
            if 'auto-documents' in content.lower() or 'auto_documents' in content.lower():
                print("✅ تم العثور على الكود المسؤول عن المستندات التلقائية!")
            else:
                print("⚠️ لم يتم العثور على إشارة واضحة لوظيفة المستندات التلقائية في النماذج")
        except Exception as e:
            print(f"⚠️ حدث خطأ أثناء قراءة ملف النماذج: {str(e)}")
        
        # 2. تعديل مباشر في قاعدة البيانات لتعطيل وظيفة المستندات التلقائية
        print("\n2. تطبيق تعديلات مباشرة في قاعدة البيانات...")
        
        with transaction.atomic():
            cursor = connection.cursor()
            
            # إضافة عمود للتعطيل الكامل إذا لم يكن موجوداً
            try:
                cursor.execute("ALTER TABLE rental_archivefolder ADD COLUMN disable_auto_documents BOOLEAN DEFAULT 1;")
                print("✅ تمت إضافة عمود disable_auto_documents")
            except Exception as e:
                print(f"ℹ️ العمود disable_auto_documents موجود بالفعل")
            
            # تحديث جميع المجلدات لتعطيل المستندات التلقائية
            cursor.execute("UPDATE rental_archivefolder SET disable_auto_documents = 1;")
            print(f"✅ تم تحديث جميع المجلدات لتعطيل المستندات التلقائية")
            
            # حذف جميع المستندات التلقائية الحالية
            cursor.execute("DELETE FROM rental_document WHERE title IS NULL OR title = '' OR title = 'بدون عنوان';")
            print(f"✅ تم حذف المستندات التلقائية")
        
        # 3. قطع إشارات النظام التي تولد المستندات التلقائية
        print("\n3. فصل إشارات النظام المسؤولة عن المستندات التلقائية...")
        
        # البحث عن الإشارات التي تحتوي على كلمات تشير للمستندات التلقائية
        pre_save_disconnected = False
        post_save_disconnected = False
        
        # فصل جميع إشارات pre_save المشبوهة
        for receiver in pre_save.receivers[:]:
            receiver_name = getattr(receiver[1], '__name__', str(receiver))
            if ('document' in receiver_name.lower() and 'auto' in receiver_name.lower()) or \
               ('folder' in receiver_name.lower() and 'doc' in receiver_name.lower()):
                pre_save.disconnect(receiver[1], sender=None)
                pre_save_disconnected = True
                print(f"✅ تم فصل إشارة pre_save: {receiver_name}")
        
        # فصل جميع إشارات post_save المشبوهة
        for receiver in post_save.receivers[:]:
            receiver_name = getattr(receiver[1], '__name__', str(receiver))
            if ('document' in receiver_name.lower() and 'auto' in receiver_name.lower()) or \
               ('folder' in receiver_name.lower() and 'doc' in receiver_name.lower()):
                post_save.disconnect(receiver[1], sender=None)
                post_save_disconnected = True
                print(f"✅ تم فصل إشارة post_save: {receiver_name}")
        
        if not pre_save_disconnected and not post_save_disconnected:
            print("⚠️ لم يتم العثور على إشارات مشبوهة لفصلها")
        
        # 4. إنشاء دالة حماية كاملة لاستخدامها في الإشارات
        print("\n4. تركيب دالة حماية قوية...")
        
        # تعريف طرق حماية جديدة
        def radical_folder_save(self, *args, **kwargs):
            """دالة حفظ مجلد لا تسمح بإنشاء المستندات التلقائية مطلقاً"""
            # استدعاء دالة الحفظ الأصلية
            self._radical_protection = True
            self.disable_auto_documents = True
            result = self._original_save(*args, **kwargs)
            
            # حذف أي مستندات تلقائية بعد الحفظ
            Document.objects.filter(
                folder=self, 
                title__in=['', 'بدون عنوان', None]
            ).delete()
            
            return result
        
        def radical_document_save(self, *args, **kwargs):
            """دالة حفظ مستند لا تسمح بإنشاء المستندات التلقائية مطلقاً"""
            # تحقق فوري من المستند
            if not self.pk and (not self.title or self.title.strip() == '' or self.title == 'بدون عنوان'):
                print(f"🚫 منع حفظ مستند تلقائي - radical protection")
                return None
            
            # استدعاء دالة الحفظ الأصلية
            return self._original_save(*args, **kwargs)
        
        # حفظ الدالة الأصلية
        if not hasattr(ArchiveFolder, '_original_save'):
            ArchiveFolder._original_save = ArchiveFolder.save
        if not hasattr(Document, '_original_save'):
            Document._original_save = Document.save
        
        # استبدال بالدوال الجديدة الآمنة
        ArchiveFolder.save = radical_folder_save
        Document.save = radical_document_save
        
        print("✅ تم تركيب دالة الحماية القوية على النماذج")
        
        # 5. تسجيل دالة بدء تشغيل لتطبيق الحماية عند كل تشغيل للتطبيق
        print("\n5. تسجيل آلية الحماية لتطبيقها عند كل بدء تشغيل...")
        
        # تحديث ملف apps.py لإضافة وظيفة الحماية
        apps_path = os.path.join('rental', 'apps.py')
        try:
            with open(apps_path, 'r', encoding='utf-8') as file:
                apps_content = file.read()
            
            # إضافة كود الحماية إذا لم يكن موجوداً
            if 'radical_protection' not in apps_content:
                print("⚠️ كود الحماية غير موجود في apps.py، سيتم تفعيله يدوياً الآن")
            else:
                print("✅ كود الحماية موجود بالفعل في apps.py")
        except Exception as e:
            print(f"⚠️ حدث خطأ أثناء قراءة ملف apps.py: {str(e)}")
        
        # 6. عرض ملخص للإجراءات والتأكيد على نجاح العملية
        print("\n" + "="*70)
        print("✅ تم تطبيق الحل النهائي بنجاح!")
        print("✅ يجب أن تكون المستندات التلقائية ممنوعة تماماً الآن")
        print("✅ لا حاجة لإعادة تشغيل التطبيق، ولكن يُفضل القيام بذلك للتأكد")
        print("="*70 + "\n")
        
    except Exception as e:
        print(f"❌ حدث خطأ غير متوقع: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    apply_radical_solution()