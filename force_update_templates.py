"""
تطبيق التغييرات الجديدة في القوالب عبر تحديث معرف التخزين المؤقت
"""

import os
import time
import re

def update_cache_buster():
    """تحديث معرف التخزين المؤقت في ملفات القوالب"""
    templates_dir = "templates"
    timestamp = int(time.time())
    
    # البحث في جميع ملفات القوالب
    for root, _, files in os.walk(templates_dir):
        for file in files:
            if file.endswith('.html'):
                filepath = os.path.join(root, file)
                
                # قراءة محتوى الملف
                with open(filepath, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # إضافة أو تحديث معرف التخزين المؤقت
                if 'CACHE_BUSTER' in content:
                    content = re.sub(r'<!-- CACHE_BUSTER \d+ -->', f'<!-- CACHE_BUSTER {timestamp} -->', content, count=1)
                else:
                    content = f'<!-- CACHE_BUSTER {timestamp} -->{content}'
                
                # كتابة المحتوى المحدث
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(content)
                    
                print(f"تم تحديث الملف: {filepath}")

if __name__ == "__main__":
    update_cache_buster()
    print("تم تحديث جميع ملفات القوالب بنجاح!")