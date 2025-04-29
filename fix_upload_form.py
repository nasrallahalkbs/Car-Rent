"""
إصلاح نموذج رفع المستندات في صفحة الأرشيف الإلكتروني

هذا السكريبت يقوم بالتالي:
1. إنشاء نموذج مخصص لتحميل المستندات
2. إضافة JavaScript للتحقق من النموذج قبل الإرسال
3. تحديث وظيفة رفع المستندات للعمل بشكل صحيح
4. حل مشكلة عدم ظهور رسائل الخطأ للمستخدم
"""

def create_new_upload_form():
    """إنشاء نموذج رفع جديد مبسط ومباشر للتعامل مع المشكلات"""
    
    # إنشاء قالب جديد لرفع الملفات
    upload_form_template = """{% extends 'admin/admin_layout.html' %}
{% load static %}
{% load i18n %}

{% block title %}{% trans "رفع مستند جديد" %}{% endblock %}

{% block css %}
<style>
    .upload-form {
        max-width: 600px;
        margin: 0 auto;
        padding: 20px;
        background-color: #f8f9fa;
        border-radius: 10px;
        box-shadow: 0 2px 5px rgba(0,0,0,0.1);
    }
    
    .form-title {
        text-align: center;
        margin-bottom: 20px;
        color: #343a40;
    }
    
    .preview-image {
        max-width: 100%;
        max-height: 200px;
        margin-top: 10px;
        border-radius: 5px;
        display: none;
    }
    
    .file-info {
        font-size: 0.85rem;
        color: #6c757d;
        margin-top: 5px;
    }
    
    .progress {
        display: none;
        margin-top: 10px;
    }
</style>
{% endblock %}

{% block content %}
<div class="container my-4">
    <div class="row">
        <div class="col-12">
            <nav aria-label="breadcrumb">
                <ol class="breadcrumb">
                    <li class="breadcrumb-item"><a href="{% url 'admin_index' %}">{% trans "لوحة التحكم" %}</a></li>
                    <li class="breadcrumb-item"><a href="{% url 'admin_archive' %}">{% trans "الأرشيف الإلكتروني" %}</a></li>
                    <li class="breadcrumb-item active" aria-current="page">{% trans "رفع مستند" %}</li>
                </ol>
            </nav>
            
            <div class="upload-form">
                <h2 class="form-title">{% trans "رفع مستند جديد" %}</h2>
                
                <!-- رسائل النظام -->
                {% if messages %}
                <div class="messages">
                    {% for message in messages %}
                    <div class="alert {% if message.tags %}alert-{{ message.tags }}{% else %}alert-info{% endif %} alert-dismissible fade show" role="alert">
                        {{ message }}
                        <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
                    </div>
                    {% endfor %}
                </div>
                {% endif %}
                
                <!-- نموذج رفع الملف -->
                <form method="post" action="{% url 'admin_archive_upload' %}" enctype="multipart/form-data" id="uploadForm">
                    {% csrf_token %}
                    
                    <!-- المجلد الأب (إذا كان موجودًا) -->
                    {% if current_folder %}
                    <input type="hidden" name="folder" value="{{ current_folder.id }}">
                    <div class="mb-3">
                        <label class="form-label">{% trans "المجلد المختار" %}</label>
                        <div class="form-control bg-light">{{ current_folder.name }}</div>
                    </div>
                    {% else %}
                    <div class="mb-3">
                        <label for="folder" class="form-label">{% trans "المجلد" %} ({% trans "اختياري" %})</label>
                        <select class="form-select" name="folder" id="folder">
                            <option value="">{% trans "المجلد الرئيسي" %}</option>
                            {% for folder in folders %}
                            <option value="{{ folder.id }}">{{ folder.name }}</option>
                            {% endfor %}
                        </select>
                    </div>
                    {% endif %}
                    
                    <!-- نوع المستند -->
                    <div class="mb-3">
                        <label for="document_type" class="form-label">{% trans "نوع المستند" %}</label>
                        <select class="form-select" name="document_type" id="document_type" required>
                            <option value="other">{% trans "مستند عام" %}</option>
                            <option value="contract">{% trans "عقد" %}</option>
                            <option value="invoice">{% trans "فاتورة" %}</option>
                            <option value="receipt">{% trans "إيصال" %}</option>
                            <option value="report">{% trans "تقرير" %}</option>
                            <option value="letter">{% trans "خطاب" %}</option>
                        </select>
                    </div>
                    
                    <!-- عنوان المستند -->
                    <div class="mb-3">
                        <label for="title" class="form-label">{% trans "عنوان المستند" %} *</label>
                        <input type="text" class="form-control" id="title" name="title" required>
                    </div>
                    
                    <!-- وصف المستند -->
                    <div class="mb-3">
                        <label for="description" class="form-label">{% trans "وصف المستند" %}</label>
                        <textarea class="form-control" id="description" name="description" rows="3"></textarea>
                    </div>
                    
                    <!-- اختيار الملف -->
                    <div class="mb-3">
                        <label for="file" class="form-label">{% trans "اختر الملف" %} *</label>
                        <input type="file" class="form-control" id="file" name="file" required>
                        <div class="file-info mt-2" id="fileInfo"></div>
                        <img id="filePreview" class="preview-image" src="" alt="معاينة الملف">
                        
                        <!-- شريط التقدم -->
                        <div class="progress">
                            <div class="progress-bar progress-bar-striped progress-bar-animated" id="uploadProgress" role="progressbar" style="width: 0%"></div>
                        </div>
                    </div>
                    
                    <!-- أزرار الإجراءات -->
                    <div class="d-grid gap-2 d-md-flex justify-content-md-end">
                        <a href="{% url 'admin_archive' %}" class="btn btn-secondary">{% trans "إلغاء" %}</a>
                        <button type="submit" class="btn btn-primary" id="submitButton">{% trans "رفع المستند" %}</button>
                    </div>
                </form>
            </div>
        </div>
    </div>
</div>
{% endblock %}

{% block js %}
<script>
    document.addEventListener('DOMContentLoaded', function() {
        const fileInput = document.getElementById('file');
        const fileInfo = document.getElementById('fileInfo');
        const filePreview = document.getElementById('filePreview');
        const uploadForm = document.getElementById('uploadForm');
        const submitButton = document.getElementById('submitButton');
        const progress = document.querySelector('.progress');
        const progressBar = document.getElementById('uploadProgress');
        
        // معالج تغيير الملف
        fileInput.addEventListener('change', function() {
            if (this.files && this.files[0]) {
                const file = this.files[0];
                
                // عرض معلومات الملف
                fileInfo.innerHTML = `<strong>${file.name}</strong> (${formatFileSize(file.size)}, ${file.type})`;
                
                // عرض معاينة للصور
                if (file.type.startsWith('image/')) {
                    const reader = new FileReader();
                    reader.onload = function(e) {
                        filePreview.src = e.target.result;
                        filePreview.style.display = 'block';
                    }
                    reader.readAsDataURL(file);
                } else {
                    filePreview.style.display = 'none';
                }
            } else {
                fileInfo.innerHTML = '';
                filePreview.style.display = 'none';
            }
        });
        
        // التحقق من النموذج قبل الإرسال
        uploadForm.addEventListener('submit', function(event) {
            event.preventDefault();
            
            // التحقق من الحقول المطلوبة
            const title = document.getElementById('title').value.trim();
            const file = fileInput.files;
            
            if (!title) {
                alert('{% trans "يرجى إدخال عنوان للمستند" %}');
                return;
            }
            
            if (!file || file.length === 0) {
                alert('{% trans "يرجى اختيار ملف للرفع" %}');
                return;
            }
            
            // إظهار شريط التقدم
            progress.style.display = 'flex';
            submitButton.disabled = true;
            
            // محاكاة تقدم الرفع (بما أن الرفع الفعلي لا يحتوي على شريط تقدم)
            let width = 0;
            const interval = setInterval(function() {
                if (width >= 90) {
                    clearInterval(interval);
                } else {
                    width += 5;
                    progressBar.style.width = width + '%';
                }
            }, 150);
            
            // تنفيذ الإرسال الفعلي
            console.log('بدء رفع الملف...');
            this.submit();
        });
        
        // تنسيق حجم الملف ليكون سهل القراءة
        function formatFileSize(bytes) {
            if (bytes === 0) return '0 Bytes';
            const k = 1024;
            const sizes = ['Bytes', 'KB', 'MB', 'GB'];
            const i = Math.floor(Math.log(bytes) / Math.log(k));
            return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
        }
    });
</script>
{% endblock %}
"""
    
    # حفظ القالب الجديد
    upload_form_path = "templates/admin/archive/direct_upload_form.html"
    try:
        with open(upload_form_path, "w", encoding="utf-8") as f:
            f.write(upload_form_template)
        print(f"✅ تم إنشاء قالب جديد لرفع الملفات في {upload_form_path}")
    except Exception as e:
        print(f"❌ فشل في إنشاء قالب جديد: {str(e)}")
        return False
    
    return True

def add_upload_view_and_url():
    """إضافة وظيفة عرض جديدة ومسار لرفع الملفات"""
    
    # إضافة الوظيفة الجديدة إلى ملف admin_views.py
    from rental.admin_views import admin_required, login_required, render, redirect, get_object_or_404, messages
    from rental.models import ArchiveFolder
    
    new_function_code = """
@login_required
@admin_required
def admin_archive_upload_form(request):
    \"\"\"عرض نموذج رفع ملف جديد (مستقل)\"\"\"
    # الحصول على رقم المجلد الحالي من المعلمات
    folder_id = request.GET.get('folder', None)
    current_folder = None
    
    # إذا تم تحديد مجلد، نحصل على معلوماته
    if folder_id:
        try:
            current_folder = ArchiveFolder.objects.get(id=folder_id)
        except ArchiveFolder.DoesNotExist:
            messages.error(request, "المجلد المحدد غير موجود")
    
    # الحصول على قائمة المجلدات للاختيار
    folders = ArchiveFolder.objects.all().order_by('name')
    
    context = {
        'current_folder': current_folder,
        'folders': folders,
    }
    
    return render(request, 'admin/archive/direct_upload_form.html', context)
"""
    
    # إضافة المسار الجديد إلى ملف urls.py
    import re
    
    # التحقق من وجود الوظيفة في admin_views.py
    admin_views_path = "rental/admin_views.py"
    try:
        with open(admin_views_path, "r", encoding="utf-8") as f:
            content = f.read()
        
        # التحقق من عدم وجود الوظيفة مسبقًا
        if "def admin_archive_upload_form" not in content:
            # إضافة الوظيفة في نهاية الملف
            with open(admin_views_path, "a", encoding="utf-8") as f:
                f.write("\n\n" + new_function_code)
            print(f"✅ تمت إضافة وظيفة admin_archive_upload_form إلى {admin_views_path}")
        else:
            print("ℹ️ وظيفة admin_archive_upload_form موجودة بالفعل")
    except Exception as e:
        print(f"❌ فشل في إضافة الوظيفة الجديدة: {str(e)}")
        return False
    
    # إضافة المسار الجديد إلى urls.py
    urls_path = "rental/urls.py"
    try:
        with open(urls_path, "r", encoding="utf-8") as f:
            content = f.read()
        
        # التحقق من عدم وجود المسار مسبقًا
        if "admin_archive_upload_form" not in content:
            # إضافة المسار بعد نمط مسارات الأرشيف
            pattern = r"(path\('dashboard/archive/upload/.*?,.*?,.*?\),)"
            match = re.search(pattern, content)
            
            if match:
                replacement = match.group(1) + "\n    path('dashboard/archive/upload-form/', admin_views.admin_archive_upload_form, name='admin_archive_upload_form'),"
                new_content = content.replace(match.group(1), replacement)
                
                with open(urls_path, "w", encoding="utf-8") as f:
                    f.write(new_content)
                print(f"✅ تمت إضافة مسار جديد للنموذج في {urls_path}")
            else:
                print("⚠️ لم يتم العثور على نمط مسار الرفع في urls.py")
                return False
        else:
            print("ℹ️ مسار admin_archive_upload_form موجود بالفعل")
    except Exception as e:
        print(f"❌ فشل في إضافة المسار الجديد: {str(e)}")
        return False
    
    return True

def add_link_to_direct_fix():
    """إضافة رابط لنموذج الرفع الجديد في صفحة direct_fix.html"""
    
    direct_fix_path = "templates/admin/archive/direct_fix.html"
    try:
        with open(direct_fix_path, "r", encoding="utf-8") as f:
            content = f.read()
        
        # إضافة زر للنموذج الجديد بعد زر إضافة ملف الحالي
        pattern = r'(<button class="btn btn-success" data-bs-toggle="modal" data-bs-target="#addFileModal">.*?</button>)'
        match = re.search(pattern, content, re.DOTALL)
        
        if match:
            replacement = match.group(1) + '\n                        <a href="{% url \'admin_archive_upload_form\' %}{% if current_folder %}?folder={{ current_folder.id }}{% endif %}" class="btn btn-info mt-2">\n                            <i class="fas fa-cloud-upload-alt me-2"></i> {% trans "رفع مستند (النموذج المباشر)" %}\n                        </a>'
            new_content = content.replace(match.group(1), replacement)
            
            with open(direct_fix_path, "w", encoding="utf-8") as f:
                f.write(new_content)
            print(f"✅ تمت إضافة رابط للنموذج الجديد في {direct_fix_path}")
        else:
            print("⚠️ لم يتم العثور على زر إضافة ملف في direct_fix.html")
            return False
    except Exception as e:
        print(f"❌ فشل في إضافة رابط للنموذج الجديد: {str(e)}")
        return False
    
    return True

def main():
    """تنفيذ الحلول المقترحة"""
    success = True
    
    print("🔄 جاري إنشاء نموذج رفع مستندات جديد...")
    if not create_new_upload_form():
        success = False
    
    print("\n🔄 جاري إضافة وظيفة العرض والمسار...")
    if not add_upload_view_and_url():
        success = False
    
    print("\n🔄 جاري إضافة رابط للنموذج الجديد في صفحة الأرشيف...")
    if not add_link_to_direct_fix():
        success = False
    
    if success:
        print("\n✅ تم إكمال جميع التغييرات بنجاح!")
        print("ℹ️ يمكنك الآن استخدام نموذج الرفع الجديد عن طريق الرابط المباشر:")
        print("    /ar/dashboard/archive/upload-form/")
    else:
        print("\n⚠️ حدثت بعض الأخطاء. راجع الرسائل أعلاه للتفاصيل.")

if __name__ == "__main__":
    import re
    main()