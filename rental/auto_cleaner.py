# -*- coding: utf-8 -*-
"""
مشغل تلقائي للتنظيف المنتظم للمستندات التلقائية
"""

from django.db.models import Q
from .models import Document, ArchiveFolder
import threading
import time

class AutoCleaner:
    """فئة التنظيف التلقائي للمستندات"""
    
    def __init__(self):
        self.running = False
        self.thread = None
    
    def start(self):
        """بدء التنظيف التلقائي"""
        if not self.running:
            self.running = True
            self.thread = threading.Thread(target=self.cleaner_loop)
            self.thread.daemon = True
            self.thread.start()
            print("🧹 [AUTO_CLEANER] تم بدء خدمة التنظيف التلقائي")
    
    def stop(self):
        """إيقاف التنظيف التلقائي"""
        self.running = False
        if self.thread:
            self.thread.join(1)
            print("🧹 [AUTO_CLEANER] تم إيقاف خدمة التنظيف التلقائي")
    
    def cleaner_loop(self):
        """حلقة التنظيف المستمرة"""
        while self.running:
            try:
                self.clean_auto_documents()
                # السبات لمدة 5 دقائق قبل التنظيف التالي
                for _ in range(300):
                    if not self.running:
                        break
                    time.sleep(1)
            except Exception as e:
                print(f"⚠️ [AUTO_CLEANER] حدث خطأ: {str(e)}")
                time.sleep(60)
    
    def clean_auto_documents(self):
        """تنظيف المستندات التلقائية"""
        try:
            # البحث عن المستندات التلقائية
            auto_docs = Document.objects.filter(
                Q(title__isnull=True) | Q(title='') | Q(title='بدون عنوان')
            )
            
            count = auto_docs.count()
            if count > 0:
                print(f"🧹 [AUTO_CLEANER] تنظيف {count} مستند تلقائي")
                auto_docs.delete()
        except Exception as e:
            print(f"⚠️ [AUTO_CLEANER] حدث خطأ أثناء التنظيف: {str(e)}")

# إنشاء نسخة من التنظيف التلقائي
auto_cleaner = AutoCleaner()

def start_auto_cleaner():
    """بدء خدمة التنظيف التلقائي"""
    auto_cleaner.start()

# بدء التنظيف التلقائي عند استيراد الوحدة
start_auto_cleaner()
