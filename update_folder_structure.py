"""
تحديث هيكل المجلدات في الأرشيف حسب المتطلبات الجديدة
"""
from rental.models import ArchiveFolder, Document, User
from django.utils import timezone
from django.db import transaction


def update_folder_structure():
    """تحديث هيكل المجلدات في الأرشيف ليتطابق مع المتطلبات الجديدة"""
    print("بدء تحديث هيكل المجلدات في الأرشيف...")
    
    # حذف المجلدات الحالية للبدء من جديد
    with transaction.atomic():
        ArchiveFolder.objects.all().delete()
        print("- تم حذف المجلدات القديمة")
        
        # إنشاء المجلدات الرئيسية مع ترقيم حسب الصورة
        main_folders = [
            {"name": "رسوم", "number": 1, "is_system_folder": True},
            {"name": "حضور", "number": 2, "is_system_folder": True},
            {"name": "حسابات", "number": 3, "is_system_folder": True},
            {"name": "محفوظات", "number": 4, "is_system_folder": True},
            {"name": "توكيلات", "number": 5, "is_system_folder": True},
        ]
        
        # إنشاء المجلدات الرئيسية
        created_folders = []
        for folder_data in main_folders:
            folder = ArchiveFolder.objects.create(
                name=f"{folder_data['name']} ({folder_data['number']})",
                description=f"مجلد {folder_data['name']}",
                is_system_folder=folder_data["is_system_folder"],
                created_at=timezone.now()
            )
            created_folders.append(folder)
            print(f"- تم إنشاء مجلد {folder.name}")
    
    print("تم تحديث هيكل المجلدات بنجاح!")


if __name__ == "__main__":
    update_folder_structure()