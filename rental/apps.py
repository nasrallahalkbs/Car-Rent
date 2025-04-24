from django.apps import AppConfig


class RentalConfig(AppConfig):
    name = 'rental'
    verbose_name = 'نظام الإيجار'

    def ready(self):
        """تشغيل التنظيف والحماية عند بدء تشغيل التطبيق"""
        try:
            # تشغيل الحماية والتنظيف عند بدء التشغيل
            import rental.signals  # لتسجيل الإشارات
            try:
                from rental.guard import start
                start()  # تشغيل الحماية
                print("✅ تم تفعيل الحماية عند بدء التشغيل")
            except Exception as e:
                print(f"⚠️ لم يتم تفعيل نظام الحماية: {str(e)}")
            
            # تحسين الحماية مباشرة
            from django.db.models import Q
            from rental.models import Document, ArchiveFolder
            
            # تنظيف مبدئي للمستندات التلقائية
            auto_docs = Document.objects.filter(
                Q(title__isnull=True) | Q(title='') | Q(title='بدون عنوان')
            )
            if auto_docs.exists():
                count = auto_docs.count()
                auto_docs.delete()
                print(f"🧹 تنظيف {count} مستند تلقائي عند بدء التشغيل")
            
            # تشغيل التنظيف التلقائي
            try:
                from rental.auto_cleaner import start_auto_cleaner
                start_auto_cleaner()
                print("✅ تم تشغيل التنظيف التلقائي")
            except Exception as e:
                print(f"⚠️ لم يتم تشغيل التنظيف التلقائي: {str(e)}")
            
            print("✅ تم تفعيل نظام منع المستندات التلقائية")
            
        except Exception as e:
            print(f"⚠️ حدث خطأ أثناء تهيئة التطبيق: {str(e)}")
            import traceback
            traceback.print_exc()