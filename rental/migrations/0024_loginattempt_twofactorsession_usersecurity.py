# Generated by Django 5.2 on 2025-05-06 23:27

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('rental', '0023_systemsetting_scheduledjob_systembackup_systemissue_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='LoginAttempt',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('username', models.CharField(max_length=150)),
                ('ip_address', models.GenericIPAddressField(blank=True, null=True)),
                ('user_agent', models.CharField(blank=True, max_length=512, null=True)),
                ('status', models.CharField(choices=[('success', 'نجاح'), ('failed', 'فشل'), ('locked', 'الحساب مقفل')], max_length=20)),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
                ('notes', models.CharField(blank=True, max_length=255, null=True)),
                ('user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='login_attempts', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'محاولة تسجيل دخول',
                'verbose_name_plural': 'محاولات تسجيل الدخول',
                'ordering': ['-timestamp'],
            },
        ),
        migrations.CreateModel(
            name='TwoFactorSession',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('session_key', models.CharField(max_length=64, unique=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('expires_at', models.DateTimeField()),
                ('is_verified', models.BooleanField(default=False)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='two_factor_sessions', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'جلسة المصادقة الثنائية',
                'verbose_name_plural': 'جلسات المصادقة الثنائية',
            },
        ),
        migrations.CreateModel(
            name='UserSecurity',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('two_factor_enabled', models.BooleanField(default=False)),
                ('totp_secret', models.CharField(blank=True, max_length=255, null=True)),
                ('backup_codes', models.JSONField(blank=True, default=list)),
                ('failed_login_attempts', models.IntegerField(default=0)),
                ('last_failed_login', models.DateTimeField(blank=True, null=True)),
                ('locked_until', models.DateTimeField(blank=True, null=True)),
                ('password_changed_at', models.DateTimeField(auto_now_add=True)),
                ('password_last_used', models.DateTimeField(blank=True, null=True)),
                ('previous_passwords', models.JSONField(blank=True, default=list)),
                ('last_login_ip', models.GenericIPAddressField(blank=True, null=True)),
                ('last_active', models.DateTimeField(auto_now=True)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='security', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'أمان المستخدم',
                'verbose_name_plural': 'أمان المستخدمين',
            },
        ),
    ]
