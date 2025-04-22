"""
تحديث طريقة عرض شجرة المجلدات في قالب الأرشيف الرئيسي
"""

import os
import re
import django

# إعداد بيئة Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'car_rental_project.settings')
django.setup()

def update_archive_main_template():
    """
    تحديث ملف archive_main.html لعرض شجرة المجلدات بمظهر ويندوز
    """
    template_path = 'templates/admin/archive/archive_main.html'
    
    try:
        # قراءة محتوى القالب
        with open(template_path, 'r', encoding='utf-8') as file:
            content = file.read()
        
        # البحث عن سكريبت تهيئة JSTree
        jstree_init_pattern = r'(\$\(\'#folder-tree\'\)\.jstree\(\{[\s\S]*?\}\)\s*\.\s*on\(\'select_node\.jstree\')'
        
        # إضافة حدث تحميل الشجرة
        jstree_ready_event = """
        // عند اكتمال تحميل الشجرة
        $('#folder-tree').on('ready.jstree', function() {
            // فتح جميع العقد الجذرية
            $(this).jstree('open_all');
            console.log("تم تحميل شجرة المجلدات بنجاح");
        });
        """
        
        # تحديث محتوى الملف بإضافة حدث ready.jstree
        if re.search(jstree_init_pattern, content):
            updated_content = re.sub(
                jstree_init_pattern,
                lambda m: m.group(1) + jstree_ready_event,
                content
            )
            
            # كتابة المحتوى المحدث
            with open(template_path, 'w', encoding='utf-8') as file:
                file.write(updated_content)
                
            print(f"✓ تم تحديث ملف {template_path} بنجاح")
            return True
        else:
            print(f"× لم يتم العثور على سكريبت تهيئة JSTree في الملف {template_path}")
            return False
            
    except Exception as e:
        print(f"× حدث خطأ أثناء تحديث القالب: {str(e)}")
        return False
        
def update_admin_views():
    """
    تحديث ملف admin_views.py للتأكد من استخدام البيانات المخصصة للشجرة
    """
    views_path = 'rental/admin_views.py'
    
    try:
        # قراءة محتوى ملف الدوال
        with open(views_path, 'r', encoding='utf-8') as file:
            content = file.read()
            
        # البحث عن دالة عرض الأرشيف الرئيسية
        archive_view_pattern = r'def admin_archive\(request\):([\s\S]*?)return render\('
        
        # التأكد من وجود تحميل لبيانات المجلدات
        if 'folder_tree' not in content or 'ArchiveFolder' not in content:
            print(f"× لم يتم العثور على الكود المطلوب في ملف {views_path}")
            return False
            
        print(f"✓ تم التحقق من ملف {views_path}")
        return True
        
    except Exception as e:
        print(f"× حدث خطأ أثناء تحديث ملف الدوال: {str(e)}")
        return False

if __name__ == '__main__':
    print("بدء تحديث طريقة عرض شجرة المجلدات...")
    update_archive_main_template()
    update_admin_views()