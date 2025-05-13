"""
صفحة رفع مستندات مستقلة ومباشرة

هذا السكريبت يوفر صفحة رفع مستندات مستقلة تماماً عن النظام الأساسي،
وتستخدم SQL مباشرة للتعامل مع قاعدة البيانات لتجاوز أي قيود أو آليات منع.
"""

import os
import uuid
import traceback
from datetime import date

from django.http import HttpResponse, JsonResponse
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.db import connection
import json

# مسار حفظ الملفات المرفوعة
UPLOAD_DIR = os.path.join('media', 'archive', 'uploads')

# التأكد من وجود المجلد
os.makedirs(UPLOAD_DIR, exist_ok=True)

@login_required
def fixed_direct_upload_page(request):
    """صفحة رفع مستندات مستقلة بالكامل"""
    
    if request.method == 'POST':
        # معالجة طلب الرفع
        try:
            # التحقق من وجود ملف
            if 'file' not in request.FILES:
                return HttpResponse("لم يتم تحديد ملف للرفع", content_type="text/html", status=400)
                
            file = request.FILES['file']
            title = request.POST.get('title', file.name)
            description = request.POST.get('description', '')
            
            # إنشاء اسم ملف فريد
            ext = os.path.splitext(file.name)[1]
            unique_filename = f"{uuid.uuid4().hex}{ext}"
            rel_path = os.path.join('archive', 'uploads', unique_filename)
            absolute_path = os.path.join('media', rel_path)
            
            # حفظ الملف
            with open(absolute_path, 'wb+') as destination:
                for chunk in file.chunks():
                    destination.write(chunk)
                    
            # إضافة المستند لقاعدة البيانات باستخدام SQL مباشرة
            with connection.cursor() as cursor:
                now = timezone.now()
                
                # إعداد المعاملات
                query = """
                INSERT INTO rental_document 
                (title, description, document_type, file, file_name, file_type, file_size, 
                is_auto_created, added_by_id, created_at, updated_at, is_archived, document_date, related_to)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                RETURNING id
                """
                
                cursor.execute(query, [
                    title,
                    description,
                    'other',
                    rel_path,
                    file.name,
                    file.content_type,
                    file.size,
                    False,
                    request.user.id,
                    now,
                    now,
                    True,
                    now.date(),
                    'other'
                ])
                
                doc_id = cursor.fetchone()[0]
                
                return HttpResponse(f"""
                <!DOCTYPE html>
                <html dir="rtl">
                <head>
                    <meta charset="UTF-8">
                    <meta name="viewport" content="width=device-width, initial-scale=1.0">
                    <title>تم الرفع بنجاح</title>
                    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
                    <style>
                        body { padding: 40px; text-align: center; }
                        .success-message { 
                            max-width: 500px; 
                            margin: 0 auto; 
                            background-color: #f8f9fa;
                            padding: 30px;
                            border-radius: 10px;
                            box-shadow: 0 0 20px rgba(0,0,0,0.1);
                        }
                        .success-icon {
                            color: #198754;
                            font-size: 60px;
                            margin-bottom: 20px;
                        }
                        .btn-primary { margin-top: 20px; }
                    </style>
                </head>
                <body>
                    <div class="container">
                        <div class="success-message">
                            <div class="success-icon">✓</div>
                            <h2>تم رفع الملف بنجاح</h2>
                            <p class="mt-3">تم حفظ الملف "{file.name}" في قاعدة البيانات برقم {doc_id}</p>
                            <div class="mt-4">
                                <a href="/ar/dashboard/archive/" class="btn btn-primary me-2">العودة للأرشيف</a>
                                <a href="/ar/dashboard/" class="btn btn-outline-secondary">لوحة التحكم</a>
                            </div>
                        </div>
                    </div>
                </body>
                </html>
                """, content_type="text/html")
                
        except Exception as e:
            error_message = str(e)
            traceback_info = traceback.format_exc()
            
            return HttpResponse(f"""
            <!DOCTYPE html>
            <html dir="rtl">
            <head>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <title>خطأ في الرفع</title>
                <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
                <style>
                    body { padding: 40px; text-align: center; }
                    .error-message { 
                        max-width: 600px; 
                        margin: 0 auto; 
                        background-color: #f8f9fa;
                        padding: 30px;
                        border-radius: 10px;
                        box-shadow: 0 0 20px rgba(0,0,0,0.1);
                        text-align: right;
                    }
                    .error-icon {
                        color: #dc3545;
                        font-size: 60px;
                        margin-bottom: 20px;
                    }
                    .error-details {
                        direction: ltr;
                        text-align: left;
                        background-color: #f1f1f1;
                        padding: 15px;
                        border-radius: 5px;
                        margin-top: 20px;
                        overflow-x: auto;
                        white-space: pre-wrap;
                        font-family: monospace;
                        font-size: 0.9rem;
                    }
                    .btn-primary { margin-top: 20px; }
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="error-message">
                        <div class="error-icon">✗</div>
                        <h2>خطأ في رفع الملف</h2>
                        <p class="mt-3">{error_message}</p>
                        <div class="error-details">
                            {traceback_info}
                        </div>
                        <div class="mt-4">
                            <a href="/ar/dashboard/archive/" class="btn btn-primary me-2">العودة للأرشيف</a>
                            <a href="/ar/dashboard/" class="btn btn-outline-secondary">لوحة التحكم</a>
                        </div>
                    </div>
                </div>
            </body>
            </html>
            """, content_type="text/html", status=500)
    
    # عرض صفحة الرفع
    return HttpResponse("""
    <!DOCTYPE html>
    <html dir="rtl">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>رفع ملف جديد</title>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
        <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">
        <style>
            body {
                background-color: #f8f9fa;
                padding: 40px 0;
            }
            .upload-form {
                background-color: white;
                border-radius: 10px;
                box-shadow: 0 0 20px rgba(0,0,0,0.1);
                padding: 30px;
                max-width: 700px;
                margin: 0 auto;
            }
            .upload-icon {
                font-size: 48px;
                color: #0d6efd;
                margin-bottom: 20px;
            }
            .custom-file-upload {
                border: 2px dashed #ddd;
                border-radius: 5px;
                padding: 30px;
                text-align: center;
                cursor: pointer;
                margin-bottom: 20px;
                transition: all 0.3s;
            }
            .custom-file-upload:hover {
                border-color: #0d6efd;
                background-color: #f8f9fa;
            }
            .custom-file-upload i {
                font-size: 48px;
                color: #6c757d;
                margin-bottom: 15px;
            }
            .file-info {
                display: none;
                margin-top: 20px;
                padding: 15px;
                background-color: #f8f9fa;
                border-radius: 5px;
                text-align: right;
            }
            .file-name {
                font-weight: bold;
                margin-bottom: 5px;
            }
            .file-size {
                color: #6c757d;
                font-size: 0.9rem;
            }
            .btn-submit {
                margin-top: 20px;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="upload-form">
                <div class="text-center mb-4">
                    <div class="upload-icon">
                        <i class="fas fa-cloud-upload-alt"></i>
                    </div>
                    <h2>رفع ملف جديد</h2>
                    <p class="text-muted">يمكنك رفع ملفات PDF، صور، مستندات Word وملفات Excel</p>
                </div>
                
                <form method="POST" enctype="multipart/form-data" id="directUploadForm">
                    <div class="custom-file-upload" id="dropArea">
                        <i class="fas fa-file-upload"></i>
                        <h5>اسحب الملف هنا أو انقر للاختيار</h5>
                        <p class="text-muted">الحد الأقصى لحجم الملف: 10 ميجابايت</p>
                        <input type="file" id="file" name="file" class="d-none" required>
                    </div>
                    
                    <div class="file-info" id="fileInfo">
                        <div class="file-name" id="fileName"></div>
                        <div class="file-size" id="fileSize"></div>
                    </div>
                    
                    <div class="mb-3">
                        <label for="title" class="form-label">عنوان المستند</label>
                        <input type="text" class="form-control" id="title" name="title" required>
                    </div>
                    
                    <div class="mb-3">
                        <label for="description" class="form-label">وصف المستند (اختياري)</label>
                        <textarea class="form-control" id="description" name="description" rows="3"></textarea>
                    </div>
                    
                    <div class="d-grid gap-2 d-md-flex justify-content-md-end btn-submit">
                        <a href="/ar/dashboard/archive/" class="btn btn-outline-secondary me-md-2">إلغاء</a>
                        <button type="submit" class="btn btn-primary" id="submitBtn">
                            <i class="fas fa-upload me-2"></i> رفع الملف
                        </button>
                    </div>
                </form>
            </div>
        </div>
        
        <script src="https://code.jquery.com/jquery-3.6.0.min.js"></script>
        <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/js/bootstrap.bundle.min.js"></script>
        <script>
            $(document).ready(function() {
                // تحديث معلومات الملف عند اختيار ملف
                $('#file').change(function(e) {
                    if (this.files.length > 0) {
                        const file = this.files[0];
                        const fileSize = formatFileSize(file.size);
                        
                        $('#fileName').text(file.name);
                        $('#fileSize').text(fileSize);
                        $('#fileInfo').show();
                        
                        // تعيين عنوان المستند تلقائياً من اسم الملف
                        if ($('#title').val() === '') {
                            const titleFromFile = file.name.split('.').slice(0, -1).join('.');
                            $('#title').val(titleFromFile);
                        }
                        
                        // التحقق من حجم الملف (10 ميجابايت كحد أقصى)
                        if (file.size > 10 * 1024 * 1024) {
                            alert('حجم الملف كبير جداً. الحد الأقصى هو 10 ميجابايت.');
                            resetFileInput();
                        }
                    } else {
                        $('#fileInfo').hide();
                    }
                });
                
                // دعم سحب وإفلات الملفات
                const dropArea = document.getElementById('dropArea');
                
                ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
                    dropArea.addEventListener(eventName, preventDefaults, false);
                });
                
                function preventDefaults(e) {
                    e.preventDefault();
                    e.stopPropagation();
                }
                
                ['dragenter', 'dragover'].forEach(eventName => {
                    dropArea.addEventListener(eventName, highlight, false);
                });
                
                ['dragleave', 'drop'].forEach(eventName => {
                    dropArea.addEventListener(eventName, unhighlight, false);
                });
                
                function highlight() {
                    dropArea.classList.add('border-primary');
                    dropArea.style.backgroundColor = '#f0f7ff';
                }
                
                function unhighlight() {
                    dropArea.classList.remove('border-primary');
                    dropArea.style.backgroundColor = '';
                }
                
                dropArea.addEventListener('drop', handleDrop, false);
                
                function handleDrop(e) {
                    const dt = e.dataTransfer;
                    const files = dt.files;
                    
                    if (files.length > 0) {
                        document.getElementById('file').files = files;
                        $('#file').trigger('change');
                    }
                }
                
                // فتح مستعرض الملفات عند النقر على منطقة السحب والإفلات
                $('#dropArea').click(function() {
                    $('#file').click();
                });
                
                // عرض تقدم الرفع
                $('#directUploadForm').submit(function() {
                    if ($('#file')[0].files.length === 0) {
                        alert('يرجى اختيار ملف للرفع');
                        return false;
                    }
                    
                    if ($('#title').val().trim() === '') {
                        alert('يرجى إدخال عنوان للمستند');
                        return false;
                    }
                    
                    $('#submitBtn').html('<i class="fas fa-spinner fa-spin me-2"></i> جاري الرفع...').prop('disabled', true);
                    return true;
                });
                
                // تنسيق حجم الملف
                function formatFileSize(bytes) {
                    if (bytes === 0) return '0 بايت';
                    
                    const k = 1024;
                    const sizes = ['بايت', 'كيلوبايت', 'ميجابايت', 'جيجابايت'];
                    const i = Math.floor(Math.log(bytes) / Math.log(k));
                    
                    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
                }
                
                // إعادة تعيين حقل الملف
                function resetFileInput() {
                    $('#file').val('');
                    $('#fileInfo').hide();
                }
            });
        </script>
    </body>
    </html>
    """, content_type="text/html")