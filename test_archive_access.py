"""
اختبار الوصول إلى صفحة الأرشيف
"""

import os
import sys
import django
import requests
from urllib.parse import urljoin

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'car_rental_project.settings')
django.setup()

# الرابط الأساسي للتطبيق
BASE_URL = "http://localhost:5000"

# روابط صفحات الأرشيف للاختبار
ARCHIVE_URLS = [
    "/ar/dashboard/archive/",
    "/dashboard/archive/",
    "/ar/dashboard/archive/reliable-upload/",
    "/dashboard/archive/reliable-upload/",
    "/ar/dashboard/archive/upload/",
    "/dashboard/archive/upload/"
]

print("اختبار الوصول إلى صفحة الأرشيف:\n")

for url_path in ARCHIVE_URLS:
    full_url = urljoin(BASE_URL, url_path)
    print(f"محاولة الوصول إلى: {full_url}")
    
    try:
        response = requests.get(full_url)
        status = response.status_code
        
        if status == 200:
            print(f"✅ تم الوصول بنجاح (200 OK)")
            content_length = len(response.text)
            print(f"   حجم المحتوى: {content_length} بايت")
            
            # التحقق من نوع المحتوى
            if 'text/html' in response.headers.get('Content-Type', ''):
                print(f"   نوع المحتوى: HTML")
                
                # عرض جزء من المحتوى
                content_preview = response.text[:100].replace('\n', ' ').strip()
                print(f"   معاينة: {content_preview}...")
        else:
            print(f"❌ فشل الوصول ({status})")
            
    except Exception as e:
        print(f"❌ حدث خطأ: {str(e)}")
    
    print()