#!/usr/bin/env python3
"""
هذا السكريبت يقوم بتوحيد تنسيقات الثيم في التطبيق لضمان تجربة مستخدم متناسقة
"""

import re
import os

def update_layout_html():
    """تحديث ملف layout.html لتوحيد تنسيقات الثيم والألوان"""
    with open('templates/layout.html', 'r', encoding='utf-8') as file:
        content = file.read()
    
    # توحيد ألوان الثيم الأساسية
    updated_content = re.sub(
        r'background-color: #007bff;',
        r'background-color: #3a86ff;',
        content
    )
    
    # توحيد نمط CSS للهيدر
    style_section = """
    <style>
        :root {
            --primary-color: #3a86ff;
            --secondary-color: #334155;
            --accent-color: #4dabf7;
            --light-bg: #f8f9fa;
            --dark-bg: #121212;
            --dark-surface: #1e1e1e;
            --border-radius: 8px;
            --box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
        }
        
        body {
            font-family: {{ font_family }};
            background-color: var(--light-bg);
            color: #333;
        }
        
        body[data-theme="dark"] {
            background-color: var(--dark-bg);
            color: #e0e0e0;
        }
        
        .navbar {
            box-shadow: var(--box-shadow);
            background-color: white;
        }
        
        body[data-theme="dark"] .navbar {
            background-color: var(--dark-surface) !important;
        }
        
        .navbar .navbar-nav {
            {% if is_arabic %}margin-right: auto !important;{% else %}margin-left: auto !important;{% endif %}
        }
        
        .title-border {
            width: 80px;
            height: 4px;
            background: linear-gradient(90deg, var(--primary-color), var(--accent-color));
            margin-top: 10px;
            margin-bottom: 30px;
            border-radius: 2px;
        }
        
        .btn-primary {
            background-color: var(--primary-color);
            border-color: var(--primary-color);
        }
        
        .btn-primary:hover {
            background-color: #2875e6;
            border-color: #2875e6;
        }
        
        .text-primary {
            color: var(--primary-color) !important;
        }
    </style>
    """
    
    # استبدال قسم CSS الحالي بالقسم الجديد
    updated_content = re.sub(
        r'<style>.*?</style>',
        style_section,
        updated_content,
        flags=re.DOTALL
    )
    
    with open('templates/layout.html', 'w', encoding='utf-8') as file:
        file.write(updated_content)
    
    print("تم تحديث layout.html")

def update_layout_django_html():
    """تحديث ملف layout_django.html لتوحيد تنسيقات الثيم والألوان"""
    with open('templates/layout_django.html', 'r', encoding='utf-8') as file:
        content = file.read()
    
    # توحيد نمط CSS للهيدر
    style_section = """
    <style>
        :root {
            --primary-color: #3a86ff;
            --secondary-color: #334155;
            --accent-color: #4dabf7;
            --light-bg: #f8f9fa;
            --dark-bg: #121212;
            --dark-surface: #1e1e1e;
            --border-radius: 8px;
            --box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
        }
        
        body {
            font-family: {% if is_english %}'Poppins'{% else %}'Tajawal'{% endif %}, sans-serif;
            background-color: var(--light-bg);
            color: #333;
        }
        
        body.dark-mode {
            background-color: var(--dark-bg);
            color: #e0e0e0;
        }
        
        .navbar {
            box-shadow: var(--box-shadow);
        }
        
        body.dark-mode .navbar {
            background-color: var(--dark-surface) !important;
        }
        
        .btn-primary {
            background-color: var(--primary-color);
            border-color: var(--primary-color);
        }
        
        .btn-primary:hover {
            background-color: #2875e6;
            border-color: #2875e6;
        }
        
        .text-primary {
            color: var(--primary-color) !important;
        }
    </style>
    """
    
    # استبدال قسم CSS الحالي بالقسم الجديد
    updated_content = re.sub(
        r'<style>.*?</style>',
        style_section,
        content,
        flags=re.DOTALL
    )
    
    with open('templates/layout_django.html', 'w', encoding='utf-8') as file:
        file.write(updated_content)
    
    print("تم تحديث layout_django.html")

def update_theme_colors_css():
    """إنشاء ملف CSS متغيرات الألوان المشتركة"""
    css_content = """/* Unified Theme Colors and Variables */
:root {
    --primary-color: #3a86ff;
    --primary-hover: #2875e6;
    --secondary-color: #334155;
    --accent-color: #4dabf7;
    --success-color: #28a745;
    --warning-color: #ffc107;
    --danger-color: #dc3545;
    --info-color: #17a2b8;
    
    --light-bg: #f8f9fa;
    --dark-bg: #121212;
    --dark-surface: #1e1e1e;
    --dark-border: #3d3d3d;
    
    --text-dark: #212529;
    --text-muted: #6c757d;
    --text-light: #e0e0e0;
    
    --border-radius: 8px;
    --border-radius-lg: 10px;
    --border-radius-sm: 5px;
    --box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
    --box-shadow-hover: 0 8px 24px rgba(0, 0, 0, 0.12);
}

/* Color classes */
.bg-primary {
    background-color: var(--primary-color) !important;
}

.text-primary {
    color: var(--primary-color) !important;
}

.border-primary {
    border-color: var(--primary-color) !important;
}

/* Button Styles */
.btn-primary {
    background-color: var(--primary-color);
    border-color: var(--primary-color);
}

.btn-primary:hover {
    background-color: var(--primary-hover);
    border-color: var(--primary-hover);
}

.btn-outline-primary {
    color: var(--primary-color);
    border-color: var(--primary-color);
}

.btn-outline-primary:hover {
    background-color: var(--primary-color);
    border-color: var(--primary-color);
}

/* Card Styles */
.card {
    border-radius: var(--border-radius);
    box-shadow: var(--box-shadow);
    transition: all 0.3s ease;
    border: none;
}

.card:hover {
    box-shadow: var(--box-shadow-hover);
}

/* Gradient Effects */
.gradient-primary {
    background: linear-gradient(135deg, var(--primary-color) 0%, var(--accent-color) 100%);
}

/* Dark Mode Support */
body.dark-mode, body[data-theme="dark"] {
    background-color: var(--dark-bg);
    color: var(--text-light);
}

body.dark-mode .card, body[data-theme="dark"] .card {
    background-color: var(--dark-surface);
    border-color: var(--dark-border);
}

body.dark-mode .text-dark, body[data-theme="dark"] .text-dark {
    color: var(--text-light) !important;
}

body.dark-mode .text-muted, body[data-theme="dark"] .text-muted {
    color: #a0a0a0 !important;
}
"""
    
    # إنشاء الملف الجديد
    with open('static/css/theme-variables.css', 'w', encoding='utf-8') as file:
        file.write(css_content)
    
    print("تم إنشاء ملف متغيرات الثيم theme-variables.css")
    
    # تحديث style.css لاستخدام المتغيرات
    with open('static/css/style.css', 'r', encoding='utf-8') as file:
        style_content = file.read()
    
    # إضافة استيراد ملف المتغيرات في بداية ملف style.css
    if '@import url' in style_content:
        updated_style = re.sub(
            r'(@import url.*?;(\n|$))+',
            r'\g<0>@import url("theme-variables.css");\n',
            style_content
        )
    else:
        updated_style = '@import url("theme-variables.css");\n' + style_content
    
    # كتابة المحتوى المحدث
    with open('static/css/style.css', 'w', encoding='utf-8') as file:
        file.write(updated_style)
    
    print("تم تحديث style.css للاستفادة من متغيرات الثيم")

def update_dark_mode_css():
    """تحديث ملف dark-mode.css لاستخدام متغيرات الثيم"""
    with open('static/css/dark-mode.css', 'r', encoding='utf-8') as file:
        content = file.read()
    
    # تحديث المتغيرات في الملف
    updated_content = content.replace(
        'background-color: #121212;',
        'background-color: var(--dark-bg);'
    ).replace(
        'background-color: #1e1e1e',
        'background-color: var(--dark-surface)'
    ).replace(
        'border-color: #3d3d3d',
        'border-color: var(--dark-border)'
    )
    
    with open('static/css/dark-mode.css', 'w', encoding='utf-8') as file:
        file.write(updated_content)
    
    print("تم تحديث dark-mode.css للاستفادة من متغيرات الثيم")

def main():
    """تنفيذ الدالة الرئيسية للسكريبت"""
    # تأكد من وجود المجلدات المطلوبة
    if not os.path.exists('static/css'):
        os.makedirs('static/css')
    
    # تحديث ملفات القوالب
    update_layout_html()
    update_layout_django_html()
    
    # إنشاء وتحديث ملفات CSS
    update_theme_colors_css()
    update_dark_mode_css()
    
    print("تم توحيد تنسيقات الثيم بنجاح!")

if __name__ == "__main__":
    main()
