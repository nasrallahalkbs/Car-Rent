# -*- coding: utf-8 -*-
from django.db import migrations, models
import django.db.models.deletion
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('rental', '0001_initial'),  # تأكد من تغيير هذا إلى آخر ترحيل موجود
    ]

    operations = [
        migrations.CreateModel(
            name='Backup',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, verbose_name='الاسم')),
                ('description', models.TextField(blank=True, null=True, verbose_name='الوصف')),
                ('backup_type', models.CharField(choices=[('full', 'كامل'), ('partial', 'جزئي'), ('settings', 'الإعدادات فقط'), ('database', 'قاعدة البيانات فقط')], default='full', max_length=20, verbose_name='نوع النسخة الاحتياطية')),
                ('file_path', models.CharField(blank=True, max_length=255, null=True, verbose_name='مسار الملف')),
                ('size', models.BigIntegerField(default=0, verbose_name='الحجم (بايت)')),
                ('status', models.CharField(choices=[('pending', 'قيد الانتظار'), ('in_progress', 'قيد التنفيذ'), ('completed', 'مكتمل'), ('failed', 'فشل')], default='pending', max_length=20, verbose_name='الحالة')),
                ('include_media', models.BooleanField(default=True, verbose_name='تضمين الوسائط')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='تاريخ الإنشاء')),
                ('completed_at', models.DateTimeField(blank=True, null=True, verbose_name='تاريخ الاكتمال')),
                ('created_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='created_backups', to=settings.AUTH_USER_MODEL, verbose_name='بواسطة')),
            ],
            options={
                'verbose_name': 'نسخة احتياطية',
                'verbose_name_plural': 'النسخ الاحتياطية',
                'ordering': ['-created_at'],
            },
        ),
    ]