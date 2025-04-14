"""
عرض قائمة المستخدمين المتاحين في النظام
"""
import os
import django

# إعداد البيئة لجانغو
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'car_rental_project.settings')
django.setup()

from rental.models import User

def list_users():
    """عرض قائمة المستخدمين المتاحين"""
    print('المستخدمون المتاحون:')
    for user in User.objects.all():
        print(f'- {user.username} (ID: {user.id})')

if __name__ == "__main__":
    list_users()