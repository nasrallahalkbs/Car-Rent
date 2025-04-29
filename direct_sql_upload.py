"""
حل مباشر وفوري لمشكلة رفع الملفات باستخدام SQL مباشر

يتجاوز هذا السكريبت كل الآليات الموجودة ويستخدم SQL مباشرة لإضافة مستند
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

from django.db import connection, transaction
from django.conf import settings
import shutil
import datetime

def direct_sql_upload():
    """رفع ملف مباشرة إلى قاعدة البيانات من خلال SQL"""
    print("\n=== بدء رفع ملف باستخدام SQL المباشر ===\n")
    
    # 1. تحديد مسار ملف للرفع (يمكن للمستخدم تغيير هذا المسار حسب الحاجة)
    test_file_path = os.path.join("attached_assets", "IMG_٢٠٢٥٠٤٢٣_٠٢٥٢٤٥.jpg")
    
    # التحقق من وجود الملف
    if not os.path.exists(test_file_path):
        print(f"خطأ: ملف الاختبار غير موجود في المسار {test_file_path}")
        print("يرجى تغيير مسار الملف في السكريبت أو وضع ملف في المسار المحدد")
        return
    
    # قراءة الملف
    with open(test_file_path, 'rb') as f:
        file_content = f.read()
    
    # معلومات الملف
    file_name = os.path.basename(test_file_path)
    file_size = len(file_content)
    file_type = "image/jpeg"  # تُحدد يدويًا أو تُستنتج من الامتداد
    
    print(f"معلومات الملف:")
    print(f"  - الاسم: {file_name}")
    print(f"  - الحجم: {file_size} بايت")
    print(f"  - النوع: {file_type}")
    
    try:
        # 2. استخدام SQL مباشرة لإدراج المستند
        with transaction.atomic():
            # نسخ الملف إلى مجلد الوسائط
            media_dir = os.path.join(settings.MEDIA_ROOT, 'documents')
            os.makedirs(media_dir, exist_ok=True)
            
            # إنشاء اسم فريد للملف
            unique_filename = f"direct_upload_{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}_{file_name}"
            destination_path = os.path.join(media_dir, unique_filename)
            
            # نسخ الملف
            with open(destination_path, 'wb') as dest:
                dest.write(file_content)
            
            # المسار النسبي للملف (للتخزين في قاعدة البيانات)
            relative_path = os.path.relpath(destination_path, settings.MEDIA_ROOT)
            
            print(f"تم نسخ الملف إلى: {destination_path}")
            
            # إدراج السجل في قاعدة البيانات
            with connection.cursor() as cursor:
                # 1. الحصول على آخر معرف للمستندات
                cursor.execute("SELECT MAX(id) FROM rental_document")
                max_id_result = cursor.fetchone()[0]
                new_id = 1 if max_id_result is None else max_id_result + 1
                
                # 2. استعلام إدراج المستند
                query = """
                INSERT INTO rental_document 
                (id, title, description, document_type, file, file_name, file_type, file_size, file_content, 
                created_at, updated_at, is_archived, is_auto_created, document_date, related_to) 
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """
                
                # 3. تنفيذ الاستعلام
                title = "مستند تم رفعه باستخدام SQL مباشرة"
                description = "تم إنشاء هذا المستند باستخدام SQL مباشرة لتجاوز آلية منع المستندات التلقائية"
                now = datetime.datetime.now()
                
                cursor.execute(query, [
                    new_id,
                    title,
                    description,
                    'other',  # document_type
                    relative_path,  # file
                    file_name,
                    file_type,
                    file_size,
                    file_content,  # file_content
                    now,  # created_at
                    now,  # updated_at
                    True,  # is_archived
                    False,  # is_auto_created
                    now.date(),  # document_date
                    'other'  # related_to
                ])
                
                # 4. التحقق من نجاح الإدراج
                cursor.execute("SELECT id, title FROM rental_document WHERE id = %s", [new_id])
                result = cursor.fetchone()
                
                if result:
                    print(f"\n✅ تم رفع المستند بنجاح!")
                    print(f"  - معرف المستند: {result[0]}")
                    print(f"  - عنوان المستند: {result[1]}")
                    print(f"  - مسار الملف: {relative_path}")
                else:
                    print("\n❌ فشل في التحقق من وجود المستند بعد الإدراج")
                
                # 5. التحقق من عدد المستندات الإجمالي
                cursor.execute("SELECT COUNT(*) FROM rental_document")
                count = cursor.fetchone()[0]
                print(f"  - إجمالي عدد المستندات: {count}")
    
    except Exception as e:
        print(f"\n❌ حدث خطأ أثناء رفع المستند: {str(e)}")
        print(traceback.format_exc())
    
    print("\n=== انتهى رفع الملف باستخدام SQL المباشر ===\n")

if __name__ == "__main__":
    direct_sql_upload()