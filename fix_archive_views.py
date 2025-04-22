"""
تحديث دالة عرض الأرشيف في ملف admin_views.py
"""

import os
import re
import django

# إعداد بيئة Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'car_rental_project.settings')
django.setup()

def update_admin_archive_view():
    """
    تحديث دالة admin_archive في ملف admin_views.py
    لضمان عرض شجرة المجلدات بشكل صحيح
    """
    views_path = 'rental/admin_views.py'
    
    try:
        # قراءة محتوى ملف الدوال
        with open(views_path, 'r', encoding='utf-8') as file:
            content = file.read()
            
        # البحث عن دالة عرض الأرشيف الرئيسية
        archive_view_pattern = r'def admin_archive\(request\):([\s\S]*?)return render\('
        
        # تحقق مما إذا كان نمط البحث موجودًا
        archive_view_match = re.search(archive_view_pattern, content)
        
        if not archive_view_match:
            print(f"× لم يتم العثور على دالة admin_archive في ملف {views_path}")
            return False
            
        view_body = archive_view_match.group(1)
        
        # إنشاء الكود المطلوب لتحميل بيانات المجلدات
        folder_tree_code = """
    # الحصول على هيكل المجلدات لعرضه في الشجرة
    import json
    from .models import ArchiveFolder
    
    # المجلد الرئيسي
    root_folder = ArchiveFolder.objects.filter(name='تصميم (شجرة)', parent=None).first()
    
    if root_folder:
        # المجلدات الفرعية
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
            
        folder_tree = json.dumps([folder_structure], ensure_ascii=False)
    else:
        # استخدام هيكل افتراضي إذا لم يتم العثور على المجلد الرئيسي
        folder_tree = json.dumps([{
            'id': 'folder-root', 
            'text': 'تصميم (شجرة)', 
            'icon': 'fas fa-folder text-warning',
            'type': 'root',
            'state': {'opened': True},
            'children': [
                {'id': 'folder-1', 'text': 'رسوم (1)', 'icon': 'fas fa-folder text-warning', 'type': 'folder'},
                {'id': 'folder-2', 'text': 'حضور (2)', 'icon': 'fas fa-folder text-warning', 'type': 'folder'},
                {'id': 'folder-3', 'text': 'حسابات (3)', 'icon': 'fas fa-folder text-warning', 'type': 'folder'},
                {'id': 'folder-4', 'text': 'محفوظات (4)', 'icon': 'fas fa-folder text-warning', 'type': 'folder'},
                {'id': 'folder-5', 'text': 'توكيلات (5)', 'icon': 'fas fa-folder text-warning', 'type': 'folder'}
            ]
        }], ensure_ascii=False)
        """
        
        # تحقق مما إذا كان الكود الحالي يحتوي على تعريف لـ folder_tree
        if "folder_tree" not in view_body:
            # إضافة الكود لتحميل بيانات المجلدات
            updated_view_body = view_body + folder_tree_code
            updated_content = content.replace(view_body, updated_view_body)
            
            # كتابة المحتوى المحدث
            with open(views_path, 'w', encoding='utf-8') as file:
                file.write(updated_content)
                
            print(f"✓ تم تحديث دالة admin_archive في ملف {views_path}")
            return True
        else:
            print(f"ℹ دالة admin_archive تحتوي بالفعل على تعريف لـ folder_tree")
            return True
            
    except Exception as e:
        print(f"× حدث خطأ أثناء تحديث ملف الدوال: {str(e)}")
        return False
        
if __name__ == '__main__':
    print("بدء تحديث دالة عرض الأرشيف...")
    update_admin_archive_view()