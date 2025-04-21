"""
سكريبت لتحديث ملفات القوالب مع إضافة ختم زمني
لحل مشكلة التخزين المؤقت
"""
import os
import time
import datetime

# القوالب المطلوب تحديثها
templates = [
    'templates/reservation_detail.html',
    'templates/reservation_detail_django.html',
    'templates/admin/archive/archive_main.html',
]

# إضافة ختم زمني في سطر التعليق في بداية الملف
timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
update_marker = f"<!-- Template updated: {timestamp} -->\n"

for template_path in templates:
    if not os.path.exists(template_path):
        print(f"الملف غير موجود: {template_path}")
        continue
        
    with open(template_path, 'r', encoding='utf-8') as file:
        content = file.read()
    
    # إذا كان هناك ختم زمني قديم، قم بإزالته
    if "<!-- Template updated:" in content:
        lines = content.split('\n')
        filtered_lines = [line for line in lines if "<!-- Template updated:" not in line]
        content = '\n'.join(filtered_lines)
    
    # إضافة الختم الزمني الجديد في بداية الملف
    with open(template_path, 'w', encoding='utf-8') as file:
        file.write(update_marker + content)
    
    print(f"تم تحديث الملف: {template_path}")

print("تم الانتهاء من تحديث جميع القوالب. يرجى إعادة تحميل الصفحات.")