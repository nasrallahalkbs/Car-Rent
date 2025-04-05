from datetime import datetime
from models import reservations, cart_items

def calculate_total_price(car, start_date, end_date):
    """
    Calculate the total price for a car rental
    
    Args:
        car: Car object
        start_date: datetime object for rental start
        end_date: datetime object for rental end
        
    Returns:
        float: total price
    """
    if isinstance(start_date, str):
        start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
    if isinstance(end_date, str):
        end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
    
    days = (end_date - start_date).days
    if days < 1:
        days = 1
    
    return car.daily_rate * days

def get_car_availability(car_id, start_date, end_date):
    """
    Check if a car is available for the specified date range
    
    Args:
        car_id: ID of the car
        start_date: datetime object for rental start
        end_date: datetime object for rental end
        
    Returns:
        bool: True if car is available, False otherwise
    """
    if isinstance(start_date, str):
        start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
    if isinstance(end_date, str):
        end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
    
    # Check existing reservations
    for reservation in reservations.values():
        if reservation.car_id == car_id and reservation.status != 'cancelled':
            # Check if there's an overlap in dates
            if (start_date <= reservation.end_date and end_date >= reservation.start_date):
                return False
    
    # Check items in carts (temporary holds)
    for item in cart_items.values():
        if item.car_id == car_id:
            # Check if there's an overlap in dates
            if (start_date <= item.end_date and end_date >= item.start_date):
                return False
    
    return True

def format_currency(value):
    """Format a value as currency"""
    return f"${value:.2f}"

def get_unavailable_dates(car_id):
    """
    Get a list of date ranges when the car is unavailable
    
    Args:
        car_id: ID of the car
        
    Returns:
        list: List of date ranges (tuples of start_date, end_date)
    """
    unavailable_dates = []
    
    # Check existing reservations
    for reservation in reservations.values():
        if reservation.car_id == car_id and reservation.status != 'cancelled':
            unavailable_dates.append((reservation.start_date, reservation.end_date))
    
    # Check items in carts (temporary holds)
    for item in cart_items.values():
        if item.car_id == car_id:
            unavailable_dates.append((item.start_date, item.end_date))
    
    return unavailable_dates
