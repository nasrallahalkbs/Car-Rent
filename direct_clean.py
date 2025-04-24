"""
تنظيف مباشر لقاعدة البيانات من المستندات التلقائية
"""

import os
import django

# إعداد بيئة Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'car_rental_project.settings')
django.setup()

from django.db import connection, transaction

def clean_all_auto_documents():
    """تنظيف جميع المستندات التلقائية من قاعدة البيانات مباشرة"""
    print("\n" + "="*70)
    print("🧹 التنظيف المباشر لقاعدة البيانات")
    print("="*70 + "\n")
    
    try:
        # استخدام SQL مباشر للحذف الفوري
        with transaction.atomic():
            cursor = connection.cursor()
            cursor.execute("""
            DELETE FROM rental_document 
            WHERE title IS NULL OR title = '' OR title = 'بدون عنوان';
            """)
            
            # الحصول على عدد الصفوف المتأثرة
            cursor.execute("SELECT changes();")
            result = cursor.fetchone()
            if result:
                count = result[0]
                print(f"✅ تم حذف {count} مستند تلقائي")
            else:
                print("✅ تم تنفيذ الحذف (عدد المستندات المحذوفة غير معروف)")
                
        print("\n✅ تم تنظيف قاعدة البيانات بنجاح")
        print("="*70 + "\n")
        
    except Exception as e:
        print(f"❌ حدث خطأ أثناء تنظيف قاعدة البيانات: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    clean_all_auto_documents()