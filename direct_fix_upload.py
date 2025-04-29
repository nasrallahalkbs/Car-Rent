"""
إصلاح مباشر لمشكلة رفع الملفات
"""
import re
import os
import importlib
import sys

def fix_document_signals():
    """تعديل طريقة تعامل النظام مع إشارات المستندات التلقائية"""
    print("تعديل آلية إشارات المستندات التلقائية...")
    
    from rental.models import Document
    from django.db.models.signals import pre_save, post_save
    from rental import signals
    
    # فصل جميع إشارات pre_save للمستندات
    print("فصل إشارات pre_save عن نموذج Document...")
    pre_save.disconnect(dispatch_uid="prevent_auto_document_creation", sender=Document)
    
    # طباعة رسالة تأكيد
    print("✓ تم فصل إشارات رفض المستندات التلقائية بنجاح")
    
    # تسجيل الإشارة من جديد مع معالج محسن
    def improved_prevent_auto_document_creation(sender, instance, **kwargs):
        """معالج محسن يسمح برفع الملفات المباشر ويمنع فقط المستندات التلقائية"""
        # السماح للمستندات التي تم تعيين علامة التجاوز عليها
        if getattr(instance, '_ignore_auto_document_signal', False):
            print("✓ السماح بالمستند لأنه يحمل علامة التجاوز")
            return
            
        # السماح للمستندات التي تم إنشاؤها من خلال واجهة المستخدم
        # هذه المستندات يتم تحميل ملف معها عادة أو لها عنوان مخصص
        if instance.file or (instance.title and instance.title != "بدون عنوان"):
            print(f"✓ السماح بالمستند: {instance.title} (تم إنشاؤه من واجهة المستخدم)")
            return
            
        # منع المستندات التلقائية فقط (بدون عنوان وبدون ملف)
        if instance.title == "بدون عنوان" or not instance.title:
            print("⛔ رفض مستند تلقائي")
            instance._auto_rejected = True
            raise Exception("تم رفض المستند التلقائي")
    
    # تسجيل المعالج الجديد
    pre_save.connect(
        improved_prevent_auto_document_creation,
        sender=Document,
        dispatch_uid="improved_prevent_auto_document_creation"
    )
    
    print("✓ تم تسجيل معالج محسن للمستندات التلقائية")
    
    return True

def fix_admin_archive_upload():
    """تحسين وظيفة رفع الملفات في admin_views.py"""
    print("تحسين وظيفة رفع الملفات...")
    
    admin_views_path = "rental/admin_views.py"
    
    with open(admin_views_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # إضافة تسجيل معلومات أفضل وتوضيح
    improved_function = '''
@login_required
@admin_required
def admin_archive_upload(request):
    """وظيفة رفع الملفات بطريقة محسنة"""
    import traceback
    
    # طباعة معلومات الطلب للتشخيص
    print("بدء معالجة طلب رفع مستند جديد")
    print(f"طريقة الطلب: {request.method}")
    
    if request.method != 'POST':
        messages.error(request, "طريقة طلب غير صالحة")
        return redirect('admin_archive')
    
    # استخراج البيانات المرسلة
    title = request.POST.get('title', '').strip()
    description = request.POST.get('description', '')
    folder_id = request.POST.get('folder', None)
    document_type = request.POST.get('document_type', 'other')
    
    print(f"البيانات المستلمة: العنوان='{title}', النوع='{document_type}', المجلد={folder_id}")
    
    # التحقق من وجود البيانات المطلوبة
    if not title:
        messages.error(request, "يرجى إدخال عنوان للمستند")
        return redirect('admin_archive')
    
    if 'file' not in request.FILES:
        messages.error(request, "يرجى تحديد ملف للتحميل")
        return redirect('admin_archive')
    
    # معالجة الملف المرفوع
    uploaded_file = request.FILES['file']
    file_name = uploaded_file.name
    file_type = uploaded_file.content_type
    file_size = uploaded_file.size
    
    print(f"معلومات الملف: اسم='{file_name}', النوع='{file_type}', الحجم={file_size} بايت")
    
    # تحديد المجلد إذا كان موجوداً
    folder = None
    if folder_id:
        try:
            folder = ArchiveFolder.objects.get(id=folder_id)
            print(f"تم تحديد المجلد: {folder.name} (ID: {folder.id})")
        except ArchiveFolder.DoesNotExist:
            messages.error(request, "المجلد المحدد غير موجود")
            return redirect('admin_archive')
    
    try:
        # إنشاء المستند في معاملة واحدة
        with transaction.atomic():
            print("بدء معاملة قاعدة البيانات...")
            
            # قراءة محتوى الملف
            file_content = uploaded_file.read()
            print(f"تم قراءة محتوى الملف: {len(file_content)} بايت")
            
            # إعادة مؤشر الملف للبداية
            uploaded_file.seek(0)
            
            # إنشاء المستند
            document = Document(
                title=title,
                description=description,
                document_type=document_type,
                folder=folder,
                file_name=file_name,
                file_type=file_type,
                file_size=file_size,
                file_content=file_content,
                created_by=request.user,
                added_by=request.user,
                is_auto_created=False  # هذا مهم جداً
            )
            
            # تعيين علامة تجاوز إشارة المستندات التلقائية
            document._ignore_auto_document_signal = True
            print("تم تعيين علامة تجاوز الإشارة على المستند")
            
            # حفظ المستند
            document.save()
            print(f"تم حفظ المستند بنجاح: ID={document.id}")
            
            # تعيين الملف المرفوع
            document.file = uploaded_file
            document.save(update_fields=['file'])
            print("تم حفظ الملف المرفوع")
            
            # عرض رسالة نجاح للمستخدم
            messages.success(request, f"تم رفع المستند '{title}' بنجاح")
            
            # إعادة التوجيه بناءً على المجلد الحالي
            if folder:
                return redirect('admin_archive_folder', folder_id=folder.id)
            else:
                return redirect('admin_archive')
                
    except Exception as e:
        print(f"حدث خطأ أثناء رفع المستند: {str(e)}")
        print(traceback.format_exc())
        messages.error(request, f"حدث خطأ أثناء رفع المستند: {str(e)[:100]}")
    
    return redirect('admin_archive')
'''
    
    # استبدال الدالة القديمة بالدالة المحسنة
    pattern = r'@login_required\s+@admin_required\s+def admin_archive_upload\(request\):.*?return redirect\(\'admin_archive\'\)'
    new_content = re.sub(pattern, improved_function, content, flags=re.DOTALL)
    
    # التحقق من نجاح التعديل
    if new_content == content:
        print("لم يتم تعديل الدالة. فشل في استبدال النص.")
        return False
    
    # حفظ الملف المعدل
    with open(admin_views_path, 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    print("✓ تم تحديث وظيفة رفع الملفات بنجاح")
    return True

def main():
    """الدالة الرئيسية لتنفيذ الإصلاحات"""
    print("=== بدء إصلاح مشكلة رفع الملفات ===")
    
    # إضافة مسار المشروع للأنظمة
    sys.path.append(os.getcwd())
    
    success = True
    
    # 1. تعديل آلية إشارات المستندات التلقائية
    print("\n1. تعديل آلية إشارات المستندات التلقائية...")
    try:
        if not fix_document_signals():
            success = False
    except Exception as e:
        print(f"فشل في تعديل إشارات المستندات: {str(e)}")
        success = False
    
    # 2. تحسين وظيفة رفع الملفات
    print("\n2. تحسين وظيفة رفع الملفات...")
    try:
        if not fix_admin_archive_upload():
            success = False
    except Exception as e:
        print(f"فشل في تحسين وظيفة رفع الملفات: {str(e)}")
        success = False
    
    # طباعة ملخص
    if success:
        print("\n=== تم إكمال إصلاح مشكلة رفع الملفات بنجاح! ===")
        print("يمكنك الآن استخدام أي من الطرق التالية لرفع الملفات:")
        print("1. الضغط على زر 'إضافة ملف' في صفحة الأرشيف الإلكتروني")
        print("2. استخدام النموذج المباشر من خلال زر 'رفع مستند (النموذج المباشر)'")
    else:
        print("\n=== فشل في إصلاح مشكلة رفع الملفات بالكامل ===")
        print("يرجى مراجعة الأخطاء أعلاه وإعادة المحاولة")

if __name__ == "__main__":
    main()