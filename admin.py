from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from forms import CarForm
from models import cars, reservations, users, Car
from datetime import date
from functools import wraps

admin_blueprint = Blueprint('admin', __name__)

# Admin required decorator
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin:
            flash('You do not have permission to access this page', 'danger')
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    return decorated_function

@admin_blueprint.route('/')
@login_required
@admin_required
def admin_index():
    # Dashboard statistics
    total_cars = len(cars)
    total_users = len(users) - 1  # Excluding admin
    total_reservations = len(reservations)
    active_reservations = len([r for r in reservations.values() if r.status == 'confirmed'])
    
    recent_reservations = sorted(
        list(reservations.values()),
        key=lambda r: r.created_at,
        reverse=True
    )[:5]
    
    reservation_data = []
    for res in recent_reservations:
        car = cars.get(res.car_id)
        user = users.get(res.user_id)
        reservation_data.append({
            'reservation': res,
            'car': car,
            'user': user
        })
    
    return render_template(
        'admin/index.html',
        total_cars=total_cars,
        total_users=total_users,
        total_reservations=total_reservations,
        active_reservations=active_reservations,
        recent_reservations=reservation_data
    )

@admin_blueprint.route('/cars')
@login_required
@admin_required
def admin_cars():
    car_list = list(cars.values())
    return render_template('admin/cars.html', cars=car_list)

@admin_blueprint.route('/car/add', methods=['GET', 'POST'])
@login_required
@admin_required
def add_car():
    form = CarForm()
    
    if form.validate_on_submit():
        # Create new car
        car_id = max(cars.keys() or [0]) + 1
        
        features = []
        if form.features.data:
            features = [f.strip() for f in form.features.data.split(',')]
        
        new_car = Car(
            id=car_id,
            make=form.make.data,
            model=form.model.data,
            year=form.year.data,
            color=form.color.data,
            license_plate=form.license_plate.data,
            daily_rate=form.daily_rate.data,
            category=form.category.data,
            seats=form.seats.data,
            transmission=form.transmission.data,
            fuel_type=form.fuel_type.data,
            features=features,
            image_url=form.image_url.data or f"https://via.placeholder.com/300x200.png?text={form.make.data}+{form.model.data}",
            is_available=form.is_available.data
        )
        
        cars[car_id] = new_car
        
        flash('Car added successfully', 'success')
        return redirect(url_for('admin.admin_cars'))
    
    return render_template('admin/cars.html', form=form, add_mode=True)

@admin_blueprint.route('/car/edit/<int:car_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_car(car_id):
    car = cars.get(car_id)
    if not car:
        flash('Car not found', 'danger')
        return redirect(url_for('admin.admin_cars'))
    
    form = CarForm()
    
    if request.method == 'GET':
        form.make.data = car.make
        form.model.data = car.model
        form.year.data = car.year
        form.color.data = car.color
        form.license_plate.data = car.license_plate
        form.daily_rate.data = car.daily_rate
        form.category.data = car.category
        form.seats.data = car.seats
        form.transmission.data = car.transmission
        form.fuel_type.data = car.fuel_type
        form.features.data = ', '.join(car.features)
        form.image_url.data = car.image_url
        form.is_available.data = car.is_available
    
    if form.validate_on_submit():
        # Update car
        car.make = form.make.data
        car.model = form.model.data
        car.year = form.year.data
        car.color = form.color.data
        car.license_plate = form.license_plate.data
        car.daily_rate = form.daily_rate.data
        car.category = form.category.data
        car.seats = form.seats.data
        car.transmission = form.transmission.data
        car.fuel_type = form.fuel_type.data
        
        features = []
        if form.features.data:
            features = [f.strip() for f in form.features.data.split(',')]
        car.features = features
        
        car.image_url = form.image_url.data or car.image_url
        car.is_available = form.is_available.data
        
        flash('Car updated successfully', 'success')
        return redirect(url_for('admin.admin_cars'))
    
    return render_template('admin/cars.html', form=form, edit_mode=True, car=car)

@admin_blueprint.route('/car/delete/<int:car_id>')
@login_required
@admin_required
def delete_car(car_id):
    if car_id in cars:
        # Check if car has active reservations
        active_res = [r for r in reservations.values() if r.car_id == car_id and r.end_date >= date.today()]
        if active_res:
            flash('Cannot delete car with active reservations', 'danger')
            return redirect(url_for('admin.admin_cars'))
        
        del cars[car_id]
        flash('Car deleted successfully', 'success')
    else:
        flash('Car not found', 'danger')
    
    return redirect(url_for('admin.admin_cars'))

@admin_blueprint.route('/reservations')
@login_required
@admin_required
def admin_reservations():
    reservation_list = []
    
    for res in reservations.values():
        car = cars.get(res.car_id)
        user = users.get(res.user_id)
        reservation_list.append({
            'reservation': res,
            'car': car,
            'user': user
        })
    
    # Sort by date, most recent first
    reservation_list.sort(key=lambda x: x['reservation'].created_at, reverse=True)
    
    return render_template('admin/reservations.html', reservations=reservation_list)

@admin_blueprint.route('/reservation/status/<int:reservation_id>/<string:status>')
@login_required
@admin_required
def update_reservation_status(reservation_id, status):
    if reservation_id in reservations:
        valid_statuses = ['pending', 'confirmed', 'completed', 'cancelled']
        if status in valid_statuses:
            reservations[reservation_id].status = status
            flash('Reservation status updated', 'success')
        else:
            flash('Invalid status', 'danger')
    else:
        flash('Reservation not found', 'danger')
    
    return redirect(url_for('admin.admin_reservations'))

@admin_blueprint.route('/users')
@login_required
@admin_required
def admin_users():
    user_list = list(users.values())
    return render_template('admin/users.html', users=user_list)
