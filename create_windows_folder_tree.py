"""
إنشاء هيكل مجلدات الأرشيف بتصميم مشابه لويندوز كما في الصورة المرجعية
"""

import os
import sys
import django

# إعداد بيئة Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'car_rental_project.settings')
django.setup()

from django.utils import timezone
from django.db import transaction
from rental.models import ArchiveFolder

def create_windows_folder_structure():
    """
    إنشاء هيكل مجلدات يشبه ويندوز مع المجلدات المطلوبة:
    - تصميم (شجرة)
      - رسوم (1)
      - حضور (2)
      - حسابات (3)
      - محفوظات (4)
      - توكيلات (5)
    """
    try:
        with transaction.atomic():
            # التحقق مما إذا كانت المجلدات موجودة بالفعل وحذفها
            # حذف مجلدات النظام القديمة
            ArchiveFolder.objects.filter(
                name__in=['تصميم (شجرة)', 'رسوم (1)', 'حضور (2)', 'حسابات (3)', 'محفوظات (4)', 'توكيلات (5)']
            ).delete()
            
            # إنشاء المجلد الرئيسي
            root_folder = ArchiveFolder.objects.create(
                name='تصميم (شجرة)',
                parent=None,
                folder_type='system',
                description='المجلد الرئيسي لهيكل الأرشيف الإلكتروني',
                is_system_folder=True
            )
            
            # إنشاء المجلدات الفرعية
            subfolders = [
                {'name': 'رسوم (1)'},
                {'name': 'حضور (2)'},
                {'name': 'حسابات (3)'},
                {'name': 'محفوظات (4)'},
                {'name': 'توكيلات (5)'},
            ]
            
            for i, folder_data in enumerate(subfolders):
                ArchiveFolder.objects.create(
                    name=folder_data['name'],
                    parent=root_folder,
                    folder_type='system',
                    description=f'مجلد {folder_data["name"]}',
                    is_system_folder=True
                )
                
            print(f"✓ تم إنشاء هيكل المجلدات بنجاح")
            print(f"- المجلد الرئيسي: {root_folder.name}")
            print(f"- عدد المجلدات الفرعية: {len(subfolders)}")
                
    except Exception as e:
        print(f"× حدث خطأ أثناء إنشاء هيكل المجلدات: {str(e)}")
        return False
        
    return True
    
def get_folder_tree_json():
    """
    إنشاء تمثيل JSON لشجرة المجلدات لاستخدامه في JSTree
    """
    try:
        # الحصول على المجلد الرئيسي
        root_folder = ArchiveFolder.objects.filter(name='تصميم (شجرة)', parent=None).first()
        
        if not root_folder:
            print("× لم يتم العثور على المجلد الرئيسي")
            return None
            
        # الحصول على المجلدات الفرعية
        subfolders = ArchiveFolder.objects.filter(parent=root_folder)
        
        # إنشاء هيكل JSON
        folder_structure = {
            'id': f'folder-{root_folder.id}',
            'text': root_folder.name,
            'icon': 'fas fa-folder text-warning',
            'type': 'root',
            'state': {'opened': True},
            'children': []
        }
        
        # إضافة المجلدات الفرعية
        for subfolder in subfolders:
            folder_structure['children'].append({
                'id': f'folder-{subfolder.id}',
                'text': subfolder.name,
                'icon': 'fas fa-folder text-warning',
                'type': 'folder'
            })
            
        import json
        print(json.dumps(folder_structure, ensure_ascii=False, indent=2))
            
    except Exception as e:
        print(f"× حدث خطأ أثناء إنشاء تمثيل JSON لشجرة المجلدات: {str(e)}")
        return None
    
if __name__ == '__main__':
    print("بدء إنشاء هيكل مجلدات الأرشيف...")
    if create_windows_folder_structure():
        print("الآن سيتم عرض هيكل JSON:")
        get_folder_tree_json()