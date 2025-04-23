"""
تصحيح عرض الأرشيف باستخدام قالب وظيفي جديد يعمل بشكل كامل
"""

def fix_admin_archive_view():
    """تعديل دالة admin_archive لاستخدام القالب الوظيفي الجديد"""
    import os
    
    # مسار ملف المشاهدات الإدارية
    admin_views_path = "rental/admin_views.py"
    
    # التحقق من وجود الملف
    if not os.path.exists(admin_views_path):
        print(f"خطأ: ملف {admin_views_path} غير موجود")
        return False
    
    # قراءة محتوى الملف
    with open(admin_views_path, 'r', encoding='utf-8') as file:
        content = file.read()
    
    # تعديل دالة admin_archive لاستخدام القالب الوظيفي
    old_render_line = "    return render(request, 'admin/archive/simple_archive.html', context)"
    new_render_line = "    return render(request, 'admin/archive/functional_archive.html', context)"
    
    # استبدال سطر الإرجاع
    if old_render_line in content:
        updated_content = content.replace(old_render_line, new_render_line)
        
        # كتابة المحتوى المحدث إلى الملف
        with open(admin_views_path, 'w', encoding='utf-8') as file:
            file.write(updated_content)
        
        print(f"تم تحديث ملف {admin_views_path} لاستخدام قالب الأرشيف الوظيفي")
        return True
    
    # البحث عن أي استخدام لقالب الأرشيف وتحديثه
    lines = content.split('\n')
    updated = False
    
    for i in range(len(lines)):
        if "def admin_archive(" in lines[i]:
            # البحث عن سطر الإرجاع في دالة admin_archive
            for j in range(i, min(i + 100, len(lines))):
                if "return render" in lines[j] and "admin/archive/" in lines[j]:
                    # استبدال اسم القالب
                    lines[j] = "    return render(request, 'admin/archive/functional_archive.html', context)"
                    updated = True
                    break
            
            if updated:
                break
    
    if updated:
        # كتابة المحتوى المحدث إلى الملف
        updated_content = '\n'.join(lines)
        with open(admin_views_path, 'w', encoding='utf-8') as file:
            file.write(updated_content)
        
        print(f"تم تحديث ملف {admin_views_path} لاستخدام قالب الأرشيف الوظيفي")
        return True
    
    print(f"لم يتم العثور على دالة admin_archive في ملف {admin_views_path}")
    return False

def main():
    """تنفيذ الإصلاحات"""
    print("بدء إصلاح عرض الأرشيف باستخدام قالب وظيفي جديد...")
    
    result = fix_admin_archive_view()
    
    if result:
        print("تم إصلاح عرض الأرشيف بنجاح!")
    else:
        print("حدث خطأ أثناء محاولة إصلاح عرض الأرشيف.")

if __name__ == "__main__":
    main()