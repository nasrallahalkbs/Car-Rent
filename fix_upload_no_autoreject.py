"""
إصلاح مشكلة رفع الملفات - إيقاف رفض المستندات أثناء رفع الملفات
"""

def fix_upload_function():
    """
    تحديث وظيفة admin_archive_upload للتأكد من تجاوز إشارة رفض المستندات التلقائية
    وإضافة معالجة أخطاء أفضل للتشخيص
    """
    import re
    
    admin_views_path = "rental/admin_views.py"
    
    # البحث عن الوظيفة وإضافة تصحيح للتأكد من تعيين علامة التجاوز
    with open(admin_views_path, "r", encoding="utf-8") as f:
        content = f.read()
    
    # تحديث وظيفة admin_archive_upload
    # ابحث عن بداية الوظيفة
    upload_function_match = re.search(r"def admin_archive_upload\(request\):.*?""".*?""".*?if request\.method != 'POST':", content, re.DOTALL)
    
    if not upload_function_match:
        print("⚠️ لم يتم العثور على وظيفة admin_archive_upload")
        return False
    
    # تحديث الوظيفة بإضافة طريقة بديلة وتسجيل أفضل
    new_upload_function = """def admin_archive_upload(request):
    """وظيفة مخصصة لرفع المستندات إلى الأرشيف - نسخة محسنة مع منع الرفض التلقائي"""
    import logging
    import traceback
    from django.db import connection
    
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)
    
    print("📥 بيانات طلب الرفع:")
    print(f"📥 طريقة الطلب: {request.method}")
    print(f"📥 البيانات المرسلة: {request.POST}")
    print(f"📥 الملفات المرفوعة: {request.FILES}")
    
    if request.method != 'POST':
        print("❌ طريقة الطلب غير صحيحة - يجب أن تكون POST")
        messages.error(request, "طريقة طلب غير صالحة")
        return redirect('admin_archive')
    
    # 1. استخراج البيانات من النموذج
    title = request.POST.get('title', '').strip()
    description = request.POST.get('description', '')
    folder_id = request.POST.get('folder', None)
    document_type = request.POST.get('document_type', 'other')
    
    print(f"📋 البيانات: العنوان='{title}', النوع='{document_type}', المجلد={folder_id}")
    
    # 2. التحقق من البيانات المطلوبة
    if not title:
        print("❌ لم يتم تحديد عنوان للمستند")
        messages.error(request, "يرجى إدخال عنوان للمستند")
        return redirect('admin_archive')
    
    if 'file' not in request.FILES:
        print("❌ لم يتم تحديد ملف للرفع")
        messages.error(request, "يرجى اختيار ملف للرفع")
        return redirect('admin_archive')
    
    # 3. الحصول على الملف المرفوع والمعلومات المتعلقة به
    uploaded_file = request.FILES['file']
    file_name = uploaded_file.name
    file_type = uploaded_file.content_type
    file_size = uploaded_file.size
    
    print(f"📁 معلومات الملف: اسم={file_name}, نوع={file_type}, حجم={file_size} بايت")
    
    # تعطيل آلية منع المستندات التلقائية بشكل مباشر
    import sys
    from rental.models import Document
    
    # حفظ نسخة من دالة __init__ الأصلية
    original_init = Document.__init__
    
    # تعريف دالة مؤقتة تتجاوز الحماية
    def no_reject_init(self, *args, **kwargs):
        # استدعاء الدالة الأصلية
        original_init(self, *args, **kwargs)
        # تعيين علامة التجاوز دائماً
        self._ignore_auto_document_signal = True
        print(f"🔓 تعيين علامة التجاوز للمستند الجديد: {getattr(self, '_ignore_auto_document_signal', False)}")
    
    # استبدال دالة __init__ مؤقتاً
    Document.__init__ = no_reject_init
    
    try:
        # 4. قراءة محتوى الملف
        try:
            file_content = uploaded_file.read()
            print(f"📄 تم قراءة محتوى الملف: {len(file_content)} بايت")
            
            # إعادة تعيين مؤشر الملف للبداية
            uploaded_file.seek(0)
        except Exception as file_read_err:
            print(f"❌ فشل في قراءة الملف: {str(file_read_err)}")
            messages.error(request, "فشل في قراءة الملف المرفوع")
            return redirect('admin_archive')
        
        # 5. تحديد المجلد إذا كان موجودًا
        folder = None
        if folder_id:
            try:
                folder = ArchiveFolder.objects.get(id=folder_id)
                print(f"📂 تم العثور على المجلد: {folder.name} (ID: {folder.id})")
            except ArchiveFolder.DoesNotExist:
                print(f"❌ المجلد رقم {folder_id} غير موجود")
                messages.error(request, "المجلد المحدد غير موجود")
                return redirect('admin_archive')
        
        # 6. إنشاء وحفظ المستند - باستخدام SQL المباشر لتجنب رفض آلية المستندات التلقائية
        with transaction.atomic():
            from django.db import connection
            
            cursor = connection.cursor()
            
            try:
                # استعلام SQL المباشر لإدراج المستند مع الحقول المطلوبة
                query = """
                INSERT INTO rental_document 
                (title, description, document_type, folder_id, created_by_id, added_by_id,
                file_name, file_type, file_size, file_content, created_at, updated_at, is_auto_created) 
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, NOW(), NOW(), %s) 
                RETURNING id;
                """
                
                # تحضير قيمة المستخدم الحالي
                user_id = None
                if hasattr(request, 'user') and request.user.is_authenticated:
                    user_id = request.user.id
                
                print("📝 تنفيذ استعلام SQL لإنشاء المستند...")
                cursor.execute(query, [
                    title, 
                    description, 
                    document_type, 
                    folder.id if folder else None, 
                    user_id,  # created_by_id
                    user_id,  # added_by_id
                    file_name, 
                    file_type, 
                    file_size, 
                    file_content,
                    False  # is_auto_created - هذا مهم جداً لمنع الرفض
                ])
                
                # الحصول على معرف المستند المدرج
                document_id = cursor.fetchone()[0]
                print(f"✅ تم إنشاء المستند بنجاح: ID={document_id}")
                
                # حفظ الملف المادي
                import os
                from django.conf import settings
                
                # إنشاء مجلد الملفات إذا لم يكن موجوداً
                upload_dir = os.path.join(settings.MEDIA_ROOT, 'documents')
                os.makedirs(upload_dir, exist_ok=True)
                
                # مسار الملف المادي
                file_path = os.path.join(upload_dir, f"doc_{document_id}_{file_name}")
                
                # حفظ الملف
                print(f"💾 حفظ الملف في: {file_path}")
                with open(file_path, 'wb+') as destination:
                    uploaded_file.seek(0)  # إعادة تعيين المؤشر
                    for chunk in uploaded_file.chunks():
                        destination.write(chunk)
                
                # تحديث حقل الملف في قاعدة البيانات
                rel_path = os.path.relpath(file_path, settings.MEDIA_ROOT)
                cursor.execute("UPDATE rental_document SET file = %s WHERE id = %s", [rel_path, document_id])
                
                print(f"✅ تم حفظ الملف المادي في: {rel_path}")
                
                messages.success(request, f"تم رفع المستند '{title}' بنجاح")
                
                # إعادة التوجيه بناءً على المجلد الحالي
                if folder:
                    redirect_url = f"/ar/dashboard/archive/?folder={folder.id}"
                else:
                    redirect_url = "/ar/dashboard/archive/"
                
                print(f"🔄 إعادة التوجيه إلى: {redirect_url}")
                return redirect(redirect_url)
                
            except Exception as sql_err:
                print(f"❌ فشل في تنفيذ استعلام SQL: {str(sql_err)}")
                print(f"تفاصيل الخطأ: {traceback.format_exc()}")
                messages.error(request, f"فشل في إضافة المستند: {str(sql_err)[:100]}")
                return redirect('admin_archive')
        
    except Exception as e:
        print(f"❌ خطأ عام أثناء رفع المستند: {str(e)}")
        print(f"تفاصيل الخطأ: {traceback.format_exc()}")
        messages.error(request, "حدث خطأ أثناء رفع المستند")
    finally:
        # إعادة دالة __init__ الأصلية
        Document.__init__ = original_init
        print("🔄 تمت إعادة دالة __init__ الأصلية")
    
    return redirect('admin_archive')"""
    
    # استبدال الوظيفة في الملف
    updated_content = re.sub(r"def admin_archive_upload\(request\):.*?return redirect\('admin_archive'\)", new_upload_function, content, flags=re.DOTALL)
    
    if updated_content == content:
        print("⚠️ لم يتم تعديل الوظيفة - فشل في استبدال النص")
        return False
    
    # حفظ الملف المحدث
    with open(admin_views_path, "w", encoding="utf-8") as f:
        f.write(updated_content)
    
    print("✅ تم تحديث وظيفة admin_archive_upload بنجاح")
    return True

def fix_upload_form_template():
    """
    تحسين نموذج رفع الملفات المباشر لطباعة معلومات تفصيلية أكثر
    """
    template_path = "templates/admin/archive/direct_upload_form.html"
    
    # تحديث نموذج الرفع لطباعة معلومات تفصيلية للتشخيص
    with open(template_path, "r", encoding="utf-8") as f:
        content = f.read()
    
    # إضافة طباعة معلومات إضافية للتشخيص في JavaScript
    upload_js_section = """<script>
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
                console.log(`ملف محدد: ${file.name}, الحجم: ${formatFileSize(file.size)}, النوع: ${file.type}`);
                
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
            console.log('بدء إرسال النموذج...');
            
            // التحقق من الحقول المطلوبة
            const title = document.getElementById('title').value.trim();
            const file = fileInput.files;
            
            console.log(`التحقق من الحقول: العنوان="${title}", الملف=${file ? file[0].name : 'غير محدد'}`);
            
            if (!title) {
                alert('{% trans "يرجى إدخال عنوان للمستند" %}');
                console.log('خطأ: عنوان المستند غير محدد');
                event.preventDefault();
                return;
            }
            
            if (!file || file.length === 0) {
                alert('{% trans "يرجى اختيار ملف للرفع" %}');
                console.log('خطأ: لم يتم تحديد ملف');
                event.preventDefault();
                return;
            }
            
            // إظهار شريط التقدم
            progress.style.display = 'flex';
            submitButton.disabled = true;
            submitButton.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> {% trans "جاري الرفع..." %}';
            
            // طباعة معلومات النموذج قبل الإرسال
            console.log('إرسال النموذج:');
            console.log(`العنوان: ${title}`);
            console.log(`الوصف: ${document.getElementById('description').value}`);
            console.log(`نوع المستند: ${document.getElementById('document_type').value}`);
            console.log(`الملف: ${file[0].name} (${formatFileSize(file[0].size)})`);
            
            // محاكاة تقدم الرفع
            let width = 0;
            const interval = setInterval(function() {
                if (width >= 90) {
                    clearInterval(interval);
                } else {
                    width += 5;
                    progressBar.style.width = width + '%';
                }
            }, 150);
            
            console.log('تنفيذ الإرسال الفعلي للنموذج');
            return true;
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
</script>"""
    
    # استبدال قسم الجافا سكريبت في النموذج
    import re
    updated_content = re.sub(r'<script>.*?</script>', upload_js_section, content, flags=re.DOTALL)
    
    if updated_content == content:
        print("⚠️ لم يتم تعديل نموذج الرفع - فشل في استبدال قسم JavaScript")
        return False
    
    # حفظ النموذج المحدث
    with open(template_path, "w", encoding="utf-8") as f:
        f.write(updated_content)
    
    print("✅ تم تحديث نموذج رفع الملفات بنجاح")
    return True

def main():
    print("جاري إصلاح مشكلة رفع الملفات...")
    
    success = True
    
    print("\n1. تحديث وظيفة رفع الملفات...")
    if not fix_upload_function():
        success = False
    
    print("\n2. تحسين نموذج رفع الملفات...")
    if not fix_upload_form_template():
        success = False
    
    if success:
        print("\nتم إكمال جميع التغييرات بنجاح!")
        print("يمكنك الآن استخدام نموذج رفع الملفات من خلال أي من الطريقتين:")
        print("   1. زر 'إضافة ملف' في الصفحة الرئيسية للأرشيف")
        print("   2. زر 'رفع مستند (النموذج المباشر)' للنموذج المحسن")
    else:
        print("\nحدثت بعض الأخطاء أثناء التحديثات. راجع الرسائل السابقة للتفاصيل.")

if __name__ == "__main__":
    main()