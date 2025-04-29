"""
اختبار وظيفة رفع الملفات في الأرشيف الإلكتروني باستخدام دالة الرفع الموثوقة الجديدة
"""

import os
import sys
import django
import requests
from urllib.parse import urljoin
import tempfile
from django.conf import settings
from django.utils import timezone

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'car_rental_project.settings')
django.setup()

# استيراد النماذج المطلوبة
from rental.models import ArchiveFolder, Document, User

# الرابط الأساسي للتطبيق
BASE_URL = "http://localhost:5000"

# إنشاء ملف اختبار مؤقت
def create_test_file():
    with tempfile.NamedTemporaryFile(suffix='.txt', delete=False) as temp:
        temp.write(b"this is a test file for upload")
        temp_filename = temp.name
    return temp_filename

def test_reliable_upload():
    """اختبار دالة الرفع الموثوقة الجديدة"""
    print("\n== اختبار وظيفة رفع الملفات باستخدام دالة الرفع الموثوقة ==\n")
    
    # الحصول على مجلد الأرشيف الرئيسي أو إنشائه إذا لم يكن موجوداً
    root_folder = ArchiveFolder.objects.filter(name="الأرشيف الرئيسي").first()
    if not root_folder:
        print("إنشاء مجلد الأرشيف الرئيسي...")
        root_folder = ArchiveFolder.objects.create(
            name="الأرشيف الرئيسي",
            parent=None,
            is_system_folder=True,
            created_by=User.objects.filter(is_staff=True).first()
        )
    
    print(f"تم العثور على مجلد الأرشيف الرئيسي (ID: {root_folder.id})")
    
    # إنشاء ملف اختبار
    test_file_path = create_test_file()
    print(f"تم إنشاء ملف اختبار مؤقت: {test_file_path}")
    
    # شكل الطلب لرفع الملف
    upload_url = urljoin(BASE_URL, "/dashboard/archive/reliable-upload/")
    print(f"جاري محاولة رفع الملف إلى: {upload_url}")
    
    try:
        # رفع الملف باستخدام طلب POST
        with open(test_file_path, 'rb') as f:
            files = {'document_file': (os.path.basename(test_file_path), f)}
            data = {
                'title': 'ملف اختبار الرفع الموثوق',
                'folder': root_folder.id,
                'document_type': 'عام',
                'description': 'هذا ملف اختبار لوظيفة الرفع الموثوقة',
                'is_public': 'on'
            }
            
            response = requests.post(upload_url, files=files, data=data)
            
            # التحقق من نجاح الرفع
            if response.status_code == 200 or response.status_code == 302:
                print(f"✅ تم رفع الملف بنجاح (رمز الاستجابة: {response.status_code})")
                print(f"   حجم الاستجابة: {len(response.text)} بايت")
                print(f"   العناوين: {dict(response.headers)}")
                
                # التحقق من إضافة المستند في قاعدة البيانات
                latest_doc = Document.objects.filter(title='ملف اختبار الرفع الموثوق').order_by('-id').first()
                if latest_doc:
                    print(f"✅ تم العثور على المستند في قاعدة البيانات:")
                    print(f"   رقم المعرف: {latest_doc.id}")
                    print(f"   العنوان: {latest_doc.title}")
                    print(f"   تاريخ الإضافة: {latest_doc.added_date}")
                    print(f"   النوع: {latest_doc.document_type}")
                    print(f"   المجلد: {latest_doc.folder.name if latest_doc.folder else 'لا يوجد'}")
                else:
                    print("❌ لم يتم العثور على المستند في قاعدة البيانات!")
            else:
                print(f"❌ فشل رفع الملف (رمز الاستجابة: {response.status_code})")
                print(f"   الاستجابة: {response.text[:500]}")
    except Exception as e:
        print(f"❌ حدث خطأ أثناء رفع الملف: {str(e)}")
    finally:
        # حذف الملف المؤقت
        try:
            os.unlink(test_file_path)
            print(f"تم حذف ملف الاختبار المؤقت: {test_file_path}")
        except:
            pass

def test_protected_upload():
    """اختبار أن المستندات التلقائية ما زالت محمية"""
    print("\n== اختبار أن المستندات التلقائية ما زالت محمية ==\n")
    
    try:
        # محاولة إنشاء مستند بطريقة مباشرة (يجب أن يتم منعه)
        import django.db.models.signals
        from rental.signals import prevent_auto_document_creation
        
        doc_count_before = Document.objects.count()
        print(f"عدد المستندات قبل محاولة الإنشاء: {doc_count_before}")
        
        # إنشاء مستند بطريقة مباشرة
        doc = Document(
            title="مستند اختبار تلقائي",
            document_type="اختبار",
            is_auto_document=True,
            added_by=User.objects.filter(is_staff=True).first(),
            added_date=timezone.now()
        )
        
        # محاولة حفظ المستند
        try:
            doc.save()
            saved = True
        except:
            saved = False
        
        # التحقق من عدد المستندات بعد المحاولة
        doc_count_after = Document.objects.count()
        print(f"عدد المستندات بعد محاولة الإنشاء: {doc_count_after}")
        
        if doc_count_after > doc_count_before:
            print("❌ تم إنشاء المستند التلقائي! الحماية لا تعمل.")
        else:
            print("✅ تم منع إنشاء المستند التلقائي بنجاح.")
            
    except Exception as e:
        print(f"❌ حدث خطأ أثناء اختبار الحماية: {str(e)}")

# تنفيذ الاختبارات
if __name__ == "__main__":
    test_reliable_upload()
    test_protected_upload()