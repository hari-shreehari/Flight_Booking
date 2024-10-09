from flask import Flask, render_template, redirect, url_for, flash, request
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, DateTimeField
from wtforms.validators import DataRequired
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from datetime import datetime

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///flight_booking.db'
db = SQLAlchemy(app)

# Initialize Flask-Login
login_manager = LoginManager()
login_manager.login_view = 'login'
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Register')

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')

class FlightForm(FlaskForm):
    flight_number = StringField('Flight Number', validators=[DataRequired()])
    departure_city = StringField('Departure City', validators=[DataRequired()])
    arrival_city = StringField('Arrival City', validators=[DataRequired()])
    departure_time = DateTimeField('Departure Time', validators=[DataRequired()],
                                   format='%Y-%m-%d %H:%M:%S')
    submit = SubmitField('Add Flight')

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    bookings = db.relationship('Booking', backref='user', lazy=True)

    def __init__(self, username, password):
        self.username = username
        self.password = generate_password_hash(password, method='sha256')

class Flight(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    flight_number = db.Column(db.String(10), unique=True, nullable=False)
    departure_city = db.Column(db.String(50), nullable=False)
    arrival_city = db.Column(db.String(50), nullable=False)
    departure_time = db.Column(db.DateTime, default=datetime.utcnow)
    bookings = db.relationship('Booking', backref='flight', lazy=True)

class Booking(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    flight_id = db.Column(db.Integer, db.ForeignKey('flight.id'), nullable=False)
    booking_date = db.Column(db.DateTime, default=datetime.utcnow)

@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        user = User.query.filter_by(username=username).first()
        if user:
            flash('Username already exists. Choose another username.', 'danger')
        else:
            new_user = User(username=username, password=password)
            db.session.add(new_user)
            db.session.commit()
            flash('Registration successful. You can now log in.', 'success')
            return redirect(url_for('login'))
    return render_template('registration.html', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password, password):
            login_user(user)
            flash('Login successful!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Login failed. Check your username and password.', 'danger')
    return render_template('login.html', form=form)

@app.route('/dashboard')
@login_required
def dashboard():
    bookings = Booking.query.filter_by(user_id=current_user.id).all()
    return render_template('dashboard.html', bookings=bookings)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/book_flight/<int:flight_id>', methods=['GET', 'POST'])
@login_required
def book_flight(flight_id):
    flight = Flight.query.get(flight_id)
    if request.method == 'POST':
        booking = Booking(user_id=current_user.id, flight_id=flight_id, booking_date=datetime.utcnow())
        db.session.add(booking)
        db.session.commit()
        flash('Booking successful!', 'success')
        return redirect(url_for('dashboard'))
    return render_template('book_flight.html', flight=flight)

@app.route('/add_flight', methods=['GET', 'POST'])
@login_required
def add_flight():
    form = FlightForm()
    if form.validate_on_submit():
        flight = Flight(
            flight_number=form.flight_number.data,
            departure_city=form.departure_city.data,
            arrival_city=form.arrival_city.data,
            departure_time=form.departure_time.data
        )
        db.session.add(flight)
        db.session.commit()
        flash('Flight added successfully!', 'success')
        return redirect(url_for('dashboard'))
    return render_template('add_flight.html', form=form)

@app.route('/remove_flight/<int:flight_id>', methods=['POST'])
@login_required
def remove_flight(flight_id):
    flight = Flight.query.get(flight_id)
    if flight:
        db.session.delete(flight)
        db.session.commit()
        flash('Flight removed successfully!', 'success')
    else:
        flash('Flight not found.', 'danger')
    return redirect(url_for('dashboard'))

@app.route('/view_bookings')
@login_required
def view_bookings():
    booked_flights = Booking.query.filter_by(user_id=current_user.id).all()
    return render_template('view_bookings.html', booked_flights=booked_flights)

@app.route('/booked_flight')
@login_required
def booked_flight():
    all_booked_flights = Booking.query.all()
    return render_template('booked_flight.html', all_booked_flights=all_booked_flights)

@app.route('/')
def home():
    return render_template('home.html')

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)

