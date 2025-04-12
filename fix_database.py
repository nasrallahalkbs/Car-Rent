#!/usr/bin/env python3
"""
سكريبت لإصلاح قاعدة البيانات وإضافة الأعمدة الناقصة
"""
import os
import sqlite3
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'car_rental_project.settings')
django.setup()

from django.db import connection

def add_missing_columns():
    """إضافة الأعمدة المفقودة في قاعدة البيانات"""
    print("بدء عملية إضافة الأعمدة المفقودة...")
    
    # الاتصال بقاعدة البيانات
    with connection.cursor() as cursor:
        # التحقق من وجود الأعمدة وإضافتها إذا كانت مفقودة
        try:
            # التحقق من عمود full_name
            cursor.execute("SELECT full_name FROM rental_reservation LIMIT 1")
        except:
            print("إضافة عمود full_name...")
            cursor.execute("ALTER TABLE rental_reservation ADD COLUMN full_name VARCHAR(100) NULL")
        
        try:
            # التحقق من عمود national_id
            cursor.execute("SELECT national_id FROM rental_reservation LIMIT 1")
        except:
            print("إضافة عمود national_id...")
            cursor.execute("ALTER TABLE rental_reservation ADD COLUMN national_id VARCHAR(20) NULL")
        
        try:
            # التحقق من عمود id_card_image
            cursor.execute("SELECT id_card_image FROM rental_reservation LIMIT 1")
        except:
            print("إضافة عمود id_card_image...")
            cursor.execute("ALTER TABLE rental_reservation ADD COLUMN id_card_image VARCHAR(255) NULL")
        
        try:
            # التحقق من عمود rental_type
            cursor.execute("SELECT rental_type FROM rental_reservation LIMIT 1")
        except:
            print("إضافة عمود rental_type...")
            cursor.execute("ALTER TABLE rental_reservation ADD COLUMN rental_type VARCHAR(20) NULL")
        
        try:
            # التحقق من عمود guarantee_type
            cursor.execute("SELECT guarantee_type FROM rental_reservation LIMIT 1")
        except:
            print("إضافة عمود guarantee_type...")
            cursor.execute("ALTER TABLE rental_reservation ADD COLUMN guarantee_type VARCHAR(20) NULL")
        
        try:
            # التحقق من عمود guarantee_details
            cursor.execute("SELECT guarantee_details FROM rental_reservation LIMIT 1")
        except:
            print("إضافة عمود guarantee_details...")
            cursor.execute("ALTER TABLE rental_reservation ADD COLUMN guarantee_details TEXT NULL")
        
        try:
            # التحقق من عمود booking_date
            cursor.execute("SELECT booking_date FROM rental_reservation LIMIT 1")
        except:
            print("إضافة عمود booking_date...")
            cursor.execute("ALTER TABLE rental_reservation ADD COLUMN booking_date TIMESTAMP NULL")
        
        try:
            # التحقق من عمود deposit_amount
            cursor.execute("SELECT deposit_amount FROM rental_reservation LIMIT 1")
        except:
            print("إضافة عمود deposit_amount...")
            cursor.execute("ALTER TABLE rental_reservation ADD COLUMN deposit_amount DECIMAL(10, 2) NULL")
    
    print("تم إضافة جميع الأعمدة المفقودة بنجاح.")

if __name__ == "__main__":
    add_missing_columns()