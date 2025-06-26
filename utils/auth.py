# auth.py

from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from functools import wraps
from models import User
from werkzeug.security import check_password_hash, generate_password_hash

auth = Blueprint('auth', __name__)

# ✅ Decorator
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "email" not in session:
            flash("Please log in to access this page.")
            return redirect(url_for("auth.login"))
        return f(*args, **kwargs)
    return decorated_function

# ✅ Login route
@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = User.query.filter_by(email=email).first()

        if user and check_password_hash(user.password, password):
            session['email'] = user.email
            flash("Successfully logged in")
            return redirect(url_for('user_views.all_problems'))

        else:
            flash("Invalid credentials")
            return redirect(url_for('auth.login'))
    return render_template('login.html')

# ✅ Signup route (optional but helpful here)
# ✅ Signup route (fixed)
@auth.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        name = request.form.get('username', 'User')  # or use 'name' if input is <input name="name">

        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            flash("Email already registered.")
            return redirect(url_for('auth.signup'))

        hashed_pw = generate_password_hash(password)
        new_user = User(email=email, password=hashed_pw, name=name)  # ✅ FIXED HERE

        from app import db  # assuming db is defined in app.py
        db.session.add(new_user)
        db.session.commit()

        flash("Account created successfully. Please log in.")
        return redirect(url_for('auth.login'))
    return render_template('signup.html')


# ✅ Logout route
@auth.route('/logout')
def logout():
    session.pop('email', None)
    flash("You’ve been logged out.")
    return redirect(url_for('auth.login'))
