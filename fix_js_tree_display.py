"""
إنشاء صفحة أرشيف مستقلة تماماً لضمان ظهور المجلدات بالشكل المناسب
"""

import os

def create_simple_archive_template():
    """إنشاء صفحة أرشيف بسيطة ومستقلة لضمان عمل شجرة المجلدات"""
    template_path = "templates/admin/archive/simple_archive.html"
    
    # المحتوى الجديد للقالب
    content = """{% extends "admin/admin_layout.html" %}
{% load i18n %}

{% block styles %}
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/jstree@3.3.12/dist/themes/default/style.min.css">
<style>
    /* تنسيق حاويات الصفحة */
    .archive-page {
        padding: 20px;
    }
    .archive-header {
        margin-bottom: 20px;
    }
    .archive-content {
        background-color: #fff;
        border-radius: 5px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
    }
    
    /* تنسيق شجرة المجلدات */
    .folder-tree-container {
        border: 1px solid #ddd;
        border-radius: 4px;
        margin-bottom: 20px;
        padding: 10px;
        background-color: #fff;
    }
    .folder-header {
        border-bottom: 1px solid #eee;
        padding-bottom: 10px;
        margin-bottom: 10px;
    }
    #folder-tree {
        max-height: 500px;
        overflow-y: auto;
        padding: 10px;
    }
    
    /* تحسين مظهر الأيقونات والمجلدات */
    .jstree-default .jstree-icon.fa-folder {
        color: #ffc107 !important;
    }
    .jstree-default .jstree-anchor {
        height: 28px !important;
        line-height: 28px !important;
    }
    .jstree-default .jstree-wholerow-clicked {
        background-color: #e3f2fd !important;
    }
    .jstree-default .jstree-wholerow-hovered {
        background-color: #f5f5f5 !important;
    }
    
    /* تنسيق محتوى المجلد */
    .folder-content {
        padding: 20px;
        border: 1px solid #ddd;
        border-radius: 4px;
        min-height: 300px;
    }
    .folder-info {
        background-color: #f8f9fa;
        padding: 15px;
        border-radius: 4px;
        margin-bottom: 15px;
    }
    
    /* تنسيق أدوات الأرشيف */
    .archive-toolbar {
        margin-bottom: 15px;
    }
    
    /* دعم RTL للشجرة */
    .jstree-rtl .jstree-anchor {
        padding: 0 4px 0 0 !important;
    }
</style>
{% endblock %}

{% block content %}
<div class="archive-page">
    <!-- عنوان الصفحة -->
    <div class="archive-header d-flex justify-content-between align-items-center">
        <h3>{% trans "الأرشيف الإلكتروني" %}</h3>
        <a href="/ar/dashboard/" class="btn btn-outline-secondary">
            <i class="fas fa-arrow-{% if is_rtl %}right{% else %}left{% endif %} {% if is_rtl %}ms-2{% else %}me-2{% endif %}"></i>
            {% trans "العودة إلى لوحة التحكم" %}
        </a>
    </div>

    <!-- محتوى الأرشيف -->
    <div class="archive-content">
        <div class="container-fluid">
            <div class="row">
                <!-- شريط الأدوات العلوي -->
                <div class="col-12 archive-toolbar p-3 bg-light border-bottom">
                    <div class="d-flex justify-content-between">
                        <div>
                            <button type="button" class="btn btn-sm btn-primary" data-bs-toggle="modal" data-bs-target="#addFolderModal">
                                <i class="fas fa-folder-plus"></i> {% trans "إضافة مجلد" %}
                            </button>
                            <button type="button" class="btn btn-sm btn-success ms-2" data-bs-toggle="modal" data-bs-target="#uploadFileModal">
                                <i class="fas fa-file-upload"></i> {% trans "رفع ملف" %}
                            </button>
                        </div>
                        <div class="d-flex align-items-center">
                            <div class="input-group input-group-sm w-auto">
                                <input type="text" id="folder-search" class="form-control" placeholder="{% trans 'بحث...' %}">
                                <span class="input-group-text">
                                    <i class="fas fa-search"></i>
                                </span>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
            
            <div class="row p-3">
                <!-- شجرة المجلدات -->
                <div class="col-md-4 mb-4">
                    <div class="folder-tree-container">
                        <div class="folder-header d-flex justify-content-between align-items-center">
                            <span><i class="fas fa-folder me-2 text-warning"></i> {% trans "المجلدات" %}</span>
                            <a href="#" class="text-primary" id="refresh-tree">
                                <i class="fas fa-sync-alt"></i>
                            </a>
                        </div>
                        <div id="folder-tree" dir="{% if is_rtl %}rtl{% else %}ltr{% endif %}"></div>
                    </div>
                </div>
                
                <!-- محتوى المجلد -->
                <div class="col-md-8">
                    <!-- عرض حالة عدم اختيار مجلد -->
                    <div id="no-folder-selected" class="text-center p-5">
                        <div class="p-5">
                            <i class="fas fa-folder-open text-warning mb-3" style="font-size: 64px;"></i>
                            <h4>{% trans "اختر مجلداً لعرض محتوياته" %}</h4>
                            <p class="text-muted">{% trans "يرجى اختيار مجلد من شجرة المجلدات على اليمين" %}</p>
                        </div>
                    </div>
                    
                    <!-- عرض محتوى المجلد (مخفي افتراضياً) -->
                    <div id="folder-contents" class="d-none">
                        <div class="d-flex justify-content-between align-items-center mb-3">
                            <h4 class="mb-0">
                                <i class="fas fa-folder-open text-warning me-2"></i>
                                <span id="selected-folder-name"></span>
                            </h4>
                            <div>
                                <a href="#" id="view-folder-btn" class="btn btn-sm btn-outline-primary">
                                    <i class="fas fa-eye me-1"></i> {% trans "عرض" %}
                                </a>
                            </div>
                        </div>
                        
                        <div class="folder-info">
                            <div class="mb-2">
                                <small class="text-muted">
                                    <i class="fas fa-sitemap me-1"></i> {% trans "المسار:" %}
                                    <span id="folder-path">/</span>
                                </small>
                            </div>
                            <div class="row">
                                <div class="col-6">
                                    <small>
                                        <i class="fas fa-folder me-1 text-warning"></i>
                                        <span id="subfolder-count">0</span> {% trans "مجلد فرعي" %}
                                    </small>
                                </div>
                                <div class="col-6">
                                    <small>
                                        <i class="fas fa-file me-1 text-primary"></i>
                                        <span id="file-count">0</span> {% trans "ملف" %}
                                    </small>
                                </div>
                            </div>
                        </div>
                        
                        <div class="folder-content">
                            <div id="folder-files" class="row g-3">
                                <div class="col-12 text-center py-5">
                                    <p class="text-muted">{% trans "المجلد فارغ" %}</p>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>
</div>

<!-- نموذج إضافة مجلد جديد -->
<div class="modal fade" id="addFolderModal" tabindex="-1" aria-hidden="true">
    <div class="modal-dialog">
        <div class="modal-content">
            <div class="modal-header">
                <h5 class="modal-title">{% trans "إضافة مجلد جديد" %}</h5>
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
                        <label for="parent-folder" class="form-label">{% trans "المجلد الأب" %}</label>
                        <select class="form-select" id="parent-folder" name="parent_id">
                            <option value="">{% trans "بدون مجلد أب (مجلد رئيسي)" %}</option>
                            {% for folder in subfolders %}
                                <option value="{{ folder.id }}">{{ folder.name }}</option>
                            {% endfor %}
                        </select>
                    </div>
                    <input type="hidden" id="selected-parent-id" name="selected_parent_id" value="">
                </form>
            </div>
            <div class="modal-footer">
                <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">{% trans "إلغاء" %}</button>
                <button type="submit" class="btn btn-primary">{% trans "إضافة" %}</button>
            </div>
        </div>
    </div>
</div>

<!-- نموذج رفع ملف -->
<div class="modal fade" id="uploadFileModal" tabindex="-1" aria-hidden="true">
    <div class="modal-dialog">
        <div class="modal-content">
            <div class="modal-header">
                <h5 class="modal-title">{% trans "رفع ملف جديد" %}</h5>
                <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
            </div>
            <div class="modal-body">
                <form action="/ar/dashboard/archive/add/" method="post" enctype="multipart/form-data">
                    {% csrf_token %}
                    <div class="mb-3">
                        <label for="file-title" class="form-label">{% trans "عنوان الملف" %}</label>
                        <input type="text" class="form-control" id="file-title" name="title" required>
                    </div>
                    <div class="mb-3">
                        <label for="file-upload" class="form-label">{% trans "اختر الملف" %}</label>
                        <input type="file" class="form-control" id="file-upload" name="file" required>
                    </div>
                    <div class="mb-3">
                        <label for="file-folder" class="form-label">{% trans "المجلد" %}</label>
                        <select class="form-select" id="file-folder" name="folder">
                            <option value="">{% trans "اختر مجلد" %}</option>
                            {% for folder in subfolders %}
                                <option value="{{ folder.id }}">{{ folder.name }}</option>
                            {% endfor %}
                        </select>
                    </div>
                    <input type="hidden" id="selected-folder-id" name="selected_folder_id" value="">
                </form>
            </div>
            <div class="modal-footer">
                <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">{% trans "إلغاء" %}</button>
                <button type="submit" class="btn btn-primary">{% trans "رفع" %}</button>
            </div>
        </div>
    </div>
</div>
{% endblock %}

{% block extra_js %}
<script src="https://cdn.jsdelivr.net/npm/jstree@3.3.12/dist/jstree.min.js"></script>
<script>
    $(document).ready(function() {
        // سجلات تصحيح لمراقبة سلوك الصفحة
        console.log("تهيئة صفحة الأرشيف الإلكتروني...");
        
        // بيانات شجرة المجلدات من الخادم
        let treeData = {{ folder_tree|safe }};
        console.log("بيانات شجرة المجلدات:", treeData);
        
        // تحويل معرفات المجلدات إلى تنسيق مناسب لـ jsTree
        function processTreeData(data) {
            if (!data || !Array.isArray(data)) {
                console.error("بيانات الشجرة غير صالحة:", data);
                return [];
            }
            
            return data.map(function(node) {
                // إنشاء نسخة من العقدة لعدم تعديل الأصل
                let processedNode = {...node};
                
                // إضافة بادئة للمعرف إذا كان رقماً
                if (typeof processedNode.id === 'number') {
                    processedNode.id = 'folder-' + processedNode.id;
                }
                
                // معالجة الأطفال بشكل متكرر
                if (processedNode.children && Array.isArray(processedNode.children)) {
                    processedNode.children = processedNode.children.map(function(child) {
                        // معالجة كل طفل
                        if (typeof child.id === 'number') {
                            child.id = 'folder-' + child.id;
                        }
                        // إرجاع الطفل المعالج
                        return child;
                    });
                }
                
                // إرجاع العقدة المعالجة
                return processedNode;
            });
        }
        
        // معالجة بيانات المجلدات
        let processedTreeData = processTreeData(treeData);
        console.log("بيانات الشجرة المعالجة:", processedTreeData);
        
        // إضافة خيارات تهيئة الشجرة لتصحيح أي مشاكل محتملة
        let jstreeConfig = {
            'core': {
                'data': processedTreeData,
                'themes': {
                    'name': 'default',
                    'dots': false,
                    'icons': true
                },
                'check_callback': true
            },
            'plugins': ['types', 'wholerow', 'search'],
            'types': {
                'default': { 'icon': 'fas fa-folder' },
                'system': { 'icon': 'fas fa-trash-alt' },
                'folder': { 'icon': 'fas fa-folder' }
            },
            'search': {
                'show_only_matches': true,
                'show_only_matches_children': true
            }
        };
        
        // إذا كانت اللغة العربية، إضافة إعدادات RTL
        {% if is_rtl %}
        jstreeConfig.rtl = true;
        {% endif %}
        
        // تهيئة شجرة المجلدات
        try {
            $('#folder-tree').jstree(jstreeConfig);
            console.log("تم تهيئة شجرة المجلدات");
        } catch (error) {
            console.error("خطأ في تهيئة شجرة المجلدات:", error);
            $('#folder-tree').html('<div class="alert alert-danger">حدث خطأ أثناء تحميل المجلدات. يرجى تحديث الصفحة.</div>');
        }
        
        // معالجة حدث إكمال تحميل الشجرة
        $('#folder-tree').on('ready.jstree', function() {
            console.log("اكتمل تهيئة شجرة المجلدات");
            
            // تحديث عداد العناصر
            const itemsCount = $('#folder-tree').jstree('get_json').length;
            console.log("عدد العناصر في الشجرة:", itemsCount);
            
            // اختيار عقدة افتراضية (أول عقدة ليست سلة المحذوفات)
            if (processedTreeData && processedTreeData.length > 0) {
                let defaultNode = null;
                
                for (let i = 0; i < processedTreeData.length; i++) {
                    if (processedTreeData[i].id !== 'recycle-bin' && !defaultNode) {
                        defaultNode = processedTreeData[i].id;
                        break;
                    }
                }
                
                if (defaultNode) {
                    console.log("اختيار العقدة الافتراضية:", defaultNode);
                    $('#folder-tree').jstree('select_node', defaultNode);
                }
            }
        });
        
        // معالجة حدث اختيار العقدة
        $('#folder-tree').on('select_node.jstree', function(e, data) {
            const nodeId = data.node.id;
            const nodeName = data.node.text;
            console.log("تم اختيار المجلد:", nodeId, nodeName);
            
            // إظهار قسم عرض محتويات المجلد
            $('#no-folder-selected').addClass('d-none');
            $('#folder-contents').removeClass('d-none');
            
            // تحديث اسم المجلد المحدد
            $('#selected-folder-name').text(nodeName);
            
            // تحديث المسار
            const path = '/' + nodeName;
            $('#folder-path').text(path);
            
            // تحديث عدد المجلدات الفرعية
            let childCount = 0;
            if (data.node.children) {
                childCount = data.node.children.length;
            }
            $('#subfolder-count').text(childCount);
            
            // رابط عرض المجلد
            if (nodeId.startsWith('folder-')) {
                const folderId = nodeId.replace('folder-', '');
                $('#view-folder-btn').attr('href', '/ar/dashboard/archive/folder/' + folderId + '/');
                $('#selected-folder-id').val(folderId);
                $('#selected-parent-id').val(folderId);
            } else {
                $('#view-folder-btn').attr('href', '#');
                $('#selected-folder-id').val('');
                $('#selected-parent-id').val('');
            }
            
            // تحديث عدد الملفات (قيمة افتراضية)
            $('#file-count').text(0);
        });
        
        // معالجة حدث البحث
        let searchTimeout = null;
        $('#folder-search').on('keyup', function() {
            const searchText = $(this).val();
            
            if (searchTimeout) {
                clearTimeout(searchTimeout);
            }
            
            searchTimeout = setTimeout(function() {
                $('#folder-tree').jstree('search', searchText);
            }, 250);
        });
        
        // معالجة حدث تحديث الشجرة
        $('#refresh-tree').on('click', function(e) {
            e.preventDefault();
            window.location.reload();
        });
    });
</script>
{% endblock %}"""
    
    # كتابة القالب الجديد
    with open(template_path, 'w', encoding='utf-8') as file:
        file.write(content)
        
    print(f"تم إنشاء القالب البسيط الجديد: {template_path}")

def modify_admin_view():
    """تعديل دالة admin_archive لاستخدام قالب مستقل جديد"""
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
    
    # إنشاء دالة محدثة تستخدم القالب الجديد
    updated_function = """def admin_archive(request):
    \"\"\"عرض الأرشيف الإلكتروني مع شجرة المجلدات\"\"\"
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
    
    # استخدام القالب الجديد البسيط الذي تم إنشاؤه
    return render(request, 'admin/archive/simple_archive.html', context)
"""
    
    # استبدال الدالة القديمة بالدالة المحدثة
    updated_content = content.replace(function_code, updated_function)
    
    # حفظ الملف المحدث
    with open(file_path, 'w', encoding='utf-8') as file:
        file.write(updated_content)
    
    print("تم تحديث دالة admin_archive لاستخدام القالب الجديد")

if __name__ == "__main__":
    create_simple_archive_template()
    modify_admin_view()