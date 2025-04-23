"""
إضافة معالجة لإضافة المجلدات والملفات في دالة admin_archive
"""

def update_admin_archive_function():
    """تحديث دالة admin_archive لمعالجة إضافة المجلدات والملفات"""
    # مسار ملف admin_views.py
    views_path = "rental/admin_views.py"
    
    # قراءة الملف
    with open(views_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # البحث عن بداية معالجة معلمات URL
    pattern = r'# الحصول على معلمات URL.*?print\(f"DEBUG - معلمة الإجراء: \{action_param\}"\)'
    
    # استبدال بمعالجة محسنة تتضمن إضافة المجلدات والملفات
    import re
    
    replacement = """# الحصول على معلمات URL
    folder_param = request.GET.get('folder', None)
    document_param = request.GET.get('document', None)
    action_param = request.GET.get('action', None)
    
    print(f"DEBUG - معلمة المجلد: {folder_param}")
    print(f"DEBUG - معلمة المستند: {document_param}")
    print(f"DEBUG - معلمة الإجراء: {action_param}")
    
    # معالجة إضافة مجلد جديد
    if action_param == 'add_folder' and request.method == 'POST':
        name = request.POST.get('name', '')
        description = request.POST.get('description', '')
        parent_id = request.POST.get('parent', None)
        
        if name:
            # البحث عن المجلد الأب إذا تم تحديده
            parent = None
            if parent_id:
                try:
                    parent = ArchiveFolder.objects.get(id=parent_id)
                except:
                    pass
            
            # إنشاء المجلد الجديد
            folder = ArchiveFolder.objects.create(
                name=name,
                description=description,
                parent=parent,
                created_by=request.user if request.user.is_authenticated else None
            )
            
            print(f"DEBUG - تم إنشاء مجلد جديد: {folder.name}")
            messages.success(request, f"تم إنشاء المجلد '{name}' بنجاح")
            
            # إعادة توجيه إلى المجلد الجديد
            return redirect(f"{request.path}?folder={folder.id}")
        else:
            messages.error(request, "يرجى إدخال اسم المجلد")
    
    # معالجة إضافة ملف جديد
    if action_param == 'add_file' and request.method == 'POST':
        title = request.POST.get('title', '')
        description = request.POST.get('description', '')
        folder_id = request.POST.get('folder', None)
        uploaded_file = request.FILES.get('file', None)
        
        if title and uploaded_file:
            # البحث عن المجلد المستهدف إذا تم تحديده
            folder = None
            if folder_id:
                try:
                    folder = ArchiveFolder.objects.get(id=folder_id)
                except:
                    pass
            
            # حساب حجم الملف بطريقة مناسبة
            file_size = f"{uploaded_file.size / 1024:.1f} KB" if uploaded_file.size < 1024 * 1024 else f"{uploaded_file.size / (1024 * 1024):.1f} MB"
            
            # تحديد نوع الملف بناءً على الامتداد
            file_name = uploaded_file.name.lower()
            file_type = 'other'
            if file_name.endswith('.pdf'):
                file_type = 'pdf'
            elif file_name.endswith(('.doc', '.docx')):
                file_type = 'doc'
            elif file_name.endswith(('.xls', '.xlsx')):
                file_type = 'xls'
            elif file_name.endswith(('.jpg', '.jpeg', '.png', '.gif')):
                file_type = 'img'
            elif file_name.endswith(('.zip', '.rar')):
                file_type = 'zip'
            
            # إنشاء مستند جديد (ملف)
            document = Document.objects.create(
                title=title,
                description=description,
                folder=folder,
                file=uploaded_file,
                file_type=file_type,
                file_size=file_size,
                created_by=request.user if request.user.is_authenticated else None
            )
            
            print(f"DEBUG - تم إنشاء مستند جديد: {document.title}")
            messages.success(request, f"تم إضافة الملف '{title}' بنجاح")
            
            # إعادة توجيه
            if folder:
                return redirect(f"{request.path}?folder={folder.id}")
            else:
                return redirect(request.path)
        else:
            if not title:
                messages.error(request, "يرجى إدخال عنوان الملف")
            if not uploaded_file:
                messages.error(request, "يرجى اختيار ملف للرفع")"""
    
    # استبدال الجزء القديم بالمعالجة المحسنة
    content = re.sub(pattern, replacement, content, flags=re.DOTALL)
    
    # كتابة المحتوى المحدث إلى الملف
    with open(views_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"تم تحديث دالة admin_archive لمعالجة إضافة المجلدات والملفات في {views_path}")
    return True

def main():
    """تنفيذ تحديث دالة admin_archive"""
    print("بدء تحديث دالة admin_archive لمعالجة إضافة المجلدات والملفات...")
    
    result = update_admin_archive_function()
    
    if result:
        print("تم تحديث دالة admin_archive بنجاح!")
    else:
        print("حدث خطأ أثناء محاولة تحديث دالة admin_archive.")

if __name__ == "__main__":
    main()