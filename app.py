from crypt import methods
import os

from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import login_required

# Configure application
app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True


# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///project.db")

@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


@app.route("/")
def index():

    return render_template("index.html")


@app.route("/admin", methods=["GET", "POST"])
@login_required
def admin():

    if request.method == "POST":
        
        id = request.form.get("id")
        courses = db.execute("SELECT * FROM courses WHERE id = ?", id)

        return render_template("admin.html", courses = courses)

    else:
        ids = db.execute("SELECT * FROM courses")

        return render_template("admin.html", ids = ids)


@app.route("/account")
@login_required
def account():

    users_courses = db.execute("SELECT * FROM users_courses, courses WHERE courses.id = users_courses.course_id AND user_id = ?",
         session["user_id"])

    return render_template("account.html", ids = users_courses)


@app.route("/courses")
def courses():

    courses = db.execute("SELECT * FROM courses")
    
    return render_template("courses.html", ids = courses)


@app.route("/course1")
def course1():

    return render_template("./courses/1.html")


@app.route("/login", methods=["GET", "POST"])
def login():

    # Forget any user_id
    session.clear()

    """Login user"""

    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            flash('must provide username')
            return redirect("/login")
        # Ensure password was submitted
        elif not request.form.get("password"):
            flash("Must provide password")
            return redirect("/login")

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = ?", request.form.get("username"))

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            flash("Wrong username/password")
            return redirect("/login")

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        flash("You are logged in")
        return redirect("/")

    return render_template("login.html")


@app.route("/logout")
def logout():

    # Forget any user_id
    session.clear()

    """Logout user"""
    flash("Logged out")
    return redirect("/")


@app.route("/signup", methods=["GET", "POST"])
def signup():

    # Forget any user_id
    session.clear()

    """Register user"""
    username = request.form.get("username")
    password = request.form.get("password")
    confirmation = request.form.get("confirmation")

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            flash("Must provide username")
            return redirect("/signup")
        # Ensure password was submitted
        elif not request.form.get("password"):
            flash("Must provide password")
            return redirect("/signup")
        # Ensure password confirmation was submitted
        elif not request.form.get("confirmation"):
            flash("Must provide password")
            return redirect("/signup")
        # # Ensure the passwords are the same
        elif password != confirmation:
            flash("Passwords dont match")
            return redirect("/signup")
            
        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = ?", request.form.get("username"))

        # Check if user is allready taken
        if len(rows) == 1:
            flash("Username allready exists!")
            return redirect("/signup")

        # Create new row in people table
        db.execute("INSERT INTO users (username, hash) VALUES (?, ?)", username, generate_password_hash(password))

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = ?", request.form.get("username"))

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]
        
        flash("You are logged in")
        # Redirect user to home page
        return redirect("/")

    else:
        return render_template("signup.html")


