from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone

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
    booking_date = models.DateTimeField(auto_now_add=True, help_text="Date and time of booking")
    deposit_amount = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    
    # معلومات الدفع
    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default='pending')
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES, blank=True, null=True)
    payment_reference = models.CharField(max_length=50, blank=True, null=True, help_text="Reference number for payment")
    payment_date = models.DateTimeField(blank=True, null=True)
    transaction_id = models.CharField(max_length=100, blank=True, null=True)
    
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