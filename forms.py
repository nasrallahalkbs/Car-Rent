from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField, SelectField, IntegerField, FloatField, TextAreaField, DateField, HiddenField
from wtforms.validators import DataRequired, Email, EqualTo, Length, NumberRange, ValidationError
from datetime import date

class RegisterForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=3, max=50)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    first_name = StringField('First Name', validators=[DataRequired()])
    last_name = StringField('Last Name', validators=[DataRequired()])
    phone = StringField('Phone Number', validators=[DataRequired()])
    submit = SubmitField('Sign Up')

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Login')

class CarSearchForm(FlaskForm):
    category = SelectField('Car Type', choices=[
        ('', 'All Types'),
        ('Economy', 'Economy'),
        ('Compact', 'Compact'),
        ('Mid-size', 'Mid-size'),
        ('Luxury', 'Luxury'),
        ('SUV', 'SUV'),
        ('Truck', 'Truck')
    ])
    transmission = SelectField('Transmission', choices=[
        ('', 'Any'),
        ('Automatic', 'Automatic'),
        ('Manual', 'Manual')
    ])
    fuel_type = SelectField('Fuel Type', choices=[
        ('', 'Any'),
        ('Gas', 'Gas'),
        ('Diesel', 'Diesel'),
        ('Electric', 'Electric'),
        ('Hybrid', 'Hybrid')
    ])
    min_price = FloatField('Min Price', validators=[NumberRange(min=0)])
    max_price = FloatField('Max Price', validators=[NumberRange(min=0)])
    submit = SubmitField('Search')

class ReservationForm(FlaskForm):
    car_id = HiddenField('Car ID', validators=[DataRequired()])
    start_date = DateField('Pick-up Date', format='%Y-%m-%d', validators=[DataRequired()])
    end_date = DateField('Return Date', format='%Y-%m-%d', validators=[DataRequired()])
    submit = SubmitField('Add to Cart')
    
    def validate_start_date(self, field):
        if field.data < date.today():
            raise ValidationError('Pick-up date cannot be in the past')
    
    def validate_end_date(self, field):
        if field.data < self.start_date.data:
            raise ValidationError('Return date must be after pick-up date')

class CheckoutForm(FlaskForm):
    card_number = StringField('Card Number', validators=[DataRequired(), Length(min=16, max=16)])
    card_name = StringField('Name on Card', validators=[DataRequired()])
    expiry_month = SelectField('Expiry Month', choices=[(str(i), str(i)) for i in range(1, 13)], validators=[DataRequired()])
    expiry_year = SelectField('Expiry Year', choices=[(str(i), str(i)) for i in range(date.today().year, date.today().year + 11)], validators=[DataRequired()])
    cvv = StringField('CVV', validators=[DataRequired(), Length(min=3, max=4)])
    submit = SubmitField('Complete Payment')

class ReviewForm(FlaskForm):
    rating = SelectField('Rating', choices=[(str(i), str(i)) for i in range(1, 6)], validators=[DataRequired()])
    comment = TextAreaField('Comment', validators=[DataRequired()])
    submit = SubmitField('Submit Review')

class CarForm(FlaskForm):
    make = StringField('Make', validators=[DataRequired()])
    model = StringField('Model', validators=[DataRequired()])
    year = IntegerField('Year', validators=[DataRequired(), NumberRange(min=2000, max=date.today().year + 1)])
    color = StringField('Color', validators=[DataRequired()])
    license_plate = StringField('License Plate', validators=[DataRequired()])
    daily_rate = FloatField('Daily Rate', validators=[DataRequired(), NumberRange(min=0)])
    category = SelectField('Category', choices=[
        ('Economy', 'Economy'),
        ('Compact', 'Compact'),
        ('Mid-size', 'Mid-size'),
        ('Luxury', 'Luxury'),
        ('SUV', 'SUV'),
        ('Truck', 'Truck')
    ])
    seats = IntegerField('Seats', validators=[DataRequired(), NumberRange(min=2, max=12)])
    transmission = SelectField('Transmission', choices=[
        ('Automatic', 'Automatic'),
        ('Manual', 'Manual')
    ])
    fuel_type = SelectField('Fuel Type', choices=[
        ('Gas', 'Gas'),
        ('Diesel', 'Diesel'),
        ('Electric', 'Electric'),
        ('Hybrid', 'Hybrid')
    ])
    features = StringField('Features (comma separated)')
    image_url = StringField('Image URL')
    is_available = BooleanField('Available')
    submit = SubmitField('Save Car')

class ProfileForm(FlaskForm):
    first_name = StringField('First Name', validators=[DataRequired()])
    last_name = StringField('Last Name', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    phone = StringField('Phone Number', validators=[DataRequired()])
    submit = SubmitField('Update Profile')
