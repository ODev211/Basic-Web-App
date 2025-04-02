from flask import Flask, render_template, request, session, redirect, url_for, flash
from werkzeug.security import generate_password_hash, check_password_hash
from extensions import db
from datetime import datetime, date
from models import Customer, Booking

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Needed for session handling

# Database configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///customers.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Bind SQLAlchemy instance to the Flask app
db.init_app(app)

# Create tables if they don't exist
with app.app_context():
    db.create_all()
    print("Database and tables created successfully!")

# Routes
@app.route('/')
def home():
    user_logged_in = 'user_id' in session
    return render_template('home.html', user_logged_in=user_logged_in)

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
        terms = request.form.get('terms')  # Checkbox field for Terms & Privacy Policy

        if password != confirm_password:
            flash("Passwords do not match. Please try again.", "error")
            return redirect(url_for('register'))

        if not terms:
            flash("You must agree to the Terms and Conditions and Privacy Policy.", "error")
            return redirect(url_for('register'))

        existing_user = Customer.query.filter((Customer.uname == uname) | (Customer.email == email)).first()
        if existing_user:
            flash("User already exists! Please login instead.", "error")
            return redirect(url_for('register'))

        hashed_password = generate_password_hash(password, method='pbkdf2:sha256')
        new_customer = Customer(fname=fname, lname=lname, uname=uname, email=email, password=hashed_password)
        db.session.add(new_customer)
        db.session.commit()
        flash("Registration successful! Please login.", "success")
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
            flash("Login successful!", "success")
            return redirect(url_for('home'))
        else:
            flash("Invalid credentials. Please try again.", "error")
            return redirect(url_for('login'))

    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    flash("You have been logged out.", "success")
    return redirect(url_for('home'))

@app.route('/carbon-footprint')
def carbon_footprint():
    return render_template('carboncalc.html')

@app.route('/accessibility', methods=['GET'])
def accessibility():
    return render_template('access.html')

@app.route('/profile', methods=['GET', 'POST'])
def profile():
    if 'user_id' not in session:
        flash('Please log in to access your profile.', 'error')
        return redirect(url_for('login'))
    user = Customer.query.get(session['user_id'])
    if not user:
        flash('User not found.', 'error')
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        user.fname = request.form['fname']
        user.lname = request.form['lname']
        user.uname = request.form['uname']
        user.email = request.form['email']
        new_password = request.form['password']
        if new_password and new_password != "********":
            user.password = generate_password_hash(new_password, method='pbkdf2:sha256')
        db.session.commit()
        flash('Profile updated successfully!', 'success')
        return redirect(url_for('profile'))
    
    bookings = Booking.query.filter_by(customer_id=user.id).order_by(Booking.date_time).all()
    return render_template('profile.html', user=user, bookings=bookings)

@app.route('/delete_profile', methods=['POST'])
def delete_profile():
    if 'user_id' not in session:
        flash('You are not logged in.', 'error')
        return redirect(url_for('login'))
    user = Customer.query.get(session['user_id'])
    if user:
        db.session.delete(user)
        db.session.commit()
        session.pop('user_id', None)
        flash('Your profile has been deleted.', 'success')
    else:
        flash('User not found.', 'error')
    return redirect(url_for('home'))

@app.route('/booking', methods=['GET', 'POST'])
def booking():
    # Ensure user is logged in
    if 'user_id' not in session:
        flash("You need to register or log in before booking.", "error")
        return redirect(url_for('register'))

    # Handle POST submission
    if request.method == 'POST':
        service_type = request.form.get('service_type')
        selected_date = request.form.get('selected_date')
        time_slot = request.form.get('time_slot')

        try:
            booking_dt = datetime.strptime(selected_date + ' ' + time_slot, "%Y-%m-%d %I%p")
        except Exception as e:
            flash("Invalid date or time format.", "error")
            return redirect(url_for('booking'))

        # Check for existing bookings
        existing = Booking.query.filter(
            db.func.date(Booking.date_time) == selected_date,
            Booking.date_time == booking_dt
        ).first()
        if existing:
            flash("That time slot is no longer available. Please choose another time.", "error")
            return redirect(url_for('booking'))

        # Save new booking
        new_booking = Booking(customer_id=session['user_id'], service_type=service_type, date_time=booking_dt)
        db.session.add(new_booking)
        db.session.commit()
        flash(f"Booking successfully created for {time_slot} on {selected_date}!", "success")
        return redirect(url_for('booking'))

    # For GET requests, determine the selected date
    selected_date = request.args.get('selected_date', date.today().strftime("%Y-%m-%d"))

    # Fetch bookings for the selected date
    bookings_on_day = Booking.query.filter(
        db.func.date(Booking.date_time) == selected_date
    ).all()
    booked_slots = [booking.date_time.strftime("%I%p").lstrip("0").lower() for booking in bookings_on_day]

    return render_template('booking.html', selected_date=selected_date, booked_slots=booked_slots)

@app.route('/get_booked_slots', methods=['GET'])
def get_booked_slots():
    selected_date = request.args.get('selected_date')
    bookings_on_day = Booking.query.filter(
        db.func.date(Booking.date_time) == selected_date
    ).all()
    booked_slots = [booking.date_time.strftime("%I%p").lstrip("0").lower() for booking in bookings_on_day]
    return {"booked_slots": booked_slots}

@app.route('/delete_booking/<int:booking_id>', methods=['POST'])
def delete_booking(booking_id):
    booking = Booking.query.get_or_404(booking_id)
    db.session.delete(booking)
    db.session.commit()
    flash('Booking deleted successfully!', 'success')
    return redirect(url_for('profile'))

# This is a major component in making sure all the pages are showing profile button when the user is logged in
# Instead of being a login button on every page when the user has already logged in
@app.context_processor
def inject_user():
    return dict(user_logged_in=('user_id' in session))


if __name__ == "__main__":
    app.run(debug=True)