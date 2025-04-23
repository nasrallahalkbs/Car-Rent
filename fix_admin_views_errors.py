"""
إصلاح الأخطاء النحوية في ملف admin_views.py
"""

def fix_syntax_errors():
    """إصلاح الأخطاء النحوية في ملف admin_views.py"""
    # مسار ملف admin_views.py
    views_path = "rental/admin_views.py"
    
    # قراءة الملف
    with open(views_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # إصلاح متغير all_folders غير المعرّف
    import re
    
    # البحث عن التعريفات الحالية قبل إنشاء السياق
    pattern_before_context = r'# الحصول على مجلدات الجذر\s*root_folders = ArchiveFolder\.objects\.filter\(parent=None\)\.order_by\(\'name\'\)'
    
    # إضافة تعريف متغير all_folders
    replacement = """# الحصول على مجلدات الجذر
    root_folders = ArchiveFolder.objects.filter(parent=None).order_by('name')
    # الحصول على جميع المجلدات للاستخدام في القوائم المنسدلة
    all_folders = ArchiveFolder.objects.all().order_by('name')"""
    
    # استبدال المتطابقات في المحتوى
    content = re.sub(pattern_before_context, replacement, content)
    
    # كتابة المحتوى المحدث إلى الملف
    with open(views_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"تم إصلاح الأخطاء النحوية في {views_path}")
    
    return True

def main():
    """تنفيذ إصلاحات الأخطاء النحوية"""
    print("بدء إصلاح الأخطاء النحوية في ملف admin_views.py...")
    
    result = fix_syntax_errors()
    
    if result:
        print("تم إصلاح الأخطاء النحوية بنجاح!")
    else:
        print("حدث خطأ أثناء محاولة إصلاح الأخطاء النحوية.")

if __name__ == "__main__":
    main()