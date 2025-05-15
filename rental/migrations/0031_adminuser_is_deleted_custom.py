from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('rental', '0030_adminactivity_affected_item_id_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='adminuser',
            name='is_deleted',
            field=models.BooleanField(default=False, verbose_name='محذوف (مخفي)'),
        ),
    ]