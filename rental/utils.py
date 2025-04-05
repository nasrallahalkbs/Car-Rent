from datetime import timedelta
from .models import Reservation

def calculate_total_price(car, start_date, end_date):
    """
    Calculate the total price for a car rental
    
    Args:
        car: Car object
        start_date: date object for rental start
        end_date: date object for rental end
        
    Returns:
        float: total price
    """
    days = (end_date - start_date).days + 1  # Include both start and end days
    return car.daily_rate * days

def get_car_availability(car_id, start_date, end_date, exclude_reservation=None):
    """
    Check if a car is available for the specified date range
    
    Args:
        car_id: ID of the car
        start_date: date object for rental start
        end_date: date object for rental end
        exclude_reservation: Optional ID of a reservation to exclude from check (for modifications)
        
    Returns:
        bool: True if car is available, False otherwise
    """
    # Check for any overlapping reservations that are not cancelled
    query = Reservation.objects.filter(
        car_id=car_id,
        status__in=['pending', 'confirmed'],
    ).exclude(
        # Exclude completely non-overlapping reservations
        start_date__gt=end_date,
        end_date__lt=start_date,
    )
    
    # If we're modifying an existing reservation, exclude it from the check
    if exclude_reservation:
        query = query.exclude(id=exclude_reservation)
    
    # If any overlapping reservations exist, car is not available
    return not query.exists()

def format_currency(value):
    """Format a value as currency"""
    return f"${float(value):.2f}"

def get_unavailable_dates(car_id, exclude_reservation=None):
    """
    Get a list of date ranges when the car is unavailable
    
    Args:
        car_id: ID of the car
        exclude_reservation: Optional ID of a reservation to exclude from check (for modifications)
        
    Returns:
        list: List of date ranges (tuples of start_date, end_date)
    """
    query = Reservation.objects.filter(
        car_id=car_id,
        status__in=['pending', 'confirmed']
    )
    
    # If we're modifying an existing reservation, exclude it from the check
    if exclude_reservation:
        query = query.exclude(id=exclude_reservation)
    
    reservations = query.order_by('start_date')
    
    unavailable_dates = []
    for reservation in reservations:
        # Create a date range for each reservation
        current_date = reservation.start_date
        while current_date <= reservation.end_date:
            unavailable_dates.append(current_date)
            current_date += timedelta(days=1)
    
    return unavailable_dates