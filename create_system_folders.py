"""
إنشاء المجلدات النظامية للأرشيف الإلكتروني
"""
import os
import sys
import django
from django.utils import timezone

# إعداد البيئة لاستخدام نماذج Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'car_rental_project.settings')
django.setup()

from rental.models import ArchiveFolder
from django.contrib.auth import get_user_model

User = get_user_model()

def create_system_folders():
    """إنشاء المجلدات النظامية للأرشيف الإلكتروني"""
    
    print("بدء إنشاء مجلدات الأرشيف الإلكتروني...")
    
    # الحصول على أول مستخدم مشرف لإضافته كمنشئ للمجلدات
    admin_user = User.objects.filter(is_superuser=True).first()
    if not admin_user:
        admin_user = User.objects.filter(is_admin=True).first()
    
    if not admin_user:
        print("تحذير: لم يتم العثور على مستخدم مشرف. سيتم إنشاء المجلدات بدون ربطها بمستخدم.")
    
    # المجلد الرئيسي
    root_folder, created = ArchiveFolder.objects.get_or_create(
        name="تصميم (شجرة)",
        parent=None,
        defaults={
            "folder_type": "root",
            "is_system_folder": True,
            "description": "المجلد الرئيسي للأرشيف الإلكتروني",
            "created_by": admin_user
        }
    )
    
    status = "تم إنشاؤه" if created else "موجود بالفعل"
    print(f"المجلد الرئيسي: {root_folder.name} ({status})")
    
    # المجلدات الفرعية
    subfolders = [
        {"name": "رسوم (1)", "type": "department"},
        {"name": "حضور (2)", "type": "department"},
        {"name": "حسابات (3)", "type": "department"},
        {"name": "محفوظات (4)", "type": "department"},
        {"name": "توكيلات (5)", "type": "department"},
    ]
    
    for folder_data in subfolders:
        subfolder, created = ArchiveFolder.objects.get_or_create(
            name=folder_data["name"],
            parent=root_folder,
            defaults={
                "folder_type": folder_data["type"],
                "is_system_folder": True,
                "description": f"مجلد {folder_data['name']}",
                "created_by": admin_user
            }
        )
        
        status = "تم إنشاؤه" if created else "موجود بالفعل"
        print(f"- المجلد الفرعي: {subfolder.name} ({status})")
    
    # عرض إحصائيات النظام
    total_folders = ArchiveFolder.objects.count()
    root_folders_count = ArchiveFolder.objects.filter(parent=None).count()
    
    print(f"\nتم الانتهاء من إنشاء المجلدات.")
    print(f"إجمالي المجلدات في النظام: {total_folders}")
    print(f"عدد المجلدات الرئيسية: {root_folders_count}")
    
    # عرض هيكل المجلدات
    print("\nهيكل المجلدات:")
    for root in ArchiveFolder.objects.filter(parent=None):
        print(f"● {root.name}")
        for child in root.children.all():
            print(f"  ├─ {child.name}")

if __name__ == "__main__":
    create_system_folders()