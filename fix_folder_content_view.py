"""
إصلاح عرض محتويات المجلدات في صفحة الأرشيف
"""

def fix_folder_content_display():
    """تعديل دالة admin_archive لعرض محتويات المجلدات بشكل صحيح"""
    
    # مسار ملف admin_views.py
    views_path = "rental/admin_views.py"
    
    # قراءة الملف
    with open(views_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # ملف دالة admin_archive المحسنة
    import re
    
    # استخراج الدالة الحالية
    function_pattern = r'def admin_archive\(request\):.*?return render\(request, [^)]+\)'
    match = re.search(function_pattern, content, re.DOTALL)
    
    if not match:
        print("لم يتم العثور على دالة admin_archive")
        return False
    
    current_function = match.group(0)
    
    # تحديث الجزء الخاص بعرض المجلدات
    updated_section = """    # الحصول على المستندات والمجلدات الفرعية
    documents = []
    subfolders = []
    current_folder = None
    folder_path = []
    
    if folder_param:
        try:
            # تحقق إذا كان معرف المجلد عدداً صحيحاً
            try:
                folder_id = int(folder_param)
                # محاولة العثور على المجلد
                current_folder = ArchiveFolder.objects.get(id=folder_id)
                # الحصول على المجلدات الفرعية والمستندات
                subfolders = ArchiveFolder.objects.filter(parent=current_folder).order_by('name')
                documents = Document.objects.filter(folder=current_folder).order_by('-created_at')
                
                # بناء مسار المجلد
                folder_path = []
                temp_folder = current_folder
                while temp_folder:
                    folder_path.insert(0, temp_folder)
                    temp_folder = temp_folder.parent
                
                print(f"DEBUG - المجلد الحالي: {current_folder.name}")
                print(f"DEBUG - عدد المجلدات الفرعية: {subfolders.count()}")
                print(f"DEBUG - عدد المستندات: {documents.count()}")
            except ValueError:
                # إذا كان معرف المجلد ليس عدداً صحيحاً، نستخدم العرض الافتراضي
                print(f"DEBUG - استخدام العرض الافتراضي للمجلد: {folder_param}")
        except ArchiveFolder.DoesNotExist:
            print(f"DEBUG - المجلد غير موجود: {folder_param}")
    else:
        # عرض المستندات في المجلد الرئيسي (بدون مجلد)
        documents = Document.objects.filter(folder__isnull=True).order_by('-created_at')"""
    
    # استبدال الجزء القديم بالمحسّن
    old_section_pattern = r'# الحصول على المستندات.*?documents = Document\.objects\.filter\(folder__isnull=True\)\.order_by\(\'-created_at\'\)'
    new_function = re.sub(old_section_pattern, updated_section, current_function, flags=re.DOTALL)
    
    # تحديث سياق البيانات
    context_section_pattern = r'# إعداد سياق البيانات.*?\'active_section\': \'archive\''
    context_section = """    # إعداد سياق البيانات
    context = {
        'root_folders': root_folders,
        'subfolders': subfolders,
        'documents': documents,
        'current_folder': current_folder,
        'folder_path': folder_path,
        'folder_param': folder_param,
        'document_param': document_param,
        'is_english': is_english,
        'is_rtl': is_rtl,
        'active_section': 'archive'
    }"""
    
    new_function = re.sub(context_section_pattern, context_section, new_function, flags=re.DOTALL)
    
    # تحديث الملف
    new_content = re.sub(function_pattern, new_function, content, flags=re.DOTALL)
    
    with open(views_path, 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    print(f"تم تحديث دالة admin_archive في {views_path}")
    
    # تحديث قالب الأرشيف لعرض المجلدات الفرعية
    template_path = "templates/admin/archive/static_archive.html"
    
    # قراءة القالب
    with open(template_path, 'r', encoding='utf-8') as f:
        template_content = f.read()
    
    # تحديث جزء عرض المجلدات لعرض المجلدات الفرعية والمجلدات الرئيسية
    folders_section_pattern = r'<div class="folder-grid">.*?</div>\s*</div>\s*\s*<!-- الملفات -->'
    
    # جزء المجلدات المحدث
    new_folders_section = """<div class="folder-grid">
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
            {% endif %}
        </div>
    </div>
    
    <!-- الملفات -->"""
    
    updated_template = re.sub(folders_section_pattern, new_folders_section, template_content, flags=re.DOTALL)
    
    # تحديث مسار المجلد
    path_section_pattern = r'<!-- مسار المجلد -->.*?</div>\s*\s*<!-- المجلدات -->'
    
    new_path_section = """<!-- مسار المجلد -->
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
    
    <!-- المجلدات -->"""
    
    updated_template = re.sub(path_section_pattern, new_path_section, updated_template, flags=re.DOTALL)
    
    # كتابة القالب المحدث
    with open(template_path, 'w', encoding='utf-8') as f:
        f.write(updated_template)
    
    print(f"تم تحديث قالب الأرشيف في {template_path}")
    
    return True

def main():
    """تنفيذ الإصلاحات"""
    print("بدء إصلاح عرض محتويات المجلدات...")
    
    result = fix_folder_content_display()
    
    if result:
        print("تم إصلاح عرض محتويات المجلدات بنجاح!")
    else:
        print("حدث خطأ أثناء محاولة إصلاح عرض محتويات المجلدات.")

if __name__ == "__main__":
    main()