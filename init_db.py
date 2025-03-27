from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash  # Import for hashing passwords

# Initialize Flask app (only for creating DB)
app = Flask(__name__)

# Database configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///customers.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize the database
db = SQLAlchemy(app)

# Define Customer model
class Customer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    fname = db.Column(db.String(50), nullable=False)
    lname = db.Column(db.String(50), nullable=False)
    uname = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)

# Define Booking model
class Booking(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, db.ForeignKey('customer.id', ondelete="CASCADE"), nullable=False)
    service_type = db.Column(db.String(50), nullable=False)
    date_time = db.Column(db.DateTime, nullable=False)

    customer = db.relationship('Customer', backref=db.backref('bookings', lazy=True, cascade='all, delete-orphan'))

# Function to add a new customer with a hashed password
def add_customer(fname, lname, uname, email, password):
    # Hash the password before storing
    hashed_password = generate_password_hash(password)
    
    # Create new customer instance
    new_customer = Customer(fname=fname, lname=lname, uname=uname, email=email, password=hashed_password)
    
    # Add customer to the database
    db.session.add(new_customer)
    db.session.commit()
    print(f"Customer {uname} added successfully!")

# Create all tables
with app.app_context():
    db.create_all()
    print("Database and tables created successfully!")
    