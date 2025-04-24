# -*- coding: utf-8 -*-
"""
ملف الحماية الدائمة ضد المستندات التلقائية
تم إنشاؤه تلقائيًا
"""

def start():
    """تطبيق حماية المستندات التلقائية"""
    from rental.models import Document, ArchiveFolder
    from django.db.models import Q
    
    # حفظ طرق الحفظ الأصلية
    if not hasattr(Document, '_guarded_save'):
        Document._guarded_save = Document.save
    
    if not hasattr(ArchiveFolder, '_guarded_save'):
        ArchiveFolder._guarded_save = ArchiveFolder.save
    
    # تعريف طرق الحفظ الآمنة
    def safe_document_save(self, *args, **kwargs):
        """منع إنشاء المستندات التلقائية بشكل قاطع"""
        # فحص ما إذا كان هذا مستند جديد
        if not self.pk:
            # فحص ما إذا كان عنوان المستند فارغ أو "بدون عنوان"
            if not self.title or self.title.strip() == '' or self.title == 'بدون عنوان':
                print(f"🛑 [GUARD] منع إنشاء مستند تلقائي: '{self.title}'")
                return None
        
        # استخدام الطريقة الأصلية للمستندات العادية
        return self._guarded_save(*args, **kwargs)
    
    def safe_folder_save(self, *args, **kwargs):
        """منع المستندات التلقائية في المجلدات"""
        self._skip_auto_document_creation = True
        if hasattr(self, 'disable_auto_documents'):
            self.disable_auto_documents = True
        result = self._guarded_save(*args, **kwargs)
        if self.pk:
            Document.objects.filter(folder=self, title__in=['', 'بدون عنوان', None]).delete()
        return result
    
    # تطبيق طرق الحفظ الآمنة
    Document.save = safe_document_save
    ArchiveFolder.save = safe_folder_save
    
    print("🛡️ تم تفعيل الحماية الدائمة ضد المستندات التلقائية")
