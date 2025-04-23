"""
إصلاح عرض شجرة المجلدات في صفحة الأرشيف مع إضافة سجلات تصحيح
"""
import os
import sys
import django
import json

# إعداد البيئة لاستخدام نماذج Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'car_rental_project.settings')
django.setup()

from rental.admin_views import admin_archive
from rental.models import ArchiveFolder
from django.utils.translation import gettext as _

def fix_admin_archive():
    """تحديث دالة admin_archive في admin_views.py"""
    file_path = "rental/admin_views.py"
    
    # قراءة الملف
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
        print("لم يتم العثور على نهاية الدالة")
        return
    
    # استخراج كود الدالة
    function_code = content[start_index:next_def_index]
    
    # إنشاء دالة محدثة مع سجلات تصحيح
    updated_function = """def admin_archive(request):
    \"\"\"صفحة إدارة الأرشيف الإلكتروني - الواجهة الرئيسية للأرشيف الشجري\"\"\"
    # تحديد لغة العرض
    from django.utils.translation import get_language
    current_language = get_language()
    is_english = current_language == 'en'
    is_rtl = current_language == 'ar'
    
    # البحث والتصفية
    search = request.GET.get('search', '')
    
    # الحصول على مجلدات الجذر
    root_folders = ArchiveFolder.get_root_folders()
    print(f"DEBUG: عدد المجلدات الرئيسية: {root_folders.count()}")
    for folder in root_folders:
        print(f"DEBUG: مجلد رئيسي: {folder.name} (ID: {folder.id})")
    
    # الحصول على المستندات في المجلد الرئيسي (بدون مجلد)
    files = Document.objects.filter(folder__isnull=True).order_by('-created_at')
    
    # تطبيق البحث إذا كان موجودًا
    if search:
        files = files.filter(
            Q(title__icontains=search) | 
            Q(description__icontains=search) | 
            Q(reference_number__icontains=search) |
            Q(tags__icontains=search)
        )
    
    # بناء هيكل البيانات الشجري في تصميم مشابه للويندوز
    def build_tree(folder):
        result = {
            'id': folder.id,
            'text': folder.name,
            'icon': 'fas fa-folder',
            'type': 'folder',
            'state': {
                'opened': False
            },
            'children': []
        }
        
        # إضافة المجلدات الفرعية
        for child in folder.children.all().order_by('name'):
            result['children'].append(build_tree(child))
        
        return result
    
    # بناء شجرة المجلدات للعرض في تصميم مشابه للصورة المرجعية
    folder_tree = []
    
    # إضافة سلة المحذوفات
    folder_tree.append({
        'id': 'recycle-bin', 
        'text': _('سلة المحذوفات'), 
        'icon': 'fas fa-trash-alt',
        'type': 'system',
        'state': { 'opened': False }
    })
    
    # إضافة المجلدات الرئيسية الحقيقية من قاعدة البيانات
    for folder in root_folders:
        folder_tree.append(build_tree(folder))
    
    # إضافة سجل تصحيح لشجرة المجلدات
    print(f"DEBUG: بيانات شجرة المجلدات: {json.dumps(folder_tree, ensure_ascii=False, indent=2)}")
    
    # إحصائيات النظام
    total_folders = ArchiveFolder.objects.count()
    total_files = Document.objects.count()
    
    context = {
        'folder_tree': json.dumps(folder_tree),
        'subfolders': root_folders,
        'files': files,
        'total_folders': total_folders,
        'total_files': total_files,
        'search': search,
        'today': timezone.now().date().strftime('%Y-%m-%d'),
        'current_user': request.user,
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
    fix_admin_archive()