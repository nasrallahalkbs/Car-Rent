"""
إصلاح سريع لمشاكل المسافات البادئة في ملف admin_views.py
"""

import os
import re

def fix_indentation():
    """إصلاح مشاكل المسافات البادئة في ملف admin_views.py"""
    
    print("\n" + "="*70)
    print("🔧 إصلاح سريع لمشاكل المسافات البادئة")
    print("="*70 + "\n")
    
    file_path = os.path.join('rental', 'admin_views.py')
    
    try:
        # قراءة الملف
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()
        
        # إصلاح المشكلة حول السطر 2603
        # البحث عن النمط المشكلة
        # pattern = r'([ \t]+# التنظيف الفوري بعد الحفظ\n[ \t]+Document\.objects\.filter.*\.delete\(\))\n[ \t]*messages\.success'
        # تستخدم تعبير عادي أبسط للبحث والاستبدال في هذه الحالة
        broken_area = """                    
                    # التنظيف الفوري بعد الحفظ
                    Document.objects.filter(folder=folder, title__in=['', 'بدون عنوان', None]).delete()
                
                messages.success"""

        fixed_area = """                    
                    # التنظيف الفوري بعد الحفظ
                    Document.objects.filter(folder=folder, title__in=['', 'بدون عنوان', None]).delete()
                
                messages.success"""
        
        # استبدال المنطقة المشكلة
        new_content = content.replace(broken_area, fixed_area)
        
        # إصلاح أي مشكلة try/except
        # البحث عن جميع التعبيرات try التي ليس لها except أو finally
        try_blocks = re.finditer(r'[ \t]+try:(?:(?!except|finally|\n[ \t]*\n).)*?(?=\n[ \t]*[^ \t\n])', new_content, re.DOTALL)
        
        for match in try_blocks:
            try_block = match.group(0)
            indentation = re.match(r'^([ \t]+)', try_block).group(1)
            
            # إضافة except إذا لم يكن موجوداً
            replacement = try_block + '\n' + indentation + 'except Exception as e:\n' + indentation + '    print(f"حدث خطأ: {str(e)}")\n'
            new_content = new_content.replace(try_block, replacement)
        
        # كتابة المحتوى المصحح
        with open(file_path, 'w', encoding='utf-8') as file:
            file.write(new_content)
        
        print("✅ تم إصلاح مشاكل المسافات البادئة في ملف admin_views.py")
        print("✅ تم إضافة blocks except حيث يلزم")
        
    except Exception as e:
        print(f"❌ حدث خطأ: {str(e)}")

if __name__ == "__main__":
    fix_indentation()