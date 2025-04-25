"""
تحديث عرض الأرشيف الإلكتروني ليكون مشابه لمستكشف ويندوز
"""
import json
import functools
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.utils.translation import gettext as _, get_language
from django.utils import timezone
from django.contrib import messages
from .views import get_template_by_language
from .models import ArchiveFolder, Document

def admin_required(view_func):
    """
    Decorator for views that checks if the user is an admin.
    """
    @functools.wraps(view_func)
    def wrapper(request, *args, **kwargs):
        # Debug output for admin_required
        print(f"Admin check for {request.user}, authenticated: {request.user.is_authenticated}")
        if not request.user.is_authenticated:
            messages.error(request, "يرجى تسجيل الدخول للوصول إلى لوحة التحكم")
            return redirect('login')
        elif not request.user.is_admin:
            messages.error(request, "غير مصرح لك بالوصول إلى هذه الصفحة!")
            return redirect('index')

        # Set a global current_user variable for admin templates
        request.current_user = request.user
        return view_func(request, *args, **kwargs)
    return wrapper

def get_folder_tree(request):
    """بناء شجرة المجلدات للعرض في jsTree"""
    from django.utils.translation import get_language
    current_language = get_language()
    is_english = current_language == 'en'
    
    # بناء شجرة المجلدات
    def build_tree(folder):
        """بناء شجرة المجلدات بشكل تكراري"""
        result = {
            'id': f'folder-{folder.id}',
            'text': folder.name,
            'icon': 'fas fa-folder',
            'type': 'folder',
            'children': []
        }
        
        # إضافة المجلدات الفرعية
        for child in ArchiveFolder.objects.filter(parent=folder).order_by('name'):
            result['children'].append(build_tree(child))
        
        return result
    
    # بدء بناء الشجرة
    folder_tree = []
    
    # إضافة علامة الجذر
    folder_tree.append({
        'id': 'root',
        'text': _('الرئيسية'),
        'icon': 'fas fa-home',
        'type': 'root',
        'state': {
            'opened': True
        }
    })
    
    # إضافة المجلدات الرئيسية
    root_folders = ArchiveFolder.objects.filter(parent=None).order_by('name')
    for folder in root_folders:
        folder_tree.append(build_tree(folder))
    
    return folder_tree

def clean_document_list(documents):
    """تنظيف المستندات الوهمية من قائمة المستندات المعروضة"""
    if documents:
        # فقط استبعاد المستندات التي ليس لها عنوان أو عناوين فارغة تمامًا
        return documents.filter(title__isnull=False).exclude(title="").exclude(title=" ")
    return documents

@login_required
@admin_required
def admin_archive_windows(request):
    """عرض الأرشيف الإلكتروني بتصميم مشابه لمستكشف ويندوز"""
    from django.utils.translation import get_language
    current_language = get_language()
    is_english = current_language == 'en'
    is_rtl = current_language == 'ar'
    
    # الحصول على معلمات URL
    folder_param = request.GET.get('folder', None)
    document_param = request.GET.get('document', None)
    action_param = request.GET.get('action', None)
    
    print(f"DEBUG - معلمة المجلد: {folder_param}")
    print(f"DEBUG - معلمة المستند: {document_param}")
    print(f"DEBUG - معلمة الإجراء: {action_param}")
    
    # معالجة إضافة مجلد جديد
    if action_param == 'add_folder' and request.method == 'POST':
        name = request.POST.get('name', '')
        description = request.POST.get('description', '')
        parent_id = request.POST.get('parent', None)
        
        if name:
            try:
                # البحث عن المجلد الأب إذا تم تحديده
                parent = None
                if parent_id:
                    try:
                        parent = ArchiveFolder.objects.get(id=parent_id)
                    except ArchiveFolder.DoesNotExist:
                        pass
                
                # إنشاء المجلد بطريقة آمنة تماماً تمنع إنشاء المستندات التلقائية
                # استخدام SQL المباشر لتجاوز آليات النظام
                from django.db import connection, transaction
                
                try:
                    with transaction.atomic():
                        cursor = connection.cursor()
                        
                        # تعطيل المحفزات (triggers) أثناء عملية الإنشاء
                        cursor.execute("SET session_replication_role = 'replica';")
                        
                        # الحصول على معرف المستخدم المنشئ إذا وجد
                        created_by_id = None
                        if request.user.is_authenticated:
                            created_by_id = request.user.id
                        
                        # تحضير قيمة parent_id
                        parent_id = None
                        if parent:
                            parent_id = parent.id
                        
                        # إنشاء المجلد مباشرة في قاعدة البيانات
                        sql = """
                        INSERT INTO rental_archivefolder 
                        (name, parent_id, created_at, updated_at, description, created_by_id, is_system_folder, folder_type) 
                        VALUES (%s, %s, NOW(), NOW(), %s, %s, %s, %s)
                        RETURNING id;
                        """
                        
                        cursor.execute(sql, [
                            name, 
                            parent_id, 
                            description, 
                            created_by_id,
                            False,  # is_system_folder
                            None    # folder_type
                        ])
                        
                        folder_id = cursor.fetchone()[0]
                        
                        # إعادة تفعيل المحفزات
                        cursor.execute("SET session_replication_role = 'origin';")
                        
                        # الحصول على كائن المجلد من قاعدة البيانات
                        folder = ArchiveFolder.objects.get(id=folder_id)
                        
                        # للتأكد - حذف أي مستندات قد تكون أنشئت بعد استعادة المحفزات
                        Document.objects.filter(folder=folder, title__in=['', 'بدون عنوان', None]).delete()
                        
                        print(f"DEBUG - تم إنشاء مجلد جديد: {folder.name} بأسلوب SQL المباشر الآمن ومنع أي مستندات تلقائية")
                except Exception as e:
                    print(f"ERROR - حدث خطأ أثناء إنشاء المجلد باستخدام SQL المباشر: {str(e)}")
                    # في حالة حدوث خطأ، ننشئ المجلد بالطريقة العادية المحسنة
                    folder = ArchiveFolder(name=name, description=description, parent=parent)
                    folder._skip_auto_document_creation = True  # منع المستندات التلقائية
                    # تعطيل المستندات التلقائية تماماً
                    folder.disable_auto_documents = True
                    folder._skip_auto_document_creation = True
                    folder._prevent_auto_docs = True
                    folder.save()
                    
                    # التنظيف الفوري بعد الحفظ
                    Document.objects.filter(folder=folder, title__in=['', 'بدون عنوان', None]).delete()
                    print(f"DEBUG - تم إنشاء المجلد باستخدام الطريقة البديلة: {folder.name}")
                messages.success(request, f"تم إنشاء المجلد '{name}' بنجاح")
                
                # إعادة توجيه إلى المجلد الجديد
                return redirect(f"{request.path}?folder={folder.id}")
            except Exception as e:
                # لوج أي استثناءات للمساعدة في عملية التصحيح
                print(f"ERROR - فشل في إنشاء المجلد: {str(e)}")
                messages.error(request, f"حدث خطأ أثناء إنشاء المجلد: {str(e)}")
        else:
            messages.error(request, "يرجى إدخال اسم المجلد")
    
    # معالجة إضافة ملف جديد
    if action_param == 'add_file' and request.method == 'POST':
        title = request.POST.get('title', '')
        description = request.POST.get('description', '')
        folder_id = request.POST.get('folder', None)
        uploaded_file = request.FILES.get('file', None)
        
        if title and uploaded_file:
            # البحث عن المجلد المستهدف إذا تم تحديده
            folder = None
            if folder_id:
                try:
                    folder = ArchiveFolder.objects.get(id=folder_id)
                except:
                    pass
            
            # حساب حجم الملف بوحدة البايت
            file_size = uploaded_file.size
            
            # تأكد من أن المستند ليس تلقائياً
            if not title or title.strip() == '' or title == 'بدون عنوان':
                print(f"DEBUG - محاولة إنشاء مستند تلقائي مرفوضة!")
                messages.error(request, "لا يمكن إنشاء مستند بدون عنوان")
                return redirect(request.path)
            
            # إنشاء مستند جديد (ملف) بطريقة آمنة
            try:
                # إضافة علامة واضحة لمنع إنشاء مستندات بشكل تلقائي
                if folder is not None:
                    if not hasattr(folder, '_skip_auto_document_creation'):
                        setattr(folder, '_skip_auto_document_creation', True)
                    
                # قراءة معلومات الملف لتخزينه في قاعدة البيانات
                file_name = uploaded_file.name
                file_type = uploaded_file.content_type
                file_content = uploaded_file.read()
                
                # إنشاء المستند مع تخزين الملف في قاعدة البيانات
                document = Document.objects.create(
                    title=title,
                    description=description,
                    document_type='other',  # استخدام القيمة الافتراضية 'other'
                    # تخزين معلومات الملف في قاعدة البيانات
                    file_name=file_name,
                    file_type=file_type,
                    file_size=file_size,
                    file_content=file_content,
                    document_date=timezone.now().date(),
                    related_to='other',  # استخدام القيمة الافتراضية 'other'
                    added_by=request.user if request.user.is_authenticated else None,
                    folder=folder
                )
                
                print(f"DEBUG - تم إنشاء مستند جديد: {document.title}")
            except Exception as e:
                print(f"ERROR - فشل في إنشاء المستند: {str(e)}")
                messages.error(request, f"حدث خطأ أثناء إنشاء المستند: {str(e)}")
                return redirect(request.path)
            messages.success(request, f"تم إضافة الملف '{title}' بنجاح")
            
            # إعادة توجيه
            if folder:
                return redirect(f"{request.path}?folder={folder.id}")
            else:
                return redirect(request.path)
        else:
            if not title:
                messages.error(request, "يرجى إدخال عنوان الملف")
            if not uploaded_file:
                messages.error(request, "يرجى اختيار ملف للرفع")
    
    # الحصول على مجلدات الجذر وتجاهل المجلدات بدون اسم
    try:
        # استبعاد المجلدات بدون اسم أو باسم "بدون اسم"
        root_folders = ArchiveFolder.objects.filter(
            parent=None,
            name__isnull=False
        ).exclude(
            name__in=['بدون اسم', '', ' ']
        ).order_by('name')
        
        # الحصول على جميع المجلدات مع استبعاد المجلدات التلقائية
        all_folders = ArchiveFolder.objects.filter(
            name__isnull=False
        ).exclude(
            name__in=['بدون اسم', '', ' ']
        ).order_by('name')
        
        print(f"DEBUG - عدد المجلدات الرئيسية المفلترة: {root_folders.count()}")
        
        # حذف أي مجلدات غير صالحة تلقائيًا
        invalid_folders = ArchiveFolder.objects.filter(
            name__in=['بدون اسم', '', ' ']
        )
        if invalid_folders.exists():
            print(f"DEBUG - حذف {invalid_folders.count()} مجلد غير صالح تلقائيًا")
            invalid_folders.delete()
    except Exception as e:
        print(f"ERROR - حدثت مشكلة في استرجاع المجلدات: {str(e)}")
        # تعيين قوائم فارغة في حالة حدوث خطأ
        root_folders = ArchiveFolder.objects.none()
        all_folders = ArchiveFolder.objects.none()
    
    # الحصول على المستندات والمجلدات الفرعية
    documents = []
    subfolders = []
    current_folder = None
    folder_path = []
    
    if folder_param:
        try:
            # تحقق إذا كان معرف المجلد عدداً صحيحاً
            try:
                folder_id = int(folder_param)
                # محاولة العثور على المجلد
                current_folder = ArchiveFolder.objects.get(id=folder_id)
                # الحصول على المجلدات الفرعية والمستندات
                subfolders = ArchiveFolder.objects.filter(parent=current_folder).order_by('name')
                documents = Document.objects.filter(folder=current_folder).order_by('-created_at')
                
                # طباعة عدد المستندات قبل التنظيف للتشخيص
                print(f"DEBUG - عدد المستندات قبل التنظيف: {documents.count()}")
                # تنظيف المستندات
                documents = clean_document_list(documents)
                print(f"DEBUG - عدد المستندات بعد التنظيف: {documents.count()}")
                
                # بناء مسار المجلد
                folder_path = []
                temp_folder = current_folder
                while temp_folder:
                    folder_path.insert(0, temp_folder)
                    temp_folder = temp_folder.parent
                
                print(f"DEBUG - المجلد الحالي: {current_folder.name}")
                print(f"DEBUG - عدد المجلدات الفرعية: {subfolders.count()}")
                print(f"DEBUG - عدد المستندات: {documents.count()}")
            except ValueError:
                # إذا كان معرف المجلد ليس عدداً صحيحاً، نستخدم العرض الافتراضي
                print(f"DEBUG - استخدام العرض الافتراضي للمجلد: {folder_param}")
        except ArchiveFolder.DoesNotExist:
            print(f"DEBUG - المجلد غير موجود: {folder_param}")
    else:
        # عرض المستندات في المجلد الرئيسي (بدون مجلد)
        documents = Document.objects.filter(folder__isnull=True).order_by('-created_at')
        
        # طباعة عدد المستندات قبل التنظيف للتشخيص
        print(f"DEBUG - المجلد الرئيسي - عدد المستندات قبل التنظيف: {documents.count()}")
        # تنظيف المستندات
        documents = clean_document_list(documents)
        print(f"DEBUG - المجلد الرئيسي - عدد المستندات بعد التنظيف: {documents.count()}")
    
    # بناء شجرة المجلدات للعرض في jsTree
    folder_tree = get_folder_tree(request)
    
    # إعداد سياق البيانات
    # إضافة وقت حالي لمنع التخزين المؤقت
    from datetime import datetime
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")
    
    context = {
        'root_folders': root_folders,
        'subfolders': subfolders,
        'documents': documents,
        'current_folder': current_folder,
        'folder_path': folder_path,
        'folder_param': folder_param,
        'document_param': document_param,
        'all_folders': all_folders,  # إضافة قائمة كاملة بجميع المجلدات
        'is_english': is_english,
        'is_rtl': is_rtl,
        'folder_tree': json.dumps(folder_tree),
        'active_section': 'archive',
        'current_date_time': current_time  # إضافة وقت حالي لمنع التخزين المؤقت
    }
    
    # استخدام قالب مشابه لمستكشف ويندوز
    return render(request, 'admin/archive/windows_explorer_enhanced.html', context)