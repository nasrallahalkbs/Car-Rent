from django.apps import AppConfig


class RentalConfig(AppConfig):
    name = 'rental'
    verbose_name = 'نظام الإيجار'

    def ready(self):
        """
        تنفيذ مهام بدء التشغيل عند بدء التطبيق
        """
        # استيراد إشارات التطبيق
        import rental.signals
        
        # تطبيق إصلاح منع المستندات التلقائية
        from rental.models import Document, ArchiveFolder
        
        # تعديل طريقة save في نموذج Document
        original_document_save = getattr(Document, '_original_save', Document.save)
        
        def custom_document_save(self, *args, **kwargs):
            """طريقة حفظ مخصصة للمستندات تمنع إنشاء المستندات التلقائية"""
            is_new = self.pk is None
            
            # التحقق من إذا كان هذا مستند تلقائي يجب تجاهله
            if is_new and hasattr(self, 'folder') and self.folder:
                # المستندات التلقائية غالباً لا تحتوي على عنوان أو لها عنوان فارغ
                if not self.title or self.title.strip() == '' or self.title == 'بدون عنوان':
                    print(f"⛔ منع إنشاء مستند تلقائي لمجلد: {self.folder.name}")
                    # إيقاف عملية الحفظ عن طريق العودة دون تنفيذ الحفظ الأصلي
                    return None
            
            # استمرار بعملية الحفظ العادية للمستندات غير التلقائية
            return original_document_save(self, *args, **kwargs)
        
        # تخزين نسخة من الدالة الأصلية إذا لم تكن موجودة بالفعل
        if not hasattr(Document, '_original_save'):
            Document._original_save = Document.save
        
        # استبدال دالة save
        Document.save = custom_document_save
        
        # تعديل طريقة save في نموذج ArchiveFolder
        original_folder_save = getattr(ArchiveFolder, '_original_save', ArchiveFolder.save)
        
        def custom_folder_save(self, *args, **kwargs):
            """طريقة حفظ مخصصة للمجلدات تمنع إنشاء المستندات التلقائية"""
            is_new = self.pk is None
            
            # تعيين علامة تجاوز إنشاء المستندات التلقائية
            self._skip_auto_document_creation = True
            
            # استخدام الطريقة الأصلية للحفظ
            result = original_folder_save(self, *args, **kwargs)
            
            # بعد الحفظ، حذف أي مستندات تلقائية قد تكون أنشئت
            if is_new:
                try:
                    # حذف المستندات التلقائية
                    auto_docs = Document.objects.filter(
                        folder=self, 
                        title__in=['', 'بدون عنوان', None]
                    )
                    
                    if auto_docs.exists():
                        count = auto_docs.count()
                        auto_docs.delete()
                        print(f"🗑️ تم حذف {count} مستند تلقائي بعد إنشاء المجلد")
                except Exception as e:
                    print(f"❌ حدث خطأ أثناء حذف المستندات التلقائية: {str(e)}")
            
            return result
        
        # تخزين نسخة من الدالة الأصلية إذا لم تكن موجودة بالفعل
        if not hasattr(ArchiveFolder, '_original_save'):
            ArchiveFolder._original_save = ArchiveFolder.save
        
        # استبدال دالة save
        ArchiveFolder.save = custom_folder_save
        
        print("✅ تم تطبيق إصلاح منع المستندات التلقائية عند بدء تشغيل التطبيق")