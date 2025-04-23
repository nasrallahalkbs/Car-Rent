"""
التحقق من المجلدات الموجودة في قاعدة البيانات وإنشاء مجلدات جديدة إذا لم تكن موجودة
"""
import os
import sys
import django

# إعداد البيئة لاستخدام نماذج Django
sys.path.append('.')  # إضافة المسار الحالي إلى مسارات البحث
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings')
django.setup()

from rental.models import ArchiveFolder
from django.contrib.auth import get_user_model

User = get_user_model()

def check_folders():
    """التحقق من وجود المجلدات في قاعدة البيانات"""
    print(f"عدد المجلدات في قاعدة البيانات: {ArchiveFolder.objects.count()}")
    
    root_folders = ArchiveFolder.get_root_folders()
    print(f"المجلدات الرئيسية: {root_folders.count()}")
    
    for folder in root_folders:
        print(f"- {folder.name} (ID: {folder.id})")
        children = folder.children.all()
        for child in children:
            print(f"  -- {child.name} (ID: {child.id})")

def create_system_folders():
    """إنشاء المجلدات الأساسية للنظام إذا لم تكن موجودة"""
    # المجلدات الرئيسية
    main_folders = [
        {"name": "تصميم (شجرة)", "type": "root"},
        {"name": "رسوم (1)", "type": "department"},
        {"name": "حضور (2)", "type": "department"},
        {"name": "حسابات (3)", "type": "department"},
        {"name": "محفوظات (4)", "type": "department"},
        {"name": "توكيلات (5)", "type": "department"},
    ]
    
    # الحصول على أو إنشاء مستخدم نظام
    admin_user = User.objects.filter(is_superuser=True).first()
    
    for folder_data in main_folders:
        folder, created = ArchiveFolder.objects.get_or_create(
            name=folder_data["name"],
            defaults={
                "folder_type": folder_data["type"],
                "is_system_folder": True,
                "created_by": admin_user
            }
        )
        
        if created:
            print(f"تم إنشاء المجلد: {folder.name}")
        else:
            print(f"المجلد موجود بالفعل: {folder.name}")

if __name__ == "__main__":
    print("التحقق من المجلدات...")
    check_folders()
    
    print("\nإنشاء المجلدات الأساسية...")
    create_system_folders()
    
    print("\nالتحقق بعد الإنشاء...")
    check_folders()