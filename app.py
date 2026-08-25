from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_login import (
    LoginManager,
    login_user,
    logout_user,
    login_required,
    current_user
)
from werkzeug.security import (
    generate_password_hash,
    check_password_hash
)

from models import db, User

app = Flask(__name__)

# ==========================
# FLASK CONFIGURATION
# ==========================
app.config["SECRET_KEY"] = "anime-world-secret-key"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///database.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# ==========================
# DATABASE
# ==========================
db.init_app(app)

# ==========================
# LOGIN MANAGER
# ==========================
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))

# ==========================
# CREATE DATABASE
# ==========================
with app.app_context():
    db.create_all()

# ==========================
# HOME
# ==========================
@app.route("/")
def home():
    if current_user.is_authenticated:
        return render_template("home.html", username=current_user.username)
    return redirect(url_for("login"))

# ==========================
# DORAEMON SHOW PAGE
# ==========================
@app.route("/doraemon")
@login_required
def doraemon():
    return render_template("doraemon.html")

# ==========================
# LOGIN
# ==========================
@app.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("home"))

    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        # Find user using SQLAlchemy 2.0 syntax
        user = db.session.scalar(db.select(User).where(User.username == username))

        # Check user and password
        if user and check_password_hash(user.password, password):
            login_user(user)
            return redirect(url_for("home"))

        return render_template(
            "login.html",
            error="Invalid username or password!"
        )

    return render_template("login.html")

# ==========================
# SIGNUP & REGISTER
# ==========================
@app.route("/signup", methods=["GET", "POST"])
@app.route("/register", methods=["GET", "POST"])
def signup():
    if current_user.is_authenticated:
        return redirect(url_for("home"))

    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        # Check existing username
        existing_user = db.session.scalar(db.select(User).where(User.username == username))
        if existing_user:
            return render_template("login.html", error="Username already exists!")

        # Hash password
        hashed_password = generate_password_hash(password)

        # Create user
        user = User(
            username=username,
            password=hashed_password
        )

        db.session.add(user)
        db.session.commit()

        # Automatically log in after successful sign up
        login_user(user)
        return redirect(url_for("home"))

    return render_template("login.html")

# ==========================
# LOGOUT
# ==========================
@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("login"))

# ==========================
# RUN
# ==========================
if __name__ == "__main__":
    app.run(debug=True)
