"""
إنشاء سجلات نشاط للمسؤولين العاديين بطريقة مبسطة باستخدام SQL مباشرة
"""
import sqlite3
import random
import datetime
import time
from datetime import timedelta

# اتصال بقاعدة البيانات
conn = sqlite3.connect('db.sqlite3')
cursor = conn.cursor()

# الحصول على معلومات المسؤولين
print("جاري التحقق من المسؤولين...")
cursor.execute("""
    SELECT au.id, u.username, au.is_superadmin
    FROM rental_adminuser au
    JOIN rental_user u ON au.user_id = u.id
""")
admins = cursor.fetchall()

print(f"إجمالي عدد المسؤولين: {len(admins)}")
for admin in admins:
    print(f"المسؤول: {admin[1]} (ID: {admin[0]}) | مشرف أعلى: {admin[2]}")

# البحث عن مسؤول غير مشرف أعلى
regular_admins = [admin for admin in admins if admin[2] == 0]

# إذا لم يوجد مسؤولين عاديين، أنشئ واحداً
if not regular_admins:
    print("لا يوجد مسؤولين عاديين. جاري إنشاء مسؤول عادي...")
    
    # البحث عن دور
    cursor.execute("SELECT id FROM rental_role LIMIT 1")
    role = cursor.fetchone()
    
    role_id = role[0] if role else None
    
    # إذا لم يكن هناك دور، أنشئ واحداً
    if not role_id:
        print("إنشاء دور جديد...")
        cursor.execute("""
            INSERT INTO rental_role (name, description, created_at, updated_at)
            VALUES ('مسؤول المبيعات', 'دور مسؤول المبيعات والحجوزات', datetime('now'), datetime('now'))
        """)
        conn.commit()
        
        cursor.execute("SELECT last_insert_rowid()")
        role_id = cursor.fetchone()[0]
    
    # إنشاء مستخدم جديد
    cursor.execute("""
        INSERT INTO rental_user 
        (username, email, first_name, last_name, password, is_staff, is_active, date_joined, is_admin, is_superuser)
        VALUES 
        ('admin_regular', 'admin_regular@example.com', 'مسؤول', 'عادي', 
        'pbkdf2_sha256$600000$hOm9YH2hIwRsfLGJuEOFSr$GZT88yZl1fJtGsXprzuRRklQ46wp0zyCKp8G3MyQeyU=', 
        1, 1, datetime('now'), 0, 0)
    """)
    conn.commit()
    
    # الحصول على معرف المستخدم المنشأ
    cursor.execute("SELECT last_insert_rowid()")
    user_id = cursor.fetchone()[0]
    
    # إنشاء ملف المسؤول
    cursor.execute("""
        INSERT INTO rental_adminuser 
        (user_id, role_id, is_superadmin, last_login_ip, is_deleted, notes, created_at, updated_at)
        VALUES (?, ?, 0, '127.0.0.1', 0, 'مسؤول عادي تم إنشاؤه للاختبار', datetime('now'), datetime('now'))
    """, [user_id, role_id])
    conn.commit()
    
    # الحصول على معرف المسؤول المنشأ
    cursor.execute("SELECT id FROM rental_adminuser WHERE user_id = ?", [user_id])
    admin_id = cursor.fetchone()[0]
    
    regular_admins = [(admin_id, 'admin_regular', 0)]

print(f"المسؤولين العاديين: {len(regular_admins)}")
for admin in regular_admins:
    print(f"المسؤول العادي: {admin[1]} (ID: {admin[0]})")

# إنشاء سجلات نشاط للمسؤولين العاديين
actions = [
    "تسجيل دخول",
    "تعديل حجز",
    "إضافة حجز", 
    "إلغاء حجز",
    "عرض تقرير",
    "تصدير بيانات",
    "تحديث معلومات عميل"
]

details_templates = [
    "تم {} للعميل",
    "قام المسؤول ب{}",
    "{} للعميل رقم {}",
    "{} للسيارة رقم {}"
]

logs_created = 0

# إنشاء سجلات لكل مسؤول عادي
for admin_id, username, _ in regular_admins:
    print(f"إنشاء سجلات للمسؤول: {username} (ID: {admin_id})")
    
    # إنشاء 20 سجل نشاط لكل مسؤول
    for i in range(20):
        # اختيار نوع النشاط
        action = random.choice(actions)
        
        # إنشاء تفاصيل النشاط
        detail_template = random.choice(details_templates)
        
        if "{}" in detail_template:
            if detail_template.count("{}") == 1:
                details = detail_template.format(action.lower())
            else:
                if "عميل" in detail_template:
                    details = detail_template.format(action.lower(), random.randint(1000, 9999))
                else:
                    details = detail_template.format(action.lower(), random.randint(100, 999))
        else:
            details = detail_template
        
        # إنشاء تاريخ عشوائي في آخر 30 يوم
        days_ago = random.randint(0, 30)
        hours_ago = random.randint(0, 23)
        minutes_ago = random.randint(0, 59)
        
        now = datetime.datetime.now()
        created_at = now - timedelta(days=days_ago, hours=hours_ago, minutes=minutes_ago)
        created_at_str = created_at.strftime("%Y-%m-%d %H:%M:%S")
        
        # إنشاء عنوان IP عشوائي
        ip_address = f"192.168.1.{random.randint(2, 254)}"
        
        # إنشاء معرف العنصر المتأثر (إن وجد)
        affected_item_type = random.choice([None, "reservation", "car", "customer"]) if random.random() > 0.3 else None
        affected_item_id = random.randint(1, 1000) if affected_item_type else None
        
        # إدراج السجل في قاعدة البيانات
        cursor.execute("""
            INSERT INTO rental_adminactivity 
            (admin_id, action, details, ip_address, created_at, is_hidden, affected_item_type, affected_item_id)
            VALUES (?, ?, ?, ?, ?, 0, ?, ?)
        """, [admin_id, action, details, ip_address, created_at_str, affected_item_type, affected_item_id])
        
        logs_created += 1
    
    # التزام بالتغييرات بعد كل مسؤول
    conn.commit()

print(f"تم إنشاء {logs_created} سجل نشاط للمسؤولين العاديين بنجاح")

# إغلاق الاتصال بقاعدة البيانات
conn.close()