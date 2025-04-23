"""
تحسين نماذج إضافة المجلدات والملفات للسماح بالإضافة إلى مجلدات محددة
"""

def fix_folder_add_modal():
    """تحسين نموذج إضافة المجلد للسماح باختيار المجلد الأب"""
    template_path = "templates/admin/archive/static_archive.html"
    
    # قراءة ملف القالب
    with open(template_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # البحث عن نموذج إضافة المجلد الحالي
    folder_modal_pattern = r'<!-- Modal لإنشاء مجلد جديد -->\s*<div class="modal fade" id="newFolderModal".*?</div>\s*</div>\s*</div>'
    
    # إنشاء نموذج إضافة مجلد محسن مع قائمة منسدلة للمجلدات الأب
    enhanced_folder_modal = """<!-- Modal لإنشاء مجلد جديد -->
<div class="modal fade" id="newFolderModal" tabindex="-1" aria-labelledby="newFolderModalLabel" aria-hidden="true">
    <div class="modal-dialog">
        <div class="modal-content">
            <div class="modal-header">
                <h5 class="modal-title" id="newFolderModalLabel">{% trans "إنشاء مجلد جديد" %}</h5>
                <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
            </div>
            <div class="modal-body">
                <form id="newFolderForm" method="post" action="{% url 'admin_archive' %}?action=add_folder">
                    {% csrf_token %}
                    <div class="mb-3">
                        <label for="folderName" class="form-label">{% trans "اسم المجلد" %}</label>
                        <input type="text" class="form-control" id="folderName" name="name" placeholder="{% trans 'أدخل اسم المجلد' %}" required>
                    </div>
                    <div class="mb-3">
                        <label for="parentFolder" class="form-label">{% trans "المجلد الأب" %}</label>
                        <select class="form-select" id="parentFolder" name="parent">
                            <option value="">{% trans "-- مجلد رئيسي (بدون أب) --" %}</option>
                            {% for folder in all_folders %}
                                <option value="{{ folder.id }}" {% if current_folder and current_folder.id == folder.id %}selected{% endif %}>{{ folder.name }}</option>
                            {% endfor %}
                        </select>
                        <small class="form-text text-muted">{% trans "اترك فارغاً لإنشاء مجلد رئيسي، أو اختر المجلد الأب" %}</small>
                    </div>
                    <div class="mb-3">
                        <label for="folderDescription" class="form-label">{% trans "الوصف" %}</label>
                        <textarea class="form-control" id="folderDescription" name="description" rows="3" placeholder="{% trans 'وصف اختياري للمجلد' %}"></textarea>
                    </div>
                </form>
            </div>
            <div class="modal-footer">
                <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">{% trans "إلغاء" %}</button>
                <button type="button" class="btn btn-primary" onclick="document.getElementById('newFolderForm').submit()">{% trans "إنشاء" %}</button>
            </div>
        </div>
    </div>
</div>"""
    
    # استبدال نموذج إضافة المجلد القديم بالمحسن
    import re
    content = re.sub(folder_modal_pattern, enhanced_folder_modal, content, flags=re.DOTALL)
    
    # كتابة المحتوى المحدث إلى الملف
    with open(template_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"تم تحديث نموذج إضافة المجلد في {template_path}")

def fix_file_upload_modal():
    """تحسين نموذج إضافة الملف للسماح باختيار المجلد المستهدف"""
    template_path = "templates/admin/archive/static_archive.html"
    
    # قراءة ملف القالب
    with open(template_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # البحث عن نموذج إضافة الملف الحالي
    file_modal_pattern = r'<!-- Modal لرفع ملف جديد -->\s*<div class="modal fade" id="uploadFileModal".*?</div>\s*</div>\s*</div>'
    
    # إنشاء نموذج إضافة ملف محسن مع قائمة منسدلة للمجلدات
    enhanced_file_modal = """<!-- Modal لرفع ملف جديد -->
<div class="modal fade" id="uploadFileModal" tabindex="-1" aria-labelledby="uploadFileModalLabel" aria-hidden="true">
    <div class="modal-dialog">
        <div class="modal-content">
            <div class="modal-header">
                <h5 class="modal-title" id="uploadFileModalLabel">{% trans "رفع ملف جديد" %}</h5>
                <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
            </div>
            <div class="modal-body">
                <form id="uploadFileForm" method="post" action="{% url 'admin_archive' %}?action=add_file" enctype="multipart/form-data">
                    {% csrf_token %}
                    <div class="mb-3">
                        <label for="fileTitle" class="form-label">{% trans "عنوان الملف" %}</label>
                        <input type="text" class="form-control" id="fileTitle" name="title" placeholder="{% trans 'أدخل عنوان الملف' %}" required>
                    </div>
                    <div class="mb-3">
                        <label for="targetFolder" class="form-label">{% trans "المجلد المستهدف" %}</label>
                        <select class="form-select" id="targetFolder" name="folder">
                            <option value="">{% trans "-- الجذر (بدون مجلد) --" %}</option>
                            {% for folder in all_folders %}
                                <option value="{{ folder.id }}" {% if current_folder and current_folder.id == folder.id %}selected{% endif %}>{{ folder.name }}</option>
                            {% endfor %}
                        </select>
                        <small class="form-text text-muted">{% trans "اختر المجلد الذي تريد إضافة الملف إليه" %}</small>
                    </div>
                    <div class="mb-3">
                        <label for="fileUpload" class="form-label">{% trans "اختر الملف" %}</label>
                        <input type="file" class="form-control" id="fileUpload" name="file" required>
                    </div>
                    <div class="mb-3">
                        <label for="fileDescription" class="form-label">{% trans "الوصف" %}</label>
                        <textarea class="form-control" id="fileDescription" name="description" rows="3" placeholder="{% trans 'وصف اختياري للملف' %}"></textarea>
                    </div>
                </form>
            </div>
            <div class="modal-footer">
                <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">{% trans "إلغاء" %}</button>
                <button type="button" class="btn btn-primary" onclick="document.getElementById('uploadFileForm').submit()">{% trans "رفع الملف" %}</button>
            </div>
        </div>
    </div>
</div>"""
    
    # استبدال نموذج إضافة الملف القديم بالمحسن
    import re
    content = re.sub(file_modal_pattern, enhanced_file_modal, content, flags=re.DOTALL)
    
    # كتابة المحتوى المحدث إلى الملف
    with open(template_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"تم تحديث نموذج إضافة الملف في {template_path}")

def update_admin_archive_view():
    """تحديث دالة admin_archive لتوفير قائمة كاملة بالمجلدات في السياق"""
    views_path = "rental/admin_views.py"
    
    # قراءة ملف admin_views.py
    with open(views_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # البحث عن جزء إعداد السياق في دالة admin_archive
    context_pattern = r'# إعداد سياق البيانات\s*context = \{\s*\'root_folders\': root_folders,.*?\'active_section\': \'archive\'\s*\}'
    
    # سياق محدث يشمل جميع المجلدات المتاحة
    updated_context = """# إعداد سياق البيانات
    context = {
        'root_folders': root_folders,
        'subfolders': subfolders,
        'documents': documents,
        'current_folder': current_folder,
        'folder_path': folder_path,
        'folder_param': folder_param,
        'document_param': document_param,
        'all_folders': all_folders,  # إضافة قائمة كاملة بجميع المجلدات
        'is_english': is_english,
        'is_rtl': is_rtl,
        'active_section': 'archive'
    }"""
    
    # استبدال جزء السياق القديم بالمحدث
    import re
    content = re.sub(context_pattern, updated_context, content, flags=re.DOTALL)
    
    # كتابة المحتوى المحدث إلى الملف
    with open(views_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"تم تحديث دالة admin_archive لتضمين قائمة كاملة بالمجلدات في {views_path}")

def main():
    """تنفيذ التحسينات على نماذج إضافة المجلدات والملفات"""
    print("بدء تحسين نماذج إضافة المجلدات والملفات...")
    
    # تحديث دالة admin_archive أولاً
    update_admin_archive_view()
    
    # تحسين نموذج إضافة المجلد
    fix_folder_add_modal()
    
    # تحسين نموذج إضافة الملف
    fix_file_upload_modal()
    
    print("تم تحسين نماذج إضافة المجلدات والملفات بنجاح!")

if __name__ == "__main__":
    main()