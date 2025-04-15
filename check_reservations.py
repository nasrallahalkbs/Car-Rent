
import os
import django

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'car_rental_project.settings')
django.setup()

# Import models after setup
from rental.models import Reservation, User
from django.utils import timezone

def check_reservations():
    """Check and display all reservations in the system, grouped by status"""
    
    # Get counts by status
    total = Reservation.objects.count()
    pending = Reservation.objects.filter(status='pending').count()
    confirmed = Reservation.objects.filter(status='confirmed').count()
    completed = Reservation.objects.filter(status='completed').count()
    cancelled = Reservation.objects.filter(status='cancelled').count()
    
    print(f"\n=== RESERVATION SYSTEM CHECK ({timezone.now().strftime('%Y-%m-%d %H:%M:%S')}) ===")
    print(f"Total reservations: {total}")
    print(f"Status breakdown:")
    print(f"  - Pending: {pending}")
    print(f"  - Confirmed: {confirmed}")
    print(f"  - Completed: {completed}")
    print(f"  - Cancelled: {cancelled}")
    print(f"  - Sum: {pending + confirmed + completed + cancelled}")
    
    # Check for any discrepancy
    if total != (pending + confirmed + completed + cancelled):
        print(f"WARNING: Total count {total} doesn't match status sum {pending + confirmed + completed + cancelled}")
    
    # List users with cancelled reservations
    users_with_cancelled = User.objects.filter(reservation__status='cancelled').distinct()
    print(f"\nNumber of users with cancelled reservations: {users_with_cancelled.count()}")
    
    for user in users_with_cancelled:
        cancelled_count = Reservation.objects.filter(user=user, status='cancelled').count()
        print(f"  - User {user.username}: {cancelled_count} cancelled reservations")
    
    print("\n=== CHECK COMPLETE ===")

if __name__ == "__main__":
    check_reservations()
