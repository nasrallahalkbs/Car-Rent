"""
تصحيح عرض الأرشيف باستخدام قالب مبسط جديد يعمل بشكل فعال
"""

def fix_admin_archive_view():
    """تعديل دالة admin_archive لاستخدام القالب البسيط الجديد"""
    
    import os
    
    # مسار ملف admin_views.py
    views_path = "rental/admin_views.py"
    
    # قراءة الملف
    with open(views_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # دالة admin_archive الجديدة
    new_function = """def admin_archive(request):
    \"\"\"عرض الأرشيف الإلكتروني بتصميم بسيط\"\"\"
    from django.utils.translation import get_language
    from django.shortcuts import redirect
    current_language = get_language()
    is_english = current_language == 'en'
    is_rtl = current_language == 'ar'
    
    # الحصول على معلمات URL
    folder_param = request.GET.get('folder', None)
    document_param = request.GET.get('document', None)
    action_param = request.GET.get('action', None)
    
    print(f"DEBUG - معلمة المجلد: {folder_param}")
    print(f"DEBUG - معلمة المستند: {document_param}")
    print(f"DEBUG - معلمة الإجراء: {action_param}")
    
    # الحصول على مجلدات الجذر
    root_folders = ArchiveFolder.objects.filter(parent=None).order_by('name')
    print(f"DEBUG - عدد المجلدات الرئيسية: {root_folders.count()}")
    
    # معالجة إضافة مجلد جديد
    if action_param == 'add_folder' and request.method == 'POST':
        name = request.POST.get('name', '')
        description = request.POST.get('description', '')
        parent_id = request.POST.get('parent', None)
        
        if name:
            parent = None
            if parent_id:
                try:
                    parent = ArchiveFolder.objects.get(id=parent_id)
                except ArchiveFolder.DoesNotExist:
                    pass
            
            folder = ArchiveFolder.objects.create(
                name=name,
                description=description,
                parent=parent,
                created_by=request.user if hasattr(request, 'user') else None
            )
            print(f"DEBUG - تم إنشاء مجلد جديد: {folder.name}")
            
            # إعادة توجيه
            if parent_id:
                return redirect('admin_archive')
            else:
                return redirect('admin_archive')
    
    # معالجة إضافة ملف جديد
    if action_param == 'add_file' and request.method == 'POST':
        title = request.POST.get('title', '')
        description = request.POST.get('description', '')
        folder_id = request.POST.get('folder', None)
        uploaded_file = request.FILES.get('file', None)
        
        if title and uploaded_file:
            folder = None
            if folder_id:
                try:
                    folder = ArchiveFolder.objects.get(id=folder_id)
                except ArchiveFolder.DoesNotExist:
                    pass
            
            # إنشاء مستند جديد
            document = Document.objects.create(
                title=title,
                description=description,
                folder=folder,
                created_by=request.user if hasattr(request, 'user') else None,
                file=uploaded_file
            )
            print(f"DEBUG - تم إنشاء مستند جديد: {document.title}")
            
            # إعادة توجيه
            if folder_id:
                return redirect('admin_archive')
            else:
                return redirect('admin_archive')
    
    # الحصول على المستندات
    documents = []
    if folder_param:
        try:
            folder_id = int(folder_param)
            current_folder = ArchiveFolder.objects.get(id=folder_id)
            documents = Document.objects.filter(folder=current_folder).order_by('-created_at')
        except (ValueError, ArchiveFolder.DoesNotExist):
            # استخدام وضع العرض المباشر للمجلدات الثابتة
            pass
    else:
        # عرض المستندات في المجلد الرئيسي (بدون مجلد)
        documents = Document.objects.filter(folder__isnull=True).order_by('-created_at')
    
    # إعداد سياق البيانات
    context = {
        'root_folders': root_folders,
        'documents': documents,
        'folder_param': folder_param,
        'document_param': document_param,
        'is_english': is_english,
        'is_rtl': is_rtl,
        'active_section': 'archive'
    }
    
    # استخدام قالب الأرشيف الثابت البسيط
    return render(request, 'admin/archive/static_archive.html', context)"""
    
    # استبدال دالة admin_archive الحالية
    import re
    pattern = r'def admin_archive\(request\):.*?return render\(request,[^)]+\)'
    new_content = re.sub(pattern, new_function, content, flags=re.DOTALL)
    
    # كتابة المحتوى المحدث
    with open(views_path, 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    print(f"تم تحديث دالة admin_archive في {views_path}")
    
def main():
    """تنفيذ الإصلاحات"""
    print("بدء تحديث دالة عرض الأرشيف...")
    
    # تحديث دالة admin_archive
    fix_admin_archive_view()
    
    print("تم تحديث دالة عرض الأرشيف بنجاح.")

if __name__ == "__main__":
    main()