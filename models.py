from dataclasses import dataclass, field
from datetime import datetime
from flask_login import UserMixin
from typing import Dict, List, Optional
from werkzeug.security import generate_password_hash, check_password_hash

# In-memory storage
users = {}
cars = {}
reservations = {}
reviews = {}
cart_items = {}

@dataclass
class User(UserMixin):
    id: int
    username: str
    email: str
    password_hash: str
    first_name: str = ""
    last_name: str = ""
    phone: str = ""
    is_admin: bool = False
    created_at: datetime = field(default_factory=datetime.now)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
        
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'phone': self.phone,
            'is_admin': self.is_admin,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S')
        }

@dataclass
class Car:
    id: int
    make: str
    model: str
    year: int
    color: str
    license_plate: str
    daily_rate: float
    category: str  # economy, compact, mid-size, luxury, SUV, etc.
    seats: int
    transmission: str  # automatic or manual
    fuel_type: str  # gas, diesel, electric, hybrid
    features: List[str] = field(default_factory=list)
    image_url: str = ""
    is_available: bool = True
    
    def to_dict(self):
        return {
            'id': self.id,
            'make': self.make,
            'model': self.model,
            'year': self.year,
            'color': self.color,
            'license_plate': self.license_plate,
            'daily_rate': self.daily_rate,
            'category': self.category,
            'seats': self.seats,
            'transmission': self.transmission,
            'fuel_type': self.fuel_type,
            'features': self.features,
            'image_url': self.image_url,
            'is_available': self.is_available
        }

@dataclass
class Reservation:
    id: int
    user_id: int
    car_id: int
    start_date: datetime
    end_date: datetime
    total_price: float
    status: str  # pending, confirmed, completed, cancelled
    payment_status: str  # pending, paid, refunded
    created_at: datetime = field(default_factory=datetime.now)
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'car_id': self.car_id,
            'start_date': self.start_date.strftime('%Y-%m-%d'),
            'end_date': self.end_date.strftime('%Y-%m-%d'),
            'total_price': self.total_price,
            'status': self.status,
            'payment_status': self.payment_status,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S')
        }

@dataclass
class Review:
    id: int
    user_id: int
    car_id: int
    reservation_id: int
    rating: int  # 1-5
    comment: str
    created_at: datetime = field(default_factory=datetime.now)
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'car_id': self.car_id,
            'reservation_id': self.reservation_id,
            'rating': self.rating,
            'comment': self.comment,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S')
        }

@dataclass
class CartItem:
    id: int
    user_id: int
    car_id: int
    start_date: datetime
    end_date: datetime
    created_at: datetime = field(default_factory=datetime.now)
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'car_id': self.car_id,
            'start_date': self.start_date.strftime('%Y-%m-%d'),
            'end_date': self.end_date.strftime('%Y-%m-%d'),
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S')
        }

# Initialize with sample data
def initialize_data():
    # Create admin user
    admin = User(
        id=1,
        username="admin",
        email="admin@carrentals.com",
        first_name="Admin",
        last_name="User",
        phone="555-123-4567",
        is_admin=True,
        password_hash=""
    )
    admin.set_password("admin123")
    users[admin.id] = admin
    
    # Create some cars
    car_data = [
        {"make": "Toyota", "model": "Corolla", "category": "Economy", "transmission": "Automatic", "fuel_type": "Gas", "seats": 5},
        {"make": "Honda", "model": "Civic", "category": "Compact", "transmission": "Automatic", "fuel_type": "Gas", "seats": 5},
        {"make": "Ford", "model": "Fusion", "category": "Mid-size", "transmission": "Automatic", "fuel_type": "Hybrid", "seats": 5},
        {"make": "BMW", "model": "3 Series", "category": "Luxury", "transmission": "Automatic", "fuel_type": "Gas", "seats": 5},
        {"make": "Jeep", "model": "Grand Cherokee", "category": "SUV", "transmission": "Automatic", "fuel_type": "Gas", "seats": 5},
        {"make": "Chevrolet", "model": "Silverado", "category": "Truck", "transmission": "Automatic", "fuel_type": "Gas", "seats": 3},
        {"make": "Tesla", "model": "Model 3", "category": "Luxury", "transmission": "Automatic", "fuel_type": "Electric", "seats": 5},
        {"make": "Volkswagen", "model": "Golf", "category": "Compact", "transmission": "Manual", "fuel_type": "Diesel", "seats": 5}
    ]
    
    for i, data in enumerate(car_data, 1):
        year = 2020 + (i % 3)  # Different years 2020-2022
        car = Car(
            id=i,
            make=data["make"],
            model=data["model"],
            year=year,
            color=["White", "Black", "Silver", "Red", "Blue"][i % 5],
            license_plate=f"ABC{i}23",
            daily_rate=50.0 + (i * 10),  # Different rates
            category=data["category"],
            seats=data["seats"],
            transmission=data["transmission"],
            fuel_type=data["fuel_type"],
            features=["GPS", "Bluetooth", "Backup Camera"][:i % 4],
            image_url=f"https://via.placeholder.com/300x200.png?text={data['make']}+{data['model']}",
            is_available=True
        )
        cars[car.id] = car

# Initialize data when module is imported
initialize_data()
