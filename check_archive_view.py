"""
تحقق من عرض الأرشيف وإضافة وضع التصحيح
"""
import os
import sys
import django

# إعداد البيئة لاستخدام نماذج Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'car_rental_project.settings')
django.setup()

from rental.models import ArchiveFolder

def check_archive_view():
    """التحقق من مشكلة عرض الأرشيف"""
    
    # عرض المجلدات الموجودة في النظام
    root_folders = ArchiveFolder.objects.filter(parent=None)
    print(f"عدد المجلدات الرئيسية: {root_folders.count()}")
    
    for folder in root_folders:
        print(f"- {folder.name} (ID: {folder.id})")
        
        # عرض المجلدات الفرعية
        children = folder.children.all()
        for child in children:
            print(f"  -- {child.name} (ID: {child.id})")
    
    # إنشاء نص JSON للمجلدات
    print("\nمثال تنسيق JSON للشجرة:")
    print("[")
    for index, folder in enumerate(root_folders):
        print(f'  {{')
        print(f'    "id": {folder.id},')
        print(f'    "text": "{folder.name}",')
        print(f'    "icon": "fas fa-folder",')
        print(f'    "state": {{ "opened": true }},')
        
        # التحقق من وجود مجلدات فرعية
        children = folder.children.all()
        if children.exists():
            print(f'    "children": [')
            for i, child in enumerate(children):
                print(f'      {{')
                print(f'        "id": {child.id},')
                print(f'        "text": "{child.name}",')
                print(f'        "icon": "fas fa-folder"')
                if i < children.count() - 1:
                    print(f'      }},')
                else:
                    print(f'      }}')
            print(f'    ]')
        else:
            print(f'    "children": []')
        
        if index < root_folders.count() - 1:
            print(f'  }},')
        else:
            print(f'  }}')
    print("]")

if __name__ == "__main__":
    check_archive_view()