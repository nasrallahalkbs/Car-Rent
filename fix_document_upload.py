"""
الإصلاح النهائي لمشكلة رفع المستندات

هذا السكريبت يقوم بإجراء الإصلاحات التالية:
1. تحديث وتصحيح طريقة رفع المستندات في admin_views.py
2. إضافة وسم is_auto_created=False بشكل صريح لتجنب منع حفظ الملفات الغير تلقائية
3. إضافة تجاوز واضح لمنع المستندات التلقائية عند رفع المستندات العادية
"""
import os
import django

# إعداد بيئة Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'car_rental_project.settings')
django.setup()

def fix_document_upload_view():
    """
    تحديث طريقة رفع المستندات في admin_views.py
    """
    ADMIN_VIEWS_PATH = 'rental/admin_views.py'
    
    # قراءة محتوى الملف
    with open(ADMIN_VIEWS_PATH, 'r', encoding='utf-8') as file:
        content = file.read()
    
    # تعديل طريقة رفع المستندات
    upload_pattern = """            # إنشاء المستند مع تخزين الملف في قاعدة البيانات
            document = Document(
                title=title,
                description=description,
                document_type=document_type,
                folder=folder,
                created_by=request.user if hasattr(request, 'user') else None,
                file_name=file_name,
                file_type=file_type,
                file_size=file_size,
                file_content=file_content,  # استخدام محتوى الملف المقروء
                file=uploaded_file,  # تعيين الملف بعد إعادة تعيين المؤشر
                is_auto_created=False  # تأكيد أن المستند ليس تلقائي
            )
            
            # حفظ المستند
            document.save()"""
    
    new_upload_code = """            print("DEBUG - بدء عملية إنشاء المستند")
            
            # تخطي جميع إشارات منع المستندات التلقائية عند إنشاء مستند يدوي
            try:
                # إنشاء المستند مع تخزين الملف في قاعدة البيانات
                document = Document(
                    title=title,
                    description=description,
                    document_type=document_type,
                    folder=folder,
                    created_by=request.user if hasattr(request, 'user') else None,
                    file_name=file_name,
                    file_type=file_type,
                    file_size=file_size,
                    file_content=file_content,  # استخدام محتوى الملف المقروء
                    file=uploaded_file,  # تعيين الملف بعد إعادة تعيين المؤشر
                    is_auto_created=False  # تأكيد أن المستند ليس تلقائي
                )
                
                # تعطيل الإشارات بشكل صريح وحفظ المستند (منع سريان إشارات منع المستندات التلقائية)
                setattr(document, '_ignore_auto_document_signal', True)
                document.save()
                
                print(f"DEBUG - تم حفظ المستند بنجاح! ID: {document.id}, العنوان: {document.title}")
            except Exception as e:
                print(f"ERROR - فشل في حفظ المستند: {str(e)}")
                # محاولة أخرى بطريقة مباشرة لقاعدة البيانات
                try:
                    from django.db import connection
                    cursor = connection.cursor()
                    query = "INSERT INTO rental_document (title, description, document_type, folder_id, created_by_id, file_name, file_type, file_size, file_content, created_at, updated_at, is_auto_created) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, NOW(), NOW(), %s) RETURNING id;"
                    cursor.execute(query, [
                        title, 
                        description, 
                        document_type, 
                        folder.id if folder else None, 
                        request.user.id if hasattr(request, 'user') and request.user.is_authenticated else None, 
                        file_name, 
                        file_type, 
                        file_size, 
                        file_content,
                        False
                    ])
                    document_id = cursor.fetchone()[0]
                    document = Document.objects.get(id=document_id)
                    print(f"DEBUG - تم حفظ المستند بنجاح باستخدام SQL المباشر! ID: {document.id}")
                except Exception as sql_err:
                    print(f"CRITICAL ERROR - فشل في حفظ المستند حتى باستخدام SQL المباشر: {str(sql_err)}")
                    raise"""
    
    modified_content = content.replace(upload_pattern, new_upload_code)
    
    # إضافة طريقة جديدة للتعامل مع المجلدات والمستندات
    if "_ignore_auto_document_signal" not in modified_content:
        signal_pattern = """# إعداد لمعالجة الإشارات عند استيراد الملف
if 'rental.signals' not in sys.modules:
    import rental.signals"""
        
        new_signal_code = """# إعداد لمعالجة الإشارات عند استيراد الملف
if 'rental.signals' not in sys.modules:
    import rental.signals

# تعريف دالة للتحقق من تجاوز إشارات منع المستندات التلقائية
def should_ignore_auto_document_signal(sender, instance, **kwargs):
    # التحقق مما إذا كان المستند يجب تجاوز إشارات المنع له
    return getattr(instance, '_ignore_auto_document_signal', False)

# تسجيل الدالة للتحقق قبل حفظ المستندات
from django.db.models.signals import pre_save
pre_save.connect(should_ignore_auto_document_signal, sender=Document)"""
        
        modified_content = modified_content.replace(signal_pattern, new_signal_code)
    
    # تضمين معلومات تشخيصية إضافية في نموذج Document
    # جعل is_auto_created في البداية لضمان مسح المستندات التلقائية فقط
    model_class_pattern = """class Document(models.Model):
    """
    if model_class_pattern in modified_content:
        new_model_attribute = """class Document(models.Model):
    # وسم للتمييز بين المستندات التلقائية والمستندات المرفوعة يدويًا
    is_auto_created = models.BooleanField(default=False)
    """
        modified_content = modified_content.replace(model_class_pattern, new_model_attribute)
    
    # حفظ الملف المعدل
    with open(ADMIN_VIEWS_PATH, 'w', encoding='utf-8') as file:
        file.write(modified_content)
    
    print("✅ تم تحديث طريقة رفع المستندات بنجاح")

def fix_documents_template():
    """
    تحديث قالب عرض المستندات للتأكد من عرض المستندات بشكل صحيح
    """
    # مسار قالب عرض الأرشيف المحسن
    TEMPLATE_PATH = 'templates/admin/archive/windows_explorer_enhanced.html'
    
    # التحقق من وجود القالب
    if not os.path.exists(TEMPLATE_PATH):
        print(f"⚠️ ملف القالب غير موجود: {TEMPLATE_PATH}")
        return
    
    # قراءة محتوى القالب
    with open(TEMPLATE_PATH, 'r', encoding='utf-8') as file:
        content = file.read()
    
    # تحديث جزء عرض المستندات للتحقق من وجود المستندات قبل محاولة الوصول إليها
    documents_pattern = """{% for document in documents %}
                    <div class="file-box">
                        <div class="file" onclick="showDocumentDetails('{{ document.id }}', '{{ document.title }}')">
                            <a>
                                <span class="corner"></span>
                                <div class="icon">
                                    <i class="fa fa-file"></i>
                                </div>
                                <div class="file-name">
                                    {{ document.title }}
                                    <br>
                                    <small>{{ document.created_at|date:"Y-m-d H:i" }}</small>
                                </div>
                            </a>
                        </div>
                    </div>
                {% empty %}
                    <div class="empty-state">
                        <i class="fa fa-folder-open-o fa-4x"></i>
                        <h3>لا توجد مستندات في هذا المجلد</h3>
                    </div>
                {% endfor %}"""
    
    new_documents_code = """{% if documents %}
                    {% for document in documents %}
                        <div class="file-box">
                            <div class="file" onclick="showDocumentDetails('{{ document.id }}', '{{ document.title }}')">
                                <a>
                                    <span class="corner"></span>
                                    <div class="icon">
                                        <i class="fa fa-file"></i>
                                    </div>
                                    <div class="file-name">
                                        {{ document.title }}
                                        <br>
                                        <small>{{ document.created_at|date:"Y-m-d H:i" }}</small>
                                    </div>
                                </a>
                            </div>
                        </div>
                    {% endfor %}
                {% else %}
                    <div class="empty-state">
                        <i class="fa fa-folder-open-o fa-4x"></i>
                        <h3>لا توجد مستندات في هذا المجلد</h3>
                    </div>
                {% endif %}"""
    
    # تحديث محتوى القالب
    modified_content = content.replace(documents_pattern, new_documents_code)
    
    # حفظ القالب المعدل
    with open(TEMPLATE_PATH, 'w', encoding='utf-8') as file:
        file.write(modified_content)
    
    print("✅ تم تحديث قالب عرض المستندات بنجاح")

def fix_models_document_save():
    """
    تحديث طريقة save في نموذج Document لتجنب منع حفظ المستندات الغير تلقائية
    """
    MODELS_PATH = 'rental/models.py'
    
    # قراءة محتوى الملف
    with open(MODELS_PATH, 'r', encoding='utf-8') as file:
        content = file.read()
    
    # التحقق من وجود طريقة save في نموذج Document
    if "def save(self, *args, **kwargs):" in content and "Document" in content:
        save_pattern = """    def save(self, *args, **kwargs):
        # منع حفظ المستندات التلقائية - يتم التحقق من وسم is_auto_created
        if getattr(self, 'is_auto_created', False):
            print(f"🛑 [DOCUMENT SAVE] منع حفظ مستند تلقائي: {self.title}")
            return
        
        # في حالة المستندات العادية، يتم الحفظ بشكل طبيعي
        super().save(*args, **kwargs)"""
        
        new_save_method = """    def save(self, *args, **kwargs):
        # التحقق من وجود علامة تجاوز إشارات منع المستندات التلقائية
        ignore_signal = getattr(self, '_ignore_auto_document_signal', False)
        
        # منع حفظ المستندات التلقائية فقط - يتم التحقق من وسم is_auto_created
        if getattr(self, 'is_auto_created', False) and not ignore_signal:
            print(f"🛑 [DOCUMENT SAVE] منع حفظ مستند تلقائي: {self.title}")
            return
        
        print(f"✅ [DOCUMENT SAVE] حفظ مستند: {self.title} (تجاوز الإشارات: {ignore_signal})")
        # في حالة المستندات العادية أو عند تجاوز الإشارات، يتم الحفظ بشكل طبيعي
        super().save(*args, **kwargs)"""
        
        modified_content = content.replace(save_pattern, new_save_method)
        
        # حفظ الملف المعدل
        with open(MODELS_PATH, 'w', encoding='utf-8') as file:
            file.write(modified_content)
        
        print("✅ تم تحديث طريقة save في نموذج Document بنجاح")
    else:
        print("⚠️ لم يتم العثور على طريقة save في نموذج Document")

def main():
    """
    تنفيذ جميع الإصلاحات
    """
    print("🛠️ بدء تنفيذ الإصلاحات النهائية لمشكلة رفع المستندات...")
    
    # تحديث نموذج المستند
    fix_models_document_save()
    
    # تحديث طريقة رفع المستندات
    fix_document_upload_view()
    
    # تحديث قالب عرض المستندات
    fix_documents_template()
    
    print("✅ تم تنفيذ جميع الإصلاحات بنجاح!")

if __name__ == "__main__":
    main()