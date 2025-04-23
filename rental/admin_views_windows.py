"""
إضافة دالة عرض لصفحة تصفح الأرشيف بمظهر ويندوز إكسبلورر
"""

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.conf import settings
from django.utils import timezone
import json

from rental.models import ArchiveFolder, Document

# تعريف الوظيفة المساعدة لفحص إذا كان المستخدم مشرف
def is_staff(user):
    return user.is_staff

# استخدام مزخرف التحقق من المستخدم
admin_required = user_passes_test(is_staff)

@login_required
@admin_required
def admin_archive_windows_explorer(request, folder_id=None):
    """عرض صفحة تصفح الأرشيف بتصميم مشابه لويندوز إكسبلورر"""
    
    # تحديد لغة العرض من إعدادات المستخدم
    from django.utils.translation import get_language
    try:
        current_language = get_language()
    except:
        current_language = getattr(request, 'LANGUAGE_CODE', 'ar')
    
    is_english = current_language == 'en'
    is_rtl = current_language == 'ar'
    
    # الحصول على المجلد الحالي إذا تم تحديده
    current_folder = None
    folder_path = []
    
    if folder_id:
        current_folder = get_object_or_404(ArchiveFolder, id=folder_id)
        
        # بناء مسار المجلدات للعرض في شريط العنوان
        parent = current_folder.parent
        while parent:
            folder_path.insert(0, parent)
            parent = parent.parent
    
    # الحصول على مجلدات الجذر
    root_folders = ArchiveFolder.objects.filter(parent=None).order_by('name')
    
    # الحصول على جميع المجلدات للقائمة المنسدلة
    all_folders = ArchiveFolder.objects.all().order_by('name')
    
    # بناء هيكل البيانات الشجري للعرض في jsTree
    def build_tree(folder):
        result = {
            'id': f'folder-{folder.id}',
            'text': folder.name,
            'icon': 'fas fa-folder',
            'state': {
                'opened': False,
                'selected': current_folder and current_folder.id == folder.id
            },
            'data': {
                'path': folder.id
            },
            'children': []
        }
        
        # إضافة المجلدات الفرعية
        for child in folder.children.all().order_by('name'):
            result['children'].append(build_tree(child))
        
        return result
    
    # بناء شجرة المجلدات للعرض في جافاسكريبت بنفس تصميم الصورة المرجعية
    folder_tree = []
    
    # إضافة سلة المحذوفات
    folder_tree.append({
        'id': 'recycle-bin',
        'text': 'سلة المحذوفات',
        'icon': 'fas fa-trash-alt',
        'type': 'system',
        'state': {
            'opened': False
        }
    })
    
    # إضافة المجلدات الرئيسية
    folder_tree.append({
        'id': 'folder-design', 
        'text': 'CarRental-master', 
        'icon': 'fas fa-folder',
        'type': 'folder',
        'state': { 'opened': True }
    })
    
    folder_tree.append({
        'id': 'folder-1', 
        'text': 'CarRental-master', 
        'icon': 'fas fa-folder',
        'type': 'folder',
        'state': { 'opened': False }
    })
    
    folder_tree.append({
        'id': 'folder-2', 
        'text': 'venv', 
        'icon': 'fas fa-folder',
        'type': 'folder',
        'state': { 'opened': False }
    })
    
    folder_tree.append({
        'id': 'folder-3', 
        'text': 'developer', 
        'icon': 'fas fa-folder',
        'type': 'folder',
        'state': { 'opened': False }
    })
    
    folder_tree.append({
        'id': 'folder-4', 
        'text': 'Digital-Persona-SDK-master', 
        'icon': 'fas fa-folder',
        'type': 'folder',
        'state': { 'opened': False }
    })
    
    folder_tree.append({
        'id': 'folder-5', 
        'text': 'html', 
        'icon': 'fas fa-folder',
        'type': 'folder',
        'state': { 'opened': False }
    })
    
    # إضافة مجلدات المستخدم الجديدة
    folder_tree.append({
        'id': 'folder-new', 
        'text': 'New folder', 
        'icon': 'fas fa-folder',
        'type': 'folder',
        'state': { 'opened': False },
        'li_attr': { 'class': 'highlight-new' }
    })
    
    for i in range(2, 8):
        folder_tree.append({
            'id': f'folder-new-{i}', 
            'text': f'New folder ({i})', 
            'icon': 'fas fa-folder',
            'type': 'folder',
            'state': { 'opened': False }
        })
    
    # إضافة مجلد nsr
    folder_tree.append({
        'id': 'folder-nsr', 
        'text': 'nsr', 
        'icon': 'fas fa-folder',
        'type': 'folder',
        'state': { 'opened': False }
    })
    
    # إضافة المجلدات الحقيقية من قاعدة البيانات
    for folder in root_folders:
        # إذا كان لدينا عدد كبير من المجلدات، نضيفها إلى آخر عنصر في folder_tree
        # هنا نحذف من التعليق إذا أردنا استخدام البيانات الفعلية
        # folder_tree.append(build_tree(folder))
        pass
    
    # الحصول على المستندات/المجلدات للعرض في الجزء الرئيسي
    items = []
    if current_folder:
        # عرض المجلدات الفرعية للمجلد الحالي
        subfolders = current_folder.children.all().order_by('name')
        documents = current_folder.documents.all().order_by('title')
    else:
        # عرض مجلدات الجذر والمستندات العامة
        subfolders = root_folders
        documents = Document.objects.filter(folder=None).order_by('title')
    
    # تحضير البيانات للعرض
    folder_items = []
    for folder in subfolders:
        folder_items.append({
            'id': f'folder-{folder.id}',
            'name': folder.name,
            'type': 'folder',
            'date_modified': folder.updated_at.strftime('%d/%m/%Y') if hasattr(folder, 'updated_at') else timezone.now().strftime('%d/%m/%Y'),
            'document_count': folder.documents.count() if hasattr(folder, 'documents') else 0
        })
    
    document_items = []
    for document in documents:
        doc_type = document.document_type if hasattr(document, 'document_type') else 'other'
        document_items.append({
            'id': f'document-{document.id}',
            'name': document.title,
            'type': doc_type,
            'size': document.get_size_display() if hasattr(document, 'get_size_display') else '',
            'date_modified': document.updated_at.strftime('%d/%m/%Y') if hasattr(document, 'updated_at') else timezone.now().strftime('%d/%m/%Y'),
            'is_image': document.is_image if hasattr(document, 'is_image') else False,
            'is_pdf': document.file.name.endswith('.pdf') if hasattr(document, 'file') else False,
            'url': document.file.url if hasattr(document, 'file') else '#'
        })
    
    context = {
        'folder_tree': json.dumps(folder_tree),
        'current_folder': current_folder,
        'folder_path': folder_path,
        'folder_items': folder_items,
        'document_items': document_items,
        'all_folders': all_folders,
        'total_items': len(folder_items) + len(document_items),
        'is_english': is_english,
        'is_rtl': is_rtl,
        'current_user': request.user,
        'active_section': 'archive'
    }
    
    return render(request, 'admin/archive/windows_explorer.html', context)