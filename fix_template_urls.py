"""
إصلاح روابط URL في قالب الأرشيف
"""

def fix_template_urls():
    """إصلاح روابط URL في قالب الأرشيف"""
    import os
    
    # مسار قالب الأرشيف
    template_path = "templates/admin/archive/static_archive.html"
    
    # قراءة محتوى القالب
    with open(template_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # استبدال روابط URL غير الصحيحة
    replacements = [
        # استبدال كل المراجع لـ admin_archive_folder
        ("{% url 'admin_archive_folder' folder_id=folder.id %}", "{% url 'admin_archive' %}?folder={{ folder.id }}"),
        ("{% url 'admin_archive_folder' folder_id=parent.id %}", "{% url 'admin_archive' %}?folder={{ parent.id }}"),
        # استبدال روابط إضافة المجلد والملف
        ("{% url 'admin_archive_folder_add' %}", "{% url 'admin_archive' %}?action=add_folder"),
        ("{% url 'admin_archive_add' %}", "{% url 'admin_archive' %}?action=add_file"),
        # استبدال روابط تفاصيل المستند
        ("{% url 'admin_archive_detail' document_id=doc.id %}", "{% url 'admin_archive' %}?document={{ doc.id }}"),
    ]
    
    # تطبيق كل الاستبدالات
    for old, new in replacements:
        content = content.replace(old, new)
    
    # استبدال المجلد الحالي بالمعلمة من URL
    old_block = """{% if current_folder %}
            <a href="{% url 'admin_archive' %}">{% trans "الرئيسية" %}</a>
            {% for parent in folder_path %}
                <span class="mx-2">/</span>
                {% if parent.id == current_folder.id %}
                    <span class="fw-bold">{{ parent.name }}</span>
                {% else %}
                    <a href="{% url 'admin_archive' %}?folder={{ parent.id }}">{{ parent.name }}</a>
                {% endif %}
            {% endfor %}
        {% else %}"""
        
    new_block = """{% if folder_param %}
            <a href="{% url 'admin_archive' %}">{% trans "الرئيسية" %}</a>
            <span class="mx-2">/</span>
            <span class="fw-bold">{% if folder_param == "fees" %}{% trans "رسوم (1)" %}{% elif folder_param == "attendance" %}{% trans "حضور (2)" %}{% elif folder_param == "accounting" %}{% trans "حسابات (3)" %}{% elif folder_param == "records" %}{% trans "محفوظات (4)" %}{% elif folder_param == "pow" %}{% trans "توكيلات (5)" %}{% else %}{{ folder_param }}{% endif %}</span>
        {% else %}"""
    
    content = content.replace(old_block, new_block)
    
    # كتابة المحتوى المحدث إلى الملف
    with open(template_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"تم إصلاح روابط URL في قالب الأرشيف: {template_path}")
    return True

def main():
    """تنفيذ إصلاحات روابط URL"""
    print("بدء إصلاح روابط URL في قالب الأرشيف...")
    
    result = fix_template_urls()
    
    if result:
        print("تم إصلاح روابط URL بنجاح!")
    else:
        print("حدث خطأ أثناء محاولة إصلاح روابط URL.")

if __name__ == "__main__":
    main()