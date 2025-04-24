from django.apps import AppConfig

class RentalConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'rental'
    
    def ready(self):
        """تشغيل الإشارات عند تهيئة التطبيق"""
        import rental.signals