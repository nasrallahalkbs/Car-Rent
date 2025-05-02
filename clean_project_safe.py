#!/usr/bin/env python3
"""
تنظيف آمن للمشروع من ملفات الكاش بدون التأثير على مجلد .git

هذا السكريبت يقوم بتنظيف:
1. مجلدات __pycache__ و ملفات .pyc
2. ملفات الكاش المختلفة
3. المجلدات المؤقتة
4. ملفات SQLite المؤقتة
"""

import os
import shutil
import datetime
import re

def get_size_format(byte_size):
    """تحويل حجم الملف من بايت إلى تنسيق مقروء"""
    for unit in ['بايت', 'كيلوبايت', 'ميجابايت', 'جيجابايت', 'تيرابايت']:
        if byte_size < 1024.0:
            return f"{byte_size:.2f} {unit}"
        byte_size /= 1024.0
    return f"{byte_size:.2f} تيرابايت"

def is_excluded(path, exclude_patterns):
    """التحقق مما إذا كان المسار مستثنى"""
    for pattern in exclude_patterns:
        if pattern.search(path):
            return True
    return False

def clean_pycache():
    """تنظيف جميع مجلدات __pycache__ وملفات .pyc"""
    print("\n=== تنظيف ملفات بايثون المؤقتة ===")
    
    total_size = 0
    removed_dirs = 0
    removed_files = 0
    
    # مسارات للتجاهل (نتجنب مجلد .git)
    exclude_patterns = [re.compile(r'\.git/.*')]
    
    # العثور على جميع مجلدات __pycache__
    for root, dirs, files in os.walk("."):
        # تجنب المجلدات المستثناة
        if is_excluded(root, exclude_patterns):
            continue
            
        # حذف مجلدات __pycache__
        for d in dirs:
            if d == "__pycache__":
                dir_path = os.path.join(root, d)
                try:
                    dir_size = sum(os.path.getsize(os.path.join(dir_path, f)) for f in os.listdir(dir_path) if os.path.isfile(os.path.join(dir_path, f)))
                    total_size += dir_size
                    shutil.rmtree(dir_path)
                    removed_dirs += 1
                    print(f"✓ تم حذف مجلد: {dir_path} ({get_size_format(dir_size)})")
                except Exception as e:
                    print(f"✗ خطأ في حذف مجلد {dir_path}: {e}")
        
        # حذف ملفات .pyc
        for f in files:
            if f.endswith(".pyc") or f.endswith(".pyo"):
                file_path = os.path.join(root, f)
                try:
                    file_size = os.path.getsize(file_path)
                    total_size += file_size
                    os.remove(file_path)
                    removed_files += 1
                    print(f"✓ تم حذف ملف: {file_path} ({get_size_format(file_size)})")
                except Exception as e:
                    print(f"✗ خطأ في حذف ملف {file_path}: {e}")
    
    print(f"\nإجمالي التنظيف:")
    print(f"- تم حذف {removed_dirs} مجلد __pycache__")
    print(f"- تم حذف {removed_files} ملف .pyc و .pyo")
    print(f"- تم تحرير {get_size_format(total_size)} من المساحة")

def clean_temp_files():
    """تنظيف الملفات المؤقتة والكاش"""
    print("\n=== تنظيف ملفات الكاش والملفات المؤقتة ===")
    
    # أنماط المجلدات والملفات المطلوب حذفها
    patterns_to_delete = [
        r'.*\.temp$',
        r'.*\.tmp$',
        r'.*\.cache$',
        r'.*cache.*',
        r'temp/.*',
        r'tmp/.*',
        r'.*~$',
        r'.*\.bak$',
        r'.*\.log$'
    ]
    
    # أنماط الملفات والمجلدات المستثناة من الحذف
    exclude_patterns = [
        r'\.git/.*',
        r'\.venv/.*',
        r'venv/.*',
        r'env/.*',
        r'node_modules/.*',
        r'migrations/.*',
        r'locale/.*',
        r'staticfiles/.*',
        r'media/uploads/.*',
        r'\.github/.*'
    ]
    
    compiled_delete_patterns = [re.compile(pattern) for pattern in patterns_to_delete]
    compiled_exclude_patterns = [re.compile(pattern) for pattern in exclude_patterns]
    
    total_size = 0
    removed_items = 0
    
    for root, dirs, files in os.walk(".", topdown=True):
        # تجنب المجلدات المستثناة
        if is_excluded(root, compiled_exclude_patterns):
            continue
            
        dirs[:] = [d for d in dirs if not is_excluded(os.path.join(root, d), compiled_exclude_patterns)]
        
        # حذف المجلدات التي تطابق أنماط الحذف
        for d in dirs[:]:
            dir_path = os.path.join(root, d)
            if any(pattern.search(dir_path) for pattern in compiled_delete_patterns) and not is_excluded(dir_path, compiled_exclude_patterns):
                try:
                    dir_size = sum(os.path.getsize(os.path.join(dirpath, filename)) for dirpath, _, filenames in os.walk(dir_path) for filename in filenames if os.path.exists(os.path.join(dirpath, filename)))
                    shutil.rmtree(dir_path)
                    total_size += dir_size
                    removed_items += 1
                    print(f"✓ تم حذف مجلد: {dir_path} ({get_size_format(dir_size)})")
                    dirs.remove(d)
                except Exception as e:
                    print(f"✗ خطأ في حذف مجلد {dir_path}: {e}")
        
        # حذف الملفات التي تطابق أنماط الحذف
        for f in files:
            file_path = os.path.join(root, f)
            if any(pattern.search(file_path) for pattern in compiled_delete_patterns) and not is_excluded(file_path, compiled_exclude_patterns):
                try:
                    file_size = os.path.getsize(file_path)
                    os.remove(file_path)
                    total_size += file_size
                    removed_items += 1
                    print(f"✓ تم حذف ملف: {file_path} ({get_size_format(file_size)})")
                except Exception as e:
                    print(f"✗ خطأ في حذف ملف {file_path}: {e}")
    
    print(f"\nإجمالي التنظيف:")
    print(f"- تم حذف {removed_items} عنصر من الملفات والمجلدات المؤقتة")
    print(f"- تم تحرير {get_size_format(total_size)} من المساحة")

def clean_django_cache():
    """تنظيف ملفات كاش Django"""
    print("\n=== تنظيف ملفات كاش Django ===")
    
    # المجلدات المهمة في Django
    django_cache_dirs = [
        ".static_storage",
        ".media_storage",
        "static/.webassets-cache",
        "staticfiles/admin/cache",
        "staticfiles/CACHE"
    ]
    
    total_size = 0
    removed_items = 0
    
    for cache_dir in django_cache_dirs:
        if os.path.exists(cache_dir) and os.path.isdir(cache_dir):
            try:
                dir_size = sum(os.path.getsize(os.path.join(dirpath, filename)) for dirpath, _, filenames in os.walk(cache_dir) for filename in filenames if os.path.exists(os.path.join(dirpath, filename)))
                shutil.rmtree(cache_dir)
                total_size += dir_size
                removed_items += 1
                print(f"✓ تم حذف مجلد كاش Django: {cache_dir} ({get_size_format(dir_size)})")
            except Exception as e:
                print(f"✗ خطأ في حذف مجلد كاش Django {cache_dir}: {e}")
    
    print(f"\nإجمالي التنظيف:")
    print(f"- تم حذف {removed_items} مجلد كاش Django")
    print(f"- تم تحرير {get_size_format(total_size)} من المساحة")

def clean_sqlite_temp():
    """تنظيف ملفات SQLite المؤقتة"""
    print("\n=== تنظيف ملفات SQLite المؤقتة ===")
    
    # أنماط ملفات SQLite المؤقتة
    sqlite_patterns = [
        r'.*\.sqlite3-journal$',
        r'.*\.sqlite3-wal$',
        r'.*\.sqlite3-shm$'
    ]
    
    compiled_patterns = [re.compile(pattern) for pattern in sqlite_patterns]
    
    total_size = 0
    removed_files = 0
    
    for root, _, files in os.walk("."):
        # تجنب مجلد .git
        if '.git' in root:
            continue
            
        for f in files:
            file_path = os.path.join(root, f)
            if any(pattern.search(file_path) for pattern in compiled_patterns):
                try:
                    file_size = os.path.getsize(file_path)
                    os.remove(file_path)
                    total_size += file_size
                    removed_files += 1
                    print(f"✓ تم حذف ملف SQLite المؤقت: {file_path} ({get_size_format(file_size)})")
                except Exception as e:
                    print(f"✗ خطأ في حذف ملف SQLite المؤقت {file_path}: {e}")
    
    print(f"\nإجمالي التنظيف:")
    print(f"- تم حذف {removed_files} ملف SQLite مؤقت")
    print(f"- تم تحرير {get_size_format(total_size)} من المساحة")

def main():
    """الدالة الرئيسية لتنفيذ عملية التنظيف"""
    start_time = datetime.datetime.now()
    
    print("=" * 50)
    print("بدء عملية تنظيف المشروع (النسخة الآمنة)")
    print("=" * 50)
    
    # حساب الحجم الإجمالي للمشروع قبل التنظيف (باستثناء مجلد .git)
    initial_size = 0
    for root, _, files in os.walk("."):
        # تجنب مجلد .git
        if '.git' in root:
            continue
            
        for f in files:
            try:
                file_path = os.path.join(root, f)
                if os.path.exists(file_path):
                    initial_size += os.path.getsize(file_path)
            except Exception:
                continue
                
    print(f"حجم المشروع قبل التنظيف (باستثناء .git): {get_size_format(initial_size)}")
    
    # تنفيذ عمليات التنظيف
    clean_pycache()
    clean_temp_files()
    clean_django_cache()
    clean_sqlite_temp()
    
    # حساب الحجم الإجمالي للمشروع بعد التنظيف (باستثناء مجلد .git)
    final_size = 0
    for root, _, files in os.walk("."):
        # تجنب مجلد .git
        if '.git' in root:
            continue
            
        for f in files:
            try:
                file_path = os.path.join(root, f)
                if os.path.exists(file_path):
                    final_size += os.path.getsize(file_path)
            except Exception:
                continue
                
    print("\n" + "=" * 50)
    print("ملخص عملية التنظيف:")
    print(f"- حجم المشروع قبل التنظيف (باستثناء .git): {get_size_format(initial_size)}")
    print(f"- حجم المشروع بعد التنظيف (باستثناء .git): {get_size_format(final_size)}")
    print(f"- تم توفير: {get_size_format(initial_size - final_size)}")
    
    if initial_size > 0:
        print(f"- نسبة التوفير: {((initial_size - final_size) / initial_size * 100):.2f}%")
    
    end_time = datetime.datetime.now()
    duration = (end_time - start_time).total_seconds()
    print(f"- استغرقت عملية التنظيف: {duration:.2f} ثانية")
    print("=" * 50)
    
    print("\nتم الانتهاء من تنظيف المشروع")

if __name__ == "__main__":
    main()