from flask import Flask, render_template, redirect, url_for, request, session, flash
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import os

app = Flask(__name__)

# Secret key for session management
app.secret_key = os.environ.get("SECRET_KEY", "your_secret_key_here")

# Database configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///local_services.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# ------------------ DATABASE MODELS ------------------ #
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(200))
    role = db.Column(db.String(50))  # Customer / Provider / Admin
    services = db.relationship('Service', backref='provider', lazy=True)

class Service(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    provider_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    name = db.Column(db.String(100))
    description = db.Column(db.Text)
    price = db.Column(db.Float)
    location = db.Column(db.String(100))
    is_available = db.Column(db.Boolean, default=True)

class Booking(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    service_id = db.Column(db.Integer, db.ForeignKey('service.id'))
    customer_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    status = db.Column(db.String(50), default="Pending")

class Complaint(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    booking_id = db.Column(db.Integer, db.ForeignKey('booking.id'))
    description = db.Column(db.Text)
    status = db.Column(db.String(50), default="Open")

# ------------------ ROUTES ------------------ #
@app.route('/')
def index():
    services = Service.query.filter_by(is_available=True).all()
    return render_template('index.html', services=services)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = generate_password_hash(request.form['password'])
        role = request.form['role']
        new_user = User(name=name, email=email, password=password, role=role)
        db.session.add(new_user)
        db.session.commit()
        flash("Registration successful! Please login.")
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = User.query.filter_by(email=email).first()
        if user and check_password_hash(user.password, password):
            session['user_id'] = user.id
            session['role'] = user.role
            flash("Login successful!")
            return redirect(url_for('index'))
        else:
            flash("Invalid credentials. Please try again.")
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    flash("Logged out successfully.")
    return redirect(url_for('index'))

@app.route('/create_service', methods=['GET', 'POST'])
def create_service():
    if 'user_id' not in session or session['role'] != 'Provider':
        flash("Only service providers can create services.")
        return redirect(url_for('login'))

    if request.method == 'POST':
        name = request.form['name']
        desc = request.form['description']
        price = request.form['price']
        location = request.form['location']
        new_service = Service(
            provider_id=session['user_id'],
            name=name,
            description=desc,
            price=price,
            location=location,
            is_available=True
        )
        db.session.add(new_service)
        db.session.commit()
        flash("Service created successfully!")
        return redirect(url_for('index'))

    return render_template('create_service.html')

@app.route('/complaint', methods=['GET', 'POST'])
def complaint():
    if request.method == 'POST':
        user_id = session.get('user_id')
        desc = request.form['description']
        complaint = Complaint(user_id=user_id, description=desc)
        db.session.add(complaint)
        db.session.commit()
        flash("Complaint submitted successfully.")
        return redirect(url_for('index'))
    return render_template('complaint.html')

# ------------------ DATABASE INITIALIZATION ------------------ #
# Automatically creates tables if they don't exist
with app.app_context():
    db.create_all()

# ------------------ MAIN ENTRY POINT ------------------ #
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
