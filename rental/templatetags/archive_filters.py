from django import template

register = template.Library()

@register.filter
def endswith(value, arg):
    """
    فلتر قالب للتحقق مما إذا كانت السلسلة تنتهي بقيمة معينة
    مثال استخدام:
    {{ file_name|endswith:'.pdf' }}
    """
    if value is None:
        return False
    return str(value).lower().endswith(str(arg).lower())

@register.filter
def file_icon_class(filename):
    """
    تحديد صنف أيقونة الملف بناءً على امتداده
    """
    if not filename:
        return "file"  # الامتداد الافتراضي
    
    filename = str(filename).lower()
    
    if filename.endswith('.pdf'):
        return "pdf"
    elif filename.endswith('.doc') or filename.endswith('.docx'):
        return "doc"
    elif filename.endswith('.xls') or filename.endswith('.xlsx'):
        return "xls"
    elif any(filename.endswith(ext) for ext in ['.jpg', '.jpeg', '.png', '.gif', '.bmp']):
        return "img"
    elif filename.endswith('.zip') or filename.endswith('.rar'):
        return "zip"
    else:
        return "file"

@register.filter
def file_icon_fa(filename):
    """
    تحديد فئة أيقونة Font Awesome بناءً على امتداد الملف
    """
    if not filename:
        return "fa-file"  # الأيقونة الافتراضية
    
    filename = str(filename).lower()
    
    if filename.endswith('.pdf'):
        return "fa-file-pdf"
    elif filename.endswith('.doc') or filename.endswith('.docx'):
        return "fa-file-word"
    elif filename.endswith('.xls') or filename.endswith('.xlsx'):
        return "fa-file-excel"
    elif any(filename.endswith(ext) for ext in ['.jpg', '.jpeg', '.png', '.gif', '.bmp']):
        return "fa-file-image"
    elif filename.endswith('.zip') or filename.endswith('.rar'):
        return "fa-file-archive"
    else:
        return "fa-file"