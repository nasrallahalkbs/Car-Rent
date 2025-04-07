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
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    car = models.ForeignKey(Car, on_delete=models.CASCADE)
    start_date = models.DateField()
    end_date = models.DateField() 
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    notes = models.TextField(blank=True, null=True, help_text="Additional notes or payment details")
    
    def __str__(self):
        return f"Reservation #{self.id} - {self.car} ({self.status})"

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
    
    def __str__(self):
        return f"Cart item: {self.car} for {self.user.username}"