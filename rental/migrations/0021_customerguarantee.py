# Generated by Django 5.2 on 2025-05-04 00:47

import django.db.models.deletion
import django.utils.timezone
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('rental', '0020_carconditionreport_electronic_report_pdf_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='CustomerGuarantee',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255, verbose_name='اسم العهدة')),
                ('guarantee_type', models.CharField(choices=[('cash', 'نقدي'), ('credit_card', 'بطاقة ائتمانية'), ('property', 'مستند عقاري'), ('bank_deposit', 'وديعة بنكية'), ('insurance', 'بطاقة تأمين'), ('other', 'أخرى')], max_length=50, verbose_name='نوع العهدة')),
                ('category', models.CharField(blank=True, max_length=100, null=True, verbose_name='فئة العهدة')),
                ('handover_date', models.DateField(default=django.utils.timezone.now, verbose_name='تاريخ تسليم العهدة')),
                ('return_date', models.DateField(blank=True, null=True, verbose_name='تاريخ استرداد العهدة')),
                ('description', models.TextField(blank=True, null=True, verbose_name='وصف العهدة')),
                ('notes', models.TextField(blank=True, null=True, verbose_name='ملاحظات')),
                ('identifier', models.CharField(blank=True, max_length=100, null=True, verbose_name='معرف العهدة')),
                ('value', models.DecimalField(decimal_places=2, default=0, max_digits=10, verbose_name='قيمة العهدة')),
                ('status', models.CharField(choices=[('active', 'نشطة'), ('returned', 'مستردة'), ('partially_returned', 'مستردة جزئياً'), ('withheld', 'محتجزة'), ('claimed', 'مطالب بها')], default='active', max_length=20, verbose_name='حالة العهدة')),
                ('deductions', models.DecimalField(decimal_places=2, default=0, max_digits=10, verbose_name='مبلغ الخصومات')),
                ('deduction_reason', models.TextField(blank=True, null=True, verbose_name='سبب الخصم')),
                ('returned_amount', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True, verbose_name='المبلغ المسترد')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='تاريخ الإنشاء')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='تاريخ التحديث')),
                ('car', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='guarantees', to='rental.car', verbose_name='السيارة')),
                ('created_by', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='guarantees_created', to=settings.AUTH_USER_MODEL, verbose_name='تم الإنشاء بواسطة')),
                ('customer', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='guarantees', to=settings.AUTH_USER_MODEL, verbose_name='العميل')),
                ('reservation', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='guarantees', to='rental.reservation', verbose_name='رقم الحجز')),
                ('returned_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='guarantees_returned', to=settings.AUTH_USER_MODEL, verbose_name='تم الاسترداد بواسطة')),
            ],
            options={
                'verbose_name': 'عهدة العميل',
                'verbose_name_plural': 'عهدات العملاء',
                'ordering': ['-created_at'],
            },
        ),
    ]
