# Generated by Django 5.2 on 2025-04-21 17:46

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('rental', '0009_sitesettings_document'),
    ]

    operations = [
        migrations.CreateModel(
            name='ArchiveFolder',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255, verbose_name='اسم المجلد')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='تاريخ الإنشاء')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='تاريخ التحديث')),
                ('description', models.TextField(blank=True, null=True, verbose_name='وصف المجلد')),
                ('is_system_folder', models.BooleanField(default=False, help_text='إذا كان هذا مجلد نظام (يتم إنشاؤه تلقائيًا)', verbose_name='مجلد نظام')),
                ('folder_type', models.CharField(blank=True, help_text='نوع المجلد (مثل حجوزات، سيارات، ...إلخ)', max_length=50, null=True, verbose_name='نوع المجلد')),
                ('created_by', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='created_folders', to=settings.AUTH_USER_MODEL, verbose_name='أنشئ بواسطة')),
                ('parent', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='children', to='rental.archivefolder', verbose_name='المجلد الأب')),
            ],
            options={
                'verbose_name': 'مجلد أرشيف',
                'verbose_name_plural': 'مجلدات الأرشيف',
                'ordering': ['name'],
                'unique_together': {('parent', 'name')},
            },
        ),
        migrations.AddField(
            model_name='document',
            name='folder',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='documents', to='rental.archivefolder', verbose_name='المجلد'),
        ),
    ]
