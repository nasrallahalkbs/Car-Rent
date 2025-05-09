# Generated manually on 2025-05-09 23:25

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('rental', '0025_adminuser_current_job_adminuser_department_and_more'),
        ('rental', '0026_user_age_user_gender_user_nationality'),
    ]

    operations = [
        # This migration shows that the model fields from 0025 have already been applied
        # and merges it with 0026 that adds new user fields
    ]