"""
رفع ملف مباشرة إلى قاعدة البيانات باستخدام SQL
"""
import os
import sys
import django
import datetime
import psycopg2

# إعداد بيئة Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'car_rental_project.settings')
django.setup()

def direct_upload():
    """رفع ملف مباشرة إلى قاعدة البيانات باستخدام SQL"""
    # الحصول على معلومات الاتصال بقاعدة البيانات من متغيرات البيئة
    conn_params = {
        'host': os.environ.get('PGHOST'),
        'database': os.environ.get('PGDATABASE'),
        'user': os.environ.get('PGUSER'),
        'password': os.environ.get('PGPASSWORD'),
        'port': os.environ.get('PGPORT')
    }
    
    try:
        # إنشاء اتصال بقاعدة البيانات
        conn = psycopg2.connect(**conn_params)
        cursor = conn.cursor()
        
        # طباعة معلومات قاعدة البيانات
        print(f"✅ تم الاتصال بقاعدة البيانات: {conn_params['database']} على {conn_params['host']}:{conn_params['port']}")
        
        # 1. التحقق من وجود مجلد الاختبار
        folder_name = "مجلد_اختبار_direct_sql"
        cursor.execute("SELECT id FROM rental_archivefolder WHERE name = %s;", (folder_name,))
        folder_row = cursor.fetchone()
        
        if folder_row:
            folder_id = folder_row[0]
            print(f"✅ تم العثور على مجلد الاختبار: {folder_name} (ID: {folder_id})")
        else:
            # إنشاء مجلد جديد
            cursor.execute("""
                INSERT INTO rental_archivefolder (name, description, created_at, updated_at, is_system_folder)
                VALUES (%s, %s, NOW(), NOW(), false)
                RETURNING id;
            """, (folder_name, "مجلد اختبار للرفع المباشر باستخدام SQL",))
            folder_id = cursor.fetchone()[0]
            print(f"✅ تم إنشاء مجلد اختبار جديد: {folder_name} (ID: {folder_id})")
        
        # 2. إنشاء محتوى ملف اختباري
        file_content = "هذا ملف اختبار تم رفعه باستخدام SQL المباشر".encode('utf-8')
        # استخدام محتوى الملف مباشرة بدلاً من تحويله إلى Binary
        binary_content = file_content
        
        # 3. التحقق من وجود حقل is_auto_created في جدول المستندات
        cursor.execute("SELECT column_name FROM information_schema.columns WHERE table_name = 'rental_document' AND column_name = 'is_auto_created';")
        is_auto_created_exists = cursor.fetchone() is not None
        
        print(f"حقل is_auto_created {'موجود' if is_auto_created_exists else 'غير موجود'} في جدول المستندات")
        
        # 4. إنشاء مستند جديد
        if is_auto_created_exists:
            query = """
                INSERT INTO rental_document (
                    title, description, document_type, folder_id, 
                    file_name, file_type, file_size, file_content,
                    created_at, updated_at, is_auto_created
                ) 
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, NOW(), NOW(), %s)
                RETURNING id;
            """
            cursor.execute(query, [
                f"مستند_اختبار_sql_direct_{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}", 
                "مستند اختبار تم رفعه باستخدام SQL المباشر",
                "other",
                folder_id, 
                "test_file.txt",
                "text/plain",
                len(file_content),
                binary_content,
                False
            ])
        else:
            # إذا لم يكن حقل is_auto_created موجودًا، نستخدم استعلام بدون هذا الحقل
            query = """
                INSERT INTO rental_document (
                    title, description, document_type, folder_id, 
                    file_name, file_type, file_size, file_content,
                    created_at, updated_at
                ) 
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, NOW(), NOW())
                RETURNING id;
            """
            cursor.execute(query, [
                f"مستند_اختبار_sql_direct_{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}", 
                "مستند اختبار تم رفعه باستخدام SQL المباشر",
                "other",
                folder_id, 
                "test_file.txt",
                "text/plain",
                len(file_content),
                binary_content
            ])
        
        document_id = cursor.fetchone()[0]
        print(f"✅ تم إنشاء مستند اختبار جديد باستخدام SQL المباشر: ID: {document_id}")
        
        # 5. الالتزام بالتغييرات
        conn.commit()
        
        # 6. استعلام عن المستندات في المجلد
        cursor.execute("""
            SELECT id, title, file_size, created_at 
            FROM rental_document 
            WHERE folder_id = %s
            ORDER BY created_at DESC;
        """, (folder_id,))
        
        documents = cursor.fetchall()
        print(f"\nتم العثور على {len(documents)} مستند في المجلد {folder_name} (ID: {folder_id})")
        
        for doc in documents:
            doc_id, title, file_size, created_at = doc
            print(f"  - مستند: {title} (ID: {doc_id})")
            print(f"    حجم الملف: {file_size} بايت")
            print(f"    تاريخ الإنشاء: {created_at}")
        
        # 7. إغلاق الاتصال
        cursor.close()
        conn.close()
        print("\n✅ تم رفع الملف بنجاح باستخدام SQL المباشر")
        
        return document_id
    except Exception as e:
        print(f"❌ حدث خطأ أثناء رفع الملف: {str(e)}")
        return None

if __name__ == "__main__":
    direct_upload()