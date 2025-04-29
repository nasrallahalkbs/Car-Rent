"""
اختبار رفع ملف باستخدام SQL مباشرة
"""

import os
import traceback
import datetime
from django.conf import settings
from django.db import connection, transaction
from django.utils import timezone

# إعداد بيانات الملف
test_file_path = 'test_file.txt'
file_title = 'ملف اختباري مباشر'
file_description = 'هذا ملف تم رفعه باستخدام SQL مباشرة'

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
    # تخزين المستند في قاعدة البيانات مباشرة باستخدام SQL متوافق مع SQLite
    with transaction.atomic():
        cursor = connection.cursor()
        
        # زمن الآن بتنسيق SQLite
        now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        # الاستعلام المباشر - تجاوز التحققات بناءً على الأعمدة الفعلية في قاعدة البيانات
        query = """
        INSERT INTO rental_document 
        (title, description, document_type, folder_id, added_by_id,
        file_name, file_type, file_size, file_content, file, created_at, updated_at, is_auto_created,
        document_date) 
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        
        # معرف المستخدم الافتراضي (1 للمسؤول)
        user_id = 1
        
        # تنفيذ الاستعلام
        cursor.execute(query, [
            file_title,
            file_description,
            'other',
            None,  # folder_id
            user_id,  # added_by
            file_name,
            file_type,
            file_size,
            file_content,  # محتوى الملف
            relative_path,  # مسار الملف
            now,  # created_at
            now,  # updated_at
            0,  # is_auto_created - مهم لتمييز الملفات المرفوعة يدوياً
            now  # تاريخ المستند
        ])
        
        # الحصول على معرف المستند الجديد
        cursor.execute("SELECT last_insert_rowid()")
        document_id = cursor.fetchone()[0]
        print(f"✅ تم إنشاء المستند بنجاح، المعرف: {document_id}")
        
        # التحقق من أن المستند تم إنشاؤه فعلاً
        verification_query = "SELECT id, title FROM rental_document WHERE id = ?"
        cursor.execute(verification_query, [document_id])
        verification_result = cursor.fetchone()
        
        if verification_result:
            print(f"✅ تم التحقق من وجود المستند في قاعدة البيانات: ID={verification_result[0]}, العنوان={verification_result[1]}")
        else:
            print("⚠️ لم يتم العثور على المستند في قاعدة البيانات بعد إنشائه!")
        
        # استعلام للحصول على جميع المستندات
        cursor.execute("SELECT id, title, file_name, is_auto_created FROM rental_document ORDER BY id DESC LIMIT 5")
        rows = cursor.fetchall()
        
        print("\nآخر 5 مستندات في قاعدة البيانات:")
        for row in rows:
            print(f"ID={row[0]}, العنوان='{row[1]}', الملف='{row[2]}', تلقائي={row[3]}")

except Exception as e:
    print(f"❌ حدث خطأ: {str(e)}")
    print(traceback.format_exc())