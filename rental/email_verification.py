"""
نظام التحقق من البريد الإلكتروني للمستخدمين الجدد باستخدام Mailjet

هذا الملف يحتوي على الوظائف الأساسية للتحقق من البريد الإلكتروني عند إنشاء حساب جديد
"""

import os
import uuid
import secrets
import string
import json
from django.conf import settings
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.utils import timezone
from django.urls import reverse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.utils.translation import gettext_lazy as _
from django.contrib.auth import login
from django.http import HttpResponse

# استيراد Mailjet
from mailjet_rest import Client

from .models import User, EmailVerification

# الوقت الذي يستمر فيه رمز التحقق صالحًا (7 أيام بالثواني)
VERIFICATION_TOKEN_EXPIRY = 60 * 60 * 24 * 7

def generate_verification_token():
    """إنشاء رمز تحقق عشوائي"""
    # إنشاء رمز عشوائي من 32 حرف
    chars = string.ascii_letters + string.digits
    return ''.join(secrets.choice(chars) for _ in range(32))

def save_verification_token(user, token):
    """حفظ رمز التحقق وتاريخ انتهاء صلاحيته"""
    if not hasattr(user, 'verification'):
        # إذا لم يكن لدى المستخدم سجل تحقق، قم بإنشاء واحد
        EmailVerification.objects.create(
            user=user,
            token=token,
            expires_at=timezone.now() + timezone.timedelta(seconds=VERIFICATION_TOKEN_EXPIRY)
        )
    else:
        # تحديث الرمز وتاريخ انتهاء الصلاحية إذا كان موجودًا
        user.verification.token = token
        user.verification.expires_at = timezone.now() + timezone.timedelta(seconds=VERIFICATION_TOKEN_EXPIRY)
        user.verification.save()

def send_verification_email(request, user, token):
    """إرسال بريد إلكتروني للتحقق من عنوان البريد الإلكتروني"""
    # إنشاء رابط التحقق
    verification_url = request.build_absolute_uri(
        reverse('verify_email', kwargs={'token': token})
    )
    
    # إعداد قالب البريد الإلكتروني
    html_message = render_to_string('email/verify_email.html', {
        'user': user,
        'verification_url': verification_url,
        'site_name': 'موقع تأجير السيارات',
        'expiry_days': VERIFICATION_TOKEN_EXPIRY // (60 * 60 * 24)  # تحويل الثواني إلى أيام
    })
    
    plain_message = strip_tags(html_message)
    
    # إرسال البريد الإلكتروني
    try:
        send_mail(
            subject='تأكيد حسابك في موقع تأجير السيارات',
            message=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            html_message=html_message,
            fail_silently=False,
        )
        return True
    except Exception as e:
        print(f"خطأ في إرسال البريد الإلكتروني: {e}")
        # في وضع التطوير، نقوم بعرض البريد الإلكتروني في وحدة التحكم للاختبار
        if settings.DEBUG:
            print("\n-------- البريد الإلكتروني للتحقق ----------")
            print(f"الموضوع: تأكيد حسابك في موقع تأجير السيارات")
            print(f"إلى: {user.email}")
            print(f"رابط التحقق: {verification_url}")
            print("--------------------------------------------\n")
        return False

def verify_token(token):
    """التحقق من صحة رمز التحقق"""
    try:
        verification = EmailVerification.objects.get(token=token)
        
        # التحقق من انتهاء صلاحية الرمز
        if verification.expires_at < timezone.now():
            return None, "لقد انتهت صلاحية رمز التحقق"
        
        # التحقق من أن المستخدم غير مفعل بالفعل
        if verification.user.is_active:
            return verification.user, "تم تفعيل الحساب بالفعل"
        
        # تفعيل المستخدم
        verification.user.is_active = True
        verification.user.save()
        
        # تحديث سجل التحقق
        verification.verified_at = timezone.now()
        verification.save()
        
        return verification.user, "تم تفعيل الحساب بنجاح"
        
    except EmailVerification.DoesNotExist:
        return None, "رمز التحقق غير صالح"

def create_inactive_user(form_data):
    """إنشاء مستخدم غير نشط وإرسال بريد التحقق"""
    # إنشاء المستخدم ولكن تعيينه كغير نشط
    user = User.objects.create_user(
        username=form_data.get('username'),
        email=form_data.get('email'),
        password=form_data.get('password1'),
        first_name=form_data.get('first_name', ''),
        last_name=form_data.get('last_name', ''),
        phone=form_data.get('phone', ''),
        is_active=False  # المستخدم غير نشط حتى يتم التحقق من البريد الإلكتروني
    )
    
    # إذا كانت هناك حقول إضافية في النموذج
    if 'age' in form_data:
        user.age = form_data.get('age')
    if 'gender' in form_data:
        user.gender = form_data.get('gender')
    if 'nationality' in form_data:
        user.nationality = form_data.get('nationality')
    
    user.save()
    
    return user

# دالة لعرض صفحة التحقق من البريد الإلكتروني
def verify_email_view(request, token):
    """عرض صفحة التحقق من البريد الإلكتروني"""
    user, message = verify_token(token)
    
    if user:
        # تسجيل الدخول للمستخدم بعد التحقق
        if not user.is_authenticated:
            login(request, user)
        
        messages.success(request, message)
        return redirect('index')
    else:
        messages.error(request, message)
        return render(request, 'verification_failed.html', {'message': message})

# دالة لإعادة إرسال بريد التحقق
def resend_verification_email(request):
    """إعادة إرسال بريد التحقق"""
    if request.method == 'POST':
        email = request.POST.get('email')
        
        try:
            user = User.objects.get(email=email, is_active=False)
            token = generate_verification_token()
            save_verification_token(user, token)
            
            if send_verification_email(request, user, token):
                messages.success(request, _("تم إرسال بريد التحقق مرة أخرى. يرجى التحقق من بريدك الإلكتروني."))
            else:
                messages.error(request, _("حدث خطأ أثناء إرسال بريد التحقق. يرجى المحاولة مرة أخرى لاحقًا."))
                
        except User.DoesNotExist:
            # لا نعلم المستخدم بوجود أو عدم وجود البريد الإلكتروني لأسباب أمنية
            messages.success(request, _("إذا كان البريد الإلكتروني مسجلاً، فسيتم إرسال رابط التحقق."))
            
    return render(request, 'resend_verification.html')