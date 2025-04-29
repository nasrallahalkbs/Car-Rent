"""
اختبار رفع ملف باستخدام Django ORM بدلاً من SQL المباشر
"""

import os
import traceback
import datetime
from django.conf import settings
from django.utils import timezone
from rental.models import Document, User

print("بدء اختبار رفع ملف باستخدام Django ORM...")

# إعداد بيانات الملف
test_file_path = 'test_file.txt'
file_title = 'ملف اختباري من Django'
file_description = 'هذا ملف تم رفعه باستخدام Django ORM بدلاً من SQL المباشر'

# قراءة محتوى الملف
with open(test_file_path, 'rb') as f:
    file_content = f.read()

# تحديد خصائص الملف
file_name = os.path.basename(test_file_path)
file_type = 'text/plain'
file_size = os.path.getsize(test_file_path)

# إنشاء اسم ملف فريد
timestamp = int(datetime.datetime.now().timestamp())
unique_filename = f"test_upload_{timestamp}_{file_name}"

# مسار حفظ الملف
upload_dir = os.path.join(settings.MEDIA_ROOT, 'uploads')
os.makedirs(upload_dir, exist_ok=True)
file_path = os.path.join(upload_dir, unique_filename)

# حفظ الملف على القرص
with open(file_path, 'wb') as f:
    f.write(file_content)

# المسار النسبي للملف
relative_path = os.path.join('uploads', unique_filename)

try:
    # الحصول على مستخدم الاختبار - المسؤول
    admin_user = User.objects.first()
    if not admin_user:
        print("⚠️ لم يتم العثور على أي مستخدم في النظام")
        exit(1)
    
    print(f"استخدام المستخدم: {admin_user.email}")
    
    # معرفة عدد المستندات قبل الإضافة
    docs_before = Document.objects.count()
    print(f"عدد المستندات قبل الإضافة: {docs_before}")
    
    # إنشاء المستند باستخدام Django ORM
    new_doc = Document(
        title=file_title,
        description=file_description,
        document_type='other',
        file=relative_path,  # المسار النسبي للملف
        document_date=timezone.now(),
        related_to='general',
        is_archived=False,
        added_by=admin_user,
        file_name=file_name,
        file_type=file_type,
        file_size=file_size,
        file_content=file_content,
        is_auto_created=False
    )
    
    # تعطيل إشارات منع المستندات التلقائية
    print("تعطيل إشارات منع المستندات التلقائية مؤقتاً...")
    from django.db.models.signals import pre_save, post_save
    from rental.signals import prevent_auto_document_creation
    
    # فصل إشارة منع المستندات التلقائية
    pre_save.disconnect(prevent_auto_document_creation, sender=Document)
    
    # حفظ المستند
    print("محاولة حفظ المستند...")
    new_doc.save()
    
    # إعادة توصيل الإشارة بعد الانتهاء
    pre_save.connect(prevent_auto_document_creation, sender=Document)
    print("تمت إعادة توصيل إشارات منع المستندات التلقائية")
    
    # التحقق من نجاح الإضافة
    docs_after = Document.objects.count()
    print(f"عدد المستندات بعد الإضافة: {docs_after}")
    
    if docs_after > docs_before:
        print(f"✅ تم إضافة المستند بنجاح! (ID: {new_doc.id})")
        
        # عرض تفاصيل المستند المضاف
        print(f"\nتفاصيل المستند الجديد:")
        print(f"المعرف: {new_doc.id}")
        print(f"العنوان: {new_doc.title}")
        print(f"الوصف: {new_doc.description}")
        print(f"النوع: {new_doc.document_type}")
        print(f"المسار: {new_doc.file}")
        print(f"اسم الملف: {new_doc.file_name}")
        print(f"حجم الملف: {new_doc.file_size}")
        print(f"نوع الملف: {new_doc.file_type}")
        print(f"تلقائي: {new_doc.is_auto_created}")
        
        # عرض آخر 5 مستندات
        print("\nآخر 5 مستندات في قاعدة البيانات:")
        latest_docs = Document.objects.order_by('-id')[:5]
        for doc in latest_docs:
            print(f"ID={doc.id}, العنوان='{doc.title}', الملف='{doc.file_name}', تلقائي={doc.is_auto_created}")
    else:
        print("❌ فشل إضافة المستند!")

except Exception as e:
    print(f"❌ حدث خطأ: {str(e)}")
    print(traceback.format_exc())