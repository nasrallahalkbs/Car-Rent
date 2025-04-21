from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
import os
import uuid

class User(AbstractUser):
    """Extended User model for car rental app"""
    phone = models.CharField(max_length=20, blank=True)
    is_admin = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.username}"

class Car(models.Model):
    """Car model for rentals"""
    CATEGORY_CHOICES = [
        ('Economy', 'Economy'),
        ('Compact', 'Compact'),
        ('Mid-size', 'Mid-size'),
        ('Luxury', 'Luxury'),
        ('SUV', 'SUV'),
        ('Truck', 'Truck'),
    ]
    
    TRANSMISSION_CHOICES = [
        ('Automatic', 'Automatic'),
        ('Manual', 'Manual'),
    ]
    
    FUEL_TYPE_CHOICES = [
        ('Gas', 'Gas'),
        ('Diesel', 'Diesel'),
        ('Electric', 'Electric'),
        ('Hybrid', 'Hybrid'),
    ]
    
    STATUS_CHOICES = [
        ('available', 'متاحة للإيجار'),
        ('maintenance', 'في الصيانة'),
        ('reserved', 'محجوزة'),
    ]
    
    make = models.CharField(max_length=50)
    model = models.CharField(max_length=50)
    year = models.IntegerField()
    color = models.CharField(max_length=30)
    license_plate = models.CharField(max_length=15, unique=True)
    daily_rate = models.DecimalField(max_digits=10, decimal_places=2)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    seats = models.IntegerField()
    transmission = models.CharField(max_length=20, choices=TRANSMISSION_CHOICES)
    fuel_type = models.CharField(max_length=20, choices=FUEL_TYPE_CHOICES)
    features = models.TextField(blank=True)  # Stored as comma-separated values
    image_url = models.URLField(blank=True)
    image = models.ImageField(upload_to='car_images/', blank=True, null=True)
    is_available = models.BooleanField(default=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='available')
    avg_rating = models.DecimalField(max_digits=3, decimal_places=1, default=0)
    
    def __str__(self):
        return f"{self.year} {self.make} {self.model}"
    
    @property
    def feature_list(self):
        """Return features as a list"""
        if not self.features:
            return []
        return [f.strip() for f in self.features.split(',')]
    
    def set_features(self, feature_list):
        """Set features from a list"""
        self.features = ', '.join(feature_list)

class Reservation(models.Model):
    """Reservation model for car rentals"""
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]
    
    PAYMENT_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('paid', 'Paid'),
        ('refunded', 'Refunded'),
        ('expired', 'Expired'),
    ]
    
    PAYMENT_METHOD_CHOICES = [
        ('credit_card', 'Credit/Debit Card'),
        ('paypal', 'PayPal'),
        ('cash', 'Cash at Pickup'),
        ('bank_transfer', 'Bank Transfer'),
        ('electronic', 'Electronic Payment'),
    ]
    
    RENTAL_TYPE_CHOICES = [
        ('daily', 'Daily Rental'),
        ('weekly', 'Weekly Rental'),
        ('monthly', 'Monthly Rental'),
        ('corporate', 'Corporate Rental'),
        ('special', 'Special Event'),
    ]
    
    GUARANTEE_TYPE_CHOICES = [
        ('id_card', 'National ID Card'),
        ('passport', 'Passport'),
        ('driving_license', 'Driving License'),
        ('deposit', 'Security Deposit'),
        ('credit_card', 'Credit Card Hold'),
        ('property_doc', 'Property Document'),
    ]
    
    # Generate a unique reservation number
    reservation_number = models.CharField(max_length=10, blank=True, null=True)
    
    # Basic reservation details
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    car = models.ForeignKey(Car, on_delete=models.CASCADE)
    start_date = models.DateField()
    end_date = models.DateField() 
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    # معلومات العميل
    full_name = models.CharField(max_length=100, blank=True, null=True, help_text="Full name of the customer")
    national_id = models.CharField(max_length=20, blank=True, null=True, help_text="National ID number")
    id_card_image = models.ImageField(upload_to='customer_ids/', blank=True, null=True, help_text="Photo of national ID card")
    
    # معلومات الحجز الإضافية
    rental_type = models.CharField(max_length=20, choices=RENTAL_TYPE_CHOICES, blank=True, null=True)
    guarantee_type = models.CharField(max_length=20, choices=GUARANTEE_TYPE_CHOICES, blank=True, null=True)
    guarantee_details = models.TextField(blank=True, null=True, help_text="Additional details about the guarantee")
    booking_date = models.DateTimeField(auto_now_add=True, null=True, blank=True, help_text="Date and time of booking")
    deposit_amount = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    
    # معلومات الدفع
    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default='pending')
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES, blank=True, null=True)
    payment_reference = models.CharField(max_length=50, blank=True, null=True, help_text="Reference number for payment")
    payment_date = models.DateTimeField(blank=True, null=True)
    transaction_id = models.CharField(max_length=100, blank=True, null=True)
    
    # معلومات انتهاء صلاحية التأكيد (للحجوزات المؤكدة التي لم يتم الدفع لها)
    confirmation_expiry = models.DateTimeField(blank=True, null=True, help_text="وقت انتهاء صلاحية التأكيد (24 ساعة)")
    
    created_at = models.DateTimeField(auto_now_add=True)
    notes = models.TextField(blank=True, null=True, help_text="Additional notes or payment details")
    
    def __str__(self):
        return f"Reservation #{self.id} - {self.car} ({self.status})"
        
    @property
    def days(self):
        """عدد أيام الحجز"""
        if self.start_date and self.end_date:
            delta = (self.end_date - self.start_date).days + 1
            return delta
        return 0
        
    def save(self, *args, **kwargs):
        # إنشاء رقم حجز فريد عند إنشاء الحجز لأول مرة
        if not self.reservation_number:
            # احصل على آخر حجز وأنشئ رقمًا جديدًا
            last_reservation = Reservation.objects.order_by('-id').first()
            if last_reservation and last_reservation.id:
                new_id = last_reservation.id + 1
            else:
                new_id = 1
            self.reservation_number = f"R{new_id:06d}"
        super().save(*args, **kwargs)

class Review(models.Model):
    """Review model for car rentals"""
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    car = models.ForeignKey(Car, on_delete=models.CASCADE)
    reservation = models.ForeignKey(Reservation, on_delete=models.CASCADE)
    rating = models.IntegerField()  # 1-5 stars
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Review by {self.user.username} for {self.car}"

class CartItem(models.Model):
    """Cart item for storing cars before checkout"""
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    car = models.ForeignKey(Car, on_delete=models.CASCADE)
    start_date = models.DateField()
    end_date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    @property
    def days(self):
        """عدد أيام الحجز في عربة التسوق"""
        if self.start_date and self.end_date:
            delta = (self.end_date - self.start_date).days + 1
            return delta
        return 0
        
    @property
    def total(self):
        """المبلغ الإجمالي للسيارة في السلة"""
        return self.car.daily_rate * self.days
    
    def __str__(self):
        return f"Cart item: {self.car} for {self.user.username}"


class FavoriteCar(models.Model):
    """نموذج السيارات المفضلة للمستخدمين"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='favorite_cars',
                           verbose_name=_('المستخدم'))
    car = models.ForeignKey(Car, on_delete=models.CASCADE, related_name='favorited_by',
                          verbose_name=_('السيارة'))
    date_added = models.DateTimeField(auto_now_add=True, verbose_name=_('تاريخ الإضافة'))
    
    class Meta:
        verbose_name = _('سيارة مفضلة')
        verbose_name_plural = _('السيارات المفضلة')
        # ضمان أن كل مستخدم يمكنه إضافة سيارة واحدة فقط إلى المفضلة
        unique_together = ('user', 'car')
    
    def __str__(self):
        return f"{self.user.username} فضّل {self.car}"
        
class SiteSettings(models.Model):
    """نموذج إعدادات الموقع"""
    # إعدادات عامة
    site_name = models.CharField(max_length=100, verbose_name=_('اسم الموقع'), default="كاررنتال")
    site_description = models.TextField(blank=True, null=True, verbose_name=_('وصف الموقع'))
    site_logo = models.ImageField(upload_to='settings/', blank=True, null=True, verbose_name=_('شعار الموقع'))
    site_favicon = models.ImageField(upload_to='settings/', blank=True, null=True, verbose_name=_('أيقونة الموقع'))
    
    # معلومات الاتصال
    site_email = models.EmailField(blank=True, null=True, verbose_name=_('البريد الإلكتروني'))
    site_phone = models.CharField(max_length=20, blank=True, null=True, verbose_name=_('رقم الهاتف'))
    site_address = models.TextField(blank=True, null=True, verbose_name=_('العنوان'))
    
    # وسائل التواصل الاجتماعي
    facebook_url = models.URLField(blank=True, null=True, verbose_name=_('رابط فيسبوك'))
    twitter_url = models.URLField(blank=True, null=True, verbose_name=_('رابط تويتر'))
    instagram_url = models.URLField(blank=True, null=True, verbose_name=_('رابط انستجرام'))
    tiktok_url = models.URLField(blank=True, null=True, verbose_name=_('رابط تيك توك'))
    youtube_url = models.URLField(blank=True, null=True, verbose_name=_('رابط يوتيوب'))
    
    # إعدادات API
    google_maps_api_key = models.CharField(max_length=255, blank=True, null=True, verbose_name=_('مفتاح API لخرائط جوجل'))
    payment_gateway_api_key = models.CharField(max_length=255, blank=True, null=True, verbose_name=_('مفتاح API لبوابة الدفع'))
    
    # إعدادات الحجز
    booking_start_time = models.TimeField(default='09:00', verbose_name=_('وقت بدء الحجز'))
    booking_end_time = models.TimeField(default='18:00', verbose_name=_('وقت انتهاء الحجز'))
    min_booking_days = models.PositiveIntegerField(default=1, verbose_name=_('الحد الأدنى لأيام الحجز'))
    max_booking_days = models.PositiveIntegerField(default=30, verbose_name=_('الحد الأقصى لأيام الحجز'))
    
    # إعدادات المظهر
    primary_color = models.CharField(max_length=20, default='#3a86ff', verbose_name=_('اللون الرئيسي'))
    secondary_color = models.CharField(max_length=20, default='#334155', verbose_name=_('اللون الثانوي'))
    enable_dark_mode = models.BooleanField(default=True, verbose_name=_('تفعيل الوضع المظلم'))
    
    # إعدادات الأمان
    
    def __str__(self):
        return self.site_name
        
    class Meta:
        verbose_name = _('إعدادات الموقع')
        verbose_name_plural = _('إعدادات الموقع')


def archive_document_path(instance, filename):
    """تحديد مسار حفظ المستندات الأرشيفية بشكل منظم باستخدام هيكل شجري"""
    # الحصول على امتداد الملف
    ext = filename.split('.')[-1]
    # إنشاء اسم ملف جديد فريد
    original_filename = os.path.splitext(filename)[0]
    sanitized_filename = "".join([c for c in original_filename if c.isalnum() or c in [' ', '-', '_']]).strip()
    if len(sanitized_filename) > 50:
        sanitized_filename = sanitized_filename[:50]
    if not sanitized_filename:
        sanitized_filename = "document"
    
    unique_filename = f"{sanitized_filename}_{uuid.uuid4().hex[:8]}.{ext}"
    
    # تنظيم الملفات حسب النوع والسنة والشهر
    year = timezone.now().strftime('%Y')
    month = timezone.now().strftime('%m')
    
    # تحديد المجلد حسب نوع المستند
    folder = 'other'
    if instance.document_type == 'contract':
        folder = 'contracts'
    elif instance.document_type == 'receipt':
        folder = 'receipts'
    elif instance.document_type == 'custody':
        folder = 'custody'
    elif instance.document_type == 'custody_release':
        folder = 'custody_release'
    elif instance.document_type == 'official_document':
        folder = 'official'
    
    # إضافة مسار إضافي حسب الارتباط إذا كان متاحًا
    related_path = ''
    if hasattr(instance, 'related_to') and instance.related_to:
        related_path = instance.related_to
    
    # إرجاع المسار الكامل باستخدام هيكل شجري منظم
    return os.path.join('archive', folder, year, month, related_path, unique_filename)


class Document(models.Model):
    """نموذج أرشيف الوثائق والعقود والاستلامات والعهد"""
    
    DOCUMENT_TYPE_CHOICES = [
        ('contract', _('عقد')),
        ('receipt', _('إيصال')),
        ('custody', _('عهدة')),
        ('custody_release', _('إخلاء عهدة')),
        ('official_document', _('وثيقة رسمية')),
        ('other', _('أخرى')),
    ]
    
    RELATED_TO_CHOICES = [
        ('reservation', _('حجز')),
        ('car', _('سيارة')),
        ('user', _('مستخدم')),
        ('employee', _('موظف')),
        ('other', _('أخرى')),
    ]
    
    # معلومات المستند الأساسية
    title = models.CharField(max_length=255, verbose_name=_('عنوان المستند'))
    document_type = models.CharField(max_length=20, choices=DOCUMENT_TYPE_CHOICES, default='other', verbose_name=_('نوع المستند'))
    description = models.TextField(blank=True, null=True, verbose_name=_('وصف المستند'))
    
    # ملف المستند
    file = models.FileField(upload_to=archive_document_path, verbose_name=_('ملف المستند'))
    file_size = models.PositiveIntegerField(default=0, editable=False, verbose_name=_('حجم الملف (بايت)'))
    
    # تاريخ المستند
    document_date = models.DateField(default=timezone.now, verbose_name=_('تاريخ المستند'))
    expiry_date = models.DateField(blank=True, null=True, verbose_name=_('تاريخ انتهاء الصلاحية'))
    
    # علاقات المستند
    related_to = models.CharField(max_length=20, choices=RELATED_TO_CHOICES, default='other', verbose_name=_('متعلق بـ'))
    reservation = models.ForeignKey(Reservation, blank=True, null=True, on_delete=models.SET_NULL, related_name='documents', verbose_name=_('الحجز المرتبط'))
    car = models.ForeignKey(Car, blank=True, null=True, on_delete=models.SET_NULL, related_name='documents', verbose_name=_('السيارة المرتبطة'))
    user = models.ForeignKey(User, blank=True, null=True, on_delete=models.SET_NULL, related_name='documents', verbose_name=_('المستخدم المرتبط'))
    reference_number = models.CharField(max_length=100, blank=True, null=True, verbose_name=_('الرقم المرجعي'))
    
    # الموظف المسؤول
    added_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='added_documents', verbose_name=_('أضيف بواسطة'))
    
    # سجل المستند
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('تاريخ الإضافة'))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_('تاريخ التحديث'))
    is_archived = models.BooleanField(default=True, verbose_name=_('مؤرشف'))
    tags = models.CharField(max_length=255, blank=True, null=True, verbose_name=_('الكلمات المفتاحية'), help_text=_('فصل بفواصل'))
    
    def __str__(self):
        return self.title
    
    def save(self, *args, **kwargs):
        # حساب حجم الملف عند الحفظ
        if self.file:
            try:
                self.file_size = self.file.size
            except:
                pass
        
        # إنشاء رقم مرجعي للمستند إذا لم يكن موجودًا
        if not self.reference_number:
            now = timezone.now()
            year = now.strftime('%Y')
            month = now.strftime('%m')
            day = now.strftime('%d')
            
            # تحديد الرمز حسب نوع المستند
            doc_code = 'DOC'
            if self.document_type == 'contract':
                doc_code = 'CNT'
            elif self.document_type == 'receipt':
                doc_code = 'RCT'
            elif self.document_type == 'custody':
                doc_code = 'CUS'
            elif self.document_type == 'custody_release':
                doc_code = 'CRL'
            
            # إنشاء رقم مرجعي فريد
            # نحصل على عدد المستندات الموجودة من نفس النوع
            doc_count = Document.objects.filter(document_type=self.document_type).count() + 1
            self.reference_number = f"{doc_code}-{year}{month}{day}-{doc_count:04d}"
        
        super().save(*args, **kwargs)
    
    @property
    def file_size_display(self):
        """عرض حجم الملف بطريقة قابلة للقراءة"""
        size = self.file_size
        for unit in ['بايت', 'كيلوبايت', 'ميجابايت', 'جيجابايت']:
            if size < 1024.0:
                return f"{size:.2f} {unit}"
            size /= 1024.0
        return f"{size:.2f} تيرابايت"
    
    @property
    def file_extension(self):
        """الحصول على امتداد الملف"""
        if self.file:
            return os.path.splitext(self.file.name)[1][1:]  # استخراج الامتداد بدون النقطة
        return ""
    
    @property
    def is_image(self):
        """التحقق مما إذا كان الملف صورة"""
        image_extensions = ['jpg', 'jpeg', 'png', 'gif', 'bmp', 'webp']
        return self.file_extension.lower() in image_extensions
    
    @property
    def is_pdf(self):
        """التحقق مما إذا كان الملف PDF"""
        return self.file_extension.lower() == 'pdf'
    
    @property
    def tags_list(self):
        """إرجاع الكلمات المفتاحية كقائمة"""
        if not self.tags:
            return []
        return [tag.strip() for tag in self.tags.split(',')]
    
    def set_tags(self, tags_list):
        """تعيين الكلمات المفتاحية من قائمة"""
        self.tags = ', '.join(tags_list)
    
    class Meta:
        verbose_name = _('وثيقة مؤرشفة')
        verbose_name_plural = _('الوثائق المؤرشفة')
        ordering = ['-created_at']
    enable_two_factor_auth = models.BooleanField(default=False, verbose_name=_('تفعيل المصادقة الثنائية'))
    booking_confirmation_expiry_hours = models.PositiveIntegerField(default=24, verbose_name=_('ساعات انتهاء صلاحية تأكيد الحجز'))
    session_timeout_minutes = models.PositiveIntegerField(default=60, verbose_name=_('مدة انتهاء الجلسة بالدقائق'))
    
    # إعدادات الحجز
    enable_deposit = models.BooleanField(default=True, verbose_name=_('تفعيل نظام العربون'))
    deposit_percentage = models.PositiveIntegerField(default=20, verbose_name=_('نسبة العربون من إجمالي الحجز (%)'))
    enable_automatic_reservation_expiry = models.BooleanField(default=True, verbose_name=_('تفعيل انتهاء صلاحية الحجز التلقائي'))
    
    # إعدادات النظام
    maintenance_mode = models.BooleanField(default=False, verbose_name=_('وضع الصيانة'))
    enable_debug_mode = models.BooleanField(default=False, verbose_name=_('تفعيل وضع التصحيح'))
    cache_timeout_minutes = models.PositiveIntegerField(default=60, verbose_name=_('مدة انتهاء ذاكرة التخزين المؤقت بالدقائق'))
    
    # إعدادات الإشعارات
    enable_email_notifications = models.BooleanField(default=True, verbose_name=_('تفعيل الإشعارات بالبريد الإلكتروني'))
    enable_sms_notifications = models.BooleanField(default=False, verbose_name=_('تفعيل الإشعارات بالرسائل النصية'))
    admin_notification_email = models.EmailField(blank=True, null=True, verbose_name=_('البريد الإلكتروني لإشعارات المدير'))
    
    # ترجمة وتدويل
    default_language = models.CharField(max_length=10, default='ar', choices=[('ar', 'العربية'), ('en', 'English')], verbose_name=_('اللغة الافتراضية'))
    default_timezone = models.CharField(max_length=100, default='Asia/Kuwait', verbose_name=_('المنطقة الزمنية الافتراضية'))
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('تاريخ الإنشاء'))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_('تاريخ التحديث'))
    
    def __str__(self):
        return f"إعدادات الموقع - {self.site_name}"
    
    class Meta:
        verbose_name = _('إعدادات الموقع')
        verbose_name_plural = _('إعدادات الموقع')
        
    @classmethod
    def get_settings(cls):
        """الحصول على إعدادات الموقع، أو إنشاء إعدادات افتراضية إذا لم تكن موجودة"""
        settings, created = cls.objects.get_or_create(pk=1)
        return settings