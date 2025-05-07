"""
وحدة لضمان استخدام CSRF token بشكل صحيح
"""

import logging
from django.utils.translation import gettext_lazy as _
from django.contrib import messages

# إعداد التسجيل
logger = logging.getLogger('django.request')

def ensure_csrf_cookie(request):
    """
    التأكد من أن الكوكيز تحتوي على رمز CSRF صالح
    """
    from django.middleware.csrf import get_token
    return get_token(request)

def has_valid_csrf(request):
    """
    التحقق من وجود رمز CSRF صالح في الطلب
    """
    if request.method == 'POST' and not 'csrfmiddlewaretoken' in request.POST:
        logger.error("CSRF token مفقود في طلب POST")
        return False
    return True

def fix_csrf_in_form(request, form_id="permissions-form"):
    """
    إضافة JavaScript للتأكد من وجود حقل CSRF في النموذج
    """
    from django.middleware.csrf import get_token
    token = get_token(request)
    
    return f"""
    <script>
    document.addEventListener('DOMContentLoaded', function() {{
        console.log('⚙️ تفعيل إصلاح CSRF للنموذج: {form_id}');
        
        var form = document.getElementById('{form_id}');
        if (form) {{
            // التحقق من وجود حقل CSRF
            var csrfInput = form.querySelector('input[name="csrfmiddlewaretoken"]');
            if (!csrfInput) {{
                console.log('🔐 إضافة حقل CSRF إلى النموذج');
                
                // إنشاء حقل CSRF جديد
                var input = document.createElement('input');
                input.type = 'hidden';
                input.name = 'csrfmiddlewaretoken';
                input.value = '{token}';
                
                // إضافة حقل CSRF إلى النموذج
                form.prepend(input);
                
                console.log('✅ تم إضافة حقل CSRF بنجاح');
            }} else {{
                console.log('✓ حقل CSRF موجود بالفعل');
                
                // تحديث قيمة الرمز إذا كانت فارغة
                if (!csrfInput.value) {{
                    csrfInput.value = '{token}';
                    console.log('✅ تم تحديث قيمة رمز CSRF');
                }}
            }}
            
            // إعداد وظيفة تقديم النموذج
            var originalSubmit = form.submit;
            
            form.addEventListener('submit', function(e) {{
                console.log('📤 تقديم النموذج مع رمز CSRF: ' + form.querySelector('input[name="csrfmiddlewaretoken"]').value.substring(0, 5) + '...');
            }});
            
            console.log('✅ تم إعداد إصلاح CSRF بنجاح');
        }} else {{
            console.log('⚠️ لم يتم العثور على النموذج: {form_id}');
        }}
    }});
    </script>
    """