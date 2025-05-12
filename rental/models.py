from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
import os
import uuid
from django.conf import settings

# استيراد نموذج العهدة
from .models_custody import CustomerGuarantee
# استيراد موديل AdminUser
from .models_superadmin import AdminUser

# نموذج التحقق من البريد الإلكتروني
class EmailVerification(models.Model):
    """نموذج تخزين رموز التحقق من البريد الإلكتروني"""
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='verification')
    token = models.CharField(max_length=100, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    verified_at = models.DateTimeField(null=True, blank=True)
    
    def __str__(self):
        return f"تحقق بريد {self.user.email}"
    
    def is_valid(self):
        """التحقق من صلاحية الرمز"""
        return self.expires_at > timezone.now() and not self.verified_at
        
    class Meta:
        verbose_name = 'تحقق بريد إلكتروني'
        verbose_name_plural = 'تحققات البريد الإلكتروني'

class User(AbstractUser):
    """Extended User model for car rental app"""
    phone = models.CharField(max_length=20, blank=True)
    is_admin = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    # الحقول الجديدة المطلوبة
    GENDER_CHOICES = [
        ('male', 'ذكر'),
        ('female', 'أنثى'),
    ]
    
    age = models.PositiveIntegerField(null=True, blank=True, verbose_name='العمر')
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES, blank=True, null=True, verbose_name='النوع')
    nationality = models.CharField(max_length=50, blank=True, null=True, verbose_name='الجنسية')
    
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
        return f"{self.reservation_number}" if self.reservation_number else f"Reservation #{self.id}"
        
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


class ArchiveFolder(models.Model):
    """نموذج المجلدات في الأرشيف الإلكتروني للتنظيم الشجري"""
    
    name = models.CharField(max_length=255, verbose_name=_('اسم المجلد'))
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, 
                              related_name='children', verbose_name=_('المجلد الأب'))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('تاريخ الإنشاء'))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_('تاريخ التحديث'))
    description = models.TextField(blank=True, null=True, verbose_name=_('وصف المجلد'))
    
    # الموظف المسؤول
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, 
                                  related_name='created_folders', verbose_name=_('أنشئ بواسطة'))
    
    is_system_folder = models.BooleanField(default=False, verbose_name=_('مجلد نظام'), 
                                          help_text=_('إذا كان هذا مجلد نظام (يتم إنشاؤه تلقائيًا)'))
    folder_type = models.CharField(max_length=50, blank=True, null=True, verbose_name=_('نوع المجلد'),
                                 help_text=_('نوع المجلد (مثل حجوزات، سيارات، ...إلخ)'))
    
    def __init__(self, *args, **kwargs):
        # تحقق من وجود اسم صالح للمجلد (منع المجلدات "بدون اسم")
        folder_name = kwargs.get('name', None)
        if not folder_name or folder_name.strip() == '' or folder_name == 'بدون اسم':
            # لا نطبع هنا لتفادي الكثير من الرسائل المكررة
            pass
        else:
            print(f"DEBUG [models]: تم إنشاء كائن مجلد جديد: {folder_name}")
        
        # هذه العلامة تستخدم لمنع إنشاء مستندات تلقائية - مهم جدًا
        self._skip_auto_document_creation = True
        
        super().__init__(*args, **kwargs)
        
    def save(self, *args, **kwargs):
        is_new = self.pk is None
        if is_new:
            print(f"DEBUG [models]: حفظ مجلد جديد: {self.name}")
            
        # لا يمكننا تمرير معاملات إضافية إلى طريقة save الأساسية
        # لذا سنقوم بتخزين العلامة كخاصية للكائن نفسه
        
        # تأكد من أن المستندات التلقائية معطلة
        self._skip_auto_document_creation = True
        
        # استخدام تقنية raw SQL إذا كان هذا مجلد جديد
        if is_new:
            try:
                # استخدام منهج SQL المباشر لمنع تفعيل الإشارات والمحفزات
                from django.db import connection, transaction
                with transaction.atomic():
                    cursor = connection.cursor()
                    # تعطيل المحفزات
                    cursor.execute("SET session_replication_role = 'replica';")
                    
                    # إنشاء المجلد مباشرة في قاعدة البيانات
                    table_name = self.__class__._meta.db_table
                    parent_id = self.parent.id if self.parent else None
                    description = self.description or ''
                    is_system = self.is_system_folder
                    folder_type = self.folder_type or ''
                    
                    # الاستعلام SQL
                    sql = f"""
                    INSERT INTO {table_name} 
                    (name, parent_id, created_at, updated_at, description, is_system_folder, 
                     folder_type)
                    VALUES (%s, %s, NOW(), NOW(), %s, %s, %s)
                    RETURNING id;
                    """
                    
                    cursor.execute(sql, [self.name, parent_id, description, is_system, folder_type])
                    folder_id = cursor.fetchone()[0]
                    
                    # إعادة تفعيل المحفزات
                    cursor.execute("SET session_replication_role = 'origin';")
                    
                    # تحديث معرف الكائن الحالي
                    self.pk = folder_id
                    print(f"DEBUG [models]: تم حفظ المجلد باستخدام SQL المباشر: {self.name} بمعرف {self.pk}")
                    
                    # حذف أي مستندات تلقائية قد تكون أنشئت
                    from rental.models import Document
                    deleted_count = Document.objects.filter(
                        folder_id=folder_id, 
                        title__in=['', 'بدون عنوان', None]
                    ).delete()
                    print(f"DEBUG [models]: تم حذف {deleted_count} مستند تلقائي بعد إنشاء المجلد")
                    
                    # تحديث الكائن من قاعدة البيانات
                    for field in self._meta.fields:
                        if field.name not in ['name', 'parent', 'description', 'is_system_folder', 'folder_type']:
                            setattr(self, field.attname, None)
                    
                    # لا حاجة للاستمرار في الدالة
                    return
            except Exception as e:
                print(f"DEBUG [models]: حدث خطأ أثناء إنشاء المجلد باستخدام SQL المباشر: {str(e)}")
                print("DEBUG [models]: الانتقال إلى الطريقة العادية...")
        
        # الطريقة المعتادة كخطة بديلة
        super().save(*args, **kwargs)
        
        if is_new:
            print(f"DEBUG [models]: تم حفظ المجلد الجديد: {self.name} بمعرف {self.pk}")
            
            # حذف أي مستندات تلقائية تم إنشاؤها
            try:
                # استيراد نموذج Document هنا لتجنب استيراد دائري
                from django.db import transaction
                with transaction.atomic():
                    # نحذف أي مستندات بدون عنوان أو بعنوان "بدون عنوان"
                    from rental.models import Document
                    deleted_count = Document.objects.filter(
                        folder=self, 
                        title__in=['', 'بدون عنوان', None]
                    ).delete()
                    print(f"DEBUG [models]: تم حذف {deleted_count} مستند تلقائي بعد إنشاء المجلد {self.name}")
            except Exception as e:
                print(f"DEBUG [models]: حدث خطأ أثناء حذف المستندات التلقائية: {str(e)}")
            
            # سيتم تنظيف المستندات التلقائية أيضاً في خطاف post_save
            print(f"DEBUG [models]: ستتم إزالة المستندات التلقائية في خطاف post_save")
    
    class Meta:
        verbose_name = _('مجلد أرشيف')
        verbose_name_plural = _('مجلدات الأرشيف')
        unique_together = ('parent', 'name')
        ordering = ['name']
    
    def __str__(self):
        return self.name
    
    def get_path(self):
        """الحصول على المسار الكامل للمجلد"""
        if self.parent:
            return f"{self.parent.get_path()}/{self.name}"
        return self.name
    
    def get_absolute_url(self):
        """الحصول على الرابط المطلق للمجلد"""
        from django.urls import reverse
        return reverse('admin_archive_folder', args=[self.id])
    
    @property
    def document_count(self):
        """عدد المستندات في هذا المجلد"""
        return self.documents.count()
    
    @property
    def all_document_count(self):
        """عدد جميع المستندات في هذا المجلد وجميع المجلدات الفرعية"""
        count = self.documents.count()
        for child in self.children.all():
            count += child.all_document_count
        return count
        
    @classmethod
    def get_or_create_system_folder(cls, folder_name, folder_type=None, parent=None):
        """الحصول على أو إنشاء مجلد نظام"""
        import inspect
        from django.db import transaction
        
        print(f"📁 [System Folder] محاولة إنشاء مجلد نظام: {folder_name}, نوع: {folder_type}, الأب: {parent}")
        
        # البحث اولا عن مجلد موجود بنفس الاسم والأب
        try:
            if parent:
                existing_folder = cls.objects.get(name=folder_name, parent=parent)
            else:
                existing_folder = cls.objects.get(name=folder_name, parent__isnull=True)
                
            print(f"📁 [System Folder] تم العثور على مجلد موجود: {existing_folder.name} بمعرف {existing_folder.pk}")
            return existing_folder
        except cls.DoesNotExist:
            # المجلد غير موجود، سنقوم بإنشائه في عملية منفصلة
            pass
        
        # تطبيق نهج منع المستندات التلقائية بشكل صارم
        with transaction.atomic():
            # إنشاء المجلد بطريقة منفصلة عن save المعتادة
            from django.db import connection
            cursor = connection.cursor()
            
            # إنشاء العناصر المطلوبة فقط بدون أي جانبية
            try:
                # تحضير البيانات
                description = f'مجلد نظام لـ {folder_name}'
                is_system_folder = True
                
                # تحضير قيمة parent_id
                parent_id = None
                if parent:
                    parent_id = parent.id
                
                # استخدام SQL مباشرة لإنشاء المجلد بدون تفعيل signals أو triggers
                sql = """
                INSERT INTO rental_archivefolder 
                (name, parent_id, created_at, updated_at, description, created_by_id, is_system_folder, folder_type) 
                VALUES (%s, %s, NOW(), NOW(), %s, NULL, %s, %s)
                RETURNING id;
                """
                
                cursor.execute(sql, [folder_name, parent_id, description, is_system_folder, folder_type])
                folder_id = cursor.fetchone()[0]
                
                # الحصول على كائن المجلد من قاعدة البيانات
                folder = cls.objects.get(id=folder_id)
                print(f"📁 [System Folder] تم إنشاء مجلد نظام جديد: {folder.name} بمعرف {folder.pk}")
                
                # حذف أي مستندات تلقائية قد تكون أنشئت
                from rental.models import Document
                docs = Document.objects.filter(folder=folder)
                if docs.exists():
                    doc_count = docs.count()
                    docs.delete()
                    print(f"📁 [System Folder] تم حذف {doc_count} مستند تلقائي من المجلد الجديد")
                
                return folder
            except Exception as e:
                print(f"📁 [System Folder] حدث خطأ أثناء إنشاء المجلد: {str(e)}")
                # في حالة الخطأ، نستخدم الطريقة التقليدية كخطة بديلة
                folder = cls(
                    name=folder_name,
                    parent=parent,
                    is_system_folder=True,
                    folder_type=folder_type,
                    description=f'مجلد نظام لـ {folder_name}'
                )
                # وضع علامة تجاوز السلوك التلقائي
                folder._skip_auto_document_creation = True
                folder.save()
                print(f"📁 [System Folder] تم إنشاء المجلد بالطريقة البديلة: {folder.name} بمعرف {folder.pk}")
                
                # حذف أي مستندات قد تكون أنشئت
                from rental.models import Document
                Document.objects.filter(folder=folder).delete()
                
                return folder
        
    @classmethod
    def get_root_folders(cls):
        """الحصول على مجلدات الجذر"""
        return cls.objects.filter(parent=None)
    
    def has_children(self):
        """التحقق مما إذا كان المجلد يحتوي على مجلدات فرعية"""
        return self.children.exists()


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
    
    # ملف المستند - تخزين في قاعدة البيانات
    file = models.FileField(upload_to=archive_document_path, verbose_name=_('ملف المستند'), null=True, blank=True)
    file_content = models.BinaryField(null=True, blank=True, verbose_name=_('محتوى الملف'), editable=False)
    file_name = models.CharField(max_length=255, null=True, blank=True, verbose_name=_('اسم الملف الأصلي'))
    file_type = models.CharField(max_length=100, null=True, blank=True, verbose_name=_('نوع الملف'))
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
    
    # العلاقة مع المجلد
    folder = models.ForeignKey(ArchiveFolder, on_delete=models.SET_NULL, null=True, blank=True, 
                              related_name='documents', verbose_name=_('المجلد'))
    
    # إضافة علامة لحماية المستندات التلقائية
    is_auto_created = models.BooleanField(default=False, editable=False)
    
    def __str__(self):
        return self.title
    
    def __init__(self, *args, **kwargs):
        import inspect, sys, os
        
        # العنوان الأصلي للتسجيل
        title = kwargs.get('title', 'بدون عنوان')
        folder_id = None
        if 'folder' in kwargs and kwargs['folder'] is not None:
            if hasattr(kwargs['folder'], 'id'):
                folder_id = kwargs['folder'].id
            elif hasattr(kwargs['folder'], 'pk'): 
                folder_id = kwargs['folder'].pk
            
        print(f"🚨 [DOCUMENT INIT] إنشاء مستند: '{title}' للمجلد: {folder_id}")
        
        # كشف إذا كان المستند منشأ تلقائيا
        is_auto = title == '' or title == 'بدون عنوان' or not title
        # البحث في مسار الاستدعاء
        stack_trace = inspect.stack()
        calling_frame = stack_trace[1]
        calling_function = calling_frame.function
        calling_file = os.path.basename(calling_frame.filename)
        
        print(f"🚨 [DOCUMENT INIT] تم الاستدعاء من: {calling_file}:{calling_function}")
        
        # فحص إضافي للعلامات التي تشير إلى مستند تلقائي
        is_auto_doc = False
        # تحقق إذا كان بدون عنوان أو عنوان فارغ
        if not title or title == 'بدون عنوان' or title == '':
            is_auto_doc = True
        
        # تحقق إذا كان بدون ملف
        if not kwargs.get('file'):
            is_auto_doc = True
            
        if is_auto_doc:
            print(f"🚨 [DOCUMENT INIT] تم اكتشاف مستند تلقائي - تعيين العلامة")
            # تجنب تعيين is_auto_created مباشرة لمنع تضارب الوسيطات
            # سنعتمد على العلامة المؤقتة _auto_document بدلاً من ذلك
            self._auto_document = True
        
        # منع إنشاء المستندات التلقائية (بدون عنوان أو ملف) من الأساس
        if is_auto_doc:
            # وضع أثر للتصحيح
            print(f"🚨 [DOCUMENT INIT] رفض إنشاء مستند تلقائي")
            # سجل مكان الاستدعاء
            for i, frame in enumerate(stack_trace[1:4]):
                print(f"🚨 [DOCUMENT TRACE {i+1}] {frame.filename}:{frame.lineno} - {frame.function}")
            
            # تعيين علامة الإنشاء التلقائي
            self._auto_document = True
            
            # مسح أي علاقة مع المجلدات التي تم إنشاؤها مؤخرًا
            if 'folder' in kwargs and kwargs['folder'] is not None:
                if hasattr(kwargs['folder'], 'created_at'):
                    from django.utils import timezone
                    time_diff = timezone.now() - kwargs['folder'].created_at
                    if time_diff.total_seconds() < 60:  # إذا تم إنشاء المجلد خلال الدقيقة الماضية
                        print(f"🚨 [DOCUMENT INIT] مسح علاقة المجلد لمستند تلقائي - المجلد حديث")
                        kwargs['folder'] = None
        
        # تسجيل الاستدعاء للتصحيح
        if folder_id is not None:
            print(f"🚨 [DOCUMENT INIT] الانتقال إلى super().__init__ للمستند '{title}' المرتبط بالمجلد {folder_id}")
            
        super().__init__(*args, **kwargs)
    
    def save(self, *args, **kwargs):
        import traceback, inspect
        
        # التحقق من وجود علامة تجاوز الإشارات
        ignore_signal = getattr(self, '_ignore_auto_document_signal', False)
        
        # منع حفظ المستندات التلقائية - إلا إذا كان هناك تجاوز للإشارات
        if hasattr(self, '_auto_document') and self._auto_document and not ignore_signal:
            print(f"🚨 [DOCUMENT SAVE] تم منع حفظ مستند تلقائي '{self.title}'")
            
            # تسجيل معلومات إضافية للتصحيح
            if self.folder:
                print(f"🚨 [DOCUMENT SAVE] هذا المستند التلقائي مرتبط بالمجلد: {self.folder.name}")
                
                # محاولة حذف المستند من قاعدة البيانات إذا كان له معرف
                if self.pk:
                    try:
                        from django.db import transaction
                        with transaction.atomic():
                            # احذف نفسك
                            Document.objects.filter(pk=self.pk).delete()
                            print(f"🚨 [DOCUMENT SAVE] تم حذف المستند التلقائي من قاعدة البيانات")
                    except Exception as e:
                        print(f"🚨 [DOCUMENT SAVE] فشل حذف المستند التلقائي: {str(e)}")
            
            # تسجيل مكان الاستدعاء للتصحيح
            for i, frame in enumerate(inspect.stack()[1:3]):
                print(f"🚨 [DOCUMENT SAVE TRACE {i+1}] {frame.filename}:{frame.lineno} - {frame.function}")
            # إيقاف الحفظ هنا
            return
            
        # منع ربط المستندات بالمجلدات التي لم يتم الإنشاء اليدوي لها
        # التحقق من وجود علامة تجاوز الإشارات
        ignore_signal = getattr(self, '_ignore_auto_document_signal', False)
        
        if self.folder and not self.pk and not ignore_signal:  # مستند جديد وليس له تجاوز للإشارات
            if hasattr(self.folder, 'created_at'):
                from django.utils import timezone
                time_diff = timezone.now() - self.folder.created_at
                if time_diff.total_seconds() < 60:  # إذا تم إنشاء المجلد خلال الدقيقة الماضية
                    # اختبار إذا كان هذا حفظًا يدويًا أم تلقائيًا
                    is_manual = False
                    for frame in inspect.stack()[1:]:
                        if 'admin_archive_folder_add_document' in frame.function:
                            is_manual = True
                            break
                    
                    if not is_manual:
                        print(f"🚨 [DOCUMENT SAVE] منع ربط مستند تلقائي بمجلد حديث الإنشاء {self.folder.name}")
                        self.folder = None
        
        # معالجة الملف وتخزينه في قاعدة البيانات
        if self.file and not self.file_content:
            try:
                # حفظ محتوى الملف في قاعدة البيانات
                self.file.seek(0)
                self.file_content = self.file.read()
                
                # حفظ المعلومات الوصفية للملف
                self.file_name = self.file.name.split('/')[-1]
                self.file_size = self.file.size
                
                # تحديد نوع الملف
                import mimetypes
                self.file_type = mimetypes.guess_type(self.file.name)[0] or 'application/octet-stream'
                
                print(f"🚨 [DOCUMENT SAVE] تم حفظ الملف في قاعدة البيانات - الاسم: {self.file_name}, الحجم: {self.file_size}, النوع: {self.file_type}")
            except Exception as e:
                print(f"🚨 [DOCUMENT SAVE] خطأ في حفظ محتوى الملف: {str(e)}")
        elif self.file:
            # تحديث حجم الملف إن وجد
            try:
                self.file_size = self.file.size
            except:
                pass
        
        # إنشاء رقم مرجعي للمستند إذا لم يكن موجودًا
        if not self.reference_number:
            from django.utils import timezone
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
            doc_count = Document.objects.filter(document_type=self.document_type).count() + 1
            self.reference_number = f"{doc_code}-{year}{month}{day}-{doc_count:04d}"
        
        print(f"🚨 [DOCUMENT SAVE] حفظ المستند: {self.title}")
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
        if self.file_name:
            return os.path.splitext(self.file_name)[1][1:]  # استخراج الامتداد بدون النقطة
        elif self.file:
            return os.path.splitext(self.file.name)[1][1:]  # استخراج الامتداد بدون النقطة
        return ""
    
    @property
    def is_image(self):
        """التحقق مما إذا كان الملف صورة"""
        if self.file_type and 'image/' in self.file_type:
            return True
        
        image_extensions = ['jpg', 'jpeg', 'png', 'gif', 'bmp', 'webp']
        return self.file_extension.lower() in image_extensions
    
    @property
    def is_pdf(self):
        """التحقق مما إذا كان الملف PDF"""
        if self.file_type and 'application/pdf' in self.file_type:
            return True
        
        return self.file_extension.lower() == 'pdf'
    
    def get_file_from_db(self):
        """استرجاع الملف من قاعدة البيانات"""
        if self.file_content:
            return self.file_content
        return None
    
    def get_file_url(self):
        """إنشاء عنوان URL للملف المخزن في قاعدة البيانات"""
        from django.urls import reverse
        return reverse('document_file_view', kwargs={'pk': self.pk})
    
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


class CarConditionReport(models.Model):
    """نموذج توثيق حالة السيارة عند التسليم والاستلام"""
    
    REPORT_TYPE_CHOICES = [
        ('delivery', _('تسليم للعميل')),
        ('return', _('استلام من العميل')),
        ('maintenance', _('فحص صيانة')),
        ('periodic', _('فحص دوري')),
    ]
    
    CAR_CONDITION_CHOICES = [
        ('excellent', _('ممتازة')),
        ('good', _('جيدة')),
        ('fair', _('متوسطة')),
        ('poor', _('سيئة')),
        ('damaged', _('متضررة')),
    ]
    
    FUEL_LEVEL_CHOICES = [
        ('empty', _('فارغ')),
        ('quarter', _('ربع')),
        ('half', _('نصف')),
        ('three_quarters', _('ثلاثة أرباع')),
        ('full', _('ممتلئ')),
    ]
    
    MAINTENANCE_TYPE_CHOICES = [
        ('regular', _('صيانة دورية')),
        ('repair', _('إصلاح عطل')),
        ('inspection', _('فحص فني')),
        ('other', _('أخرى')),
    ]
    
    INSPECTION_TYPE_CHOICES = [
        ('manual', _('فحص يدوي')),
        ('electronic', _('فحص إلكتروني')),
    ]

    # معلومات أساسية
    reservation = models.ForeignKey(Reservation, on_delete=models.CASCADE, related_name='condition_reports',
                                  verbose_name=_('الحجز المرتبط'))
    car = models.ForeignKey(Car, on_delete=models.CASCADE, related_name='condition_reports',
                          verbose_name=_('السيارة'))
    report_type = models.CharField(max_length=20, choices=REPORT_TYPE_CHOICES, 
                                 verbose_name=_('نوع التقرير'))
    
    # معلومات الحالة
    mileage = models.PositiveIntegerField(verbose_name=_('المسافة المقطوعة (كم)'))
    date = models.DateTimeField(default=timezone.now, verbose_name=_('تاريخ التقرير'))
    notes = models.TextField(blank=True, null=True, verbose_name=_('ملاحظات عامة'))
    
    # معلومات الأعطال والصيانة
    defects = models.TextField(blank=True, null=True, verbose_name=_('الأعطال'))
    defect_cause = models.TextField(blank=True, null=True, verbose_name=_('سبب العطل'))
    car_condition = models.CharField(max_length=20, choices=CAR_CONDITION_CHOICES, 
                                   verbose_name=_('حالة السيارة العامة'))
    repair_cost = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True,
                                    verbose_name=_('تكلفة الإصلاح'))
    
    # معلومات إضافية
    fuel_level = models.CharField(max_length=20, choices=FUEL_LEVEL_CHOICES, 
                                verbose_name=_('مستوى الوقود'))
    maintenance_type = models.CharField(max_length=20, choices=MAINTENANCE_TYPE_CHOICES, 
                                      blank=True, null=True, verbose_name=_('نوع الصيانة'))
    inspection_type = models.CharField(max_length=20, choices=INSPECTION_TYPE_CHOICES, 
                                     default='manual', verbose_name=_('نوع الفحص'))
    
    # حقول خاصة بالفحص الإلكتروني
    electronic_report_pdf = models.FileField(upload_to='car_reports/electronic_reports/', 
                                          blank=True, null=True, verbose_name=_('ملف تقرير الفحص الإلكتروني'))
    is_electronic_inspection = models.BooleanField(default=False, verbose_name=_('فحص إلكتروني'))
    
    # الشخص المسؤول عن التوثيق
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, 
                                 related_name='created_condition_reports',
                                 verbose_name=_('تم التوثيق بواسطة'))
    
    # وقت الإنشاء والتحديث
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('تاريخ الإنشاء'))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_('تاريخ التحديث'))
    
    class Meta:
        verbose_name = _('تقرير حالة السيارة')
        verbose_name_plural = _('تقارير حالة السيارات')
        ordering = ['-date']
    
    def __str__(self):
        return f"{self.get_report_type_display()} - {self.car} - {self.date.strftime('%Y-%m-%d')}"
    
    def save(self, *args, **kwargs):
        import json
        from django.utils import timezone
        
        print(f"[{timezone.now()}] بدء عملية حفظ تقرير حالة السيارة...")
        print(f"معلومات التقرير قبل الحفظ - السيارة ID: {self.car_id}, الحجز ID: {getattr(self.reservation, 'id', 'لا يوجد')}")
        
        # التأكد من أن السيارة تطابق السيارة في الحجز
        if self.reservation and not self.car_id:
            # إذا كان هناك حجز ولكن لم يتم تحديد السيارة، نأخذ سيارة الحجز
            print(f"ℹ️ لم يتم تحديد سيارة ولكن يوجد حجز، سيتم أخذ السيارة من الحجز ({self.reservation.car})")
            self.car = self.reservation.car
            print(f"✅ تم تعيين السيارة من الحجز: {self.car}")
        
        # التأكد من تطابق السيارة في الحجز والتقرير
        if self.reservation and self.car_id and hasattr(self.reservation, 'car_id') and self.reservation.car_id != self.car_id:
            # إذا كانت السيارتان مختلفتين، نختار سيارة الحجز
            print(f"⚠️ تنبيه: تم اكتشاف اختلاف بين السيارة المختارة (ID: {self.car_id}) وسيارة الحجز (ID: {self.reservation.car_id}).")
            print(f"معلومات السيارة المختارة: {getattr(self.car, 'make', '')} {getattr(self.car, 'model', '')}")
            print(f"معلومات سيارة الحجز: {getattr(self.reservation.car, 'make', '')} {getattr(self.reservation.car, 'model', '')}")
            
            self.car = self.reservation.car
            print(f"✅ تم تعيين السيارة من الحجز: {self.car}")
        
        # في حالة عدم وجود حجز، نتأكد من وجود سيارة على الأقل
        if not self.reservation and not self.car_id:
            print(f"❌ خطأ: لا يوجد حجز ولا سيارة محددة، لا يمكن إنشاء تقرير بدون سيارة!")
            raise ValueError("لا يمكن إنشاء تقرير حالة السيارة بدون تحديد سيارة أو حجز.")
        
        # طباعة معلومات تفصيلية قبل الحفظ
        car_details = {
            'id': getattr(self.car, 'id', None),
            'make': getattr(self.car, 'make', ''),
            'model': getattr(self.car, 'model', ''),
            'license_plate': getattr(self.car, 'license_plate', '')
        }
        
        print(f"معلومات التقرير النهائية:")
        print(f"- نوع التقرير: {self.get_report_type_display()}")
        print(f"- السيارة: {json.dumps(car_details, ensure_ascii=False)}")
        print(f"- التاريخ: {self.date}")
        print(f"- حالة السيارة: {self.car_condition}")
        print(f"- نوع الفحص: {self.inspection_type}")
        
        # استدعاء save الأصلية
        try:
            super().save(*args, **kwargs)
            print(f"✅ تم حفظ تقرير حالة السيارة بنجاح! معرف التقرير: {self.id}")
        except Exception as e:
            print(f"❌ خطأ أثناء حفظ تقرير حالة السيارة: {str(e)}")
            raise


class CarInspectionCategory(models.Model):
    """فئات فحص السيارة مثل الهيكل الخارجي، المحرك، إلخ"""
    
    name = models.CharField(max_length=100, verbose_name=_('اسم الفئة'))
    description = models.TextField(blank=True, null=True, verbose_name=_('وصف الفئة'))
    display_order = models.PositiveIntegerField(default=0, verbose_name=_('ترتيب العرض'))
    is_active = models.BooleanField(default=True, verbose_name=_('نشط'))
    
    class Meta:
        verbose_name = _('فئة فحص السيارة')
        verbose_name_plural = _('فئات فحص السيارة')
        ordering = ['display_order', 'name']
        
    def __str__(self):
        return self.name


class CarInspectionItem(models.Model):
    """عناصر فحص السيارة مثل المحرك، الفرامل، الإطارات، إلخ"""
    
    CONDITION_CHOICES = [
        ('excellent', _('ممتازة')),
        ('good', _('جيدة')),
        ('fair', _('متوسطة')),
        ('poor', _('سيئة')),
        ('damaged', _('متضررة')),
        ('not_applicable', _('غير منطبق')),
    ]
    
    category = models.ForeignKey(CarInspectionCategory, on_delete=models.CASCADE,
                               related_name='inspection_items', verbose_name=_('الفئة'))
    name = models.CharField(max_length=100, verbose_name=_('اسم العنصر'))
    description = models.TextField(blank=True, null=True, verbose_name=_('وصف العنصر'))
    display_order = models.PositiveIntegerField(default=0, verbose_name=_('ترتيب العرض'))
    is_required = models.BooleanField(default=True, verbose_name=_('إلزامي'))
    is_active = models.BooleanField(default=True, verbose_name=_('نشط'))
    
    # حقول إضافية لتصنيف العناصر
    is_important = models.BooleanField(default=False, verbose_name=_('مهم'))
    is_expensive = models.BooleanField(default=False, verbose_name=_('مكلف'))
    is_critical = models.BooleanField(default=False, verbose_name=_('حرج'))
    
    class Meta:
        verbose_name = _('عنصر فحص السيارة')
        verbose_name_plural = _('عناصر فحص السيارة')
        ordering = ['category__display_order', 'display_order', 'name']
        
    def __str__(self):
        return f"{self.category.name} - {self.name}"


class CarInspectionDetail(models.Model):
    """تفاصيل فحص عنصر معين في تقرير حالة السيارة"""
    
    REPAIR_STATUS_CHOICES = [
        ('not_needed', _('لا يحتاج إصلاح')),
        ('needed', _('يحتاج إصلاح')),
        ('in_progress', _('قيد الإصلاح')),
        ('completed', _('تم الإصلاح')),
    ]
    
    report = models.ForeignKey(CarConditionReport, on_delete=models.CASCADE,
                             related_name='inspection_details', verbose_name=_('تقرير الحالة'))
    inspection_item = models.ForeignKey(CarInspectionItem, on_delete=models.CASCADE,
                                      related_name='details', verbose_name=_('عنصر الفحص'))
    condition = models.CharField(max_length=20, choices=CarInspectionItem.CONDITION_CHOICES,
                               verbose_name=_('الحالة'))
    notes = models.TextField(blank=True, null=True, verbose_name=_('ملاحظات'))
    
    # حقول الإصلاحات والتكاليف
    needs_repair = models.BooleanField(default=False, verbose_name=_('يحتاج إصلاح'))
    repair_description = models.TextField(blank=True, null=True, verbose_name=_('وصف الإصلاح المطلوب'))
    repair_parts = models.TextField(blank=True, null=True, verbose_name=_('قطع الغيار المطلوبة'))
    repair_cost = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True, verbose_name=_('تكلفة الإصلاح'))
    labor_cost = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True, verbose_name=_('تكلفة اليد العاملة'))
    repair_status = models.CharField(max_length=20, choices=REPAIR_STATUS_CHOICES, default='not_needed', verbose_name=_('حالة الإصلاح'))
    repair_date = models.DateField(blank=True, null=True, verbose_name=_('تاريخ الإصلاح'))
    repair_workshop = models.CharField(max_length=100, blank=True, null=True, verbose_name=_('الورشة المسؤولة عن الإصلاح'))
    
    class Meta:
        verbose_name = _('تفاصيل فحص العنصر')
        verbose_name_plural = _('تفاصيل فحص العناصر')
        unique_together = ('report', 'inspection_item')
        
    def __str__(self):
        return f"{self.report} - {self.inspection_item.name} - {self.get_condition_display()}"
        
    @property
    def total_repair_cost(self):
        """إجمالي تكلفة الإصلاح (قطع الغيار + اليد العاملة)"""
        parts_cost = self.repair_cost or 0
        labor = self.labor_cost or 0
        return parts_cost + labor


class CarInspectionImage(models.Model):
    """صور تقرير حالة السيارة"""
    
    def inspection_image_path(instance, filename):
        """تحديد مسار تخزين صور السيارة"""
        ext = filename.split('.')[-1]
        car_id = instance.report.car.id
        report_date = instance.report.date.strftime('%Y%m%d')
        report_type = instance.report.report_type
        return f'car_inspection/car_{car_id}/{report_date}_{report_type}/{uuid.uuid4().hex[:8]}.{ext}'
    
    report = models.ForeignKey(CarConditionReport, on_delete=models.CASCADE,
                             related_name='images', verbose_name=_('تقرير الحالة'))
    inspection_detail = models.ForeignKey(CarInspectionDetail, on_delete=models.CASCADE,
                                        related_name='images', null=True, blank=True,
                                        verbose_name=_('تفاصيل الفحص'))
    image = models.ImageField(upload_to=inspection_image_path, verbose_name=_('الصورة'))
    description = models.CharField(max_length=255, blank=True, null=True, verbose_name=_('وصف الصورة'))
    upload_date = models.DateTimeField(auto_now_add=True, verbose_name=_('تاريخ الرفع'))
    
    class Meta:
        verbose_name = _('صورة فحص السيارة')
        verbose_name_plural = _('صور فحص السيارة')
        ordering = ['-upload_date']
        
    def __str__(self):
        return f"{self.report} - {self.upload_date.strftime('%Y-%m-%d %H:%M')}"


class CustomerSignature(models.Model):
    """توقيع العميل والموظف على تقرير حالة السيارة"""
    
    def signature_path(instance, filename):
        """تحديد مسار تخزين توقيع العميل"""
        ext = filename.split('.')[-1]
        car_id = instance.report.car.id
        report_date = instance.report.date.strftime('%Y%m%d')
        report_type = instance.report.report_type
        signature_type = 'customer' if instance.is_customer else 'staff'
        return f'signatures/car_{car_id}/{report_date}_{report_type}/{signature_type}_{uuid.uuid4().hex[:8]}.{ext}'
    
    report = models.ForeignKey(CarConditionReport, on_delete=models.CASCADE,
                             related_name='signatures', verbose_name=_('تقرير الحالة'))
    signature = models.ImageField(upload_to=signature_path, verbose_name=_('التوقيع'))
    is_customer = models.BooleanField(default=True, verbose_name=_('توقيع العميل'))
    signed_by_name = models.CharField(max_length=100, verbose_name=_('اسم الموقع'))
    signed_date = models.DateTimeField(auto_now_add=True, verbose_name=_('تاريخ التوقيع'))
    ip_address = models.GenericIPAddressField(blank=True, null=True, verbose_name=_('عنوان IP'))
    
    class Meta:
        verbose_name = _('توقيع على تقرير الحالة')
        verbose_name_plural = _('توقيعات على تقارير الحالة')
        unique_together = ('report', 'is_customer')
        
    def __str__(self):
        signature_type = _("العميل") if self.is_customer else _("الموظف")
        return f"{self.report} - توقيع {signature_type} - {self.signed_by_name}"


class AdminPermission(models.Model):
    # إدارة الصلاحيات المتقدمة للمسؤولين
    admin = models.OneToOneField(AdminUser, on_delete=models.CASCADE, related_name='admin_permissions')
    permissions = models.TextField(null=True, blank=True)  # JSON سيتم تخزين الصلاحيات بتنسيق
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def set_permissions(self, permissions_dict):
        # تعيين الصلاحيات كقاموس وتخزينها كسلسلة JSON
        import json
        self.permissions = json.dumps(permissions_dict)
        
    def get_permissions(self):
        # استرجاع الصلاحيات كقاموس من سلسلة JSON
        import json
        if self.permissions:
            return json.loads(self.permissions)
        return {}
        
    def __str__(self):
        return f"صلاحيات المسؤول {self.admin.user.username}"
