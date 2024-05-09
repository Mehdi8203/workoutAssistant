import os
from cs50 import SQL
import sqlite3
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash
from helpers import apology, login_required, usd

# Configure application
app = Flask(__name__)

# Custom filter
app.jinja_env.filters["usd"] = usd

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

@app.route("/", methods=["GET", "POST"])
@login_required
def homepage():

    return render_template("homepage.html")


@app.route("/signup", methods=["GET", "POST"])
def signup():
    """Log user in"""

    # forget any user_id
    session.clear()

    # User using post method via submitting the form
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 400)

        # ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 400)

        # ensure password confirmation was submitted
        elif not request.form.get("confirmation"):
            return apology("must confirm password", 400)

        # ensure password and confirmation match
        elif request.form.get("password") != request.form.get("confirmation"):
            return apology("password do not match", 400)

        # query db for username
        rows = db.execute("SELECT * FROM users WHERE username = ?;", request.form.get("username"))

        # ensure username doesn't already exist
        if len(rows) != 0:
            return apology("username already exist", 400)

        # insert user into db
        db.execute("INSERT INTO users (username, hash, coach_gymgoer) VALUES(?, ?, ?)",
                    request.form.get("username"), generate_password_hash(request.form.get("password")), request.form.get("coach_gymgoer"))

        # query db for newly inserted user
        rows = db.execute("SELECT * FROM users WHERE username = ?;", request.form.get("username"))

        # remember which user has logged in
        session["user_id"] = rows[0]["id"]


        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username_login"):
            return apology("must provide username", 403)

        # Ensure password was submitted
        elif not request.form.get("password_login"):
            return apology("must provide password", 403)

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = ?", request.form.get("username_login"))

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password_login")):
            return apology("invalid username and/or password", 403)

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")


@app.route("/plan", methods=["GET", "POST"])
@login_required
def plan():

    result = db.execute("SELECT * FROM exercise_list;")
    chest = db.execute("SELECT * FROM exercise_list WHERE id BETWEEN 1 AND 6;")
    bicep = db.execute("SELECT * FROM exercise_list WHERE id BETWEEN 7 AND 15;")
    tricep = db.execute("SELECT * FROM exercise_list WHERE id BETWEEN 16 AND 21;")
    back = db.execute("SELECT * FROM exercise_list WHERE id BETWEEN 22 AND 30;")
    leg = db.execute("SELECT * FROM exercise_list WHERE id BETWEEN 31 AND 39;")
    Abs = db.execute("SELECT * FROM exercise_list WHERE id BETWEEN 40 AND 48;")
    session['result'] = result
    session['chest'] = chest
    session['bicep'] = bicep
    session['tricep'] = tricep
    session['back'] = back
    session['leg'] = leg
    session['Abs'] = Abs
    if request.method == "POST":
        selected_options = []
        for i in range(1, 49):
            ename = request.form.get(str(i))
            if ename:
                selected_options.append(ename)
        session['selected_options'] = selected_options
        counter = len(selected_options)
        session['counter'] = counter

        weekdays = request.form.get('days')
        session['weekdays'] = weekdays

        ename_dict = {"Monday": [], "Tuesday": [], "Wednesday": [], "Thursday": [], "Friday": [], "Saturday": [], "Sunday": []}
        if weekdays == "Monday":
            ename_dict["Monday"] = selected_options
        elif weekdays == "Tuesday":
            ename_dict["Tuesday"] = selected_options
        elif weekdays == "Wednesday":
            ename_dict["Wednesday"] = selected_options
        elif weekdays == "Thursday":
            ename_dict["Thursday"] = selected_options
        elif weekdays == "Friday":
            ename_dict["Friday"] = selected_options
        elif weekdays == "Saturday":
            ename_dict["Saturday"] = selected_options
        elif weekdays == "Sunday":
            ename_dict["Sunday"] = selected_options
        elif not weekdays:
            return apology("must select a day", 403)
        session['ename_dict'] = ename_dict
        return redirect("/planresult")
    else:
        return render_template("plan.html", result=result, chest=chest, bicep=bicep, tricep=tricep, back=back, leg=leg, Abs=Abs)


@app.route("/addplan", methods=["GET", "POST"])
@login_required
def addplan():
    
    result = session.get('result', None)
    chest = session.get('chest', None)
    bicep = session.get('bicep', None)
    tricep = session.get('tricep', None)
    back = session.get('back', None)
    leg = session.get('leg', None)
    Abs = session.get('Abs', None)
    weekday = session.get('weekdays', None)
    ename_dict = session.get('ename_dict', None)

    if request.method == "POST":
        new_selected_options = []
        for i in range(1, 49):
            ename = request.form.get(str(i))
            if ename:
                new_selected_options.append(ename)
        session['new_selected_options'] = new_selected_options

        new_weekdays = request.form.get('days')
        session['new_weekdays'] = new_weekdays

        if new_weekdays == "Monday" and not weekday == "Monday":
            ename_dict["Monday"] = new_selected_options
        elif new_weekdays == "Tuesday" and not weekday == "Tuesday":
            ename_dict["Tuesday"] = new_selected_options
        elif new_weekdays == "Wednesday" and not weekday == "Wednesday":
            ename_dict["Wednesday"] = new_selected_options
        elif new_weekdays == "Thursday" and not weekday == "Thursday":
            ename_dict["Thursday"] = new_selected_options
        elif new_weekdays == "Friday" and not weekday == "Friday":
            ename_dict["Friday"] = new_selected_options
        elif new_weekdays == "Saturday" and not weekday == "Saturday":
            ename_dict["Saturday"] = new_selected_options
        elif new_weekdays == "Sunday" and not weekday == "Sunday":
            ename_dict["Sunday"] = new_selected_options
        elif not new_weekdays:
            return apology("must select a day", 403)

        return redirect("/planresult")
    else:
        return render_template("addplan.html", result=result, chest=chest, bicep=bicep, tricep=tricep, back=back, leg=leg, Abs=Abs)


@app.route("/planresult")
@login_required
def planresult():

    #getting selected enames and seletced days from session
    selected_options = session.get('selected_options', None)
    weekday = session.get('weekdays', None)
    new_weekday = session.get('new_weekdays', None)
    counter = session.get('counter', None)
    ename_dict = session.get('ename_dict', None)

    return render_template("planresult.html", selected_options=selected_options, weekday=weekday, ename_dict=ename_dict, new_weekday=new_weekday)

@app.route("/change_password", methods=["GET", "POST"])
@login_required
def change_password():

    # If user reached via post
    if request.method == "POST":
        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 403)

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = ?", request.form.get("username"))

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            return apology("invalid username and/or password", 403)

        #ensure new password was submitted
        elif not request.form.get("new_password"):
            return apology("must provide your new password", 400)

        #ensure password confirmation was submitted
        elif not request.form.get("confirmation"):
            return apology("must confirm new password", 400)

        # ensure password and confirmation match
        elif request.form.get("new_password") != request.form.get("confirmation"):
            return apology("passwords do not match", 400)

        # query db for username
        rows = db.execute("SELECT * FROM users WHERE username = ?", request.form.get("username"))

        # update password
        db.execute("UPDATE users SET hash = :new_password WHERE username = :username",
                    username=request.form.get("username"), new_password=generate_password_hash(request.form.get("new_password")))

        # query db
        show_new_password = db.execute("SELECT hash FROM users WHERE username = ?", request.form.get("username"))

        # redirect user to homepage
        return redirect("/")

    # user reached route via get
    else:
        return render_template("change_password.html")


@app.route("/chest")
@login_required
def chest():
    return render_template("chest.html")

@app.route("/bicep")
@login_required
def bicep():
    return render_template("bicep.html")

@app.route("/tricep")
@login_required
def tricep():
    return render_template("tricep.html")

@app.route("/back")
@login_required
def back():
    return render_template("back.html")

@app.route("/leg")
@login_required
def leg():
    return render_template("leg.html")

@app.route("/abs")
@login_required
def abs():
    return render_template("abs.html")
