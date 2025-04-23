"""
تحسين نموذج إضافة الملفات ليسمح بتحديد أي مجلد (رئيسي أو فرعي) لإضافة الملف إليه
"""

def update_file_upload_modal():
    """تحديث نموذج إضافة الملفات ليعرض قائمة منسدلة بجميع المجلدات"""
    template_path = "templates/admin/archive/static_archive.html"
    
    with open(template_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # البحث عن نموذج رفع الملفات
    import re
    
    # البحث عن جزء نموذج إضافة الملفات
    file_modal_pattern = r'<!-- نموذج رفع ملف جديد -->.*?<div class="modal fade" id="uploadFileModal".*?</div>\s*</div>\s*</div>\s*</div>'
    
    file_modal_match = re.search(file_modal_pattern, content, re.DOTALL)
    
    if file_modal_match:
        old_modal = file_modal_match.group(0)
        
        # إنشاء النموذج المحسن مع قائمة منسدلة لجميع المجلدات
        new_modal = """<!-- نموذج رفع ملف جديد -->
<div class="modal fade" id="uploadFileModal" tabindex="-1" aria-labelledby="uploadFileModalLabel" aria-hidden="true">
    <div class="modal-dialog">
        <div class="modal-content">
            <div class="modal-header">
                <h5 class="modal-title" id="uploadFileModalLabel">رفع ملف جديد</h5>
                <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="إغلاق"></button>
            </div>
            <div class="modal-body">
                <form action="{% url 'admin_archive' %}?action=add_file" method="post" enctype="multipart/form-data">
                    {% csrf_token %}
                    <div class="mb-3">
                        <label for="title" class="form-label">عنوان الملف</label>
                        <input type="text" class="form-control" id="title" name="title" required>
                    </div>
                    <div class="mb-3">
                        <label for="description" class="form-label">وصف الملف</label>
                        <textarea class="form-control" id="description" name="description" rows="3"></textarea>
                    </div>
                    <div class="mb-3">
                        <label for="folder" class="form-label">المجلد</label>
                        <select class="form-select" id="folder" name="folder">
                            <option value="">المجلد الرئيسي</option>
                            {% for folder in all_folders %}
                                <option value="{{ folder.id }}">{{ folder.get_full_path }}</option>
                            {% endfor %}
                        </select>
                    </div>
                    <div class="mb-3">
                        <label for="file" class="form-label">اختر الملف</label>
                        <input type="file" class="form-control" id="file" name="file" required>
                    </div>
                    <div class="text-end">
                        <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">إلغاء</button>
                        <button type="submit" class="btn btn-primary">رفع الملف</button>
                    </div>
                </form>
            </div>
        </div>
    </div>
</div>"""
        
        # استبدال النموذج القديم بالنموذج المحسن
        updated_content = content.replace(old_modal, new_modal)
        
        with open(template_path, 'w', encoding='utf-8') as f:
            f.write(updated_content)
        
        print(f"تم تحديث نموذج إضافة الملفات في {template_path}")
        return True
    else:
        print("لم يتم العثور على نموذج إضافة الملفات في قالب الأرشيف")
        return False

def update_admin_archive_view():
    """تحديث دالة admin_archive لتوفير قائمة بجميع المجلدات للقالب"""
    views_path = "rental/admin_views.py"
    
    with open(views_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # البحث عن دالة admin_archive
    import re
    
    archive_function_pattern = r'def admin_archive\(request\):.*?return render\(request, template_name, context\)'
    
    archive_function_match = re.search(archive_function_pattern, content, re.DOTALL)
    
    if archive_function_match:
        archive_function = archive_function_match.group(0)
        
        # البحث عن جزء إنشاء سياق القالب
        context_pattern = r'context = \{.*?\}'
        
        context_match = re.search(context_pattern, archive_function, re.DOTALL)
        
        if context_match:
            old_context = context_match.group(0)
            
            # إنشاء سياق محدث يشمل قائمة بجميع المجلدات
            new_context = old_context[:-1] + ",\n        'all_folders': ArchiveFolder.objects.all(),\n    }"
            
            # استبدال السياق القديم بالسياق المحدث
            updated_function = archive_function.replace(old_context, new_context)
            
            # استبدال الدالة القديمة بالدالة المحدثة
            updated_content = content.replace(archive_function, updated_function)
            
            with open(views_path, 'w', encoding='utf-8') as f:
                f.write(updated_content)
            
            print(f"تم تحديث دالة admin_archive في {views_path}")
            return True
        else:
            print("لم يتم العثور على تعريف سياق القالب في دالة admin_archive")
            return False
    else:
        print("لم يتم العثور على دالة admin_archive في ملف admin_views.py")
        return False

def add_get_full_path_method():
    """إضافة دالة get_full_path إلى نموذج ArchiveFolder لعرض المسار الكامل للمجلد"""
    models_path = "rental/models.py"
    
    with open(models_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # البحث عن تعريف نموذج ArchiveFolder
    import re
    
    archive_folder_pattern = r'class ArchiveFolder\(models.Model\):.*?def __str__\(self\):.*?return self\.name'
    
    archive_folder_match = re.search(archive_folder_pattern, content, re.DOTALL)
    
    if archive_folder_match:
        archive_folder_class = archive_folder_match.group(0)
        
        # التحقق مما إذا كانت دالة get_full_path موجودة بالفعل
        if "def get_full_path(self):" in content:
            print("دالة get_full_path موجودة بالفعل في نموذج ArchiveFolder")
            return True
        
        # إنشاء دالة get_full_path
        get_full_path_method = """
    def get_full_path(self):
        """Get the full path of the folder"""
        if self.folder:
            return f"{self.folder.get_full_path()} / {self.name}"
        return self.name"""
        
        # إضافة دالة get_full_path بعد دالة __str__
        updated_class = archive_folder_class + get_full_path_method
        
        # استبدال تعريف الفئة القديم بالتعريف المحدث
        updated_content = content.replace(archive_folder_class, updated_class)
        
        with open(models_path, 'w', encoding='utf-8') as f:
            f.write(updated_content)
        
        print(f"تم إضافة دالة get_full_path إلى نموذج ArchiveFolder في {models_path}")
        return True
    else:
        print("لم يتم العثور على تعريف نموذج ArchiveFolder في ملف models.py")
        return False

def main():
    """تنفيذ التعديلات"""
    print("بدء تحسين نموذج إضافة الملفات...")
    
    # إضافة دالة get_full_path إلى نموذج ArchiveFolder
    add_get_full_path_method()
    
    # تحديث دالة admin_archive لتوفير قائمة بجميع المجلدات
    update_admin_archive_view()
    
    # تحديث نموذج إضافة الملفات
    result = update_file_upload_modal()
    
    if result:
        print("تم تحسين نموذج إضافة الملفات بنجاح!")
    else:
        print("حدث خطأ أثناء محاولة تحسين نموذج إضافة الملفات.")

if __name__ == "__main__":
    main()