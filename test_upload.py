"""
سكريبت لاختبار رفع ملف مباشرة إلى نظام الأرشيف.
"""

import os
import uuid
import traceback
from django.utils import timezone
from django.shortcuts import render, redirect
from django.contrib import messages
from django.db import connection
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model

# تعريف نموذج المستخدم
User = get_user_model()

def test_direct_upload():
    """وظيفة اختبار لتنفيذ رفع ملف مباشرة إلى قاعدة البيانات"""
    print("\n=== اختبار رفع ملف مباشرة ===")
    
    # بيانات الملف والمستند
    title = "ملف اختباري"
    description = "هذا ملف تم رفعه للتحقق من عمل النظام"
    document_type = "other"
    
    # الإشارة إلى ملف الاختبار
    file_name = "test_file.txt"
    file_type = "text/plain"
    
    # التأكد من وجود الملف
    if not os.path.exists(file_name):
        print(f"❌ الملف '{file_name}' غير موجود")
        return False
    
    # قراءة حجم الملف
    file_size = os.path.getsize(file_name)
    print(f"📄 معلومات الملف: الاسم={file_name}, النوع={file_type}, الحجم={file_size}")
    
    # إنشاء مسار لحفظ الملف
    upload_dir = os.path.join('media', 'archive', 'uploads')
    os.makedirs(upload_dir, exist_ok=True)
    
    # إنشاء اسم ملف فريد
    ext = os.path.splitext(file_name)[1]
    unique_filename = f"{uuid.uuid4().hex}{ext}"
    rel_path = os.path.join('archive', 'uploads', unique_filename)
    absolute_path = os.path.join('media', rel_path)
    
    # حفظ الملف على القرص
    try:
        with open(file_name, 'rb') as src, open(absolute_path, 'wb') as dest:
            dest.write(src.read())
        print(f"✅ تم حفظ الملف في: {absolute_path}")
    except Exception as e:
        print(f"❌ خطأ في حفظ الملف: {str(e)}")
        return False
    
    # الحصول على معرف المستخدم الأول (عادة المشرف)
    user_id = None
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT id FROM rental_user WHERE is_superuser=1 LIMIT 1")
            row = cursor.fetchone()
            if row:
                user_id = row[0]
                print(f"👤 معرف المستخدم المشرف: {user_id}")
            else:
                print("⚠️ لم يتم العثور على مستخدم مشرف")
                return False
    except Exception as e:
        print(f"❌ خطأ في الحصول على معرف المستخدم: {str(e)}")
        return False
    
    # استخدام SQL مباشرة لإنشاء المستند
    try:
        with connection.cursor() as cursor:
            # الوقت الحالي
            now = timezone.now()
            
            # إنشاء المستند مباشرة في قاعدة البيانات
            cursor.execute("""
            INSERT INTO rental_document 
            (title, description, document_type, file, file_name, file_type, file_size, 
            is_auto_created, added_by_id, created_at, updated_at, is_archived, document_date, related_to)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING id
            """, [
                title, description, document_type, 
                rel_path, file_name, file_type, file_size,
                False, user_id, now, now, True, now.date(), 'other'
            ])
            
            # الحصول على معرف المستند المدرج
            document_id = cursor.fetchone()[0]
            
            print(f"✅ تم إنشاء المستند في قاعدة البيانات: ID={document_id}")
            return True
            
    except Exception as e:
        print(f"❌ خطأ في قاعدة البيانات: {str(e)}")
        print(traceback.format_exc())
        
        # حذف الملف المرفوع في حالة الفشل
        try:
            if os.path.exists(absolute_path):
                os.remove(absolute_path)
                print(f"✅ تم حذف الملف المرفوع بعد فشل العملية: {absolute_path}")
        except:
            pass
            
        return False

if __name__ == "__main__":
    print("يجب تشغيل هذا السكريبت من داخل Django.")
    print("استدعاء الوظيفة مباشرة عبر Django shell.")