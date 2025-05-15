#!/usr/bin/env python
"""
سكريبت بسيط لإصلاح مشكلة CSS في صفحة إدارة التقارير
يمكن تشغيل هذا السكريبت عند مواجهة مشكلة في تنسيقات الصفحة
"""

import os
import shutil
import time

def fix_css():
    """إصلاح ملف CSS لصفحة إدارة التقارير"""
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