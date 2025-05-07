"""
إنشاء جدول AdminPermission في قاعدة البيانات لتخزين الصلاحيات المتقدمة للمسؤولين.

يقوم هذا السكريبت بإنشاء جدول rental_adminpermission في قاعدة البيانات SQLite 
لتخزين صلاحيات المسؤولين المخصصة.
"""

import os
import django
import sys
import json

# إعداد بيئة جانغو قبل استيراد النماذج
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'car_rental_project.settings')
django.setup()

def create_admin_permission_table():
    """
    إنشاء جدول AdminPermission لتخزين صلاحيات المسؤولين المتقدمة
    """
    from django.db import connection

    # التحقق من وجود الجدول
    with connection.cursor() as cursor:
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='rental_adminpermission';")
        if cursor.fetchone():
            print("جدول rental_adminpermission موجود مسبقًا.")
            return

    # إنشاء الجدول إذا لم يكن موجودًا
    with connection.cursor() as cursor:
        cursor.execute("""
        CREATE TABLE rental_adminpermission (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            admin_id INTEGER NOT NULL,
            permissions TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (admin_id) REFERENCES rental_adminuser(id)
        );
        """)
        print("تم إنشاء جدول rental_adminpermission بنجاح.")

def create_model_in_models_py():
    """
    إضافة نموذج AdminPermission إلى ملف models.py
    """
    model_definition = """

class AdminPermission(models.Model):
    # إدارة الصلاحيات المتقدمة للمسؤولين
    admin = models.OneToOneField(AdminUser, on_delete=models.CASCADE, related_name='admin_permissions')
    permissions = models.TextField(null=True, blank=True)  # JSON سيتم تخزين الصلاحيات بتنسيق
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def set_permissions(self, permissions_dict):
        # تعيين الصلاحيات كقاموس وتخزينها كسلسلة JSON
        self.permissions = json.dumps(permissions_dict)
        
    def get_permissions(self):
        # استرجاع الصلاحيات كقاموس من سلسلة JSON
        if self.permissions:
            return json.loads(self.permissions)
        return {}
        
    def __str__(self):
        return f"صلاحيات المسؤول {self.admin.user.username}"
"""

    # التحقق من وجود النموذج في ملف models.py
    models_file_path = './rental/models.py'
    with open(models_file_path, 'r', encoding='utf-8') as file:
        file_content = file.read()
        if 'class AdminPermission' in file_content:
            print("نموذج AdminPermission موجود مسبقًا في ملف models.py.")
            return

    # إضافة نموذج AdminPermission إلى ملف models.py
    with open(models_file_path, 'a', encoding='utf-8') as file:
        file.write(model_definition)
        print("تم إضافة نموذج AdminPermission إلى ملف models.py بنجاح.")

def update_superadmin_views():
    """
    تحديث دالة admin_advanced_permissions في ملف superadmin_views.py لاستخدام القالب الجديد
    """
    views_file_path = './rental/superadmin_views.py'
    
    # قراءة محتوى الملف
    with open(views_file_path, 'r', encoding='utf-8') as file:
        content = file.read()
    
    # تعديل سطر استدعاء القالب
    updated_content = content.replace(
        "return render(request, 'superadmin/admin_advanced_permissions_redesign.html', context)",
        "return render(request, 'superadmin/admin_permissions_dynamic.html', context)"
    )
    
    # كتابة المحتوى المحدث
    with open(views_file_path, 'w', encoding='utf-8') as file:
        file.write(updated_content)
        print("تم تحديث ملف superadmin_views.py لاستخدام القالب الجديد.")

if __name__ == '__main__':
    create_admin_permission_table()
    create_model_in_models_py()
    update_superadmin_views()
    print("تم إنشاء وتكوين جدول الصلاحيات المتقدمة بنجاح!")