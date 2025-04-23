"""
إنشاء عرض مبسط للغاية للمجلدات بدون استخدام مكتبات جافا سكريبت معقدة
"""
import os

def create_basic_template():
    """إنشاء قالب بسيط جداً للمجلدات"""
    template_path = "templates/admin/archive/basic_folders.html"
    
    content = """{% extends "admin/admin_layout.html" %}
{% load i18n %}

{% block styles %}
<style>
    .archive-container {
        padding: 20px;
    }
    .folder-list {
        border: 1px solid #ddd;
        border-radius: 5px;
        background-color: #fff;
        padding: 0;
        max-height: 600px;
        overflow-y: auto;
    }
    .folder-list-item {
        border-bottom: 1px solid #f0f0f0;
        padding: 12px 15px;
        display: flex;
        align-items: center;
        transition: background-color 0.15s ease;
    }
    .folder-list-item:hover {
        background-color: #f8f9fa;
    }
    .folder-list-item:last-child {
        border-bottom: none;
    }
    .folder-list-item i {
        color: #ffc107;
        font-size: 18px;
        margin-left: 10px;
    }
    .subfolder-list {
        padding-right: 20px;
        margin-top: 10px;
        border-right: 1px solid #dee2e6;
    }
    .folder-info-card {
        background-color: #f8f9fa;
        border: 1px solid #ddd;
        border-radius: 5px;
        padding: 20px;
        margin-bottom: 20px;
    }
    .folder-info-header {
        display: flex;
        align-items: center;
        margin-bottom: 15px;
    }
    .folder-info-header i {
        color: #ffc107;
        font-size: 24px;
        margin-left: 10px;
    }
    .folder-badges {
        margin-top: 15px;
    }
    .folder-badges .badge {
        margin-left: 5px;
        padding: 5px 10px;
    }
    .folder-actions {
        margin-top: 15px;
    }
    .folder-content {
        border: 1px solid #ddd;
        border-radius: 5px;
        background-color: #fff;
        padding: 20px;
    }
    .subfolder-item {
        padding: 8px 10px;
        background-color: #f8f9fa;
        border-radius: 4px;
        margin-bottom: 8px;
        display: flex;
        align-items: center;
    }
    .subfolder-item i {
        color: #ffc107;
        margin-left: 8px;
    }
</style>
{% endblock %}

{% block content %}
<div class="archive-container">
    <div class="d-flex justify-content-between align-items-center mb-4">
        <h3>{% trans "الأرشيف الإلكتروني" %}</h3>
        <a href="/ar/dashboard/" class="btn btn-outline-secondary">
            <i class="fas fa-arrow-right ms-2"></i> {% trans "العودة للوحة التحكم" %}
        </a>
    </div>

    <div class="row">
        <div class="col-12 mb-3">
            <div class="d-flex justify-content-between">
                <div>
                    <button type="button" class="btn btn-primary" data-bs-toggle="modal" data-bs-target="#newFolderModal">
                        <i class="fas fa-folder-plus ms-2"></i> {% trans "إضافة مجلد" %}
                    </button>
                    <button type="button" class="btn btn-success ms-2" data-bs-toggle="modal" data-bs-target="#uploadFileModal">
                        <i class="fas fa-file-upload ms-2"></i> {% trans "رفع ملف" %}
                    </button>
                </div>
                <div class="d-flex align-items-center">
                    <div class="input-group">
                        <input type="text" id="folder-search" class="form-control" placeholder="{% trans 'بحث...' %}">
                        <button class="btn btn-outline-secondary" type="button">
                            <i class="fas fa-search"></i>
                        </button>
                    </div>
                </div>
            </div>
        </div>

        <div class="col-md-5">
            <h5><i class="fas fa-folder ms-2 text-warning"></i> {% trans "المجلدات" %}</h5>
            <div class="folder-list">
                <!-- المجلدات الرئيسية -->
                <div class="system-folder">
                    <div class="folder-list-item">
                        <i class="fas fa-trash-alt ms-2" style="color: #0078d7;"></i>
                        <span>{% trans "سلة المحذوفات" %}</span>
                    </div>
                </div>
                
                <!-- قائمة المجلدات الفعلية من قاعدة البيانات -->
                {% for folder in root_folders %}
                <div class="folder-list-item" data-folder-id="{{ folder.id }}">
                    <i class="fas fa-folder ms-2"></i>
                    <div>
                        <span class="folder-name">{{ folder.name }}</span>
                        {% if folder.children.all %}
                            <span class="badge bg-secondary ms-2">{{ folder.children.all|length }}</span>
                        {% endif %}
                    </div>
                </div>
                {% endfor %}
            </div>
        </div>

        <div class="col-md-7">
            <!-- بطاقة معلومات المجلد -->
            <div class="folder-info-card">
                <div class="folder-info-header">
                    <i class="fas fa-folder-open ms-2"></i>
                    <h5 class="mb-0">{% trans "معلومات الأرشيف" %}</h5>
                </div>
                <p>{% trans "الأرشيف الإلكتروني هو نظام لتخزين وإدارة الملفات والمستندات بشكل منظم." %}</p>
                <div class="folder-badges">
                    <span class="badge bg-primary">{{ root_folders|length }} {% trans "مجلد رئيسي" %}</span>
                    <span class="badge bg-info">{{ subfolder_count }} {% trans "مجلد فرعي" %}</span>
                </div>
            </div>
            
            <!-- قائمة المجلدات الرئيسية -->
            <div class="folder-content">
                <h5 class="mb-3">{% trans "المجلدات الرئيسية" %}</h5>
                <div class="row">
                    {% for folder in root_folders %}
                    <div class="col-md-6 mb-3">
                        <div class="card">
                            <div class="card-body">
                                <h5 class="card-title">
                                    <i class="fas fa-folder text-warning ms-2"></i>
                                    {{ folder.name }}
                                </h5>
                                <p class="card-text small">
                                    {% if folder.children.all %}
                                    <span class="text-muted">{{ folder.children.all|length }} {% trans "مجلد فرعي" %}</span>
                                    {% else %}
                                    <span class="text-muted">{% trans "لا توجد مجلدات فرعية" %}</span>
                                    {% endif %}
                                </p>
                                <a href="/ar/dashboard/archive/folder/{{ folder.id }}/" class="btn btn-sm btn-outline-primary">
                                    <i class="fas fa-eye ms-1"></i> {% trans "عرض" %}
                                </a>
                            </div>
                        </div>
                    </div>
                    {% endfor %}
                </div>
            </div>
        </div>
    </div>
</div>

<!-- نموذج إنشاء مجلد جديد -->
<div class="modal fade" id="newFolderModal" tabindex="-1" aria-hidden="true">
    <div class="modal-dialog">
        <div class="modal-content">
            <div class="modal-header">
                <h5 class="modal-title">{% trans "إضافة مجلد جديد" %}</h5>
                <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
            </div>
            <form action="/ar/dashboard/archive/folder/add/" method="post">
                <div class="modal-body">
                    {% csrf_token %}
                    <div class="mb-3">
                        <label for="folder-name" class="form-label">{% trans "اسم المجلد" %}</label>
                        <input type="text" class="form-control" id="folder-name" name="name" required>
                    </div>
                    <div class="mb-3">
                        <label for="parent-folder" class="form-label">{% trans "المجلد الأب" %}</label>
                        <select class="form-select" id="parent-folder" name="parent_id">
                            <option value="">{% trans "بدون مجلد أب (مجلد رئيسي)" %}</option>
                            {% for folder in root_folders %}
                                <option value="{{ folder.id }}">{{ folder.name }}</option>
                            {% endfor %}
                        </select>
                    </div>
                    <div class="mb-3">
                        <label for="folder-description" class="form-label">{% trans "وصف المجلد" %}</label>
                        <textarea class="form-control" id="folder-description" name="description" rows="3"></textarea>
                    </div>
                </div>
                <div class="modal-footer">
                    <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">{% trans "إلغاء" %}</button>
                    <button type="submit" class="btn btn-primary">{% trans "إضافة" %}</button>
                </div>
            </form>
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
            <form action="/ar/dashboard/archive/add/" method="post" enctype="multipart/form-data">
                <div class="modal-body">
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
                            {% for folder in root_folders %}
                                <option value="{{ folder.id }}">{{ folder.name }}</option>
                            {% endfor %}
                        </select>
                    </div>
                    <div class="mb-3">
                        <label for="file-description" class="form-label">{% trans "وصف الملف" %}</label>
                        <textarea class="form-control" id="file-description" name="description" rows="3"></textarea>
                    </div>
                </div>
                <div class="modal-footer">
                    <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">{% trans "إلغاء" %}</button>
                    <button type="submit" class="btn btn-primary">{% trans "رفع" %}</button>
                </div>
            </form>
        </div>
    </div>
</div>
{% endblock %}

{% block extra_js %}
<script>
    $(document).ready(function() {
        console.log('تم تحميل صفحة الأرشيف بنمط بسيط');
        
        // عند النقر على المجلد عرض المعلومات
        $('.folder-list-item').click(function() {
            // إزالة الفئة النشطة من جميع العناصر
            $('.folder-list-item').removeClass('bg-light');
            
            // إضافة الفئة النشطة للعنصر المحدد
            $(this).addClass('bg-light');
            
            // عرض معلومات المجلد المحدد
            var folderId = $(this).data('folder-id');
            if (folderId) {
                console.log('تم اختيار المجلد: ' + folderId);
            }
        });

        // البحث في قائمة المجلدات
        $('#folder-search').on('keyup', function() {
            var searchText = $(this).val().toLowerCase();
            
            $('.folder-list-item').each(function() {
                var folderName = $(this).find('.folder-name').text().toLowerCase();
                if (folderName.includes(searchText)) {
                    $(this).show();
                } else {
                    $(this).hide();
                }
            });
        });
    });
</script>
{% endblock %}"""
    
    with open(template_path, 'w', encoding='utf-8') as file:
        file.write(content)
    
    print(f"تم إنشاء القالب البسيط: {template_path}")

def update_admin_view():
    """تعديل دالة admin_archive لاستخدام القالب البسيط"""
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
    
    # إنشاء دالة محدثة تستخدم القالب الجديد والمبسط جداً
    updated_function = """def admin_archive(request):
    \"\"\"عرض الأرشيف الإلكتروني بأسلوب بسيط\"\"\"
    from django.utils.translation import get_language
    current_language = get_language()
    is_english = current_language == 'en'
    is_rtl = current_language == 'ar'
    
    # الحصول على مجلدات الجذر
    root_folders = ArchiveFolder.objects.filter(parent=None).order_by('name')
    print(f"DEBUG - عدد المجلدات الرئيسية: {root_folders.count()}")
    
    # الحصول على إجمالي عدد المجلدات الفرعية
    subfolder_count = ArchiveFolder.objects.exclude(parent=None).count()
    
    # إعداد سياق البيانات
    context = {
        'root_folders': root_folders,
        'subfolder_count': subfolder_count,
        'is_english': is_english,
        'is_rtl': is_rtl,
        'active_section': 'archive'
    }
    
    # استخدام القالب البسيط الجديد
    return render(request, 'admin/archive/basic_folders.html', context)
"""
    
    # استبدال الدالة القديمة بالدالة المحدثة
    updated_content = content.replace(function_code, updated_function)
    
    # حفظ الملف المحدث
    with open(file_path, 'w', encoding='utf-8') as file:
        file.write(updated_content)
    
    print("تم تحديث دالة admin_archive لاستخدام القالب البسيط")

if __name__ == "__main__":
    create_basic_template()
    update_admin_view()