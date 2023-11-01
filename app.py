from flask import Flask, flash, render_template, redirect, request, url_for, session
from flask_bcrypt import Bcrypt
import psycopg2
from flask_login import (
    LoginManager,
    UserMixin,
    login_user,
    logout_user,
    login_required,
    current_user,
)

from models import User, Shoe, db

bcrypt = Bcrypt()

app = Flask(__name__)
app.config.from_object("config")  # Load configuration from config.py

login_manager = LoginManager(app)
login_manager.login_view = "login"

with app.app_context():
    db.init_app(app)
    db.create_all()


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


# DB_HOST = "localhost"
# DB_NAME = "postgres"
# DB_USER = "postgres"
# DB_PASS = "1234"

# conn = psycopg2.connect(
#     host=DB_HOST, dbname=DB_NAME, user=DB_USER, password=DB_PASS, port=5432
# )


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/about")
def about():
    return render_template("about.html")


# @app.route("/register")
# def register():
#     return render_template("register.html")


# @app.route("/login")
# def login():
#     return render_template("login.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        # handle login logic
        username = request.form["username"]
        password = request.form["password"]

        user = User.query.filter_by(username=username).first()

        if user and bcrypt.check_password_hash(user.password_hash, password):
            login_user(user)
            flash(f"Welcome back, {username}!", "success")
            return redirect(url_for("home"))
        else:
            flash("Invalid username or password", "error")
            return redirect(url_for("login"))

    return render_template("login.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        email = request.form["email"]
        password = request.form["password"]

        if User.query.filter_by(username=username).first():
            flash(f"The username '{username}' is already taken")
            return redirect(url_for("register"))

        user = User(username=username, email=email, password=password)
        db.session.add(user)
        db.session.commit()
        login_user(user)
        flash(f"Welcome {username}!")
        return redirect(url_for("home"))

    return render_template("register.html")


if __name__ == "__main__":
    app.run(debug=True, port=8080)
