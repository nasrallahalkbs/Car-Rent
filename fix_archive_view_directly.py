"""
إصلاح مباشر لمشكلة عرض الأرشيف
"""

import os

def fix_admin_views():
    """إصلاح ملف admin_views.py مباشرة لإظهار المجلدات بشكل صحيح"""
    file_path = "rental/admin_views.py"
    
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
        next_def_index = len(content)
    
    # استخراج كود الدالة
    function_code = content[start_index:next_def_index]
    
    # إنشاء دالة محدثة تستخدم القالب الأصلي
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
    
    # تعريف دالة بناء شجرة المجلدات
    def build_tree(folder):
        children = []
        for child in folder.children.all().order_by('name'):
            children.append(build_tree(child))
        
        return {
            'id': folder.id,
            'text': folder.name,
            'icon': 'fas fa-folder',
            'type': 'folder',
            'state': {'opened': False},
            'children': children
        }
    
    # بناء شجرة المجلدات
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
    
    # إضافة المجلدات الرئيسية مع المجلدات الفرعية
    for folder in root_folders:
        try:
            folder_tree.append(build_tree(folder))
            print(f"DEBUG - تمت إضافة المجلد: {folder.name} (ID: {folder.id})")
        except Exception as e:
            print(f"DEBUG - خطأ في إضافة المجلد {folder.name}: {str(e)}")
    
    # تحويل شجرة المجلدات إلى تنسيق JSON
    import json
    folder_tree_json = json.dumps(folder_tree, ensure_ascii=False)
    print(f"DEBUG - تم إنشاء شجرة المجلدات بنجاح")
    
    # إعداد سياق البيانات
    context = {
        'folder_tree': folder_tree_json,
        'subfolders': root_folders,
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

def fix_archive_main_template():
    """إصلاح قالب الأرشيف الرئيسي لإظهار المجلدات بشكل صحيح"""
    template_path = "templates/admin/archive/archive_main.html"
    
    with open(template_path, 'r', encoding='utf-8') as file:
        content = file.read()
    
    # تحديث قالب الأرشيف
    new_template = """{% extends "admin/admin_layout.html" %}
{% load i18n %}

{% block styles %}
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/jstree@3.3.12/dist/themes/default/style.min.css">
<style>
    .archive-container {
        padding: 20px;
    }
    .folder-tree-container {
        border: 1px solid #ddd;
        border-radius: 4px;
        height: 500px;
        overflow: hidden;
        display: flex;
        flex-direction: column;
        background-color: #fff;
    }
    .folder-tree-header, .folder-status-bar {
        color: #666;
        font-size: 14px;
        padding: 5px 10px;
        background-color: #f8f9fa;
        border-bottom: 1px solid #ddd;
    }
    .folder-status-bar {
        border-top: 1px solid #ddd;
        border-bottom: none;
    }
    #folder-tree {
        font-size: 14px;
        overflow-y: auto;
        flex-grow: 1;
        padding: 10px;
    }
    .jstree-default .jstree-icon.fa-folder {
        color: #ffc107 !important;
    }
    .jstree-default .jstree-icon.fa-trash-alt {
        color: #0078d7 !important;
    }
    .jstree-default .jstree-wholerow-clicked {
        background-color: #e5f0ff !important;
    }
    .jstree-default .jstree-wholerow-hovered {
        background-color: #f0f0f0 !important;
    }
    .jstree-default .jstree-clicked {
        color: #0d6efd !important;
    }
    .folder-toolbar {
        background-color: #f8f9fa;
        padding: 10px;
        border-radius: 4px;
        margin-bottom: 15px;
    }
    .folder-info {
        background-color: #f8f9fa;
        border-radius: 4px;
        padding: 15px;
        margin-bottom: 15px;
    }
    .hide-content {
        display: none !important;
    }
    .jstree-rtl.jstree-default .jstree-node {
        margin-right: 0;
    }
    .jstree-rtl.jstree-default .jstree-icon {
        margin-left: 5px;
        margin-right: 0;
    }
</style>
{% endblock %}

{% block content %}
<div class="archive-container">
    <div class="d-flex justify-content-between align-items-center mb-4">
        <h3 class="mb-0">{% trans "الأرشيف الإلكتروني" %}</h3>
        <div>
            <a href="/ar/dashboard/" class="btn btn-outline-secondary">
                <i class="fas fa-arrow-{% if is_rtl %}right{% else %}left{% endif %} {% if is_rtl %}ms-2{% else %}me-2{% endif %}"></i> {% trans "العودة للوحة التحكم" %}
            </a>
        </div>
    </div>
    
    <div class="row">
        <!-- قسم شجرة المجلدات -->
        <div class="col-md-4 mb-4">
            <div class="folder-toolbar d-flex justify-content-between align-items-center">
                <a href="/ar/dashboard/archive/" class="btn btn-sm btn-light">
                    <i class="fas fa-sync-alt"></i> {% trans "تحديث" %}
                </a>
                <button type="button" class="btn btn-sm btn-primary" data-bs-toggle="modal" data-bs-target="#newFolderModal">
                    <i class="fas fa-folder-plus"></i> {% trans "إضافة مجلد" %}
                </button>
            </div>
            
            <div class="input-group input-group-sm mb-3">
                <input type="text" id="folder-search" class="form-control" placeholder="{% trans 'بحث في المجلدات...' %}">
                <span class="input-group-text"><i class="fas fa-search"></i></span>
            </div>
            
            <div class="folder-tree-container">
                <div class="folder-tree-header d-flex justify-content-between align-items-center">
                    <span>{% trans "المجلدات" %}</span>
                    <i class="fas fa-folder text-warning"></i>
                </div>
                
                <div id="folder-tree" dir="{% if is_rtl %}rtl{% else %}ltr{% endif %}"></div>
                
                <div class="folder-status-bar d-flex justify-content-between align-items-center">
                    <span id="items-count">0 {% trans "عنصر" %}</span>
                    <span id="selected-status"></span>
                </div>
            </div>
        </div>
        
        <!-- قسم عرض محتويات المجلد -->
        <div class="col-md-8">
            <!-- حالة عدم تحديد مجلد -->
            <div id="no-folder-selected" class="text-center p-5">
                <div class="p-5 rounded bg-light">
                    <i class="fas fa-folder-open text-warning" style="font-size: 72px;"></i>
                    <h4 class="mt-3">{% trans "اختر مجلداً من القائمة" %}</h4>
                    <p class="text-muted">{% trans "اختر مجلداً من شجرة المجلدات لعرض محتوياته" %}</p>
                </div>
            </div>
            
            <!-- حالة تحديد مجلد (مخفية افتراضياً) -->
            <div id="folder-contents" class="d-none">
                <div class="d-flex justify-content-between align-items-center mb-3">
                    <h4 class="mb-0">
                        <i class="fas fa-folder-open text-warning {% if is_rtl %}ms-2{% else %}me-2{% endif %}"></i>
                        <span id="selected-folder-name"></span>
                    </h4>
                    
                    <div>
                        <a href="#" id="view-folder-btn" class="btn btn-sm btn-outline-primary">
                            <i class="fas fa-eye {% if is_rtl %}ms-1{% else %}me-1{% endif %}"></i> {% trans "عرض" %}
                        </a>
                        <button type="button" class="btn btn-sm btn-success {% if is_rtl %}me-2{% else %}ms-2{% endif %}" data-bs-toggle="modal" data-bs-target="#uploadFileModal">
                            <i class="fas fa-file-upload {% if is_rtl %}ms-1{% else %}me-1{% endif %}"></i> {% trans "رفع ملف" %}
                        </button>
                    </div>
                </div>
                
                <div class="folder-info">
                    <div class="row">
                        <div class="col">
                            <small class="text-muted d-block mb-2">
                                <i class="fas fa-sitemap {% if is_rtl %}ms-1{% else %}me-1{% endif %}"></i> {% trans "المسار:" %} 
                                <span id="folder-full-path"></span>
                            </small>
                        </div>
                    </div>
                    <div class="row">
                        <div class="col-6">
                            <div class="d-flex align-items-center">
                                <i class="fas fa-folder text-warning {% if is_rtl %}ms-2{% else %}me-2{% endif %}"></i>
                                <div>
                                    <small class="text-muted d-block">{% trans "المجلدات الفرعية" %}</small>
                                    <span id="subfolder-count" class="h5 mb-0">0</span>
                                </div>
                            </div>
                        </div>
                        <div class="col-6">
                            <div class="d-flex align-items-center">
                                <i class="fas fa-file text-primary {% if is_rtl %}ms-2{% else %}me-2{% endif %}"></i>
                                <div>
                                    <small class="text-muted d-block">{% trans "الملفات" %}</small>
                                    <span id="file-count" class="h5 mb-0">0</span>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
                
                <div class="card">
                    <div class="card-header d-flex justify-content-between">
                        <h5 class="mb-0">{% trans "محتويات المجلد" %}</h5>
                        <div>
                            <select class="form-select form-select-sm" id="view-type">
                                <option value="grid">{% trans "عرض شبكي" %}</option>
                                <option value="list">{% trans "عرض قائمة" %}</option>
                            </select>
                        </div>
                    </div>
                    <div class="card-body">
                        <div id="folder-files" class="row g-3">
                            <!-- يتم إضافة الملفات هنا ديناميكياً -->
                            <div class="col-12 text-center text-muted py-5">
                                <i class="fas fa-folder-open" style="font-size: 48px;"></i>
                                <p class="mt-3">{% trans "لا توجد ملفات في هذا المجلد" %}</p>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>
</div>

<!-- Modal - إضافة مجلد جديد -->
<div class="modal fade" id="newFolderModal" tabindex="-1" aria-labelledby="newFolderModalLabel" aria-hidden="true">
    <div class="modal-dialog">
        <div class="modal-content">
            <div class="modal-header">
                <h5 class="modal-title" id="newFolderModalLabel">{% trans "إضافة مجلد جديد" %}</h5>
                <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
            </div>
            <div class="modal-body">
                <form action="/ar/dashboard/archive/folder/add/" method="post">
                    {% csrf_token %}
                    <div class="mb-3">
                        <label for="folder-name" class="form-label">{% trans "اسم المجلد" %}</label>
                        <input type="text" class="form-control" id="folder-name" name="name" required>
                    </div>
                    <div class="mb-3">
                        <label for="parent-folder" class="form-label">{% trans "المجلد الرئيسي" %}</label>
                        <select class="form-select" id="parent-folder" name="parent_id">
                            <option value="">{% trans "بدون مجلد رئيسي (مجلد جذر)" %}</option>
                            {% for folder in subfolders %}
                                <option value="{{ folder.id }}">{{ folder.name }}</option>
                            {% endfor %}
                        </select>
                    </div>
                    <div class="mb-3">
                        <label for="folder-description" class="form-label">{% trans "وصف المجلد" %}</label>
                        <textarea class="form-control" id="folder-description" name="description" rows="3"></textarea>
                    </div>
                    <input type="hidden" id="selected-parent-id" name="selected_parent_id" value="">
                    <div class="text-end">
                        <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">{% trans "إلغاء" %}</button>
                        <button type="submit" class="btn btn-primary">{% trans "إضافة المجلد" %}</button>
                    </div>
                </form>
            </div>
        </div>
    </div>
</div>

<!-- Modal - رفع مستند جديد -->
<div class="modal fade" id="uploadFileModal" tabindex="-1" aria-labelledby="uploadFileModalLabel" aria-hidden="true">
    <div class="modal-dialog">
        <div class="modal-content">
            <div class="modal-header">
                <h5 class="modal-title" id="uploadFileModalLabel">{% trans "رفع مستند جديد" %}</h5>
                <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
            </div>
            <div class="modal-body">
                <form action="/ar/dashboard/archive/add/" method="post" enctype="multipart/form-data">
                    {% csrf_token %}
                    <div class="mb-3">
                        <label for="file-title" class="form-label">{% trans "عنوان المستند" %}</label>
                        <input type="text" class="form-control" id="file-title" name="title" required>
                    </div>
                    <div class="mb-3">
                        <label for="document-type" class="form-label">{% trans "نوع المستند" %}</label>
                        <select class="form-select" id="document-type" name="document_type">
                            <option value="contract">{% trans "عقد" %}</option>
                            <option value="receipt">{% trans "إيصال" %}</option>
                            <option value="custody">{% trans "عهدة" %}</option>
                            <option value="custody_release">{% trans "إخلاء عهدة" %}</option>
                            <option value="official_document">{% trans "وثيقة رسمية" %}</option>
                            <option value="other">{% trans "أخرى" %}</option>
                        </select>
                    </div>
                    <div class="mb-3">
                        <label for="file-upload" class="form-label">{% trans "الملف" %}</label>
                        <input type="file" class="form-control" id="file-upload" name="file" required>
                    </div>
                    <div class="mb-3">
                        <label for="file-folder" class="form-label">{% trans "المجلد" %}</label>
                        <select class="form-select" id="file-folder" name="folder">
                            <option value="">{% trans "بدون مجلد (الجذر)" %}</option>
                            {% for folder in subfolders %}
                                <option value="{{ folder.id }}">{{ folder.name }}</option>
                            {% endfor %}
                        </select>
                    </div>
                    <div class="mb-3">
                        <label for="file-description" class="form-label">{% trans "وصف المستند" %}</label>
                        <textarea class="form-control" id="file-description" name="description" rows="3"></textarea>
                    </div>
                    <input type="hidden" id="selected-folder-id" name="selected_folder_id" value="">
                    <div class="text-end">
                        <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">{% trans "إلغاء" %}</button>
                        <button type="submit" class="btn btn-primary">{% trans "رفع المستند" %}</button>
                    </div>
                </form>
            </div>
        </div>
    </div>
</div>
{% endblock %}

{% block extra_js %}
<script src="https://cdn.jsdelivr.net/npm/jstree@3.3.12/dist/jstree.min.js"></script>
<script>
    $(document).ready(function() {
        console.log("تهيئة صفحة الأرشيف الإلكتروني...");
        
        // عرض بيانات الشجرة المستلمة من الخادم
        let folderData = {{ folder_tree|safe }};
        console.log("بيانات المجلدات:", folderData);
        
        // إذا كانت البيانات فارغة أو غير محددة، عرض رسالة وإيقاف التنفيذ
        if (!folderData || folderData.length === 0) {
            $('#folder-tree').html('<div class="alert alert-info m-3">لا توجد مجلدات متاحة. يرجى إنشاء مجلد جديد.</div>');
            return;
        }
        
        // تحويل معرفات المجلدات لتوافق jsTree
        function processTreeData(data) {
            if (Array.isArray(data)) {
                return data.map(item => processTreeData(item));
            } else if (typeof data === 'object' && data !== null) {
                if (data.id && typeof data.id === 'number') {
                    data.id = 'folder-' + data.id;
                }
                if (data.children && Array.isArray(data.children)) {
                    data.children = data.children.map(child => processTreeData(child));
                }
                return data;
            }
            return data;
        }
        
        // معالجة بيانات الشجرة
        let treeData = processTreeData(folderData);
        
        // تهيئة jsTree
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
                'check_callback': true
            },
            'rtl': {% if is_rtl %}true{% else %}false{% endif %},
            'types': {
                'default': { 'icon': 'fas fa-folder' },
                'system': { 'icon': 'fas fa-trash-alt' },
                'folder': { 'icon': 'fas fa-folder' },
                'file': { 'icon': 'fas fa-file' }
            },
            'plugins': ['types', 'wholerow', 'search', 'changed']
        }).on('ready.jstree', function() {
            console.log("تم تهيئة شجرة المجلدات بنجاح");
            
            // تحديد عدد العناصر
            const itemsCount = $('#folder-tree').jstree('get_json').length;
            $('#items-count').text(itemsCount + ' {% trans "عنصر" %}');
            
            // تحديد المجلد الافتراضي (المجلد الأول بعد سلة المحذوفات)
            if (treeData && treeData.length > 1) {
                // البحث عن مجلد تصميم (شجرة) أو استخدام أول مجلد عادي
                let defaultNode = null;
                for (let i = 0; i < treeData.length; i++) {
                    if (treeData[i].id !== 'recycle-bin') {
                        if (treeData[i].text.includes('تصميم')) {
                            defaultNode = treeData[i].id;
                            break;
                        } else if (!defaultNode) {
                            defaultNode = treeData[i].id;
                        }
                    }
                }
                
                if (defaultNode) {
                    $('#folder-tree').jstree('select_node', defaultNode);
                    // فتح المجلد تلقائياً
                    $('#folder-tree').jstree('open_node', defaultNode);
                }
            }
        }).on('select_node.jstree', function(e, data) {
            // عرض محتويات المجلد المحدد
            const nodeId = data.node.id;
            const nodeName = data.node.text;
            console.log("تم اختيار المجلد:", nodeId, nodeName);
            
            // إظهار محتوى المجلد
            $('#no-folder-selected').addClass('d-none');
            $('#folder-contents').removeClass('d-none');
            $('#selected-folder-name').text(nodeName);
            $('#selected-status').text(nodeName);
            
            // بناء مسار المجلد
            let pathParts = [];
            let currentNode = data.node;
            
            if (nodeId === 'recycle-bin') {
                pathParts.push('سلة المحذوفات');
            } else {
                // إضافة اسم المجلد الحالي
                pathParts.push(nodeName);
                
                // إضافة أسماء المجلدات الأب بالترتيب العكسي
                let parentIds = data.node.parents;
                parentIds.forEach(function(pid) {
                    if (pid !== '#' && pid !== 'recycle-bin') {
                        let parentNode = $('#folder-tree').jstree(true).get_node(pid);
                        if (parentNode) {
                            pathParts.push(parentNode.text);
                        }
                    }
                });
                
                // عكس المصفوفة لعرض المسار بترتيب صحيح (من الأب إلى الابن)
                pathParts.reverse();
            }
            
            // بناء المسار المجمع
            const path = '/' + pathParts.join('/');
            $('#folder-full-path').text(path);
            
            // تحديث عدد المجلدات الفرعية
            if (data.node.children && data.node.children.length > 0) {
                $('#subfolder-count').text(data.node.children.length);
            } else {
                $('#subfolder-count').text('0');
            }
            
            // تحديث معرف المجلد للنماذج
            if (nodeId.startsWith('folder-')) {
                const folderId = nodeId.replace('folder-', '');
                $('#selected-parent-id').val(folderId);
                $('#selected-folder-id').val(folderId);
                $('#view-folder-btn').attr('href', '/ar/dashboard/archive/folder/' + folderId + '/');
            } else {
                $('#view-folder-btn').attr('href', '#');
            }
            
            // عدد الملفات (صفر حالياً)
            $('#file-count').text('0');
        });
        
        // البحث في شجرة المجلدات
        let searchTimeout = null;
        $('#folder-search').on('keyup', function() {
            const searchText = $(this).val();
            
            if (searchTimeout) {
                clearTimeout(searchTimeout);
            }
            
            searchTimeout = setTimeout(function() {
                $('#folder-tree').jstree('search', searchText);
            }, 300);
        });
    });
</script>
{% endblock %}"""
    
    # كتابة القالب الجديد
    with open(template_path, 'w', encoding='utf-8') as file:
        file.write(new_template)
    
    print("تم تحديث قالب الأرشيف الرئيسي بنجاح")

if __name__ == "__main__":
    fix_admin_views()
    fix_archive_main_template()