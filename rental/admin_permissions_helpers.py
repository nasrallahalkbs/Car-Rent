"""
مساعدات خاصة بإدارة الصلاحيات المتقدمة للمسؤولين
هذا الملف يحتوي على وظائف مساعدة للتعامل مع صلاحيات المسؤولين
"""

import json
import sqlite3
import logging
from django.utils.translation import gettext_lazy as _
from django.contrib import messages

# إعداد التسجيل
logger = logging.getLogger('django.request')

def get_admin_permissions(admin_id):
    """
    الحصول على صلاحيات المسؤول من قاعدة البيانات
    """
    admin_permissions = {}
    
    try:
        # الاتصال بقاعدة البيانات
        conn = sqlite3.connect('db.sqlite3')
        c = conn.cursor()
        
        # التحقق من جدول rental_adminpermission
        c.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='rental_adminpermission'")
        if not c.fetchone():
            # الجدول غير موجود، إرجاع صلاحيات فارغة
            conn.close()
            return admin_permissions
            
        # الحصول على الصلاحيات
        c.execute("SELECT permissions FROM rental_adminpermission WHERE admin_id = ?", (admin_id,))
        row = c.fetchone()
        
        if row:
            # تحويل JSON إلى قاموس
            try:
                admin_permissions = json.loads(row[0])
            except json.JSONDecodeError:
                logger.error(f"خطأ في تحويل JSON للصلاحيات لـ admin_id={admin_id}")
        
        conn.close()
    except Exception as e:
        logger.error(f"خطأ في الحصول على صلاحيات المسؤول: {e}")
    
    return admin_permissions

def save_admin_permissions(admin_id, selected_permissions, request=None):
    """
    حفظ صلاحيات المسؤول إلى قاعدة البيانات
    """
    try:
        # الاتصال بقاعدة البيانات مباشرة
        conn = sqlite3.connect('db.sqlite3')
        conn.isolation_level = None  # تمكين المعاملات اليدوية
        c = conn.cursor()
        
        try:
            # بدء المعاملة
            c.execute("BEGIN TRANSACTION")
            
            # التحقق من وجود الجدول
            c.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='rental_adminpermission'")
            if not c.fetchone():
                # إنشاء الجدول إذا لم يكن موجودًا
                c.execute('''
                CREATE TABLE rental_adminpermission (
                    id INTEGER PRIMARY KEY,
                    admin_id INTEGER,
                    permissions TEXT,
                    UNIQUE(admin_id)
                )
                ''')
                logger.info("تم إنشاء جدول rental_adminpermission")
            
            # التحقق مما إذا كان السجل موجودًا بالفعل
            c.execute("SELECT COUNT(*) FROM rental_adminpermission WHERE admin_id = ?", (admin_id,))
            exists = c.fetchone()[0] > 0
            
            permissions_json = json.dumps(selected_permissions)
            
            if exists:
                # تحديث السجل الموجود
                c.execute("UPDATE rental_adminpermission SET permissions = ? WHERE admin_id = ?", 
                        (permissions_json, admin_id))
                logger.info(f"تم تحديث صلاحيات المسؤول {admin_id}")
            else:
                # إنشاء سجل جديد
                c.execute("INSERT INTO rental_adminpermission (admin_id, permissions) VALUES (?, ?)", 
                        (admin_id, permissions_json))
                logger.info(f"تم إنشاء سجل جديد لصلاحيات المسؤول {admin_id}")
                
            # التأكيد على المعاملة
            c.execute("COMMIT")
            logger.info("تم تأكيد المعاملة بنجاح")
            
            if request:
                messages.success(request, _("تم حفظ الصلاحيات بنجاح"))
            
            return True
            
        except Exception as db_error:
            # إلغاء المعاملة في حالة حدوث أي خطأ
            c.execute("ROLLBACK")
            logger.error(f"خطأ في قاعدة البيانات: {db_error}")
            
            if request:
                messages.error(request, _("حدث خطأ أثناء حفظ الصلاحيات"))
            
            raise
        finally:
            # إغلاق الاتصال
            conn.close()
    except Exception as e:
        logger.error(f"خطأ في حفظ صلاحيات المسؤول: {e}")
        return False

def process_permissions_from_post(post_data):
    """
    معالجة البيانات المرسلة بواسطة طلب POST واستخراج الصلاحيات المحددة
    """
    selected_permissions = {}
    
    for key, value in post_data.items():
        # تخطي الحقول الخاصة
        if key in ['csrfmiddlewaretoken', 'admin_id', 'save_changes']:
            continue
            
        # معالجة حقول الصلاحيات
        if '_' in key:
            section, perm_name = key.split('_', 1)
            
            # تخطي الحقول الخاصة بالأقسام الفارغة
            if perm_name == 'empty':
                continue
                
            if section not in selected_permissions:
                selected_permissions[section] = []
                
            selected_permissions[section].append(perm_name)
    
    return selected_permissions