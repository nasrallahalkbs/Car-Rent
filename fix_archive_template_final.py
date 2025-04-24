"""
إصلاح نهائي لقالب عرض الأرشيف لمنع عرض المستندات الوهمية

هذا السكريبت يقوم بتحديث القالب الحالي المستخدم لعرض الأرشيف الإلكتروني
ويضمن عدم عرض أي مستندات وهمية أو افتراضية في واجهة المستخدم.
"""

import os
import django
import sys

# إعداد بيئة Django
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'car_rental_project.settings')
django.setup()

from django.urls import reverse
from rental.models import ArchiveFolder, Document
from rental.admin_views import admin_archive

def fix_static_archive_template():
    """
    إصلاح قالب الأرشيف الثابت لمنع عرض أي مستندات وهمية
    """
    print("بدء إصلاح قالب الأرشيف الثابت...")
    
    # مسار القالب المستخدم حاليًا
    template_path = 'templates/admin/archive/static_archive.html'
    
    # التحقق من وجود القالب
    if not os.path.exists(template_path):
        print(f"القالب {template_path} غير موجود!")
        return
    
    # قراءة محتوى القالب
    with open(template_path, 'r', encoding='utf-8') as file:
        template_content = file.read()
    
    # البحث عن أكواد عرض المستندات الافتراضية والوهمية وإزالتها
    
    # 1. تحديث حلقة عرض المستندات لتحقق من عدم كونها مستندات وهمية
    updated_content = template_content
    
    if '{% for doc in documents %}' in updated_content:
        print("تحديث حلقة عرض المستندات...")
        
        # إضافة شرط لحالة عدم وجود مستندات
        if '{% else %}' not in updated_content or '{% if documents %}' not in updated_content:
            # نقوم بإضافة التحقق من المستندات قبل الحلقة
            old_section = '{% for doc in documents %}'
            new_section = '''{% if documents %}
                    {% for doc in documents %}'''
            updated_content = updated_content.replace(old_section, new_section)
            
            # وإغلاق الحلقة بعد عرض جميع المستندات
            old_section = '{% endfor %}'
            new_section = '''{% endfor %}
                {% else %}
                    <div class="empty-state">
                        <div class="empty-state-icon">
                            <i class="fas fa-file-alt"></i>
                        </div>
                        <h4 class="empty-state-title">{% trans "لا توجد مستندات" %}</h4>
                        <p class="empty-state-description">{% trans "لا توجد مستندات في هذا المجلد. يمكنك إضافة مستندات جديدة باستخدام زر رفع ملف." %}</p>
                        <button type="button" class="btn btn-primary" data-bs-toggle="modal" data-bs-target="#uploadFileModal">
                            <i class="fas fa-file-upload me-2"></i> {% trans "رفع ملف" %}
                        </button>
                    </div>
                {% endif %}'''
            updated_content = updated_content.replace(old_section, new_section)
            
            print("تم تحديث حلقة عرض المستندات بنجاح")
    
    # 2. إزالة أي مستندات افتراضية في حالة عدم وجود مستندات حقيقية
    if '{% else %}' in updated_content and '<a href="#" class="text-decoration-none">' in updated_content:
        print("إزالة أي مستندات افتراضية في حالة عدم وجود مستندات حقيقية...")
        
        # البحث عن قسم المستندات الافتراضية واستبداله بشاشة فارغة
        start_marker = '{% else %}'
        end_marker = '{% endif %}'
        
        pos_start = updated_content.find(start_marker)
        pos_end = updated_content.find(end_marker, pos_start)
        
        if pos_start != -1 and pos_end != -1:
            section_to_replace = updated_content[pos_start:pos_end + len(end_marker)]
            
            empty_section = '''{% else %}
                <div class="empty-state">
                    <div class="empty-state-icon">
                        <i class="fas fa-file-alt"></i>
                    </div>
                    <h4 class="empty-state-title">{% trans "لا توجد مستندات" %}</h4>
                    <p class="empty-state-description">{% trans "لا توجد مستندات في هذا المجلد. يمكنك إضافة مستندات جديدة باستخدام زر رفع ملف." %}</p>
                    <button type="button" class="btn btn-primary" data-bs-toggle="modal" data-bs-target="#uploadFileModal">
                        <i class="fas fa-file-upload me-2"></i> {% trans "رفع ملف" %}
                    </button>
                </div>
            {% endif %}'''
            
            updated_content = updated_content.replace(section_to_replace, empty_section)
            print("تم استبدال قسم المستندات الافتراضية بنجاح")
    
    # 3. البحث عن وتحديث أي كود JavaScript يضيف مستندات وهمية
    if '<script>' in updated_content and 'folderContents' in updated_content:
        print("تحديث أي كود JavaScript يضيف مستندات وهمية...")
        
        # البحث عن تعريف folderContents واستبداله بتعريف فارغ
        start_marker = 'const folderContents = {'
        end_marker = '};'
        
        pos_start = updated_content.find(start_marker)
        if pos_start != -1:
            pos_end = updated_content.find(end_marker, pos_start)
            if pos_end != -1:
                section_to_replace = updated_content[pos_start:pos_end + len(end_marker)]
                
                empty_contents = '''const folderContents = {
    'home': [],
    '1': [],
    '2': [],
    '3': [],
    '4': [],
    '5': []
};'''
                
                updated_content = updated_content.replace(section_to_replace, empty_contents)
                print("تم تحديث تعريف folderContents في JavaScript")
    
    # 4. إزالة أي مستند محدد باسم "نموذج_استعلام_الارشيف"
    if 'نموذج_استعلام_الارشيف' in updated_content:
        print("إزالة أي ذكر لملف 'نموذج_استعلام_الارشيف'...")
        updated_content = updated_content.replace('نموذج_استعلام_الارشيف', 'مستند_محذوف')
        print("تم إزالة أي ذكر لملف 'نموذج_استعلام_الارشيف'")
    
    # 5. إنشاء نسخة احتياطية من القالب الأصلي
    backup_path = template_path.replace('.html', '_backup.html')
    with open(backup_path, 'w', encoding='utf-8') as file:
        file.write(template_content)
    print(f"تم إنشاء نسخة احتياطية من القالب الأصلي في {backup_path}")
    
    # 6. حفظ التغييرات
    with open(template_path, 'w', encoding='utf-8') as file:
        file.write(updated_content)
    print(f"تم حفظ التغييرات في القالب {template_path}")
    
    # 7. إنشاء القالب المحسن
    enhanced_template_path = 'templates/admin/archive/enhanced_archive.html'
    
    # إنشاء قالب محسن جديد لا يعرض أي مستندات افتراضية
    enhanced_template = '''{% extends 'admin_layout.html' %}
{% load static %}
{% load i18n %}

{% block title %}{% trans "الأرشيف الإلكتروني" %}{% endblock %}

{% block extra_head %}
<script>
document.addEventListener('DOMContentLoaded', function() {
    console.log("تم تحميل صفحة الأرشيف المحسنة - النسخة النهائية");
});
</script>
{% endblock %}

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
                    <a href="{% url 'admin_archive' %}?folder={{ parent.id }}">{{ parent.name }}</a>
                {% endif %}
            {% endfor %}
        {% elif folder_param %}
            <a href="{% url 'admin_archive' %}">{% trans "الرئيسية" %}</a>
            <span class="mx-2">/</span>
            <span class="fw-bold">{% if folder_param == "fees" %}{% trans "رسوم (1)" %}{% elif folder_param == "attendance" %}{% trans "حضور (2)" %}{% elif folder_param == "accounting" %}{% trans "حسابات (3)" %}{% elif folder_param == "records" %}{% trans "محفوظات (4)" %}{% elif folder_param == "pow" %}{% trans "توكيلات (5)" %}{% else %}{{ folder_param }}{% endif %}</span>
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
            {% if current_folder %}
                <!-- زر العودة للمجلد الأب -->
                {% if current_folder.parent %}
                    <a href="{% url 'admin_archive' %}?folder={{ current_folder.parent.id }}" class="text-decoration-none">
                        <div class="folder-card">
                            <div class="folder-icon">
                                <i class="fas fa-arrow-up"></i>
                            </div>
                            <div class="folder-name">{% trans "العودة للأعلى" %}</div>
                        </div>
                    </a>
                {% else %}
                    <a href="{% url 'admin_archive' %}" class="text-decoration-none">
                        <div class="folder-card">
                            <div class="folder-icon">
                                <i class="fas fa-home"></i>
                            </div>
                            <div class="folder-name">{% trans "العودة للرئيسية" %}</div>
                        </div>
                    </a>
                {% endif %}
                
                <!-- المجلدات الفرعية للمجلد الحالي -->
                {% if subfolders %}
                    {% for subfolder in subfolders %}
                    <a href="{% url 'admin_archive' %}?folder={{ subfolder.id }}" class="text-decoration-none">
                        <div class="folder-card">
                            <div class="folder-icon">
                                <i class="fas fa-folder"></i>
                            </div>
                            <div class="folder-name">{{ subfolder.name }}</div>
                            <div class="folder-meta">
                                {% trans "تم الإنشاء" %}: {{ subfolder.created_at|date:"d/m/Y" }}
                            </div>
                        </div>
                    </a>
                    {% endfor %}
                {% endif %}
            {% else %}
                <!-- المجلدات الرئيسية -->
                {% if root_folders %}
                    {% for folder in root_folders %}
                    <a href="{% url 'admin_archive' %}?folder={{ folder.id }}" class="text-decoration-none">
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
                    <div class="col-12">
                        <div class="empty-state">
                            <div class="empty-state-icon">
                                <i class="fas fa-folder-open"></i>
                            </div>
                            <h4 class="empty-state-title">{% trans "لا توجد مجلدات" %}</h4>
                            <p class="empty-state-description">{% trans "لا توجد مجلدات في النظام حالياً. يمكنك إنشاء مجلد جديد باستخدام زر إنشاء مجلد." %}</p>
                            <button type="button" class="btn btn-primary" data-bs-toggle="modal" data-bs-target="#newFolderModal">
                                <i class="fas fa-folder-plus me-2"></i> {% trans "إنشاء مجلد" %}
                            </button>
                        </div>
                    </div>
                {% endif %}
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
                <a href="{{ doc.file.url }}" class="text-decoration-none" target="_blank">
                    <div class="file-card">
                        <div class="file-icon {% if 'pdf' in doc.file.url %}pdf{% elif 'doc' in doc.file.url %}doc{% elif 'xls' in doc.file.url %}xls{% elif 'jpg' in doc.file.url or 'png' in doc.file.url or 'jpeg' in doc.file.url %}img{% elif 'zip' in doc.file.url %}zip{% endif %}">
                            <i class="fas {% if 'pdf' in doc.file.url %}fa-file-pdf{% elif 'doc' in doc.file.url %}fa-file-word{% elif 'xls' in doc.file.url %}fa-file-excel{% elif 'jpg' in doc.file.url or 'png' in doc.file.url or 'jpeg' in doc.file.url %}fa-file-image{% elif 'zip' in doc.file.url %}fa-file-archive{% else %}fa-file{% endif %}"></i>
                        </div>
                        <div class="file-name">{{ doc.title }}</div>
                        <div class="file-meta">
                            <div>{{ doc.created_at|date:"d/m/Y" }}</div>
                        </div>
                    </div>
                </a>
                {% endfor %}
            </div>
        {% else %}
            <div class="empty-state">
                <div class="empty-state-icon">
                    <i class="fas fa-file-alt"></i>
                </div>
                <h4 class="empty-state-title">{% trans "لا توجد ملفات" %}</h4>
                <p class="empty-state-description">{% trans "لا توجد ملفات في هذا المجلد. يمكنك إضافة ملفات جديدة باستخدام زر رفع ملف." %}</p>
                <button type="button" class="btn btn-primary" data-bs-toggle="modal" data-bs-target="#uploadFileModal">
                    <i class="fas fa-file-upload me-2"></i> {% trans "رفع ملف" %}
                </button>
            </div>
        {% endif %}
    </div>
</div>

<!-- نافذة إنشاء مجلد جديد -->
<div class="modal fade" id="newFolderModal" tabindex="-1" aria-labelledby="newFolderModalLabel" aria-hidden="true">
    <div class="modal-dialog">
        <div class="modal-content">
            <div class="modal-header">
                <h5 class="modal-title" id="newFolderModalLabel">{% trans "إنشاء مجلد جديد" %}</h5>
                <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
            </div>
            <form action="{% url 'admin_archive' %}?action=add_folder" method="post">
                <div class="modal-body">
                    {% csrf_token %}
                    <div class="mb-3">
                        <label for="name" class="form-label">{% trans "اسم المجلد" %}</label>
                        <input type="text" class="form-control" id="name" name="name" required>
                    </div>
                    <div class="mb-3">
                        <label for="description" class="form-label">{% trans "وصف المجلد (اختياري)" %}</label>
                        <textarea class="form-control" id="description" name="description" rows="3"></textarea>
                    </div>
                    <div class="mb-3">
                        <label for="parent" class="form-label">{% trans "المجلد الأب" %}</label>
                        <select class="form-select" id="parent" name="parent">
                            <option value="">{% trans "المجلد الرئيسي" %}</option>
                            {% for folder in all_folders %}
                                <option value="{{ folder.id }}" {% if current_folder and folder.id == current_folder.id %}selected{% endif %}>
                                    {{ folder.name }}
                                </option>
                            {% endfor %}
                        </select>
                    </div>
                </div>
                <div class="modal-footer">
                    <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">{% trans "إلغاء" %}</button>
                    <button type="submit" class="btn btn-primary">{% trans "إنشاء المجلد" %}</button>
                </div>
            </form>
        </div>
    </div>
</div>

<!-- نافذة رفع ملف -->
<div class="modal fade" id="uploadFileModal" tabindex="-1" aria-labelledby="uploadFileModalLabel" aria-hidden="true">
    <div class="modal-dialog">
        <div class="modal-content">
            <div class="modal-header">
                <h5 class="modal-title" id="uploadFileModalLabel">{% trans "رفع ملف" %}</h5>
                <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
            </div>
            <form action="{% url 'admin_archive' %}?action=add_file" method="post" enctype="multipart/form-data">
                <div class="modal-body">
                    {% csrf_token %}
                    <div class="mb-3">
                        <label for="title" class="form-label">{% trans "عنوان الملف" %}</label>
                        <input type="text" class="form-control" id="title" name="title" required>
                    </div>
                    <div class="mb-3">
                        <label for="description" class="form-label">{% trans "وصف الملف (اختياري)" %}</label>
                        <textarea class="form-control" id="description" name="description" rows="3"></textarea>
                    </div>
                    <div class="mb-3">
                        <label for="folder" class="form-label">{% trans "المجلد" %}</label>
                        <select class="form-select" id="folder" name="folder">
                            <option value="">{% trans "المجلد الرئيسي" %}</option>
                            {% for folder in all_folders %}
                                <option value="{{ folder.id }}" {% if current_folder and folder.id == current_folder.id %}selected{% endif %}>
                                    {{ folder.name }}
                                </option>
                            {% endfor %}
                        </select>
                    </div>
                    <div class="mb-3">
                        <label for="file" class="form-label">{% trans "اختر الملف" %}</label>
                        <input type="file" class="form-control" id="file" name="file" required>
                    </div>
                </div>
                <div class="modal-footer">
                    <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">{% trans "إلغاء" %}</button>
                    <button type="submit" class="btn btn-primary">{% trans "رفع الملف" %}</button>
                </div>
            </form>
        </div>
    </div>
</div>
{% endblock %}
'''
    
    # حفظ القالب المحسن
    with open(enhanced_template_path, 'w', encoding='utf-8') as file:
        file.write(enhanced_template)
    print(f"تم إنشاء قالب محسن جديد في {enhanced_template_path}")
    
    # 8. تحديث ملف admin_views.py لاستخدام القالب المحسن
    views_file = 'rental/admin_views.py'
    with open(views_file, 'r', encoding='utf-8') as file:
        views_content = file.read()
    
    if "return render(request, 'admin/archive/static_archive.html', context)" in views_content:
        old_line = "return render(request, 'admin/archive/static_archive.html', context)"
        new_line = "return render(request, 'admin/archive/enhanced_archive.html', context)"
        updated_views = views_content.replace(old_line, new_line)
        
        with open(views_file, 'w', encoding='utf-8') as file:
            file.write(updated_views)
        print("تم تحديث ملف admin_views.py لاستخدام القالب المحسن")
    else:
        print("لم نتمكن من العثور على سطر تقديم القالب في ملف admin_views.py")
    
    print("\nتم إصلاح قالب الأرشيف الثابت بنجاح!")

if __name__ == "__main__":
    fix_static_archive_template()