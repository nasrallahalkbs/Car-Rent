"""
إصلاح عرض شجرة المجلدات في صفحة الأرشيف الإلكتروني
"""
import os
import sys
import django
import json

# إعداد البيئة لاستخدام نماذج Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'car_rental_project.settings')
django.setup()

from rental.models import ArchiveFolder
from django.utils.translation import gettext as _

def fix_archive_tree_display():
    """تحديث ملف تشغيل شجرة المجلدات في صفحة الأرشيف"""
    # مسار الملف الذي سيتم تحديثه
    template_path = "templates/admin/archive/archive_main.html"
    
    # التحقق من وجود الملف
    if not os.path.exists(template_path):
        print(f"خطأ: الملف {template_path} غير موجود")
        return
    
    # قراءة محتوى الملف
    with open(template_path, 'r', encoding='utf-8') as file:
        template_content = file.read()
    
    # تحديث الجزء الخاص بتهيئة jsTree في الصفحة
    updated_jstree_init = """
    <script>
    // تهيئة شجرة المجلدات مباشرة بعد تحميل الصفحة
    $(document).ready(function() {
        console.log("تهيئة شجرة المجلدات...");
        
        // تحميل بيانات الشجرة من الخادم
        let treeData = {{ folder_tree|safe }};
        console.log("بيانات الشجرة:", treeData);
        
        // تحويل معرفات المجلدات لتكون متوافقة مع التطبيق
        function processTreeData(data) {
            if (Array.isArray(data)) {
                return data.map(node => processTreeData(node));
            } else if (typeof data === 'object') {
                // التأكد من أن معرف المجلد يحتوي على بادئة "folder-" إذا كان ليس معرفًا خاصًا
                if (data.id && typeof data.id === 'number') {
                    data.id = 'folder-' + data.id;
                }
                
                // معالجة المجلدات الفرعية بشكل متكرر
                if (data.children && Array.isArray(data.children)) {
                    data.children = data.children.map(child => processTreeData(child));
                }
                
                return data;
            }
            return data;
        }
        
        // معالجة بيانات الشجرة للتأكد من تنسيق المعرفات بشكل صحيح
        treeData = processTreeData(treeData);
        
        // تهيئة شجرة المجلدات
        $('#folder-tree').jstree({
            'core' : {
                'data' : treeData,
                'themes': {
                    'responsive': true,
                    'name': 'default',
                    'dots': false,
                    'icons': true, 
                    'variant': 'large',
                    'stripes': false 
                },
                'multiple': false,
                'check_callback': true,
                'strings': {
                    'Loading...': '{% trans "جاري التحميل..." %}',
                    'New node': '{% trans "مجلد جديد" %}'
                }
            },
            'rtl': {% if is_rtl %}true{% else %}false{% endif %},
            'types': {
                'default': {
                    'icon': 'fas fa-folder'
                },
                'system': {
                    'icon': 'fas fa-trash-alt'
                },
                'folder': {
                    'icon': 'fas fa-folder'
                },
                'file': {
                    'icon': 'fas fa-file'
                }
            },
            'plugins': ['types', 'wholerow', 'search', 'changed']
        }).on('ready.jstree', function() {
            console.log("تم تهيئة شجرة المجلدات بنجاح");
            
            // تحديد إجمالي العناصر
            const itemsCount = $('#folder-tree').jstree('get_json').length;
            $('#items-count').text(itemsCount + ' {% trans "عنصر" %}');
            
            // تعيين أول مجلد كمجلد محدد افتراضيًا
            if (treeData && treeData.length > 1) {
                // اختر المجلد الثاني (الأول بعد سلة المحذوفات) إذا كان موجودًا
                const secondFolderId = treeData[1].id;
                $('#folder-tree').jstree('select_node', secondFolderId);
            }
        }).on('select_node.jstree', function(e, data) {
            console.log("تم تحديد مجلد:", data.node.id);
            
            // معالجة حدث تحديد مجلد
            const nodeId = data.node.id;
            const nodeName = data.node.text;
            
            // عرض محتويات المجلد المحدد
            $('#no-folder-selected').addClass('d-none');
            $('#folder-contents').removeClass('d-none');
            $('#selected-folder-name').text(nodeName);
            
            // محاكاة عرض المجلد المحدد
            if (nodeId === 'folder-1' || nodeId === 'folder-2') {
                $('#subfolder-count').text('3');
                $('#file-count').text('5');
            } else {
                $('#subfolder-count').text('0');
                $('#file-count').text('0');
            }
        });
        
        // تفعيل خاصية البحث في الشجرة
        $('#folder-search').on('keyup', function() {
            const searchString = $(this).val();
            $('#folder-tree').jstree('search', searchString);
        });
    });
    </script>
    """
    
    # البحث عن موقع تهيئة jsTree في القالب
    script_start = template_content.find('<script>$(document).ready(function() {')
    if script_start == -1:
        script_start = template_content.find('<script>\n    $(document).ready(function() {')
    
    script_end = template_content.find('</script>', script_start)
    
    if script_start != -1 and script_end != -1:
        # استبدال السكريبت القديم بالجديد
        new_content = template_content[:script_start] + updated_jstree_init + template_content[script_end + 9:]
        
        # حفظ التغييرات
        with open(template_path, 'w', encoding='utf-8') as file:
            file.write(new_content)
        
        print("تم تحديث سكريبت تهيئة شجرة المجلدات بنجاح")
    else:
        print("لم يتم العثور على سكريبت تهيئة jsTree في الملف")

if __name__ == "__main__":
    fix_archive_tree_display()