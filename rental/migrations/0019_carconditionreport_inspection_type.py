# Generated by Django 5.2 on 2025-04-30 21:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('rental', '0018_carinspectiondetail_labor_cost_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='carconditionreport',
            name='inspection_type',
            field=models.CharField(choices=[('manual', 'فحص يدوي'), ('electronic', 'فحص إلكتروني')], default='manual', max_length=20, verbose_name='نوع الفحص'),
        ),
    ]
