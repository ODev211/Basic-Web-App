from flask import Flask, render_template, request, session, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

# Initialize SQLAlchemy instance
db = SQLAlchemy()

# Initialize the Flask app
app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Needed for session handling

# Database configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///customers.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Bind SQLAlchemy instance to the Flask app
db.init_app(app)

# Import models after initializing the db and app
from init_db import Customer, Booking

# Ensure app context is used when performing operations
with app.app_context():
    # Example operation to verify everything is working
    db.create_all()

# Routes
@app.route('/delete_booking/<int:booking_id>', methods=['POST'])
def delete_booking(booking_id):
    booking = Booking.query.get_or_404(booking_id)
    db.session.delete(booking)
    db.session.commit()
    flash('Booking deleted successfully!', 'success')
    return redirect(url_for('profile'))

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/products')
def products():
    return render_template('products.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        fname = request.form['fname']
        lname = request.form['lname']
        uname = request.form['uname']
        email = request.form['email']
        password = request.form['password']
        confirm_password = request.form['confirm_password']

        if password != confirm_password:
            return "Passwords do not match. Please try again."

        existing_user = Customer.query.filter((Customer.uname == uname) | (Customer.email == email)).first()
        if existing_user:
            return "User already exists!"

        hashed_password = generate_password_hash(password, method='sha256')
        new_customer = Customer(fname=fname, lname=lname, uname=uname, email=email, password=hashed_password)
        db.session.add(new_customer)
        db.session.commit()
        return redirect(url_for('login'))

    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        uname = request.form['uname']
        password = request.form['password']

        user = Customer.query.filter_by(uname=uname).first()
        if user and check_password_hash(user.password, password):
            session['user_id'] = user.id
            return redirect(url_for('home'))
        else:
            return "Invalid credentials!"

    return render_template('login.html')

@app.route('/carbon-footprint')
def carbon_footprint():
    return render_template('carboncalc.html')

@app.route('/booking')
def booking():
    return render_template('booking.html')

@app.route('/accessibility')
def accessibility():
    return render_template('access.html')

# Run the app
if __name__ == "__main__":
    app.run(debug=True)