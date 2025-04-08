"""
إصلاح ملف admin_layout.html لدعم تغيير اللغة
"""

def fix_admin_layout():
    with open('templates/admin_layout.html', 'r') as file:
        content = file.read()
    
    # تحديث تعريف HTML
    content = content.replace(
        '<html lang="ar" dir="rtl">',
        '<html lang="{% if is_english %}en{% else %}ar{% endif %}" dir="{% if is_english %}ltr{% else %}rtl{% endif %}">'
    )
    
    # تحديث عنوان الصفحة
    content = content.replace(
        '<title>{% block title %}كاررنتال - لوحة التحكم{% endblock %}</title>',
        '<title>{% block title %}{% if is_english %}CarRental - Admin Dashboard{% else %}كاررنتال - لوحة التحكم{% endif %}{% endblock %}</title>'
    )
    
    # تحديث Bootstrap CSS ليكون متوافقًا مع اللغة
    content = content.replace(
        '<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.rtl.min.css">',
        '<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap{% if not is_english %}.rtl{% endif %}.min.css">'
    )
    
    # حفظ الملف بعد التحديث
    with open('templates/admin_layout.html', 'w') as file:
        file.write(content)
    
    print("تم تحديث ملف admin_layout.html لدعم تغيير اللغة.")

if __name__ == "__main__":
    fix_admin_layout()
