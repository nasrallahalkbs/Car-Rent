"""
التحقق من جدول صلاحيات المشرفين في قاعدة البيانات وإصلاحه
"""

import os
import sqlite3
import json

def check_admin_permission_table():
    """
    التحقق من وجود جدول rental_adminpermission وإنشائه إذا لم يكن موجودًا
    """
    print("التحقق من جدول صلاحيات المشرفين...")
    
    # الاتصال بقاعدة البيانات
    conn = sqlite3.connect('db.sqlite3')
    c = conn.cursor()

    # التحقق من وجود الجدول
    c.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='rental_adminpermission'")
    if not c.fetchone():
        print("جدول rental_adminpermission غير موجود! سيتم إنشاؤه...")
        
        # إنشاء الجدول إذا لم يكن موجودًا
        c.execute('''
        CREATE TABLE rental_adminpermission (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            admin_id INTEGER NOT NULL,
            permissions TEXT NOT NULL,
            UNIQUE(admin_id)
        )
        ''')
        print("✅ تم إنشاء جدول rental_adminpermission")
    else:
        print("✅ جدول rental_adminpermission موجود بالفعل")
    
    # التحقق من وجود سجلات
    c.execute("SELECT COUNT(*) FROM rental_adminpermission")
    count = c.fetchone()[0]
    print(f"عدد السجلات الموجودة في الجدول: {count}")
    
    # عرض السجلات الموجودة
    if count > 0:
        c.execute("SELECT admin_id, permissions FROM rental_adminpermission")
        rows = c.fetchall()
        
        print("السجلات الموجودة:")
        for row in rows:
            admin_id = row[0]
            permissions_json = row[1]
            
            try:
                permissions = json.loads(permissions_json)
                perm_count = sum(len(perms) for perms in permissions.values())
                print(f"- المشرف {admin_id}: {perm_count} صلاحية")
            except json.JSONDecodeError:
                print(f"- المشرف {admin_id}: [خطأ في تنسيق JSON]")
    
    # حفظ التغييرات وإغلاق الاتصال
    conn.commit()
    conn.close()
    print("تم التحقق من جدول صلاحيات المشرفين بنجاح.")

def add_test_permission():
    """
    إضافة صلاحيات اختبارية للمسؤول رقم 2
    """
    admin_id = 2
    
    # صلاحيات اختبارية
    permissions = {
        'dashboard': ['view_dashboard', 'view_calendar', 'customize_dashboard'],
        'reservations': ['view_reservations', 'edit_reservations', 'create_reservations'],
        'customers': ['view_customers', 'edit_customers', 'create_customers'],
        'vehicles': ['view_vehicles', 'edit_vehicles', 'create_vehicles'],
        'payments': ['view_payments', 'edit_payments'],
        'archive': ['view_archive'],
        'repairs': ['view_repairs', 'edit_repairs'],
        'reports': ['view_reports'],
        'dashboard_analytics': ['view_dashboard_analytics'],
        'settings': ['view_settings'],
        'reviews': ['view_reviews', 'edit_reviews'],
        'backup': ['create_backup']
    }
    
    permissions_json = json.dumps(permissions)
    
    # الاتصال بقاعدة البيانات
    conn = sqlite3.connect('db.sqlite3')
    c = conn.cursor()
    
    # حذف السجل الموجود للمسؤول رقم 2 إن وجد
    c.execute("DELETE FROM rental_adminpermission WHERE admin_id = ?", (admin_id,))
    
    # إضافة السجل الجديد
    c.execute("INSERT INTO rental_adminpermission (admin_id, permissions) VALUES (?, ?)", 
              (admin_id, permissions_json))
    
    # التأكد من الإضافة
    c.execute("SELECT permissions FROM rental_adminpermission WHERE admin_id = ?", (admin_id,))
    result = c.fetchone()
    if result:
        print(f"✅ تمت إضافة صلاحيات اختبارية للمسؤول رقم {admin_id}")
        print(f"محتوى السجل: {result[0][:50]}...")
    else:
        print(f"❌ فشلت إضافة صلاحيات للمسؤول رقم {admin_id}")
    
    # حفظ التغييرات وإغلاق الاتصال
    conn.commit()
    conn.close()

if __name__ == "__main__":
    # التحقق من جدول الصلاحيات
    check_admin_permission_table()
    
    # إضافة صلاحيات اختبارية للمسؤول رقم 2
    add_test_permission()