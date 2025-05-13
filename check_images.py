import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'car_rental_project.settings')
django.setup()

from rental.models import CarConditionReport, CarInspectionImage

report = CarConditionReport.objects.last()
if report:
    print(f'تقرير آخر: ID {report.id}')
    print(f'عدد الصور: {report.images.count()}')
    
    for img in report.images.all():
        print(f'صورة: {img.description}, مسار={img.image.name}')
else:
    print('لا توجد تقارير')
