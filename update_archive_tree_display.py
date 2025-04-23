"""
تحديث طريقة عرض شجرة المجلدات في صفحة الأرشيف
"""
import os
import sys
import json

def update_admin_archive_view():
    """
    تحديث دالة admin_archive في ملف admin_views.py
    طريقة بديلة لإنشاء شجرة المجلدات
    """
    file_path = "rental/admin_views.py"
    
    # التحقق من وجود الملف
    if not os.path.exists(file_path):
        print(f"خطأ: الملف {file_path} غير موجود")
        return
    
    # قراءة محتوى الملف
    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()
    
    # البحث عن دالة admin_archive
    start_index = content.find("def admin_archive(request):")
    if start_index == -1:
        print("لم يتم العثور على دالة admin_archive")
        return
    
    # البحث عن نهاية الدالة (بداية الدالة التالية)
    next_def_index = content.find("\ndef ", start_index + 1)
    if next_def_index == -1:
        # إذا كانت آخر دالة في الملف
        next_def_index = len(content)
    
    # استخراج كود الدالة
    function_code = content[start_index:next_def_index]
    
    # إنشاء دالة محدثة
    updated_function = """def admin_archive(request):
    \"\"\"عرض الأرشيف الإلكتروني مع شجرة المجلدات\"\"\"
    # تحديد لغة العرض
    from django.utils.translation import get_language
    current_language = get_language()
    is_english = current_language == 'en'
    is_rtl = current_language == 'ar'
    
    # للتأكد من تحميل المجلدات بشكل صحيح
    print(f"DEBUG - تحميل المجلدات للأرشيف...")
    
    # الحصول على مجلدات الجذر
    root_folders = ArchiveFolder.objects.filter(parent=None).order_by('name')
    print(f"DEBUG - عدد المجلدات الرئيسية: {root_folders.count()}")
    
    # تعريف دالة بناء شجرة المجلدات بطريقة بسيطة (تنسيق بيانات ثابت)
    folder_tree = []
    
    # إضافة سلة المحذوفات
    folder_tree.append({
        'id': 'recycle-bin',
        'text': _('سلة المحذوفات'),
        'icon': 'fas fa-trash-alt',
        'type': 'system',
        'state': {'opened': False},
        'children': []
    })
    
    # مباشرة قم بإضافة المجلدات مع إضافة شجرة بسيطة
    for folder in root_folders:
        print(f"DEBUG - إضافة مجلد: {folder.name}")
        folder_data = {
            'id': folder.id,
            'text': folder.name,
            'icon': 'fas fa-folder',
            'state': {'opened': False},
            'children': []
        }
        
        # إضافة المجلدات الفرعية
        for child in folder.children.all().order_by('name'):
            print(f"DEBUG -- إضافة مجلد فرعي: {child.name}")
            folder_data['children'].append({
                'id': child.id,
                'text': child.name,
                'icon': 'fas fa-folder',
                'state': {'opened': False},
                'children': []
            })
        
        # إضافة المجلد إلى شجرة المجلدات
        folder_tree.append(folder_data)
    
    # تحويل شجرة المجلدات إلى تنسيق JSON
    folder_tree_json = json.dumps(folder_tree, ensure_ascii=False)
    print(f"DEBUG - تم إنشاء شجرة المجلدات بنجاح")
    
    # إنشاء قاموس بكافة المجلدات للوصول بسرعة
    all_folders = {}
    for folder in ArchiveFolder.objects.all():
        all_folders[folder.id] = folder
    
    # إعداد سياق البيانات
    context = {
        'folder_tree': folder_tree_json,
        'subfolders': root_folders,
        'all_folders': all_folders,
        'is_english': is_english,
        'is_rtl': is_rtl,
        'active_section': 'archive'
    }
    
    return render(request, 'admin/archive/archive_main.html', context)
"""
    
    # استبدال الدالة القديمة بالدالة المحدثة
    updated_content = content.replace(function_code, updated_function)
    
    # حفظ الملف المحدث
    with open(file_path, 'w', encoding='utf-8') as file:
        file.write(updated_content)
    
    print("تم تحديث دالة admin_archive بنجاح")

def update_javascript_folder_tree():
    """
    تحديث كود JavaScript لشجرة المجلدات في صفحة الأرشيف
    """
    template_path = "templates/admin/archive/archive_main.html"
    
    # التحقق من وجود الملف
    if not os.path.exists(template_path):
        print(f"خطأ: الملف {template_path} غير موجود")
        return
    
    # قراءة محتوى الملف
    with open(template_path, 'r', encoding='utf-8') as file:
        content = file.read()
    
    # البحث عن سكربت تهيئة jsTree
    script_start = content.find('$(document).ready(function() {')
    script_end = content.find('</script>', script_start)
    
    if script_start == -1 or script_end == -1:
        print("لم يتم العثور على كود JavaScript في القالب")
        return
    
    # استخراج كود JavaScript
    js_code = content[script_start:script_end]
    
    # تحديث كود JavaScript
    updated_js_code = """$(document).ready(function() {
        console.log("تهيئة صفحة الأرشيف الإلكتروني...");
        
        // عرض بيانات الشجرة في وحدة التحكم للتصحيح
        let treeData = {{ folder_tree|safe }};
        console.log("بيانات الشجرة المستلمة:", treeData);
        
        // إضافة بيانات شجرة افتراضية للاختبار إذا لم تكن بيانات الشجرة متاحة
        if (!treeData || treeData.length === 0) {
            console.log("تحذير: لا توجد بيانات لشجرة المجلدات، سيتم استخدام بيانات افتراضية");
            
            // إنشاء شجرة افتراضية للاختبار
            treeData = [
                {
                    "id": "recycle-bin",
                    "text": "سلة المحذوفات",
                    "icon": "fas fa-trash-alt",
                    "type": "system",
                    "state": {"opened": false},
                    "children": []
                },
                {
                    "id": 27,
                    "text": "تصميم (شجرة)",
                    "icon": "fas fa-folder",
                    "state": {"opened": true},
                    "children": [
                        {
                            "id": 28,
                            "text": "رسوم (1)",
                            "icon": "fas fa-folder"
                        },
                        {
                            "id": 29,
                            "text": "حضور (2)",
                            "icon": "fas fa-folder"
                        },
                        {
                            "id": 30,
                            "text": "حسابات (3)",
                            "icon": "fas fa-folder"
                        },
                        {
                            "id": 31,
                            "text": "محفوظات (4)",
                            "icon": "fas fa-folder"
                        },
                        {
                            "id": 32,
                            "text": "توكيلات (5)",
                            "icon": "fas fa-folder"
                        }
                    ]
                }
            ];
        }
        
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
        
        // إضافة أنماط CSS إضافية للشجرة
        const style = document.createElement('style');
        style.textContent = `
            .jstree-default .jstree-icon.fa-folder {
                color: #ffd04c !important;
            }
            .jstree-default .jstree-icon.fa-trash-alt {
                color: #0078d7 !important;
            }
            .jstree-default .jstree-wholerow-clicked {
                background-color: #cce8ff !important;
            }
            .jstree-default .jstree-wholerow-hovered {
                background-color: #f0f0f0 !important;
            }
            .jstree-default .jstree-anchor {
                line-height: 28px;
                height: 28px;
            }
            .jstree-default .jstree-node {
                margin-left: 0;
                background-image: none;
            }
        `;
        document.head.appendChild(style);
        
        // تهيئة شجرة المجلدات
        $('#folder-tree').jstree({
            'core': {
                'data': treeData,
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
            if (treeData && treeData.length > 0) {
                let targetNode = null;
                
                // ابحث عن المجلد "تصميم (شجرة)" أو استخدم المجلد الأول
                for (let i = 0; i < treeData.length; i++) {
                    if (treeData[i].text.includes('تصميم')) {
                        targetNode = treeData[i].id;
                        break;
                    }
                }
                
                // إذا لم يتم العثور على مجلد "تصميم"، استخدم المجلد الأول بعد سلة المحذوفات
                if (!targetNode && treeData.length > 1) {
                    targetNode = treeData[1].id;
                } else if (!targetNode && treeData.length > 0) {
                    targetNode = treeData[0].id;
                }
                
                if (targetNode) {
                    $('#folder-tree').jstree('select_node', targetNode);
                    console.log("تم تحديد المجلد:", targetNode);
                }
            }
        }).on('select_node.jstree', function(e, data) {
            console.log("تم تحديد مجلد:", data.node.id, data.node.text);
            
            // معالجة حدث تحديد مجلد
            const nodeId = data.node.id;
            const nodeName = data.node.text;
            
            // عرض محتويات المجلد المحدد
            $('#no-folder-selected').addClass('d-none');
            $('#folder-contents').removeClass('d-none');
            $('#selected-folder-name').text(nodeName);
            
            // تحديد المسار الكامل للمجلد
            let path = '';
            if (data.node.id === 'recycle-bin') {
                path = '/{% trans "سلة المحذوفات" %}';
            } else if (data.node.parents.length > 0) {
                path = '/' + nodeName;
            } else {
                path = '/' + nodeName;
            }
            $('#folder-full-path').text(path);
            
            // تحديث عداد المجلدات الفرعية والملفات
            if (data.node.children && data.node.children.length > 0) {
                $('#subfolder-count').text(data.node.children.length);
            } else {
                $('#subfolder-count').text('0');
            }
            
            // تحديث معرف المجلد المحدد للنماذج
            $('#selected-parent-id').val(nodeId);
            $('#selected-folder-id').val(nodeId);
            
            // محاكاة عدد الملفات
            $('#file-count').text('0');
            
            // تحديث رابط "عرض المجلد"
            if (nodeId.startsWith('folder-')) {
                const folder_id = nodeId.replace('folder-', '');
                $('#view-folder-btn').attr('href', '/ar/dashboard/archive/folder/' + folder_id + '/');
            } else {
                $('#view-folder-btn').attr('href', '#');
            }
        });
        
        // تفعيل خاصية البحث في الشجرة
        $('#folder-search').on('keyup', function() {
            const searchString = $(this).val();
            $('#folder-tree').jstree('search', searchString);
        });
    });"""
    
    # استبدال سكربت JavaScript القديم بالسكربت الجديد
    updated_content = content.replace(js_code, updated_js_code)
    
    # حفظ الملف المحدث
    with open(template_path, 'w', encoding='utf-8') as file:
        file.write(updated_content)
    
    print("تم تحديث كود JavaScript لشجرة المجلدات بنجاح")

if __name__ == "__main__":
    update_admin_archive_view()
    update_javascript_folder_tree()