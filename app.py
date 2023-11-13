from flask import (
    Flask,
    flash,
    render_template,
    redirect,
    request,
    url_for,
    session,
    send_from_directory,
    send_file,
)

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
import os
from io import BytesIO
import base64
from models import User, Shoe, Upload, db


app = Flask(__name__)
app.config.from_object("config")  # Load configuration from config.py
bcrypt = Bcrypt()

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


@app.route("/posts")
def posts():
    files = db.session.query(Upload).all()
    for file in files:
        file.base64_data = base64.b64encode(file.data).decode("utf-8")
    return render_template("posts.html", files=files)


@app.route("/upload", methods=["GET", "POST"])
@login_required
def upload():
    files = db.session.query(Upload).all()  # Fetch all uploaded files

    if request.method == "POST":
        file = request.files["file"]
        upload = Upload(filename=file.filename, data=file.read())
        db.session.add(upload)
        db.session.commit()

        # return f"Uploaded: {file.filename}"

    # Encode binary data to base64 before passing it to the template
    for file in files:
        file.base64_data = base64.b64encode(file.data).decode("utf-8")

    return render_template("upload.html", files=files)


@app.route("/upload", methods=["POST"])
@login_required
def create_upload():
    upload = Shoe(
        title=request.form["title"],
        content=request.form["content"],
        author=current_user,
    )
    db.session.add(upload)
    db.session.commit()
    return redirect(url_for("posts"))


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
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
        repassword = request.form["repassword"]
        if User.query.filter_by(username=username).first():
            flash(f"The username '{username}' is already taken")
            return redirect(url_for("register"))

        if password != repassword:
            flash("Passwords do not match. Please try again.", "error")
            return redirect("/register")

        user = User(username=username, email=email, password=password)
        db.session.add(user)
        db.session.commit()
        login_user(user)
        flash(f"Welcome {username}!")
        return redirect(url_for("home"))

    return render_template("register.html")


@app.route("/logout", methods=["GET"])
@login_required
def logout():
    return render_template("logout.html")


@app.route("/logout", methods=["POST"])
@login_required
def logout_action():
    logout_user()
    flash("You have been logged out")
    return redirect(url_for("home"))


if __name__ == "__main__":
    app.run(debug=True, port=8080)
