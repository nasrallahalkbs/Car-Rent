"""
إنشاء مجلدات اختبار للأرشيف الإلكتروني
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'car_rental_project.settings')
django.setup()

from rental.models import ArchiveFolder, Document
from django.utils import timezone


def create_test_folders():
    """إنشاء مجلدات اختبار للأرشيف الإلكتروني"""
    print("بدء إنشاء مجلدات اختبار للأرشيف الإلكتروني...")
    
    # إنشاء المجلدات الرئيسية
    main_folders = [
        {"name": "حجوزات السيارات", "description": "مجلد لحفظ مستندات الحجوزات", "is_system_folder": True},
        {"name": "عقود الإيجار", "description": "مجلد لحفظ عقود إيجار السيارات", "is_system_folder": True},
        {"name": "مستندات السيارات", "description": "مجلد لحفظ مستندات السيارات الرسمية", "is_system_folder": True},
        {"name": "إيصالات المدفوعات", "description": "مجلد لحفظ إيصالات المدفوعات", "is_system_folder": True},
        {"name": "وثائق إدارية", "description": "مجلد للوثائق الإدارية", "is_system_folder": False},
    ]
    
    # إنشاء المجلدات الرئيسية إذا لم تكن موجودة
    root_folders = []
    for folder_data in main_folders:
        folder, created = ArchiveFolder.objects.get_or_create(
            name=folder_data["name"],
            defaults={
                "description": folder_data["description"],
                "is_system_folder": folder_data["is_system_folder"],
                "parent": None
            }
        )
        root_folders.append(folder)
        action = "تم إنشاء" if created else "موجود مسبقاً"
        print(f"{action}: {folder.name}")
    
    # إنشاء مجلدات فرعية للحجوزات
    reservations_folder = root_folders[0]
    reservation_subfolders = [
        {"name": "حجوزات نشطة", "description": "الحجوزات النشطة حالياً", "is_system_folder": True},
        {"name": "حجوزات منتهية", "description": "الحجوزات المنتهية", "is_system_folder": True},
        {"name": "حجوزات ملغاة", "description": "الحجوزات الملغاة", "is_system_folder": True}
    ]
    
    for folder_data in reservation_subfolders:
        subfolder, created = ArchiveFolder.objects.get_or_create(
            name=folder_data["name"],
            defaults={
                "description": folder_data["description"],
                "is_system_folder": folder_data["is_system_folder"],
                "parent": reservations_folder
            }
        )
        action = "تم إنشاء" if created else "موجود مسبقاً"
        print(f"{action}: {subfolder.name} (مجلد فرعي لـ {reservations_folder.name})")
    
    # إنشاء مجلدات فرعية لمستندات السيارات
    cars_folder = root_folders[2]
    car_subfolders = [
        {"name": "صور السيارات", "description": "صور السيارات", "is_system_folder": False},
        {"name": "مستندات الملكية", "description": "مستندات ملكية السيارات", "is_system_folder": True},
        {"name": "تقارير الفحص", "description": "تقارير فحص السيارات", "is_system_folder": False}
    ]
    
    for folder_data in car_subfolders:
        subfolder, created = ArchiveFolder.objects.get_or_create(
            name=folder_data["name"],
            defaults={
                "description": folder_data["description"],
                "is_system_folder": folder_data["is_system_folder"],
                "parent": cars_folder
            }
        )
        action = "تم إنشاء" if created else "موجود مسبقاً"
        print(f"{action}: {subfolder.name} (مجلد فرعي لـ {cars_folder.name})")
        
        # إنشاء مجلد فرعي ثالث للتأكد من عمل الشجرة متعددة المستويات
        if subfolder.name == "صور السيارات":
            sub_subfolder, created = ArchiveFolder.objects.get_or_create(
                name="صور عالية الدقة",
                defaults={
                    "description": "صور عالية الدقة للسيارات",
                    "is_system_folder": False,
                    "parent": subfolder
                }
            )
            action = "تم إنشاء" if created else "موجود مسبقاً"
            print(f"{action}: {sub_subfolder.name} (مجلد فرعي لـ {subfolder.name})")
    
    print("تم إنشاء مجلدات الاختبار بنجاح.")


if __name__ == "__main__":
    create_test_folders()