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
app.config.from_object("config")
bcrypt = Bcrypt()

login_manager = LoginManager(app)
login_manager.login_view = "login"

with app.app_context():
    db.init_app(app)
    db.create_all()


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


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
    files = db.session.query(Upload).all()

    if request.method == "POST":
        file = request.files["file"]
        brand = request.form.get("Brand")
        shoe_type = request.form.get("Type")
        display_name = request.form.get("display_name")
        # Save the shoe information to the Upload database
        upload = Upload(
            filename=file.filename,
            data=file.read(),
            brand=brand,
            type=shoe_type,
            display_name=display_name,
        )
        db.session.add(upload)
        db.session.commit()

        return redirect(url_for("posts"))

    for file in files:
        file.base64_data = base64.b64encode(file.data).decode("utf-8")

    return render_template("upload.html", files=files)


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


@app.route("/delete/<int:post_id>", methods=["POST"])
@login_required
def delete_action(post_id):
    post = Upload.query.get_or_404(post_id)
    if current_user.username != post.display_name:
        flash(f"You don't have permission to delete this post")
        return redirect(url_for("posts"))

    db.session.delete(post)
    db.session.commit()
    flash(f"Post '{post.display_name}' has been deleted")
    return redirect("/posts")


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
