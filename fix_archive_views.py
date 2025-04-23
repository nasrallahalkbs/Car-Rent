"""
تحديث دالة عرض الأرشيف في ملف admin_views.py
"""
import os
import sys
import json

def update_admin_archive_view():
    """
    تحديث دالة admin_archive في ملف admin_views.py
    لضمان عرض شجرة المجلدات بشكل صحيح
    """
    file_path = "rental/admin_views.py"
    
    # التحقق من وجود الملف
    if not os.path.exists(file_path):
        print(f"خطأ: الملف {file_path} غير موجود")
        return
    
    # قراءة محتوى الملف
    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()
    
    # البحث عن دالة admin_archive
    start_index = content.find("def admin_archive(request):")
    if start_index == -1:
        print("لم يتم العثور على دالة admin_archive")
        return
    
    # البحث عن نهاية الدالة (بداية الدالة التالية)
    next_def_index = content.find("\ndef ", start_index + 1)
    if next_def_index == -1:
        # إذا كانت آخر دالة في الملف
        next_def_index = len(content)
    
    # استخراج كود الدالة
    function_code = content[start_index:next_def_index]
    
    # إنشاء دالة محدثة مع سجلات تصحيح
    updated_function = """def admin_archive(request):
    \"\"\"عرض الأرشيف الإلكتروني مع شجرة المجلدات\"\"\"
    # تحديد لغة العرض
    from django.utils.translation import get_language
    current_language = get_language()
    is_english = current_language == 'en'
    is_rtl = current_language == 'ar'
    
    # للتأكد من تحميل المجلدات بشكل صحيح
    print(f"DEBUG - تحميل المجلدات للأرشيف...")
    
    # الحصول على مجلدات الجذر
    root_folders = ArchiveFolder.objects.filter(parent=None).order_by('name')
    print(f"DEBUG - عدد المجلدات الرئيسية: {root_folders.count()}")
    
    # تعريف دالة بناء شجرة المجلدات
    def build_tree(folder):
        children = []
        for child in folder.children.all().order_by('name'):
            children.append(build_tree(child))
        
        return {
            'id': folder.id,
            'text': folder.name,
            'icon': 'fas fa-folder',
            'type': 'folder',
            'state': {'opened': False},
            'children': children
        }
    
    # بناء شجرة المجلدات
    folder_tree = []
    
    # إضافة سلة المحذوفات
    folder_tree.append({
        'id': 'recycle-bin',
        'text': _('سلة المحذوفات'),
        'icon': 'fas fa-trash-alt',
        'type': 'system',
        'state': {'opened': False},
        'children': []
    })
    
    # إضافة المجلدات الرئيسية مع المجلدات الفرعية
    for folder in root_folders:
        try:
            folder_tree.append(build_tree(folder))
            print(f"DEBUG - تمت إضافة المجلد: {folder.name} (ID: {folder.id})")
        except Exception as e:
            print(f"DEBUG - خطأ في إضافة المجلد {folder.name}: {str(e)}")
    
    # تحويل شجرة المجلدات إلى تنسيق JSON
    folder_tree_json = json.dumps(folder_tree, ensure_ascii=False)
    print(f"DEBUG - تم إنشاء شجرة المجلدات بنجاح")
    
    # إعداد سياق البيانات
    context = {
        'folder_tree': folder_tree_json,
        'subfolders': root_folders,
        'is_english': is_english,
        'is_rtl': is_rtl,
        'active_section': 'archive'
    }
    
    return render(request, 'admin/archive/archive_main.html', context)
"""
    
    # استبدال الدالة القديمة بالدالة المحدثة
    updated_content = content.replace(function_code, updated_function)
    
    # حفظ الملف المحدث
    with open(file_path, 'w', encoding='utf-8') as file:
        file.write(updated_content)
    
    print("تم تحديث دالة admin_archive بنجاح")

if __name__ == "__main__":
    update_admin_archive_view()