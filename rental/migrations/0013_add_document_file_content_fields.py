"""
تسجيل حقول تخزين محتوى الملفات التي تم إضافتها بالفعل لقاعدة البيانات
"""
from django.db import migrations

class Migration(migrations.Migration):

    dependencies = [
        ('rental', '0012_merge_20250425_1616'),
    ]

    # هذه الحقول موجودة بالفعل في قاعدة البيانات
    # نحتاج فقط لتسجيل هذه الهجرة في جدول django_migrations
    operations = [
    ]