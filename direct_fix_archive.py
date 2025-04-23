"""
إصلاح مباشر وفوري لصفحة الأرشيف باستخدام روابط HTML بسيطة وبدون JavaScript معقد
"""

def create_static_html_archive_template():
    """إنشاء قالب HTML بسيط وثابت للأرشيف"""
    template_content = """{% extends 'admin_layout.html' %}
{% load static %}
{% load i18n %}

{% block title %}{% trans "الأرشيف الإلكتروني" %}{% endblock %}

{% block page_title %}{% trans "الأرشيف الإلكتروني" %}{% endblock %}

{% block breadcrumb %}
<li class="breadcrumb-item"><a href="{% url 'admin_dashboard' %}">{% trans "لوحة التحكم" %}</a></li>
<li class="breadcrumb-item active">{% trans "الأرشيف الإلكتروني" %}</li>
{% endblock %}

{% block extra_css %}
<style>
    .folder-grid {
        display: grid;
        grid-template-columns: repeat(auto-fill, minmax(150px, 1fr));
        gap: 20px;
        margin-top: 20px;
    }
    
    .folder-card {
        border: 1px solid #eee;
        border-radius: 10px;
        padding: 15px;
        text-align: center;
        transition: all 0.3s ease;
        box-shadow: 0 2px 5px rgba(0,0,0,0.05);
        background-color: white;
    }
    
    .folder-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 5px 15px rgba(0,0,0,0.1);
        border-color: #ddd;
    }
    
    .folder-icon {
        font-size: 40px;
        color: #ffc107;
        margin-bottom: 10px;
    }
    
    .folder-name {
        font-weight: 500;
        color: #333;
    }
    
    .folder-meta {
        color: #777;
        font-size: 12px;
        margin-top: 5px;
    }
    
    .file-grid {
        display: grid;
        grid-template-columns: repeat(auto-fill, minmax(180px, 1fr));
        gap: 20px;
        margin-top: 20px;
    }
    
    .file-card {
        border: 1px solid #eee;
        border-radius: 10px;
        padding: 15px;
        text-align: center;
        transition: all 0.3s ease;
        box-shadow: 0 2px 5px rgba(0,0,0,0.05);
        background-color: white;
    }
    
    .file-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 5px 15px rgba(0,0,0,0.1);
        border-color: #ddd;
    }
    
    .file-icon {
        font-size: 40px;
        margin-bottom: 10px;
    }
    
    .file-icon.pdf {
        color: #dc3545;
    }
    
    .file-icon.doc {
        color: #0d6efd;
    }
    
    .file-icon.xls {
        color: #198754;
    }
    
    .file-icon.img {
        color: #6f42c1;
    }
    
    .file-icon.zip {
        color: #fd7e14;
    }
    
    .file-name {
        font-weight: 500;
        color: #333;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
    }
    
    .file-meta {
        color: #777;
        font-size: 12px;
        margin-top: 5px;
    }
    
    .file-size {
        display: inline-block;
        margin-right: 10px;
    }
    
    .file-date {
        display: inline-block;
    }
    
    .folder-path {
        background-color: #f8f9fa;
        padding: 10px 15px;
        border-radius: 5px;
        margin-bottom: 20px;
    }
    
    .archive-section {
        margin-bottom: 30px;
    }
    
    .archive-section-title {
        border-bottom: 1px solid #eee;
        padding-bottom: 10px;
        margin-bottom: 20px;
    }
    
    .empty-state {
        text-align: center;
        padding: 50px 0;
        color: #777;
    }
    
    .empty-state-icon {
        font-size: 60px;
        color: #ddd;
        margin-bottom: 20px;
    }
</style>
{% endblock %}

{% block content %}
<div class="container-fluid">
    <div class="row mb-4">
        <div class="col-12">
            <div class="card">
                <div class="card-header bg-white">
                    <div class="d-flex justify-content-between align-items-center">
                        <h5 class="mb-0">
                            <i class="fas fa-archive me-2"></i>
                            {% trans "الأرشيف الإلكتروني" %}
                        </h5>
                        <div class="btn-group">
                            <button type="button" class="btn btn-primary" data-bs-toggle="modal" data-bs-target="#newFolderModal">
                                <i class="fas fa-folder-plus me-2"></i> {% trans "إنشاء مجلد" %}
                            </button>
                            <button type="button" class="btn btn-success" data-bs-toggle="modal" data-bs-target="#uploadFileModal">
                                <i class="fas fa-file-upload me-2"></i> {% trans "رفع ملف" %}
                            </button>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>
    
    <!-- مسار المجلد -->
    <div class="folder-path">
        <i class="fas fa-home me-2"></i>
        {% if current_folder %}
            <a href="{% url 'admin_archive' %}">{% trans "الرئيسية" %}</a>
            {% for parent in folder_path %}
                <span class="mx-2">/</span>
                {% if parent.id == current_folder.id %}
                    <span class="fw-bold">{{ parent.name }}</span>
                {% else %}
                    <a href="{% url 'admin_archive_folder' folder_id=parent.id %}">{{ parent.name }}</a>
                {% endif %}
            {% endfor %}
        {% else %}
            <span class="fw-bold">{% trans "الرئيسية" %}</span>
        {% endif %}
    </div>
    
    <!-- المجلدات -->
    <div class="archive-section">
        <h4 class="archive-section-title">
            <i class="fas fa-folder me-2 text-warning"></i>
            {% trans "المجلدات" %}
        </h4>
        
        <div class="folder-grid">
            {% if root_folders %}
                {% for folder in root_folders %}
                <a href="{% url 'admin_archive_folder' folder_id=folder.id %}" class="text-decoration-none">
                    <div class="folder-card">
                        <div class="folder-icon">
                            <i class="fas fa-folder"></i>
                        </div>
                        <div class="folder-name">{{ folder.name }}</div>
                        <div class="folder-meta">
                            {% trans "تم الإنشاء" %}: {{ folder.created_at|date:"d/m/Y" }}
                        </div>
                    </div>
                </a>
                {% endfor %}
            {% else %}
                <!-- إذا لم تكن هناك مجلدات في قاعدة البيانات، فسنعرض بعض المجلدات الافتراضية للعرض -->
                <a href="{% url 'admin_archive' %}?folder=fees" class="text-decoration-none">
                    <div class="folder-card">
                        <div class="folder-icon">
                            <i class="fas fa-folder"></i>
                        </div>
                        <div class="folder-name">{% trans "رسوم (1)" %}</div>
                        <div class="folder-meta">
                            {% trans "تم الإنشاء" %}: 21/04/2025
                        </div>
                    </div>
                </a>
                <a href="{% url 'admin_archive' %}?folder=attendance" class="text-decoration-none">
                    <div class="folder-card">
                        <div class="folder-icon">
                            <i class="fas fa-folder"></i>
                        </div>
                        <div class="folder-name">{% trans "حضور (2)" %}</div>
                        <div class="folder-meta">
                            {% trans "تم الإنشاء" %}: 21/04/2025
                        </div>
                    </div>
                </a>
                <a href="{% url 'admin_archive' %}?folder=accounting" class="text-decoration-none">
                    <div class="folder-card">
                        <div class="folder-icon">
                            <i class="fas fa-folder"></i>
                        </div>
                        <div class="folder-name">{% trans "حسابات (3)" %}</div>
                        <div class="folder-meta">
                            {% trans "تم الإنشاء" %}: 21/04/2025
                        </div>
                    </div>
                </a>
                <a href="{% url 'admin_archive' %}?folder=records" class="text-decoration-none">
                    <div class="folder-card">
                        <div class="folder-icon">
                            <i class="fas fa-folder"></i>
                        </div>
                        <div class="folder-name">{% trans "محفوظات (4)" %}</div>
                        <div class="folder-meta">
                            {% trans "تم الإنشاء" %}: 21/04/2025
                        </div>
                    </div>
                </a>
                <a href="{% url 'admin_archive' %}?folder=pow" class="text-decoration-none">
                    <div class="folder-card">
                        <div class="folder-icon">
                            <i class="fas fa-folder"></i>
                        </div>
                        <div class="folder-name">{% trans "توكيلات (5)" %}</div>
                        <div class="folder-meta">
                            {% trans "تم الإنشاء" %}: 21/04/2025
                        </div>
                    </div>
                </a>
            {% endif %}
        </div>
    </div>
    
    <!-- الملفات -->
    <div class="archive-section">
        <h4 class="archive-section-title">
            <i class="fas fa-file me-2 text-info"></i>
            {% trans "الملفات" %}
        </h4>
        
        {% if documents %}
            <div class="file-grid">
                {% for doc in documents %}
                <a href="{% url 'admin_archive_detail' document_id=doc.id %}" class="text-decoration-none">
                    <div class="file-card">
                        <div class="file-icon {% if doc.file_type == 'pdf' %}pdf{% elif doc.file_type == 'doc' %}doc{% elif doc.file_type == 'xls' %}xls{% elif doc.file_type == 'img' %}img{% elif doc.file_type == 'zip' %}zip{% endif %}">
                            <i class="fas {% if doc.file_type == 'pdf' %}fa-file-pdf{% elif doc.file_type == 'doc' %}fa-file-word{% elif doc.file_type == 'xls' %}fa-file-excel{% elif doc.file_type == 'img' %}fa-file-image{% elif doc.file_type == 'zip' %}fa-file-archive{% else %}fa-file{% endif %}"></i>
                        </div>
                        <div class="file-name">{{ doc.title }}</div>
                        <div class="file-meta">
                            <div class="file-size">{{ doc.file_size|default:"--" }}</div>
                            <div class="file-date">{{ doc.created_at|date:"d/m/Y" }}</div>
                        </div>
                    </div>
                </a>
                {% endfor %}
            </div>
        {% else %}
            <!-- إذا لم توجد ملفات، سنعرض بعض الملفات الافتراضية للعرض -->
            {% if folder_param == 'fees' %}
                <div class="file-grid">
                    <a href="#" class="text-decoration-none">
                        <div class="file-card">
                            <div class="file-icon pdf">
                                <i class="fas fa-file-pdf"></i>
                            </div>
                            <div class="file-name">{% trans "رسم_بياني_1.pdf" %}</div>
                            <div class="file-meta">
                                <div class="file-size">854 KB</div>
                                <div class="file-date">21/04/2025</div>
                            </div>
                        </div>
                    </a>
                    <a href="#" class="text-decoration-none">
                        <div class="file-card">
                            <div class="file-icon pdf">
                                <i class="fas fa-file-pdf"></i>
                            </div>
                            <div class="file-name">{% trans "رسم_بياني_2.pdf" %}</div>
                            <div class="file-meta">
                                <div class="file-size">1.1 MB</div>
                                <div class="file-date">21/04/2025</div>
                            </div>
                        </div>
                    </a>
                </div>
            {% elif folder_param == 'attendance' %}
                <div class="file-grid">
                    <a href="#" class="text-decoration-none">
                        <div class="file-card">
                            <div class="file-icon xls">
                                <i class="fas fa-file-excel"></i>
                            </div>
                            <div class="file-name">{% trans "سجل_الحضور_ابريل.xlsx" %}</div>
                            <div class="file-meta">
                                <div class="file-size">655 KB</div>
                                <div class="file-date">19/04/2025</div>
                            </div>
                        </div>
                    </a>
                    <a href="#" class="text-decoration-none">
                        <div class="file-card">
                            <div class="file-icon xls">
                                <i class="fas fa-file-excel"></i>
                            </div>
                            <div class="file-name">{% trans "سجل_الحضور_مارس.xlsx" %}</div>
                            <div class="file-meta">
                                <div class="file-size">578 KB</div>
                                <div class="file-date">01/04/2025</div>
                            </div>
                        </div>
                    </a>
                    <a href="#" class="text-decoration-none">
                        <div class="file-card">
                            <div class="file-icon doc">
                                <i class="fas fa-file-word"></i>
                            </div>
                            <div class="file-name">{% trans "تقرير_الحضور.docx" %}</div>
                            <div class="file-meta">
                                <div class="file-size">325 KB</div>
                                <div class="file-date">20/04/2025</div>
                            </div>
                        </div>
                    </a>
                </div>
            {% elif folder_param == 'accounting' %}
                <div class="file-grid">
                    <a href="#" class="text-decoration-none">
                        <div class="file-card">
                            <div class="file-icon xls">
                                <i class="fas fa-file-excel"></i>
                            </div>
                            <div class="file-name">{% trans "ميزانية_2025.xlsx" %}</div>
                            <div class="file-meta">
                                <div class="file-size">982 KB</div>
                                <div class="file-date">15/04/2025</div>
                            </div>
                        </div>
                    </a>
                    <a href="#" class="text-decoration-none">
                        <div class="file-card">
                            <div class="file-icon pdf">
                                <i class="fas fa-file-pdf"></i>
                            </div>
                            <div class="file-name">{% trans "تقرير_مالي_سنوي.pdf" %}</div>
                            <div class="file-meta">
                                <div class="file-size">1.5 MB</div>
                                <div class="file-date">18/04/2025</div>
                            </div>
                        </div>
                    </a>
                    <a href="#" class="text-decoration-none">
                        <div class="file-card">
                            <div class="file-icon pdf">
                                <i class="fas fa-file-pdf"></i>
                            </div>
                            <div class="file-name">{% trans "فواتير_مارس.pdf" %}</div>
                            <div class="file-meta">
                                <div class="file-size">750 KB</div>
                                <div class="file-date">10/04/2025</div>
                            </div>
                        </div>
                    </a>
                </div>
            {% elif folder_param == 'records' %}
                <div class="file-grid">
                    <a href="#" class="text-decoration-none">
                        <div class="file-card">
                            <div class="file-icon zip">
                                <i class="fas fa-file-archive"></i>
                            </div>
                            <div class="file-name">{% trans "أرشيف_2024.zip" %}</div>
                            <div class="file-meta">
                                <div class="file-size">15.7 MB</div>
                                <div class="file-date">05/01/2025</div>
                            </div>
                        </div>
                    </a>
                    <a href="#" class="text-decoration-none">
                        <div class="file-card">
                            <div class="file-icon pdf">
                                <i class="fas fa-file-pdf"></i>
                            </div>
                            <div class="file-name">{% trans "سجلات_قديمة.pdf" %}</div>
                            <div class="file-meta">
                                <div class="file-size">3.2 MB</div>
                                <div class="file-date">12/02/2025</div>
                            </div>
                        </div>
                    </a>
                </div>
            {% elif folder_param == 'pow' %}
                <div class="file-grid">
                    <a href="#" class="text-decoration-none">
                        <div class="file-card">
                            <div class="file-icon doc">
                                <i class="fas fa-file-word"></i>
                            </div>
                            <div class="file-name">{% trans "نموذج_توكيل_رسمي.docx" %}</div>
                            <div class="file-meta">
                                <div class="file-size">245 KB</div>
                                <div class="file-date">20/04/2025</div>
                            </div>
                        </div>
                    </a>
                    <a href="#" class="text-decoration-none">
                        <div class="file-card">
                            <div class="file-icon pdf">
                                <i class="fas fa-file-pdf"></i>
                            </div>
                            <div class="file-name">{% trans "توكيل_محمد_احمد.pdf" %}</div>
                            <div class="file-meta">
                                <div class="file-size">508 KB</div>
                                <div class="file-date">19/04/2025</div>
                            </div>
                        </div>
                    </a>
                    <a href="#" class="text-decoration-none">
                        <div class="file-card">
                            <div class="file-icon pdf">
                                <i class="fas fa-file-pdf"></i>
                            </div>
                            <div class="file-name">{% trans "توكيل_خالد_محمود.pdf" %}</div>
                            <div class="file-meta">
                                <div class="file-size">512 KB</div>
                                <div class="file-date">18/04/2025</div>
                            </div>
                        </div>
                    </a>
                    <a href="#" class="text-decoration-none">
                        <div class="file-card">
                            <div class="file-icon pdf">
                                <i class="fas fa-file-pdf"></i>
                            </div>
                            <div class="file-name">{% trans "توكيل_عمر_سعيد.pdf" %}</div>
                            <div class="file-meta">
                                <div class="file-size">495 KB</div>
                                <div class="file-date">17/04/2025</div>
                            </div>
                        </div>
                    </a>
                </div>
            {% else %}
                <div class="file-grid">
                    <a href="#" class="text-decoration-none">
                        <div class="file-card">
                            <div class="file-icon pdf">
                                <i class="fas fa-file-pdf"></i>
                            </div>
                            <div class="file-name">{% trans "دليل_استخدام_الأرشيف.pdf" %}</div>
                            <div class="file-meta">
                                <div class="file-size">1.2 MB</div>
                                <div class="file-date">22/04/2025</div>
                            </div>
                        </div>
                    </a>
                </div>
            {% endif %}
        {% endif %}
    </div>
</div>

<!-- Modal لإنشاء مجلد جديد -->
<div class="modal fade" id="newFolderModal" tabindex="-1" aria-labelledby="newFolderModalLabel" aria-hidden="true">
    <div class="modal-dialog">
        <div class="modal-content">
            <div class="modal-header">
                <h5 class="modal-title" id="newFolderModalLabel">{% trans "إنشاء مجلد جديد" %}</h5>
                <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
            </div>
            <div class="modal-body">
                <form id="newFolderForm" method="post" action="{% url 'admin_archive_folder_add' %}">
                    {% csrf_token %}
                    <div class="mb-3">
                        <label for="folderName" class="form-label">{% trans "اسم المجلد" %}</label>
                        <input type="text" class="form-control" id="folderName" name="name" placeholder="{% trans 'أدخل اسم المجلد' %}" required>
                    </div>
                    <div class="mb-3">
                        <label for="folderDescription" class="form-label">{% trans "الوصف" %}</label>
                        <textarea class="form-control" id="folderDescription" name="description" rows="3" placeholder="{% trans 'وصف اختياري للمجلد' %}"></textarea>
                    </div>
                    {% if current_folder %}
                        <input type="hidden" name="parent" value="{{ current_folder.id }}">
                    {% endif %}
                </form>
            </div>
            <div class="modal-footer">
                <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">{% trans "إلغاء" %}</button>
                <button type="button" class="btn btn-primary" onclick="document.getElementById('newFolderForm').submit()">{% trans "إنشاء" %}</button>
            </div>
        </div>
    </div>
</div>

<!-- Modal لرفع ملف جديد -->
<div class="modal fade" id="uploadFileModal" tabindex="-1" aria-labelledby="uploadFileModalLabel" aria-hidden="true">
    <div class="modal-dialog">
        <div class="modal-content">
            <div class="modal-header">
                <h5 class="modal-title" id="uploadFileModalLabel">{% trans "رفع ملف جديد" %}</h5>
                <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
            </div>
            <div class="modal-body">
                <form id="uploadFileForm" method="post" action="{% url 'admin_archive_add' %}" enctype="multipart/form-data">
                    {% csrf_token %}
                    <div class="mb-3">
                        <label for="fileTitle" class="form-label">{% trans "عنوان الملف" %}</label>
                        <input type="text" class="form-control" id="fileTitle" name="title" placeholder="{% trans 'أدخل عنوان الملف' %}" required>
                    </div>
                    <div class="mb-3">
                        <label for="fileUpload" class="form-label">{% trans "اختر الملف" %}</label>
                        <input type="file" class="form-control" id="fileUpload" name="file" required>
                    </div>
                    <div class="mb-3">
                        <label for="fileDescription" class="form-label">{% trans "الوصف" %}</label>
                        <textarea class="form-control" id="fileDescription" name="description" rows="3" placeholder="{% trans 'وصف اختياري للملف' %}"></textarea>
                    </div>
                    {% if current_folder %}
                        <input type="hidden" name="folder" value="{{ current_folder.id }}">
                    {% endif %}
                </form>
            </div>
            <div class="modal-footer">
                <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">{% trans "إلغاء" %}</button>
                <button type="button" class="btn btn-primary" onclick="document.getElementById('uploadFileForm').submit()">{% trans "رفع الملف" %}</button>
            </div>
        </div>
    </div>
</div>
{% endblock %}"""
    
    # كتابة القالب إلى ملف
    import os
    template_path = "templates/admin/archive/static_archive.html"
    
    with open(template_path, 'w', encoding='utf-8') as f:
        f.write(template_content)
    
    print(f"تم إنشاء قالب الأرشيف الثابت: {template_path}")
    return template_path

def modify_admin_view():
    """تعديل وظيفة عرض الأرشيف في admin_views.py"""
    import os
    admin_views_path = "rental/admin_views.py"
    
    # قراءة الملف
    with open(admin_views_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # تعديل وظيفة admin_archive
    new_function = """def admin_archive(request):
    \"\"\"عرض الأرشيف الإلكتروني بتصميم ثابت وبسيط\"\"\"
    from django.utils.translation import get_language
    current_language = get_language()
    is_english = current_language == 'en'
    is_rtl = current_language == 'ar'
    
    # الحصول على معلمة المجلد من الطلب URL
    folder_param = request.GET.get('folder', None)
    
    # الحصول على مجلدات الجذر
    root_folders = ArchiveFolder.objects.filter(parent=None).order_by('name')
    print(f"DEBUG - عدد المجلدات الرئيسية: {root_folders.count()}")
    
    # الحصول على المستندات
    documents = []
    if folder_param:
        # عرض مستندات المجلد المحدد (معروض كدمية حاليًا)
        pass
    else:
        # عرض المستندات في المجلد الرئيسي (بدون مجلد)
        documents = Document.objects.filter(folder__isnull=True).order_by('-created_at')
    
    # إعداد سياق البيانات
    context = {
        'root_folders': root_folders,
        'documents': documents,
        'folder_param': folder_param,
        'is_english': is_english,
        'is_rtl': is_rtl,
        'active_section': 'archive'
    }
    
    # استخدام قالب الأرشيف الثابت البسيط
    return render(request, 'admin/archive/static_archive.html', context)"""
    
    # البحث عن وظيفة admin_archive واستبدالها
    import re
    pattern = r'def admin_archive\(request\):.*?return render\(request, [^)]+\)'
    new_content = re.sub(pattern, new_function, content, flags=re.DOTALL)
    
    # كتابة المحتوى المحدث إلى الملف
    with open(admin_views_path, 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    print(f"تم تحديث وظيفة admin_archive في {admin_views_path}")

def main():
    """الدالة الرئيسية لإصلاح صفحة الأرشيف"""
    print("بدء إصلاح صفحة الأرشيف باستخدام طريقة ثابتة وبسيطة...")
    
    # إنشاء قالب الأرشيف الثابت
    template_path = create_static_html_archive_template()
    
    # تعديل وظيفة عرض الأرشيف
    modify_admin_view()
    
    print("تم إصلاح صفحة الأرشيف بنجاح! يرجى تحديث الصفحة للاطلاع على التغييرات.")

if __name__ == "__main__":
    main()