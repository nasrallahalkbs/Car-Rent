# Generated by Django 5.2 on 2025-05-09 23:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('rental', '0025_adminuser_current_job_adminuser_department_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='age',
            field=models.PositiveIntegerField(blank=True, null=True, verbose_name='العمر'),
        ),
        migrations.AddField(
            model_name='user',
            name='gender',
            field=models.CharField(blank=True, choices=[('male', 'ذكر'), ('female', 'أنثى')], max_length=10, null=True, verbose_name='النوع'),
        ),
        migrations.AddField(
            model_name='user',
            name='nationality',
            field=models.CharField(blank=True, max_length=50, null=True, verbose_name='الجنسية'),
        ),
    ]
