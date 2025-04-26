#!/usr/bin/env python3
"""
تحديث قالب الأرشيف لإستخدام ملف JavaScript الجديد
"""

import os

def update_archive_template():
    """تحديث قالب الأرشيف لاستخدام ملف JavaScript الجديد"""
    template_path = 'templates/admin/archive/windows_explorer_enhanced.html'
    
    # القراءة من الملف الأصلي
    with open(template_path, 'r', encoding='utf-8') as file:
        content = file.read()
    
    # تحديد بداية ونهاية قسم JavaScript الحالي
    start_marker = '{% block extra_head %}'
    end_marker = '</script>'
    extra_css_marker = '{% block extra_css %}'
    
    start_index = content.find(start_marker)
    if start_index == -1:
        print("❌ لم يتم العثور على بداية كتلة extra_head")
        return False
    
    # البحث عن أول تواجد لنهاية وسم script بعد بداية الكتلة
    script_end_index = content.find(end_marker, start_index)
    if script_end_index == -1:
        print("❌ لم يتم العثور على نهاية وسم script")
        return False
    
    script_end_index += len(end_marker)
    
    # البحث عن بداية كتلة extra_css
    css_start_index = content.find(extra_css_marker)
    if css_start_index == -1:
        print("❌ لم يتم العثور على بداية كتلة extra_css")
        return False
    
    # استبدال كود JavaScript القديم
    new_head_content = """{% block extra_head %}
<!-- إضافة مكتبات جافا سكريبت ضرورية -->
<script src="https://cdnjs.cloudflare.com/ajax/libs/jstree/3.3.12/jstree.min.js"></script>
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/jstree/3.3.12/themes/default/style.min.css" />
<!-- استخدام ملف JavaScript المحسن للأرشيف -->
<script src="{% static 'js/archive-explorer-fixed.js' %}"></script>
"""
    
    # تجميع المحتوى النهائي
    updated_content = content[:start_index] + new_head_content + content[css_start_index:]
    
    # الكتابة إلى الملف
    with open(template_path, 'w', encoding='utf-8') as file:
        file.write(updated_content)
    
    print("✅ تم تحديث قالب الأرشيف بنجاح")
    return True

# التنفيذ
if __name__ == "__main__":
    update_archive_template()
