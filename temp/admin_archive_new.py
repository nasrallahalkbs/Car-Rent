@login_required
@admin_required
def admin_archive(request):
    """صفحة إدارة الأرشيف الإلكتروني - الواجهة الرئيسية للأرشيف الشجري"""
    # تحديد لغة العرض
    from django.utils.translation import get_language
    current_language = get_language()
    is_english = current_language == 'en'
    is_rtl = current_language == 'ar'
    
    # الحصول على مجلدات الجذر
    root_folders = ArchiveFolder.get_root_folders()
    
    # الحصول على المستندات في المجلد الرئيسي (بدون مجلد)
    files = Document.objects.filter(folder__isnull=True).order_by('-created_at')
    
    # بناء هيكل البيانات الشجري الكامل للعرض في jsTree
    def build_tree(folder):
        result = {
            'id': folder.id,
            'text': folder.name,
            'icon': 'fas fa-folder',
            'state': {
                'opened': False
            },
            'children': []
        }
        
        # إضافة المجلدات الفرعية
        for child in folder.children.all().order_by('name'):
            result['children'].append(build_tree(child))
        
        return result
    
    # بناء شجرة المجلدات للعرض في جافاسكريبت
    folder_tree = []
    
    # إضافة نقطة الجذر (الرئيسية)
    folder_tree.append({
        'id': '#',
        'text': _('الرئيسية'),
        'icon': 'fas fa-hdd',
        'state': {
            'opened': True
        }
    })
    
    # إضافة المجلدات الرئيسية
    for folder in root_folders:
        folder_tree.append(build_tree(folder))
    
    # إحصائيات النظام
    total_folders = ArchiveFolder.objects.count()
    total_files = Document.objects.count()
    
    context = {
        'folder_tree': json.dumps(folder_tree),
        'subfolders': root_folders,
        'files': files,
        'total_folders': total_folders,
        'total_files': total_files,
        'today': timezone.now().date().strftime('%Y-%m-%d'),
        'current_user': request.user,
        'is_english': is_english,
        'is_rtl': is_rtl,
        'active_section': 'archive'
    }
    
    return render(request, 'admin/archive/archive_main.html', context)