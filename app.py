from crypt import methods
import os

from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from requests import post
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

    courses = db.execute("SELECT * FROM courses ORDER BY id DESC LIMIT 3")
    return render_template("index.html", ids = courses)
    

@app.route("/admin", methods=["GET", "POST"])
@login_required
def admin():

    if request.method == "POST":

        id = request.form.get("id")
        ids = db.execute("SELECT * FROM courses")
        courses = db.execute("SELECT * FROM courses WHERE id = ?", id)

        course_id = courses[0]["id"]

        # Create a new course
        if id == "new":
            db.execute("INSERT INTO courses (text, price, name) VALUES ('Description', 'Free', 'Name')")

            flash("New Course Created")
            return redirect("/admin")

        # Delete Course
        elif id == "delete":

            db.execute("DELETE FROM courses")

        # Change course info
        elif request.form.get("name") and request.form.get("text") and course_id != 0 and request.form.get("price"):

            db.execute("UPDATE courses SET text = ?, price = ?, name = ? WHERE id = ?",
                request.form.get("text"),request.form.get("price"), request.form.get("name"), course_id)

            flash("Course Updated")
            return redirect("/admin")

        else:
            return render_template("admin.html", courses = courses, ids = ids)

    # Render Template
    else:
        id = request.form.get("id")
        ids = db.execute("SELECT * FROM courses")
        courses = db.execute("SELECT * FROM courses WHERE id = ?", id)

        return render_template("admin.html", courses = courses, ids = ids)


@app.route("/account")
@login_required
def account():

    users_courses = db.execute("SELECT * FROM users_courses, courses WHERE courses.id = users_courses.course_id AND user_id = ?",
         session["user_id"])

    if len(users_courses) == 0:

        free = db.execute("SELECT * FROM courses ORDER BY id DESC LIMIT 3")

        flash("Look for a course that you may like!")
        return render_template("account.html", frees = free)

    return render_template("account.html", ids = users_courses)


@app.route("/buy", methods=["GET", "POST"])
@login_required
def buy():

    id = request.form.get("id")
    course = db.execute("SELECT * FROM courses WHERE id = ?", id)
    users_courses = db.execute("SELECT * FROM users_courses WHERE course_id = ? AND user_id = ?", id, session["user_id"])
    price = course[0]["price"]


    # Enroll if it's a free course
    if price.casefold() == "free":

        db.execute("INSERT INTO users_courses (user_id, course_id) VALUES (?, ?)",
                    session["user_id"], course[0]["id"])
        
        return redirect("/account")

    # Go to an alreaady owned course
    elif len(users_courses[0]) == 1:

        return render_template("course.html", id = users_courses)

    return render_template("buy.html")


@app.route("/courses")
def courses():

    courses = db.execute("SELECT * FROM courses")
    return render_template("courses.html", ids = courses)


@app.route("/info", methods=["GET", "POST"])
def info():

    if request.method == "POST":

        id = request.form.get("id")
        course = db.execute("SELECT * FROM courses WHERE id = ?", id)

        return render_template("info.html", ids = course)
    
    else:
        return redirect("/info")


@app.route("/login", methods=["GET", "POST"])
def login():

    # Forget any user_id
    session.clear()

    """Login user"""

    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            flash('must provide username')
            return render_template("login.html")

        # Ensure password was submitted
        elif not request.form.get("password"):
            flash("Must provide password")
            return render_template("login.html")

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = ?", request.form.get("username"))

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            flash("Wrong username/password")
            return render_template("login.html")

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        return redirect("/account")

    return render_template("login.html")


@app.route("/logout")
def logout():

    """Logout user"""

    # Forget any user_id
    session.clear()

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
            return render_template("signup.html")

        # Ensure password was submitted
        elif not request.form.get("password"):
            flash("Must provide password")
            return render_template("signup.html")
            
        # Ensure password confirmation was submitted
        elif not request.form.get("confirmation"):
            flash("Must provide password")
            return render_template("signup.html")

        # # Ensure the passwords are the same
        elif password != confirmation:
            flash("Passwords dont match")
            return render_template("signup.html")
            
        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = ?", request.form.get("username"))

        # Check if user is allready taken
        if len(rows) == 1:
            flash("Username allready exists!")
            return render_template("signup.html")

        # Create new row in people table
        db.execute("INSERT INTO users (username, hash) VALUES (?, ?)", username, generate_password_hash(password))

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = ?", request.form.get("username"))

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]
        
        # Redirect user to home page
        return redirect("/courses")

    else:
        return render_template("signup.html")


