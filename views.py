from datetime import datetime, timedelta
import json
from flask import render_template, request, redirect, url_for, flash, session
from flask_login import login_user, logout_user, login_required, current_user
from app import app
from forms import RegisterForm, LoginForm, CarSearchForm, ReservationForm, CheckoutForm, ReviewForm, ProfileForm
from models import User, Car, Reservation, Review, CartItem, users, cars, reservations, reviews, cart_items
from utils import calculate_total_price, get_car_availability

@app.route('/')
def index():
    # Get featured cars (5 random cars)
    featured_cars = list(cars.values())[:5]
    return render_template('index.html', featured_cars=featured_cars)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    form = RegisterForm()
    if form.validate_on_submit():
        # Check if email already exists
        for user in users.values():
            if user.email == form.email.data:
                flash('Email already registered', 'danger')
                return render_template('register.html', form=form)
        
        # Generate unique user ID
        user_id = max(users.keys() or [0]) + 1
        
        # Create new user
        new_user = User(
            id=user_id,
            username=form.username.data,
            email=form.email.data,
            first_name=form.first_name.data,
            last_name=form.last_name.data,
            phone=form.phone.data,
            password_hash="",
            is_admin=False
        )
        new_user.set_password(form.password.data)
        
        # Add user to in-memory storage
        users[user_id] = new_user
        
        flash('Registration successful! You can now log in', 'success')
        return redirect(url_for('login'))
    
    return render_template('register.html', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    form = LoginForm()
    if form.validate_on_submit():
        # Find user by email
        user_found = None
        for user in users.values():
            if user.email == form.email.data:
                user_found = user
                break
        
        if user_found and user_found.check_password(form.password.data):
            login_user(user_found, remember=form.remember.data)
            next_page = request.args.get('next')
            flash('Login successful!', 'success')
            return redirect(next_page or url_for('index'))
        else:
            flash('Login failed. Please check email and password', 'danger')
    
    return render_template('login.html', form=form)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out', 'info')
    return redirect(url_for('index'))

@app.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    form = ProfileForm()
    
    if request.method == 'GET':
        form.first_name.data = current_user.first_name
        form.last_name.data = current_user.last_name
        form.email.data = current_user.email
        form.phone.data = current_user.phone
    
    if form.validate_on_submit():
        # Update user information
        current_user.first_name = form.first_name.data
        current_user.last_name = form.last_name.data
        current_user.email = form.email.data
        current_user.phone = form.phone.data
        
        flash('Profile updated successfully', 'success')
        return redirect(url_for('profile'))
    
    # Get user's reservations
    user_reservations = [r for r in reservations.values() if r.user_id == current_user.id]
    
    return render_template('profile.html', form=form, reservations=user_reservations)

@app.route('/cars', methods=['GET'])
def car_listing():
    form = CarSearchForm(request.args)
    
    # Filter cars based on search criteria
    filtered_cars = list(cars.values())
    
    category = request.args.get('category')
    if category:
        filtered_cars = [car for car in filtered_cars if car.category == category]
    
    transmission = request.args.get('transmission')
    if transmission:
        filtered_cars = [car for car in filtered_cars if car.transmission == transmission]
    
    fuel_type = request.args.get('fuel_type')
    if fuel_type:
        filtered_cars = [car for car in filtered_cars if car.fuel_type == fuel_type]
    
    min_price = request.args.get('min_price')
    if min_price and min_price.isdigit():
        min_price = float(min_price)
        filtered_cars = [car for car in filtered_cars if car.daily_rate >= min_price]
    
    max_price = request.args.get('max_price')
    if max_price and max_price.isdigit():
        max_price = float(max_price)
        filtered_cars = [car for car in filtered_cars if car.daily_rate <= max_price]
    
    return render_template('cars.html', cars=filtered_cars, form=form)

@app.route('/car/<int:car_id>', methods=['GET', 'POST'])
def car_detail(car_id):
    car = cars.get(car_id)
    if not car:
        flash('Car not found', 'danger')
        return redirect(url_for('car_listing'))
    
    # Get car reviews
    car_reviews = [r for r in reviews.values() if r.car_id == car_id]
    avg_rating = sum(r.rating for r in car_reviews) / len(car_reviews) if car_reviews else 0
    
    # Reservation form
    form = ReservationForm()
    if form.validate_on_submit():
        if not current_user.is_authenticated:
            flash('Please log in to make a reservation', 'warning')
            return redirect(url_for('login', next=request.url))
        
        start_date = form.start_date.data
        end_date = form.end_date.data
        
        # Check car availability
        is_available = get_car_availability(car_id, start_date, end_date)
        if not is_available:
            flash('Car is not available for the selected dates', 'danger')
            return redirect(url_for('car_detail', car_id=car_id))
        
        # Add to cart
        cart_item_id = max(cart_items.keys() or [0]) + 1
        cart_item = CartItem(
            id=cart_item_id,
            user_id=current_user.id,
            car_id=car_id,
            start_date=start_date,
            end_date=end_date
        )
        cart_items[cart_item_id] = cart_item
        
        flash('Car added to cart', 'success')
        return redirect(url_for('cart'))
    
    return render_template('car_detail.html', car=car, form=form, reviews=car_reviews, avg_rating=avg_rating)

@app.route('/cart')
@login_required
def cart():
    # Get user's cart items
    user_cart_items = [item for item in cart_items.values() if item.user_id == current_user.id]
    
    # Calculate total price
    total_price = 0
    cart_details = []
    
    for item in user_cart_items:
        car = cars.get(item.car_id)
        days = (item.end_date - item.start_date).days
        price = car.daily_rate * days
        total_price += price
        
        cart_details.append({
            'item': item,
            'car': car,
            'days': days,
            'price': price
        })
    
    return render_template('cart.html', cart_items=cart_details, total_price=total_price)

@app.route('/cart/remove/<int:item_id>')
@login_required
def remove_from_cart(item_id):
    if item_id in cart_items and cart_items[item_id].user_id == current_user.id:
        del cart_items[item_id]
        flash('Item removed from cart', 'success')
    else:
        flash('Item not found in cart', 'danger')
    
    return redirect(url_for('cart'))

@app.route('/checkout', methods=['GET', 'POST'])
@login_required
def checkout():
    # Get user's cart items
    user_cart_items = [item for item in cart_items.values() if item.user_id == current_user.id]
    
    if not user_cart_items:
        flash('Your cart is empty', 'warning')
        return redirect(url_for('car_listing'))
    
    form = CheckoutForm()
    if form.validate_on_submit():
        # Process each cart item into a reservation
        for item in user_cart_items:
            car = cars.get(item.car_id)
            days = (item.end_date - item.start_date).days
            price = car.daily_rate * days
            
            # Create reservation
            reservation_id = max(reservations.keys() or [0]) + 1
            reservation = Reservation(
                id=reservation_id,
                user_id=current_user.id,
                car_id=item.car_id,
                start_date=item.start_date,
                end_date=item.end_date,
                total_price=price,
                status='confirmed',
                payment_status='paid'
            )
            reservations[reservation_id] = reservation
            
            # Remove from cart
            del cart_items[item.id]
        
        flash('Reservation confirmed! Thank you for your order.', 'success')
        return redirect(url_for('confirmation'))
    
    # Calculate total price
    total_price = 0
    cart_details = []
    
    for item in user_cart_items:
        car = cars.get(item.car_id)
        days = (item.end_date - item.start_date).days
        price = car.daily_rate * days
        total_price += price
        
        cart_details.append({
            'item': item,
            'car': car,
            'days': days,
            'price': price
        })
    
    return render_template('checkout.html', form=form, cart_items=cart_details, total_price=total_price)

@app.route('/confirmation')
@login_required
def confirmation():
    # Get user's latest reservation
    user_reservations = [r for r in reservations.values() if r.user_id == current_user.id]
    latest_reservation = max(user_reservations, key=lambda r: r.created_at) if user_reservations else None
    
    if not latest_reservation:
        return redirect(url_for('my_reservations'))
    
    car = cars.get(latest_reservation.car_id)
    days = (latest_reservation.end_date - latest_reservation.start_date).days
    
    return render_template('confirmation.html', reservation=latest_reservation, car=car, days=days)

@app.route('/my-reservations')
@login_required
def my_reservations():
    # Get user's reservations
    user_reservations = [r for r in reservations.values() if r.user_id == current_user.id]
    
    # Add car details to each reservation
    reservations_with_cars = []
    for reservation in user_reservations:
        car = cars.get(reservation.car_id)
        days = (reservation.end_date - reservation.start_date).days
        
        # Check if user has already reviewed this reservation
        has_review = any(r.reservation_id == reservation.id for r in reviews.values())
        
        reservations_with_cars.append({
            'reservation': reservation,
            'car': car,
            'days': days,
            'has_review': has_review
        })
    
    return render_template('my_reservations.html', reservations=reservations_with_cars)

@app.route('/review/<int:reservation_id>', methods=['GET', 'POST'])
@login_required
def add_review(reservation_id):
    # Check if reservation exists and belongs to the user
    reservation = reservations.get(reservation_id)
    if not reservation or reservation.user_id != current_user.id:
        flash('Reservation not found', 'danger')
        return redirect(url_for('my_reservations'))
    
    # Check if user has already reviewed this reservation
    if any(r.reservation_id == reservation_id for r in reviews.values()):
        flash('You have already reviewed this reservation', 'warning')
        return redirect(url_for('my_reservations'))
    
    car = cars.get(reservation.car_id)
    form = ReviewForm()
    
    if form.validate_on_submit():
        # Create review
        review_id = max(reviews.keys() or [0]) + 1
        review = Review(
            id=review_id,
            user_id=current_user.id,
            car_id=car.id,
            reservation_id=reservation_id,
            rating=int(form.rating.data),
            comment=form.comment.data
        )
        reviews[review_id] = review
        
        flash('Review submitted successfully', 'success')
        return redirect(url_for('my_reservations'))
    
    return render_template('car_detail.html', car=car, form=form, show_review_form=True)

@app.context_processor
def inject_cart_count():
    if current_user.is_authenticated:
        count = len([item for item in cart_items.values() if item.user_id == current_user.id])
    else:
        count = 0
    return {'cart_count': count}

@app.context_processor
def inject_dark_mode():
    dark_mode = session.get('dark_mode', False)
    return {'dark_mode': dark_mode}

@app.route('/toggle-dark-mode')
def toggle_dark_mode():
    session['dark_mode'] = not session.get('dark_mode', False)
    return redirect(request.referrer or url_for('index'))
