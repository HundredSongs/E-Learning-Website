from crypt import methods
import os

from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from requests import delete, post
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


# Main Page
@app.route("/")
def index():

    courses = db.execute("SELECT * FROM courses ORDER BY id DESC LIMIT 3")
    return render_template("index.html", ids = courses)


# Users Account
@app.route("/account")
@login_required
def account():

    users_courses = db.execute("SELECT * FROM users_courses, courses WHERE courses.id = users_courses.course_id AND user_id = ?",
         session["user_id"])

    # See if user has enroled in any course
    if len(users_courses) == 0:

        free = db.execute("SELECT * FROM courses ORDER BY id DESC LIMIT 3")

        flash("Look for a course that you may like!")
        return render_template("account.html", frees = free)

    return render_template("account.html", ids = users_courses)


# Control panel
@app.route("/backoffice")
@login_required
def backoffice():

    return render_template("backoffice.html")


# Change courses info
@app.route("/backoffice-info", methods=["GET", "POST"])
@login_required
def backoffice_info():

    if request.method == "POST":

        id = request.form.get("id")
        ids = db.execute("SELECT * FROM courses")
        courses = db.execute("SELECT * FROM courses WHERE id = ?", id)

        course_id = courses[0]["id"]

        # Create a new course
        if id == "new":
            db.execute("INSERT INTO courses (price, name) VALUES ('Free', 'Name')")

            flash("New Course Created")
            return redirect("/backoffice")


        # Change course info
        elif request.form.get("name") and course_id != 0 and request.form.get("price"):

            db.execute("UPDATE courses SET price = ?, name = ? WHERE id = ?",
                request.form.get("price"), request.form.get("name"), course_id)

            flash("Course Updated")
            return redirect("/backoffice")

        else:
            return render_template("backoffice-info.html", courses = courses, ids = ids)

    # Render Template
    else:
        id = request.form.get("id")
        ids = db.execute("SELECT * FROM courses")
        courses = db.execute("SELECT * FROM courses WHERE id = ?", id)

        return render_template("backoffice-info.html", courses = courses, ids = ids)


# Change courses pages
@app.route("/backoffice-pages")
@login_required
def backoffice_pages():

    return render_template("backoffice-pages.html")


# Buy Page
@app.route("/buy", methods=["GET", "POST"])
@login_required
def buy():

    id = int(request.form.get("id"))
    course = db.execute("SELECT * FROM courses WHERE id = ?", id)
    users_courses = db.execute("SELECT * FROM users_courses WHERE course_id = ? AND user_id = ?", id, session["user_id"])
    price = course[0]["price"]

    # Enroll if it's a free course
    if price.casefold() == "free" and len(users_courses) == 0:

        db.execute("INSERT INTO users_courses (user_id, course_id) VALUES (?, ?)",
                    session["user_id"], course[0]["id"])
        
        return redirect("/account")

    # Go to an alreaady owned course
    elif len(users_courses) == 1:

        return render_template(f"courses/{id}.html")

    else:
        return render_template("buy.html")


# Individual course
@app.route("/course", methods=["GET", "POST"])
def course():

    id = int(request.form.get("id"))
    course = db.execute("SELECT * FROM courses WHERE id = ?", id)

    if id == None:
        return redirect("/courses")
    else:
        return render_template(f"courses/{id}.html")


# List all Courses
@app.route("/courses")
def courses():

    courses = db.execute("SELECT * FROM courses")
    return render_template("courses.html", ids = courses)


# Courses Info
@app.route("/info", methods=["GET", "POST"])
def info():

    try:
        id = int(request.args.get("id"))
        course = db.execute("SELECT * FROM courses WHERE id = ?", id)
        all_courses = db.execute("SELECT * FROM courses")

        if int(id) < 0 or int(id) > len(all_courses):
            return redirect("/courses")

        return render_template("info.html", ids = course)

    except ValueError:
        return redirect("/courses")


# Login
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


# Logout
@app.route("/logout")
def logout():

    """Logout user"""

    # Forget any user_id
    session.clear()

    return redirect("/")


# Register user
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


# Account Settings
@app.route("/settings", methods=["GET", "POST"])
@login_required
def settings():

    """Change account settings"""

    if request.method == "POST":

        # Ensure password was submitted
        if not request.form.get("password"):
            flash("Must provide password")
            return redirect("/account")


        # Delete account
        elif request.form.get("delete") != None:
            # Query database for username
            # Ensure username exists and password is correct
            rows = db.execute("SELECT * FROM users WHERE id = ?", session["user_id"])

            if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
                flash("Wrong Password!")
                return redirect("/settings")

            # Delete account
            else:

                db.execute("DELETE FROM users WHERE users.id = ?", session["user_id"])
                db.execute("DELETE FROM users_courses WHERE user_id = ?", session["user_id"])
                db.execute("DELETE FROM history WHERE history.person_id = ?", session["user_id"])

                flash("Account deleted")
                return redirect("/login")


        # Check if users wants to change password
        if request.form.get("button_pass") != None:
            # Ensure new password was submitted
            if not request.form.get("password_new"):
                flash("Must provide new password")
                return redirect("/account")

            # Ensure new password confirmation was submitted
            elif not request.form.get("password_confirm"):
                flash("Must confirm new password")
                return redirect("/account")

            # Ensure new password confirmation was submitted
            elif request.form.get("password_new") != request.form.get("password_confirm"):
                flash("New passwords do not match")
                return redirect("/account")

            else:
                # Check if password is acceptable - has digit, letters and no spaces
                password_new = request.form.get("password_new")
                a = b = c = False
                for i in range(len(password_new)):

                    if password_new[i].isspace():
                        a = True
                    elif password_new[i].isalpha():
                        b = True
                    elif password_new[i].isnumeric():
                        c = True

                if a == True:
                    flash("Must contain no spaces")

                elif b == False or c == False:
                    flash("Must have digits and letters!")

                elif a == False and b == True and c == True:
                    # Query database for username
                    # Ensure username exists and password is correct
                    rows = db.execute("SELECT * FROM users WHERE id = ?", session["user_id"])

                    if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
                        flash("Wrong Password!")
                        return redirect("/account")

                    # Insert new password into database
                    db.execute("UPDATE users SET hash = ? WHERE id = ?", generate_password_hash(password_new), session["user_id"])
                    flash("Password changed!")
                    return redirect("/account")


    else:
        return render_template("account_settings.html")