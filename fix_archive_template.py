"""
استخدام قالب أرشيف جديد لإصلاح مشكلة عرض المجلدات
"""
import os
import json

def fix_admin_archive_view():
    """تحديث وظيفة admin_archive لاستخدام القالب المحسن"""
    file_path = "rental/admin_views.py"
    
    if not os.path.exists(file_path):
        print(f"خطأ: الملف {file_path} غير موجود")
        return
    
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
        next_def_index = len(content)
    
    # استخراج كود الدالة
    function_code = content[start_index:next_def_index]
    
    # إنشاء دالة محدثة تستخدم القالب المحسن
    updated_function = """def admin_archive(request):
    \"\"\"عرض الأرشيف الإلكتروني مع شجرة المجلدات\"\"\"
    # تحديد لغة العرض
    from django.utils.translation import get_language
    current_language = get_language()
    is_english = current_language == 'en'
    is_rtl = current_language == 'ar'
    
    print(f"DEBUG: تحميل صفحة الأرشيف الإلكتروني...")
    
    # الحصول على مجلدات الجذر
    root_folders = ArchiveFolder.objects.filter(parent=None).order_by('name')
    print(f"DEBUG: عدد المجلدات الرئيسية: {root_folders.count()}")
    
    # بناء شجرة المجلدات - طريقة بسيطة بدون تكرار
    folder_tree = []
    
    # إضافة سلة المحذوفات كمجلد خاص
    folder_tree.append({
        'id': 'recycle-bin',
        'text': _('سلة المحذوفات'),
        'icon': 'fas fa-trash-alt',
        'type': 'system',
        'state': {'opened': False},
        'children': []
    })
    
    # إضافة المجلدات الرئيسية
    for folder in root_folders:
        print(f"DEBUG: إضافة مجلد رئيسي: {folder.name} (ID: {folder.id})")
        
        folder_data = {
            'id': folder.id,
            'text': folder.name,
            'icon': 'fas fa-folder',
            'type': 'folder',
            'state': {'opened': False},
            'children': []
        }
        
        # الحصول على المجلدات الفرعية لهذا المجلد
        child_folders = folder.children.all().order_by('name')
        
        # إضافة المجلدات الفرعية
        for child in child_folders:
            print(f"DEBUG: -- إضافة مجلد فرعي: {child.name} (ID: {child.id})")
            
            folder_data['children'].append({
                'id': child.id,
                'text': child.name,
                'icon': 'fas fa-folder',
                'type': 'folder'
            })
        
        # إضافة المجلد وأطفاله إلى شجرة المجلدات
        folder_tree.append(folder_data)
    
    # عرض شجرة المجلدات في سجل التصحيح
    print(f"DEBUG: شجرة المجلدات: {json.dumps(folder_tree, ensure_ascii=False)}")
    
    # إعداد سياق القالب
    context = {
        'folder_tree': json.dumps(folder_tree, ensure_ascii=False),
        'subfolders': root_folders,
        'is_english': is_english,
        'is_rtl': is_rtl,
        'active_section': 'archive'
    }
    
    return render(request, 'admin/archive/archive_main_fixed.html', context)
"""
    
    # استبدال الدالة القديمة بالدالة المحدثة
    updated_content = content.replace(function_code, updated_function)
    
    # حفظ الملف المحدث
    with open(file_path, 'w', encoding='utf-8') as file:
        file.write(updated_content)
    
    print("تم تحديث دالة admin_archive لاستخدام القالب المحسن")

if __name__ == "__main__":
    fix_admin_archive_view()