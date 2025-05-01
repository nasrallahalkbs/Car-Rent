#!/usr/bin/env python3
"""
تنظيف شامل ودوري للملفات المؤقتة وملفات الكاش

هذا السكريبت يقوم بتنظيف كامل وشامل لجميع:
1. ملفات __pycache__ و .pyc
2. معرفات التخزين المؤقت في ملفات HTML
3. ملفات الكاش المؤقتة في جميع أنحاء النظام
4. تنظيف سجلات الأخطاء القديمة ومجلدات التحميل المؤقتة
5. ملفات الأصول التي تم إنشاؤها ولم تعد مستخدمة

يمكن تشغيل هذا السكريبت بشكل دوري لضمان نظام نظيف وسريع.
"""

import os
import shutil
import glob
import re
import time
import logging
import tempfile
from datetime import datetime, timedelta

# إعداد السجلات
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('cache_cleaning.log')
    ]
)

def clean_pycache():
    """حذف ملفات __pycache__ و .pyc"""
    logging.info("جاري تنظيف ملفات __pycache__ و .pyc...")
    pycache_count = 0
    pyc_count = 0
    
    # استثناء المجلدات التي لا ينبغي تنظيفها
    excluded_dirs = ['.git', '.venv', '.pythonlibs']
    
    for root, dirs, files in os.walk('.'):
        # تجاهل المجلدات المستثناة
        dirs[:] = [d for d in dirs if not any(ex in root or d == ex for ex in excluded_dirs)]
        
        # حذف مجلدات __pycache__
        for dir in dirs:
            if dir == "__pycache__":
                pycache_path = os.path.join(root, dir)
                try:
                    shutil.rmtree(pycache_path)
                    logging.info(f"تم حذف: {pycache_path}")
                    pycache_count += 1
                except Exception as e:
                    logging.error(f"خطأ في حذف {pycache_path}: {e}")
        
        # حذف ملفات .pyc
        for file in files:
            if file.endswith(".pyc"):
                pyc_path = os.path.join(root, file)
                try:
                    os.remove(pyc_path)
                    logging.info(f"تم حذف: {pyc_path}")
                    pyc_count += 1
                except Exception as e:
                    logging.error(f"خطأ في حذف {pyc_path}: {e}")
    
    logging.info(f"تم حذف {pycache_count} مجلد __pycache__ و {pyc_count} ملف .pyc")
    return pycache_count, pyc_count

def update_cache_busters():
    """تحديث معرفات التخزين المؤقت في ملفات HTML"""
    logging.info("جاري تحديث معرفات التخزين المؤقت في ملفات HTML...")
    template_count = 0
    timestamp = int(time.time())
    
    for template_file in glob.glob('templates/**/*.html', recursive=True):
        try:
            with open(template_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # تحديث معرف التخزين المؤقت
            if 'CACHE_BUSTER' in content:
                new_content = re.sub(r'<!-- CACHE_BUSTER \d+ -->', f'<!-- CACHE_BUSTER {timestamp} -->', content)
                
                with open(template_file, 'w', encoding='utf-8') as f:
                    f.write(new_content)
                
                logging.info(f"تم تحديث معرف التخزين المؤقت في: {template_file}")
                template_count += 1
        except Exception as e:
            logging.error(f"خطأ في تحديث {template_file}: {e}")
    
    logging.info(f"تم تحديث معرف التخزين المؤقت في {template_count} ملف قالب")
    return template_count

def clean_temp_files():
    """تنظيف الملفات المؤقتة"""
    logging.info("جاري تنظيف الملفات المؤقتة...")
    temp_extensions = ['.tmp', '.temp', '.bak', '.~', '.old']
    temp_count = 0
    
    for ext in temp_extensions:
        for temp_file in glob.glob(f'**/*{ext}', recursive=True):
            try:
                os.remove(temp_file)
                logging.info(f"تم حذف الملف المؤقت: {temp_file}")
                temp_count += 1
            except Exception as e:
                logging.error(f"خطأ في حذف {temp_file}: {e}")
    
    # تنظيف مجلد التحميل المؤقت الخاص بالنظام
    try:
        system_temp = tempfile.gettempdir()
        project_temp_files = glob.glob(os.path.join(system_temp, 'django_*'))
        for temp_file in project_temp_files:
            try:
                if os.path.isfile(temp_file):
                    os.remove(temp_file)
                elif os.path.isdir(temp_file):
                    shutil.rmtree(temp_file)
                logging.info(f"تم حذف ملف النظام المؤقت: {temp_file}")
                temp_count += 1
            except Exception as e:
                logging.error(f"خطأ في حذف ملف النظام المؤقت {temp_file}: {e}")
    except Exception as e:
        logging.error(f"خطأ في الوصول إلى مجلد التحميل المؤقت للنظام: {e}")
    
    logging.info(f"تم حذف {temp_count} ملف مؤقت")
    return temp_count

def clean_old_logs():
    """تنظيف ملفات السجلات القديمة"""
    logging.info("جاري تنظيف ملفات السجلات القديمة...")
    log_count = 0
    log_extensions = ['.log', '.log.1', '.log.2']
    
    # حذف ملفات السجلات الأقدم من أسبوع
    week_ago = datetime.now() - timedelta(days=7)
    
    for ext in log_extensions:
        for log_file in glob.glob(f'**/*{ext}', recursive=True):
            try:
                # التحقق من عمر الملف
                file_time = os.path.getmtime(log_file)
                file_date = datetime.fromtimestamp(file_time)
                
                if file_date < week_ago:
                    os.remove(log_file)
                    logging.info(f"تم حذف ملف السجل القديم: {log_file}")
                    log_count += 1
            except Exception as e:
                logging.error(f"خطأ في حذف {log_file}: {e}")
    
    logging.info(f"تم حذف {log_count} ملف سجل قديم")
    return log_count

def clean_static_cache():
    """تنظيف ملفات التخزين المؤقت الثابتة"""
    logging.info("جاري تنظيف ملفات التخزين المؤقت الثابتة...")
    static_cache_count = 0
    
    # المجلدات المحتملة للملفات الثابتة المخزنة مؤقتًا
    cache_dirs = ['staticfiles/CACHE', 'static/CACHE']
    
    for cache_dir in cache_dirs:
        if os.path.exists(cache_dir):
            try:
                for root, dirs, files in os.walk(cache_dir):
                    for file in files:
                        try:
                            os.remove(os.path.join(root, file))
                            static_cache_count += 1
                        except Exception as e:
                            logging.error(f"خطأ في حذف {os.path.join(root, file)}: {e}")
                
                logging.info(f"تم تنظيف مجلد التخزين المؤقت: {cache_dir}")
            except Exception as e:
                logging.error(f"خطأ في تنظيف مجلد التخزين المؤقت {cache_dir}: {e}")
    
    logging.info(f"تم حذف {static_cache_count} ملف تخزين مؤقت ثابت")
    return static_cache_count

def run_django_clearcache():
    """تشغيل أمر clearcache من Django إذا كان متاحًا"""
    logging.info("محاولة تنظيف ذاكرة التخزين المؤقت باستخدام أمر Django...")
    try:
        import subprocess
        result = subprocess.run(['python', 'manage.py', 'clearcache'], 
                                capture_output=True, text=True)
        
        if result.returncode == 0:
            logging.info("تم تنظيف ذاكرة التخزين المؤقت بنجاح باستخدام أمر Django")
            logging.info(result.stdout)
        else:
            logging.warning("فشل تنظيف ذاكرة التخزين المؤقت باستخدام أمر Django")
            logging.warning(result.stderr)
    except Exception as e:
        logging.error(f"خطأ في تنفيذ أمر clearcache من Django: {e}")

def main():
    """الدالة الرئيسية لتنفيذ جميع عمليات التنظيف"""
    start_time = time.time()
    logging.info("بدء عملية التنظيف الشاملة للكاش...")
    
    # تنفيذ جميع وظائف التنظيف
    pycache_count, pyc_count = clean_pycache()
    template_count = update_cache_busters()
    temp_count = clean_temp_files()
    log_count = clean_old_logs()
    static_cache_count = clean_static_cache()
    
    # محاولة تنظيف ذاكرة التخزين المؤقت الخاصة بـ Django
    try:
        run_django_clearcache()
    except Exception as e:
        logging.warning(f"تم تجاهل خطأ في أمر Django clearcache: {e}")
    
    # حساب إجمالي الملفات التي تم تنظيفها
    total_files = pycache_count + pyc_count + template_count + temp_count + log_count + static_cache_count
    
    # حساب الوقت المستغرق
    end_time = time.time()
    duration = end_time - start_time
    
    # طباعة ملخص التنظيف
    logging.info("\n==== ملخص التنظيف الشامل ====")
    logging.info(f"إجمالي الملفات التي تم تنظيفها: {total_files}")
    logging.info(f"الوقت المستغرق: {duration:.2f} ثانية")
    logging.info(f"تاريخ ووقت التنظيف: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    logging.info("============================\n")
    
    print("\n✨✨✨ تم الانتهاء من التنظيف الشامل للكاش بنجاح! ✨✨✨")
    print(f"تم تنظيف {total_files} ملف في {duration:.2f} ثانية.")

if __name__ == "__main__":
    main()