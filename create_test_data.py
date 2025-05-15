"""
إنشاء بيانات اختبارية للعهدات وتقارير حالة السيارات والمدفوعات
"""

import os
import django
import sys

# إعداد Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'car_rental_project.settings')
django.setup()

from rental.models import Document, ArchiveFolder, User, Car, Reservation
from django.utils import timezone
import random

def create_test_data():
    """إنشاء بيانات اختبارية لتبويبات التقارير"""
    print('إنشاء بيانات اختبارية...')

    # التحقق من وجود مستخدم
    user = User.objects.first()
    if not user:
        print('لا يوجد مستخدمين!')
        return

    # التحقق من وجود سيارة
    car = Car.objects.first()
    if not car:
        print('لا يوجد سيارات!')
        return

    # التحقق من وجود حجز
    reservation = Reservation.objects.first()
    if not reservation:
        print('لا يوجد حجوزات!')
        return

    # إنشاء مجلد للعهدة
    folder, created = ArchiveFolder.objects.get_or_create(
        name='عهدات العملاء', 
        defaults={'description': 'مجلد لحفظ عهدات العملاء'}
    )
    if created:
        print(f'تم إنشاء مجلد جديد: {folder.name}')

    # إنشاء مستندات عهدة
    custody_types = ['رخصة قيادة', 'بطاقة هوية', 'جواز سفر', 'بطاقة ائتمان']
    custody_count = Document.objects.filter(document_type='custody').count()
    
    if custody_count < 5:
        for i in range(5):
            custody_doc = Document(
                title=f'عهدة - {custody_types[i % len(custody_types)]} #{i+1}',
                description=f'وثيقة عهدة نوع {custody_types[i % len(custody_types)]} للعميل',
                folder=folder,
                document_type='custody',
                user=user,
                car=car,
                reservation=reservation,
                document_date=timezone.now(),
                is_auto_created=False
            )
            custody_doc.save()
            print(f'تم إنشاء مستند عهدة: {custody_doc.title}')
    else:
        print('يوجد بالفعل مستندات عهدة كافية.')

    # إنشاء مجلد لتقارير حالة السيارات
    condition_folder, created = ArchiveFolder.objects.get_or_create(
        name='تقارير حالة السيارات', 
        defaults={'description': 'مجلد لحفظ تقارير حالة السيارات'}
    )
    if created:
        print(f'تم إنشاء مجلد جديد: {condition_folder.name}')

    # إنشاء تقارير حالة سيارات
    report_types = ['car_report', 'maintenance_report', 'condition_report']
    report_titles = ['تقرير معاينة', 'تقرير صيانة', 'تقرير حالة']
    condition_count = Document.objects.filter(document_type__in=report_types).count()
    
    if condition_count < 5:
        for i in range(5):
            report_type = report_types[i % len(report_types)]
            report_title = report_titles[i % len(report_titles)]
            condition_doc = Document(
                title=f'{report_title} - سيارة #{car.id} - #{i+1}',
                description=f'تقرير حالة للسيارة {car.make} {car.model}',
                folder=condition_folder,
                document_type=report_type,
                user=user,
                car=car,
                reservation=reservation,
                document_date=timezone.now(),
                is_auto_created=False
            )
            condition_doc.save()
            print(f'تم إنشاء تقرير حالة سيارة: {condition_doc.title}')
    else:
        print('يوجد بالفعل تقارير حالة سيارات كافية.')

    print('تم إنشاء البيانات الاختبارية بنجاح!')

if __name__ == '__main__':
    create_test_data()