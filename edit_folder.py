"""
إضافة دوال تعديل وحذف المجلدات إلى ملف admin_views.py
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from rental.models import ArchiveFolder, Document

def add_folder_functions():
    """
    إضافة دوال تعديل وحذف المجلدات
    """
    # قراءة الملف الحالي
    with open('rental/admin_views.py', 'a') as file:
        file.write("""
@login_required
def edit_folder(request, folder_id):
    \"\"\"تعديل مجلد\"\"\"
    # التحقق من أن المستخدم مسؤول
    if not request.user.is_admin:
        messages.error(request, "ليس لديك صلاحية للوصول إلى هذه الصفحة")
        return redirect('index')
    
    folder = get_object_or_404(ArchiveFolder, id=folder_id)
    
    if request.method == 'POST':
        # تحديث معلومات المجلد
        folder.name = request.POST.get('name')
        folder.description = request.POST.get('description', '')
        
        # تحديث المجلد الأب إذا تم اختياره
        parent_id = request.POST.get('parent_id')
        if parent_id and parent_id != str(folder.id):
            folder.parent = ArchiveFolder.objects.get(id=parent_id)
        elif not parent_id:
            folder.parent = None
        
        folder.save()
        messages.success(request, "تم تحديث المجلد بنجاح")
        
        # العودة إلى المجلد الأب إذا كان موجودًا
        if folder.parent:
            return redirect('admin_archive_folder', folder_id=folder.parent.id)
        else:
            return redirect('admin_archive')
    
    # إعداد سياق العرض للنموذج
    context = {
        'folder': folder,
        'folders': ArchiveFolder.objects.exclude(id=folder_id).order_by('name'),
    }
    
    return render(request, 'admin/archive/edit_folder.html', context)

@login_required
def delete_folder(request, folder_id):
    \"\"\"حذف مجلد\"\"\"
    # التحقق من أن المستخدم مسؤول
    if not request.user.is_admin:
        messages.error(request, "ليس لديك صلاحية للوصول إلى هذه الصفحة")
        return redirect('index')
    
    folder = get_object_or_404(ArchiveFolder, id=folder_id)
    
    # الاحتفاظ بالمجلد الأب للعودة إليه بعد الحذف
    parent_id = None
    if folder.parent:
        parent_id = folder.parent.id
    
    # التحقق من عدم وجود مجلدات فرعية أو مستندات
    subfolders = ArchiveFolder.objects.filter(parent=folder).exists()
    documents = Document.objects.filter(folder=folder).exists()
    
    if subfolders or documents:
        messages.error(request, "لا يمكن حذف المجلد لأنه يحتوي على مجلدات فرعية أو مستندات")
        if parent_id:
            return redirect('admin_archive_folder', folder_id=parent_id)
        else:
            return redirect('admin_archive')
    
    # حذف المجلد
    folder.delete()
    messages.success(request, "تم حذف المجلد بنجاح")
    
    # العودة إلى المجلد الأب إذا كان موجودًا
    if parent_id:
        return redirect('admin_archive_folder', folder_id=parent_id)
    else:
        return redirect('admin_archive')
""")
        print("تمت إضافة الدوال بنجاح")

if __name__ == "__main__":
    add_folder_functions()