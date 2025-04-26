"""
إضافة حقول تخزين محتوى الملفات في قاعدة البيانات
"""
from django.db import migrations, models

def archive_document_path(instance, filename):
    """تحديد مسار حفظ مستندات الأرشيف"""
    # استخدام الفولدر كجزء من المسار إن وجد
    if instance.folder:
        folder_path = f"folder_{instance.folder.id}"
    else:
        folder_path = "general"
    
    # تنقية اسم الملف
    safe_filename = filename.replace(" ", "_")
    return f"archive/{folder_path}/{safe_filename}"

class Migration(migrations.Migration):

    dependencies = [
        ('rental', '0012_merge_20250425_1616'),
    ]

    operations = [
        migrations.AddField(
            model_name='document',
            name='file_content',
            field=models.BinaryField(blank=True, editable=False, null=True, verbose_name='محتوى الملف'),
        ),
        migrations.AddField(
            model_name='document',
            name='file_name',
            field=models.CharField(blank=True, max_length=255, null=True, verbose_name='اسم الملف الأصلي'),
        ),
        migrations.AddField(
            model_name='document',
            name='file_size',
            field=models.PositiveIntegerField(default=0, editable=False, verbose_name='حجم الملف (بايت)'),
        ),
        migrations.AddField(
            model_name='document',
            name='file_type',
            field=models.CharField(blank=True, max_length=100, null=True, verbose_name='نوع الملف'),
        ),
    ]
