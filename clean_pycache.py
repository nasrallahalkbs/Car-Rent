#!/usr/bin/env python3
"""
تنظيف مجلدات __pycache__ وملفات .pyc
"""

import os
import shutil

def get_size_format(byte_size):
    """تحويل حجم الملف من بايت إلى تنسيق مقروء"""
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if byte_size < 1024.0:
            return f"{byte_size:.2f} {unit}"
        byte_size /= 1024.0
    return f"{byte_size:.2f} TB"

def clean_pycache():
    """تنظيف جميع مجلدات __pycache__ وملفات .pyc"""
    print("تنظيف ملفات بايثون المؤقتة...")
    
    total_size = 0
    removed_dirs = 0
    removed_files = 0
    
    # قائمة المجلدات التي سنتجاهلها
    exclude_dirs = ['.git', '.cache', '.replit', '.pythonlibs']
    
    # العثور على جميع مجلدات __pycache__
    for root, dirs, files in os.walk("."):
        # تجاهل المجلدات المستثناة
        if any(excluded in root for excluded in exclude_dirs):
            continue
            
        # حذف مجلدات __pycache__
        for d in dirs[:]:
            if d == "__pycache__":
                dir_path = os.path.join(root, d)
                try:
                    dir_size = sum(os.path.getsize(os.path.join(dir_path, f)) for f in os.listdir(dir_path) if os.path.isfile(os.path.join(dir_path, f)))
                    total_size += dir_size
                    shutil.rmtree(dir_path)
                    removed_dirs += 1
                    print(f"✓ تم حذف مجلد: {dir_path} ({get_size_format(dir_size)})")
                except Exception as e:
                    print(f"× خطأ في حذف مجلد {dir_path}: {e}")
        
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
                    print(f"× خطأ في حذف ملف {file_path}: {e}")
    
    print(f"\nإجمالي التنظيف:")
    print(f"- تم حذف {removed_dirs} مجلد __pycache__")
    print(f"- تم حذف {removed_files} ملف .pyc و .pyo")
    print(f"- تم تحرير {get_size_format(total_size)} من المساحة")

if __name__ == "__main__":
    print("=" * 50)
    print("بدء تنظيف مجلدات __pycache__ وملفات .pyc")
    print("=" * 50)
    clean_pycache()
    print("=" * 50)
    print("تم الانتهاء من التنظيف")
    print("=" * 50)