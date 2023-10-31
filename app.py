from flask import Flask, flash, render_template, redirect, request, url_for, session
from flask_bcrypt import Bcrypt
import psycopg2
from models import User, Shoe, db


app = Flask(__name__)


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/about")
def about():
    return render_template("about.html")


@app.route("/buy")
def buy():
    return render_template("buy.html")


@app.route("/sell")
def sell():
    return render_template("sell.html")


@app.route("/trade")
def trade():
    return render_template("trade.html")


@app.route("/cart")
def cart():
    return render_template("cart.html")


@app.route("/shipping")
def shipping():
    return render_template("shipping.html")


@app.route("/register")
def register():
    return render_template("register.html")


@app.route("/login")
def login():
    return render_template("login.html")


if __name__ == "__main__":
    app.run(debug=True, port=8080)
