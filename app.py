# app.py
import os
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

from flask import Flask, redirect, url_for, render_template, request, session, flash
from flask_dance.contrib.google import make_google_blueprint, google
from flask_dance.contrib.github import make_github_blueprint, github
from werkzeug.security import generate_password_hash, check_password_hash
from flask_migrate import Migrate

from dotenv import load_dotenv
import os

# ---------- Load Environment Variables ----------
load_dotenv()

# ---------- Flask App Setup ----------
app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY", "default_secret_key")
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///codewhiz.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# ✅ Correct: Import db and models (db is NOT initialized here)
from models import db, User, Problem, TestCase
db.init_app(app)  
migrate = Migrate(app, db)

# ✅ Register Blueprints
from routes.problems import problem_bp
app.register_blueprint(problem_bp)

from admin import admin_bp
app.register_blueprint(admin_bp)

from user_views import user_bp
app.register_blueprint(user_bp)

from utils.auth import auth
app.register_blueprint(auth)











# ✅ Create Tables
with app.app_context():
    db.create_all()

# ---------- Google OAuth ----------
google_bp = make_google_blueprint(
    client_id=os.getenv("GOOGLE_OAUTH_CLIENT_ID"),
    client_secret=os.getenv("GOOGLE_OAUTH_CLIENT_SECRET"),
    redirect_to="google_authorized",
    scope=["profile", "email"]
)
app.register_blueprint(google_bp, url_prefix="/login")

# ---------- GitHub OAuth ----------
github_bp = make_github_blueprint(
    client_id=os.getenv("GITHUB_OAUTH_CLIENT_ID"),
    client_secret=os.getenv("GITHUB_OAUTH_CLIENT_SECRET"),
    redirect_to="github_authorized"
)
app.register_blueprint(github_bp, url_prefix="/login")

# ---------- Routes ----------

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        user = User.query.filter_by(email=email).first()
        if user and user.password and check_password_hash(user.password, password):
            session["email"] = user.email
            return redirect(url_for("home"))
        else:
            flash("Invalid email or password.")
            return redirect(url_for("login"))
    return render_template("login.html")

@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        if User.query.filter_by(email=email).first():
            flash("Email already registered. Please log in.")
            return redirect(url_for("login"))

        hashed_password = generate_password_hash(password)
        new_user = User(email=email, password=hashed_password, auth_type="form")
        db.session.add(new_user)
        db.session.commit()

        session["email"] = email
        return redirect(url_for("home"))
    return render_template("signup.html")

@app.route("/google/authorized")
def google_authorized():
    if not google.authorized:
        return redirect(url_for("google.login"))

    resp = google.get("/oauth2/v2/userinfo")
    if not resp.ok:
        return f"Error fetching Google user info: {resp.text}"

    user_info = resp.json()
    email = user_info["email"]
    name = user_info.get("name")

    user = User.query.filter_by(email=email).first()
    if not user:
        user = User(email=email, name=name, auth_type="google")
        db.session.add(user)
        db.session.commit()

    session["email"] = email
    return redirect(url_for("home"))

@app.route("/github/authorized")
def github_authorized():
    if not github.authorized:
        return redirect(url_for("github.login"))

    resp = github.get("/user")
    if not resp.ok:
        return f"Error fetching GitHub user info: {resp.text}"

    user_info = resp.json()
    email = user_info.get("email", f"{user_info['login']}@github.com")
    username = user_info["login"]

    user = User.query.filter_by(email=email).first()
    if not user:
        user = User(email=email, name=username, auth_type="github")
        db.session.add(user)
        db.session.commit()

    session["email"] = email
    return redirect(url_for("home"))

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("home"))

# ---------- Run ----------
if __name__ == "__main__":
    app.run(debug=True)






