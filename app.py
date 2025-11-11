from flask import Flask, render_template, redirect, url_for, request, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import (
    LoginManager, UserMixin, login_user,
    login_required, logout_user, current_user
)
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from sqlalchemy.sql import func
import os

# -------------------- Flask Setup --------------------
app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'yoursecretkey')

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(BASE_DIR, 'local_services.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

login_manager = LoginManager()
login_manager.login_view = 'login'
login_manager.init_app(app)

# -------------------- Database Models --------------------
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), nullable=False, unique=True)
    email = db.Column(db.String(150), nullable=False, unique=True)
    password = db.Column(db.String(150), nullable=False)
    role = db.Column(db.String(50), nullable=False, default='customer')  # customer/provider/admin
    location = db.Column(db.String(100))


class Service(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    provider_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    price = db.Column(db.Float, nullable=False)
    location = db.Column(db.String(100), nullable=False)
    is_available = db.Column(db.Boolean, default=True)

    provider = db.relationship('User', backref='services')

    @property
    def avg_rating(self):
        avg = db.session.query(func.avg(Booking.rating)).filter(
            Booking.service_id == self.id,
            Booking.rating > 0
        ).scalar()
        return round(avg, 1) if avg else 0


class Booking(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    provider_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    service_id = db.Column(db.Integer, db.ForeignKey('service.id'), nullable=False)
    customer_name = db.Column(db.String(100))
    age = db.Column(db.Integer)
    gender = db.Column(db.String(20))
    address = db.Column(db.String(200))
    date = db.Column(db.String(50))
    time = db.Column(db.String(50))
    payment_method = db.Column(db.String(20))
    rating = db.Column(db.Integer, default=0)
    status = db.Column(db.String(20), default="Pending")
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    service = db.relationship('Service', backref='bookings', lazy=True)
    customer = db.relationship('User', foreign_keys=[customer_id], backref='customer_bookings', lazy=True)
    provider = db.relationship('User', foreign_keys=[provider_id], backref='provider_bookings', lazy=True)


class Complaint(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    complaint_text = db.Column(db.Text, nullable=False)
    status = db.Column(db.String(50), default="Pending")
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    user = db.relationship("User", backref="complaints")


class Chat(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    provider_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    message = db.Column(db.Text, nullable=False)
    sender_role = db.Column(db.String(20))  # 'customer' or 'provider'
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# -------------------- Context Processor --------------------
@app.context_processor
def inject_provider_notifications():
    pending_count = 0
    if current_user.is_authenticated and current_user.role == "provider":
        pending_count = Booking.query.filter_by(provider_id=current_user.id, status="Pending").count()
    return dict(provider_pending_count=pending_count)

# -------------------- Routes --------------------
@app.route('/')
def index():
    services = Service.query.filter_by(is_available=True).all()
    nearby_services = []
    if current_user.is_authenticated and current_user.location:
        nearby_services = Service.query.filter(
            Service.location.contains(current_user.location),
            Service.is_available == True
        ).all()
    return render_template('index.html', services=services, nearby_services=nearby_services)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = generate_password_hash(request.form['password'], method='pbkdf2:sha256')
        role = request.form['role']
        location = request.form['location']

        new_user = User(username=username, email=email, password=password, role=role, location=location)
        db.session.add(new_user)
        db.session.commit()
        flash('Registration successful! Please login.', 'success')
        return redirect(url_for('login'))
    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = User.query.filter_by(email=email).first()
        if not user or not check_password_hash(user.password, password):
            flash('Invalid credentials', 'danger')
            return redirect(url_for('login'))

        login_user(user)
        flash('Logged in successfully!', 'success')
        if user.role == "admin":
            return redirect(url_for('admin'))
        return redirect(url_for('index'))
    return render_template('login.html')


@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Logged out successfully.', 'info')
    return redirect(url_for('index'))


@app.route('/services')
def services():
    query = request.args.get('q', '')
    location = request.args.get('location', '')
    services = Service.query.filter(Service.is_available == True)
    if query:
        services = services.filter(Service.name.contains(query))
    if location:
        services = services.filter(Service.location.contains(location))
    services = services.all()
    return render_template('services.html', services=services)

# -------- Admin & Other routes unchanged --------
# (keep your existing admin, booking, complaint, chat routes here)

# -------------------- Auto DB Creation + Admin --------------------
with app.app_context():
    db.create_all()

    if not User.query.filter_by(role='admin').first():
        admin_user = User(
            username="admin",
            email="admin@example.com",
            password=generate_password_hash("admin123", method='pbkdf2:sha256'),
            role="admin"
        )
        db.session.add(admin_user)
        db.session.commit()
        print("✅ Default admin created: Email: admin@example.com | Password: admin123")

# -------------------- Run App (Render-friendly) --------------------
if __name__ == "__main__":
    # Render requires 0.0.0.0 host and a defined port
    port = int(os.environ.get('PORT', 5000))
    app.run(host="0.0.0.0", port=port)
