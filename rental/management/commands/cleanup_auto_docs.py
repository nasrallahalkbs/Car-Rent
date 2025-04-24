"""
تنظيف مستمر للمستندات التلقائية
"""

from rental.models import Document
from django.core.management.base import BaseCommand

class Command(BaseCommand):
    help = 'تنظيف المستندات التلقائية'
    
    def handle(self, *args, **options):
        # حذف المستندات التلقائية
        auto_docs = Document.objects.filter(title__in=['', 'بدون عنوان', None])
        count = auto_docs.count()
        auto_docs.delete()
        self.stdout.write(f"تم حذف {count} مستند تلقائي")
