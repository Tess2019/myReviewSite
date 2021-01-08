import os
from flask import(
    Flask, flash, render_template,
    redirect, request, session, url_for)
from flask_pymongo import PyMongo
from werkzeug.security import generate_password_hash, check_password_hash
from bson.objectid import ObjectId
if os.path.exists("env.py"):
    import  env 


app = Flask(__name__)

app.config["MONGO_DBNAME"] = os.environ.get("MONGO_DBNAME")
app.config["MONGO_URI"] = os.environ.get("MONGO_URI")
app.secret_key = os.environ.get("SECRET_KEY")

mongo = PyMongo(app)


# check if it works
@app.route("/")
@app.route("/get_boardgames")
def get_boardgames():
    boardgames = mongo.db.boardgames.find()
    return render_template("boardgames.html", boardgames=boardgames)


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        # check if username alredy exists in db
        existing_user = mongo.db.user.find_one(
            {"username": request.form.get("username").lower()})

        # message for user and security hash
        if existing_user:
            flash("Username already exists")
            return redirect(url_for("register"))

        register = {
            "username": request.form.get("username").lower(),
            "password": generate_password_hash(request.form.get("password"))
             # if wanted dubblecheck password put it here, check werkzeug for more info
        }
        mongo.db.users.insert_one(register)

        # put the new user into 'session' cookie
        session["user"] = request.form.get("username").lower()
        flash("Register successful!")
        return redirect(url_for("profile", username=session["user"]))
    return render_template("register.html")
        # after clicked on button the page reload and the new user register in mongodb

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        # check if username exists in db.
        # the username input in lowercase method
        existing_user = mongo.db.users.find_one(
            {"username": request.form.get("username").lower()})

        if existing_user:
            # find a match password of user input in db, werkzeug hash
            if check_password_hash(
                existing_user["password"], request.form.get("password")):
                    # use cookies, session varible
                    session["user"] = request.form.get("username").lower()
                    # make user a validation of succsessful login
                    flash("Welcome, {}".format(request.form.get("username")))
                    return redirect(url_for(
                        "profile", username=session["user"]))
            else:
                # invalid password match
                flash("Incorrect Username and/or Password")
                return redirect(url_for("login"))

        else:
             # username do not exist redirect to login
            flash("Incorrect Username and/or Password")
            return redirect(url_for("login"))

    return render_template("login.html")


@app.route("/profile/<username>", methods=["GET", "POST"])
def profile(username):
    # find the users's username in db with session
    username = mongo.db.users.find_one(
        {"username": session["user"]})["username"]
        # no not need all info like password, definie username in brackets 
    return render_template("profile.html", username=username)

if __name__ == "__main__":
    app.run(host=os.environ.get("IP"),
            port=int(os.environ.get("PORT")),
            debug=True)
