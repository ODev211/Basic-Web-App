from extensions import db
from werkzeug.security import generate_password_hash

class Customer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    fname = db.Column(db.String(50), nullable=False)
    lname = db.Column(db.String(50), nullable=False)
    uname = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)

class Booking(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, db.ForeignKey('customer.id', ondelete="CASCADE"), nullable=False)
    service_type = db.Column(db.String(50), nullable=False)
    date_time = db.Column(db.DateTime, nullable=False)

    customer = db.relationship('Customer', backref=db.backref('bookings', lazy=True, cascade='all, delete-orphan'))

    