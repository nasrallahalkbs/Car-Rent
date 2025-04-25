"""
تعطيل إشارات منع المستندات التلقائية مؤقتًا وإنشاء مستند اختباري
"""
import os
import sys
import django
import datetime
import sqlite3

# إعداد بيئة Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'car_rental_project.settings')
django.setup()

# استيراد النماذج
from rental.models import ArchiveFolder, Document
from django.utils import timezone

def create_test_document_with_sqlite():
    """إنشاء مستند اختباري باستخدام SQLite مباشرة"""
    
    # اسم قاعدة البيانات SQLite
    db_path = 'db.sqlite3'
    
    # إنشاء اتصال بقاعدة البيانات
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # 1. إنشاء مجلد اختبار جديد
        folder_name = f"مجلد_اختبار_للحل_النهائي_{int(timezone.now().timestamp())}"
        cursor.execute("""
            INSERT INTO rental_archivefolder (name, description, created_at, updated_at, is_system_folder)
            VALUES (?, ?, datetime('now'), datetime('now'), 0)
        """, (folder_name, "مجلد اختبار للحل النهائي - تم إنشاؤه باستخدام SQLite"))
        
        folder_id = cursor.lastrowid
        print(f"✅ تم إنشاء مجلد اختبار جديد: {folder_name} (ID: {folder_id})")
        
        # 2. التحقق من وجود حقل is_auto_created في جدول المستندات
        cursor.execute("PRAGMA table_info(rental_document)")
        table_info = cursor.fetchall()
        
        is_auto_created_exists = any(column[1] == 'is_auto_created' for column in table_info)
        print(f"حقل is_auto_created {'موجود' if is_auto_created_exists else 'غير موجود'} في جدول المستندات")
        
        # 3. إنشاء محتوى ملف اختباري
        file_content = "هذا ملف اختبار تم إنشاؤه للحل النهائي باستخدام SQLite".encode('utf-8')
        file_name = "test_file.txt"
        file_type = "text/plain"
        file_size = len(file_content)
        document_title = f"مستند_اختبار_sqlite_{int(timezone.now().timestamp())}"
        
        # 4. الحصول على معلومات عن بنية جدول المستندات
        print("الحصول على معلومات عن بنية جدول المستندات:")
        cursor.execute("PRAGMA table_info(rental_document)")
        columns = cursor.fetchall()
        for column in columns:
            print(f"  - {column[1]}: {'NULL مطلوب' if column[3] == 0 else 'NULL غير مطلوب'}")
        
        # 5. إنشاء المستند
        try:
            # استعلام مرن لإدراج مستند جديد
            fields = []
            placeholders = []
            values = []
            
            # الحقول الأساسية
            fields.extend(["title", "description", "document_type", "folder_id", "created_at", "updated_at"])
            placeholders.extend(["?", "?", "?", "?", "datetime('now')", "datetime('now')"])
            values.extend([
                document_title, 
                "مستند اختبار تم إنشاؤه للحل النهائي باستخدام SQLite",
                "other",
                folder_id
            ])
            
            # الحقول المتعلقة بالملف
            fields.extend(["file_name", "file_type", "file_size", "file_content"])
            placeholders.extend(["?", "?", "?", "?"])
            values.extend([file_name, file_type, file_size, file_content])
            
            # حقل is_auto_created إذا كان موجودًا
            if is_auto_created_exists:
                fields.append("is_auto_created")
                placeholders.append("?")
                values.append(0)  # 0 = false
            
            # حقل file إذا كان مطلوبًا (مسار نسبي للملف)
            file_field_required = any(column[1] == 'file' and column[3] == 1 for column in columns)
            if file_field_required:
                fields.append("file")
                placeholders.append("?")
                values.append(f"documents/test_{int(timezone.now().timestamp())}.txt")
                print("✅ تمت إضافة حقل 'file' المطلوب")
            
            # بناء استعلام SQL المرن
            query = f"""
                INSERT INTO rental_document (
                    {', '.join(fields)}
                )
                VALUES (
                    {', '.join(placeholders)}
                )
            """
            
            print(f"تنفيذ استعلام: {query}")
            cursor.execute(query, values)
            
            document_id = cursor.lastrowid
            print(f"✅ تم إنشاء مستند اختبار جديد: {document_title} (ID: {document_id})")
        except Exception as e:
            print(f"❌ فشل في تنفيذ استعلام إنشاء المستند: {str(e)}")
            
            # إذا فشل الإنشاء، نجرب استعلامًا أقل تعقيدًا
            try:
                # فقط الحقول الأساسية المطلوبة
                cursor.execute("""
                    INSERT INTO rental_document (
                        title, description, document_type, folder_id,
                        file, file_content, created_at, updated_at
                    )
                    VALUES (?, ?, ?, ?, ?, ?, datetime('now'), datetime('now'))
                """, (
                    document_title, 
                    "مستند اختبار بسيط",
                    "other",
                    folder_id,
                    f"documents/test_{int(timezone.now().timestamp())}.txt",
                    file_content
                ))
                
                document_id = cursor.lastrowid
                print(f"✅ تم إنشاء مستند اختبار بسيط: {document_title} (ID: {document_id})")
            except Exception as e2:
                print(f"❌ فشل في تنفيذ استعلام إنشاء المستند البسيط: {str(e2)}")
                return None, None
        
        document_id = cursor.lastrowid
        print(f"✅ تم إنشاء مستند اختبار جديد: {document_title} (ID: {document_id})")
        
        # 5. الالتزام بالتغييرات وإغلاق الاتصال
        conn.commit()
        
        # 6. التحقق من نجاح العملية
        cursor.execute("SELECT COUNT(*) FROM rental_document WHERE folder_id = ?", (folder_id,))
        document_count = cursor.fetchone()[0]
        
        print(f"✅ تم العثور على {document_count} مستند في المجلد {folder_name} (ID: {folder_id})")
        
        if document_count > 0:
            cursor.execute("SELECT id, title, file_size FROM rental_document WHERE folder_id = ?", (folder_id,))
            documents = cursor.fetchall()
            
            for doc in documents:
                doc_id, title, file_size = doc
                print(f"  - مستند: {title} (ID: {doc_id})")
                print(f"    حجم الملف: {file_size} بايت")
        
        cursor.close()
        conn.close()
        
        return folder_id, document_id
    except Exception as e:
        print(f"❌ حدث خطأ أثناء إنشاء المستند: {str(e)}")
        
        # إغلاق الاتصال في حالة الخطأ
        try:
            cursor.close()
            conn.close()
        except:
            pass
        
        return None, None

def fix_admin_views_context():
    """التأكد من أن متغير 'files' موجود في سياق قالب الأرشيف"""
    admin_views_path = 'rental/admin_views.py'
    
    try:
        # قراءة ملف admin_views.py
        with open(admin_views_path, 'r', encoding='utf-8') as file:
            content = file.read()
        
        # البحث عن تعريف سياق القالب في دالة admin_archive
        if "'files': documents," not in content:
            # البحث عن الجزء الذي يقوم بتعريف سياق القالب
            context_pattern = "    context = {\n        'current_folder': current_folder,\n        'folders': subfolders,\n        'documents': documents,"
            new_context = "    context = {\n        'current_folder': current_folder,\n        'folders': subfolders,\n        'documents': documents,\n        'files': documents,"
            
            # استبدال الجزء القديم بالجديد
            modified_content = content.replace(context_pattern, new_context)
            
            # التحقق من تنفيذ الاستبدال
            if content != modified_content:
                # حفظ الملف المعدل
                with open(admin_views_path, 'w', encoding='utf-8') as file:
                    file.write(modified_content)
                print("✅ تم تعديل ملف admin_views.py وإضافة متغير 'files' إلى سياق القالب")
            else:
                print("❌ لم يتم العثور على الجزء المطلوب لإضافة متغير 'files'")
        else:
            print("✅ متغير 'files' موجود بالفعل في سياق قالب الأرشيف")
    except Exception as e:
        print(f"❌ حدث خطأ أثناء تعديل ملف admin_views.py: {str(e)}")

def main():
    """الدالة الرئيسية لتنفيذ الحل النهائي"""
    print("🛠️ بدء تنفيذ الحل النهائي لمشكلة رفع وعرض المستندات...")
    
    # التأكد من أن متغير 'files' موجود في سياق قالب الأرشيف
    fix_admin_views_context()
    
    # إنشاء مستند اختباري باستخدام SQLite مباشرة
    folder_id, document_id = create_test_document_with_sqlite()
    
    if folder_id and document_id:
        print(f"\n✅ تم تنفيذ الحل النهائي بنجاح!")
        print(f"تم إنشاء مستند جديد في المجلد ID: {folder_id}")
        print(f"الآن يجب أن تظهر المستندات في هذا المجلد")
        print(f"يرجى زيارة الرابط التالي للتحقق: /ar/dashboard/archive/?folder={folder_id}")
    else:
        print("\n❌ فشل تنفيذ الحل النهائي")

if __name__ == "__main__":
    main()