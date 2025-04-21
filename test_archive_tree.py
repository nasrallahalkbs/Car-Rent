"""
اختبار عرض شجرة المجلدات في الأرشيف
"""
from django.core.wsgi import get_wsgi_application
import os
import django

# إعداد بيئة Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'car_rental_project.settings')
django.setup()

from rental.admin_views import admin_archive_tree
from django.test import RequestFactory
from rental.models import User  # استخدام نموذج User من تطبيق rental
from django.contrib.messages.storage.fallback import FallbackStorage

def test_archive_tree():
    """اختبار عرض شجرة المجلدات"""
    # إنشاء طلب تجريبي
    factory = RequestFactory()
    request = factory.get('/dashboard/archive/tree/')
    
    # إنشاء مستخدم وتعيينه للطلب
    user = User.objects.filter(is_staff=True).first()
    if not user:
        print("لا يوجد مستخدمون في قاعدة البيانات")
        return
    
    request.user = user
    
    # إضافة خاصية session للطلب (مطلوبة لـ messages)
    setattr(request, 'session', {})
    
    # إضافة خاصية messages للطلب (مطلوبة لـ messages)
    setattr(request, '_messages', FallbackStorage(request))
    
    # محاولة عرض صفحة شجرة المجلدات
    try:
        response = admin_archive_tree(request)
        print(f"نوع الاستجابة: {type(response)}")
        print(f"القالب المستخدم: {response.template_name}")
        print(f"حالة الاستجابة: {response.status_code if hasattr(response, 'status_code') else 'غير محدد'}")
        
        # التحقق من أن متغير active_section مضبوط على 'archive'
        if hasattr(response, 'context_data'):
            print(f"متغير active_section: {response.context_data.get('active_section', 'غير موجود')}")
        
        print("تم اختبار عرض شجرة المجلدات بنجاح")
    except Exception as e:
        print(f"حدث خطأ أثناء اختبار عرض شجرة المجلدات: {e}")

if __name__ == "__main__":
    test_archive_tree()