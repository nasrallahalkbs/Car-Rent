#!/usr/bin/env python3
"""
تنظيف جميع ملفات الكاش والتخزين المؤقت بشكل نهائي من المشروع

هذا السكريبت يقوم بحذف:
1. مجلدات __pycache__ وملفات .pyc
2. ملفات الكاش المؤقتة التي تم إنشاؤها بواسطة Django
3. أي ملفات مؤقتة أخرى
"""

import os
import shutil
import glob
import re

def clean_cache_files():
    """حذف جميع ملفات الكاش"""
    print("جاري تنظيف ملفات الكاش...")
    
    # 1. حذف مجلدات __pycache__ وملفات .pyc
    pycache_count = 0
    pyc_count = 0
    
    for root, dirs, files in os.walk('.'):
        # تجاهل المجلدات المخفية أو الخارجية
        dirs[:] = [d for d in dirs if not d.startswith('.git') and not d.startswith('.venv') and not d.startswith('.pythonlibs')]
        
        # حذف مجلدات __pycache__
        for dir in dirs:
            if dir == "__pycache__":
                pycache_path = os.path.join(root, dir)
                try:
                    shutil.rmtree(pycache_path)
                    print(f"✅ تم حذف: {pycache_path}")
                    pycache_count += 1
                except Exception as e:
                    print(f"❌ خطأ في حذف {pycache_path}: {e}")
        
        # حذف ملفات .pyc
        for file in files:
            if file.endswith(".pyc"):
                pyc_path = os.path.join(root, file)
                try:
                    os.remove(pyc_path)
                    print(f"✅ تم حذف: {pyc_path}")
                    pyc_count += 1
                except Exception as e:
                    print(f"❌ خطأ في حذف {pyc_path}: {e}")
    
    print(f"تم حذف {pycache_count} مجلد __pycache__ و {pyc_count} ملف .pyc")
    
    # 2. تحديث معرفات التخزين المؤقت في ملفات HTML
    template_count = 0
    
    for template_file in glob.glob('templates/**/*.html', recursive=True):
        try:
            with open(template_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # تحديث معرف التخزين المؤقت
            if 'CACHE_BUSTER' in content:
                import time
                timestamp = int(time.time())
                new_content = re.sub(r'<!-- CACHE_BUSTER \d+ -->', f'<!-- CACHE_BUSTER {timestamp} -->', content)
                
                with open(template_file, 'w', encoding='utf-8') as f:
                    f.write(new_content)
                
                print(f"✅ تم تحديث معرف التخزين المؤقت في: {template_file}")
                template_count += 1
        except Exception as e:
            print(f"❌ خطأ في تحديث {template_file}: {e}")
    
    print(f"تم تحديث معرف التخزين المؤقت في {template_count} ملف قالب")
    
    # 3. تنظيف أي ملفات مؤقتة أخرى
    temp_extensions = ['.tmp', '.temp', '.bak', '.~']
    temp_count = 0
    
    for ext in temp_extensions:
        for temp_file in glob.glob(f'**/*{ext}', recursive=True):
            try:
                os.remove(temp_file)
                print(f"✅ تم حذف الملف المؤقت: {temp_file}")
                temp_count += 1
            except Exception as e:
                print(f"❌ خطأ في حذف {temp_file}: {e}")
    
    print(f"تم حذف {temp_count} ملف مؤقت آخر")
    
    print("\n✨ تم الانتهاء من تنظيف جميع ملفات الكاش بنجاح! ✨")

if __name__ == "__main__":
    clean_cache_files()