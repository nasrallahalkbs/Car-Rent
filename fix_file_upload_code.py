"""
إصلاح كود إضافة الملفات في دالة admin_archive
"""

def fix_file_upload_code():
    """تصحيح كود إضافة الملفات ليتوافق مع حقول نموذج Document"""
    # مسار ملف admin_views.py
    views_path = "rental/admin_views.py"
    
    # قراءة الملف
    with open(views_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # البحث عن جزء كود إضافة الملفات
    import re
    
    file_upload_pattern = r'# معالجة إضافة ملف جديد.*?# إنشاء مستند جديد \(ملف\).*?document = Document\.objects\.create\(.*?\)\s*\s*print\(f"DEBUG - تم إنشاء مستند جديد: \{document\.title\}"\)'
    
    # استبدال كود إضافة الملفات القديم بكود متوافق مع نموذج Document
    fixed_code = """# معالجة إضافة ملف جديد
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
            
            # حساب حجم الملف بوحدة البايت
            file_size = uploaded_file.size
            
            # إنشاء مستند جديد (ملف)
            document = Document.objects.create(
                title=title,
                description=description,
                document_type='other',  # استخدام القيمة الافتراضية 'other'
                file=uploaded_file,
                file_size=file_size,
                document_date=timezone.now().date(),
                related_to='other',  # استخدام القيمة الافتراضية 'other'
                added_by=request.user if request.user.is_authenticated else None
            )
            
            print(f"DEBUG - تم إنشاء مستند جديد: {document.title}")"""
    
    # استبدال الكود القديم بالكود المصحح
    content = re.sub(file_upload_pattern, fixed_code, content, flags=re.DOTALL)
    
    # كتابة المحتوى المحدث إلى الملف
    with open(views_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"تم تصحيح كود إضافة الملفات في {views_path}")
    return True

def main():
    """تنفيذ تصحيح كود إضافة الملفات"""
    print("بدء تصحيح كود إضافة الملفات...")
    
    result = fix_file_upload_code()
    
    if result:
        print("تم تصحيح كود إضافة الملفات بنجاح!")
    else:
        print("حدث خطأ أثناء محاولة تصحيح كود إضافة الملفات.")

if __name__ == "__main__":
    main()