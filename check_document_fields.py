"""
التحقق من الحقول المتاحة في نموذج Document
"""
import os
import sys
import django

# إعداد بيئة Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'car_rental_project.settings')
django.setup()

# استدعاء النماذج
from rental.models import Document

def check_fields():
    """التحقق من الحقول المتاحة في نموذج المستند"""
    print("Available fields in Document model:")
    for field in Document._meta.get_fields():
        print(f"- {field.name}")

if __name__ == "__main__":
    check_fields()
