"""
سكريبت لتشغيل اختبار رفع الملفات عبر Django shell
"""

import os
import sys
import django

# إعداد بيئة Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'car_rental_project.settings')
django.setup()

# استيراد وظيفة الاختبار
from test_upload import test_direct_upload

# تنفيذ الاختبار
print("بدء اختبار رفع الملفات...")
result = test_direct_upload()
print(f"نتيجة اختبار الرفع: {'نجاح ✅' if result else 'فشل ❌'}")