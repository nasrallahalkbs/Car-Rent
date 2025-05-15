"""
إصلاح مشكلة اختفاء التنسيقات في صفحة إدارة التقارير عند الخروج من الصفحة

هذا السكريبت يقوم بالتالي:
1. التأكد من وجود ملف reports_management.css في مجلد staticfiles
2. تحديث ملف CSS بتاريخ ثابت بدلاً من timestamp متغير
3. إضافة كود في قالب إدارة التقارير للتأكد من تحميل CSS حتى بعد الخروج من الصفحة
"""

import os
import shutil
import time
import re
from pathlib import Path

def ensure_static_files():
    """التأكد من وجود ملفات CSS في مجلد staticfiles"""
    # مسارات الملفات
    static_css_path = "static/css/reports_management.css"
    staticfiles_css_path = "staticfiles/css/reports_management.css"
    
    # التأكد من وجود مجلد staticfiles/css
    os.makedirs(os.path.dirname(staticfiles_css_path), exist_ok=True)
    
    # نسخ ملف CSS إلى مجلد staticfiles إذا كان موجوداً
    if os.path.exists(static_css_path):
        print(f"جاري نسخ {static_css_path} إلى {staticfiles_css_path}")
        shutil.copy2(static_css_path, staticfiles_css_path)
    else:
        print(f"تحذير: ملف {static_css_path} غير موجود")

def update_cache_buster():
    """تحديث CACHE_BUSTER في قالب التقارير"""
    template_path = "templates/admin/reports/reports_management.html"
    
    if not os.path.exists(template_path):
        print(f"تحذير: ملف القالب {template_path} غير موجود")
        return
    
    with open(template_path, 'r', encoding='utf-8') as file:
        content = file.read()
    
    # تحديث CACHE_BUSTER بتاريخ ثابت
    today = time.strftime("%Y%m%d")
    pattern = r'<!-- CACHE_BUSTER \d+ -->'
    replacement = f'<!-- CACHE_BUSTER {today} -->'
    
    if re.search(pattern, content):
        new_content = re.sub(pattern, replacement, content)
        
        with open(template_path, 'w', encoding='utf-8') as file:
            file.write(new_content)
        
        print(f"تم تحديث CACHE_BUSTER في {template_path}")
    else:
        print(f"لم يتم العثور على CACHE_BUSTER في {template_path}")

def add_css_loading_script():
    """إضافة سكريبت للتأكد من تحميل ملف CSS حتى بعد الخروج من الصفحة"""
    # تم تنفيذه بالفعل في التغيير السابق
    print("تم بالفعل إضافة سكريبت تحميل CSS في القالب")

def add_css_integrity_check():
    """إضافة كود JavaScript للتحقق من سلامة ملف CSS"""
    js_path = "static/js/reports_css_check.js"
    
    script_content = """
// سكريبت للتحقق من تحميل CSS صفحة إدارة التقارير
document.addEventListener('DOMContentLoaded', function() {
    // التحقق مما إذا كانت صفحة إدارة التقارير
    if (window.location.href.includes('/admin/reports/') || 
        document.getElementById('reports-css')) {
        
        // التحقق من وجود تنسيقات CSS الأساسية
        const checkStyles = function() {
            // اختبار ما إذا كانت التنسيقات الأساسية موجودة
            const testElement = document.querySelector('.reports-container');
            
            if (testElement) {
                const styles = window.getComputedStyle(testElement);
                const hasStyles = styles.backgroundColor !== 'rgba(0, 0, 0, 0)' && 
                                 styles.backgroundColor !== 'transparent';
                
                if (!hasStyles) {
                    console.log('تنسيقات صفحة إدارة التقارير غير محملة بشكل صحيح، جاري إعادة تحميلها...');
                    reloadStyles();
                } else {
                    console.log('تنسيقات صفحة إدارة التقارير محملة بشكل صحيح');
                    // تخزين معلومات في localStorage للتحقق في المرات القادمة
                    localStorage.setItem('reports_css_loaded', 'true');
                }
            }
        };
        
        // إعادة تحميل التنسيقات
        const reloadStyles = function() {
            const cssLink = document.createElement('link');
            cssLink.rel = 'stylesheet';
            cssLink.href = '/static/css/reports_management.css?v=' + Date.now();
            document.head.appendChild(cssLink);
            
            // تحقق مرة أخرى بعد التحميل
            cssLink.onload = function() {
                setTimeout(checkStyles, 300);
            };
        };
        
        // التحقق بعد تحميل الصفحة
        setTimeout(checkStyles, 500);
    }
});
"""
    
    with open(js_path, 'w', encoding='utf-8') as file:
        file.write(script_content)
    
    print(f"تم إنشاء ملف {js_path} للتحقق من سلامة CSS")
    
    # إضافة السكريبت إلى قالب admin_layout.html
    template_path = "templates/admin/enhanced/admin_layout.html"
    if os.path.exists(template_path):
        with open(template_path, 'r', encoding='utf-8') as file:
            content = file.read()
        
        # التحقق من وجود السكريبت بالفعل
        if "reports_css_check.js" not in content:
            # البحث عن نهاية body
            pattern = r'</body>'
            replacement = f'<script src="{% static \'js/reports_css_check.js\' %}?v={time.strftime("%Y%m%d")}"></script>\n</body>'
            
            if pattern in content:
                new_content = content.replace(pattern, replacement)
                
                with open(template_path, 'w', encoding='utf-8') as file:
                    file.write(new_content)
                
                print(f"تم إضافة سكريبت التحقق من CSS إلى {template_path}")
            else:
                print(f"لم يتم العثور على وسم body في {template_path}")
        else:
            print(f"السكريبت موجود بالفعل في {template_path}")
    else:
        print(f"تحذير: ملف القالب {template_path} غير موجود")

def create_fix_css_script():
    """إنشاء سكريبت إضافي لإصلاح CSS عند الطلب"""
    script_path = "fix_reports_css.py"
    
    script_content = """#!/usr/bin/env python
\"\"\"
سكريبت بسيط لإصلاح مشكلة CSS في صفحة إدارة التقارير
يمكن تشغيل هذا السكريبت عند مواجهة مشكلة في تنسيقات الصفحة
\"\"\"

import os
import shutil
import time

def fix_css():
    \"\"\"إصلاح ملف CSS لصفحة إدارة التقارير\"\"\"
    # مسارات الملفات
    static_css_path = "static/css/reports_management.css"
    staticfiles_css_path = "staticfiles/css/reports_management.css"
    
    # التأكد من وجود مجلد staticfiles/css
    os.makedirs(os.path.dirname(staticfiles_css_path), exist_ok=True)
    
    # نسخ ملف CSS إلى مجلد staticfiles
    if os.path.exists(static_css_path):
        print(f"جاري نسخ {static_css_path} إلى {staticfiles_css_path}")
        shutil.copy2(static_css_path, staticfiles_css_path)
        print("تم إصلاح ملف CSS بنجاح")
    else:
        print(f"خطأ: ملف {static_css_path} غير موجود")
        return False
    
    # إضافة ملف فارغ للتأكد من تحديث staticfiles
    with open("staticfiles/css_fix_timestamp.txt", "w") as f:
        f.write(f"تم إصلاح CSS في {time.strftime('%Y-%m-%d %H:%M:%S')}")
    
    print("تم تنفيذ الإصلاح بنجاح")
    return True

if __name__ == "__main__":
    print("جاري إصلاح مشكلة CSS في صفحة إدارة التقارير...")
    if fix_css():
        print("تم الإصلاح بنجاح. يرجى تحديث الصفحة لتطبيق التغييرات.")
    else:
        print("فشل الإصلاح. يرجى التحقق من الملفات والمجلدات.")
"""
    
    with open(script_path, 'w', encoding='utf-8') as file:
        file.write(script_content)
    
    print(f"تم إنشاء سكريبت {script_path} لإصلاح CSS عند الطلب")

def main():
    """تنفيذ جميع خطوات الإصلاح"""
    print("جاري إصلاح مشكلة اختفاء التنسيقات في صفحة إدارة التقارير...")
    
    # خطوات الإصلاح
    ensure_static_files()
    update_cache_buster()
    add_css_loading_script()
    add_css_integrity_check()
    create_fix_css_script()
    
    print("تم تنفيذ الإصلاح بنجاح!")
    print("ملاحظة: يمكن تشغيل سكريبت fix_reports_css.py في أي وقت لإصلاح مشكلة CSS إذا ظهرت مرة أخرى.")

if __name__ == "__main__":
    main()