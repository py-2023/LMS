from flask import Blueprint, render_template, session
from flask_login import login_required
from sqlalchemy import or_

from sqlalchemy.exc import OperationalError
from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import login_required, login_user, logout_user, current_user
from app import bcrypt, db
from app.auth.forms import LoginForm, RegisterForm, UpdateForm

from app.auth.models import User
from app import login_manager  # the variable from Flask-login

auth_bp = Blueprint("authentication", __name__)


## fixing issue with key -- userid instead of id
@login_manager.user_loader
def load_user(userid):
    return User.query.get(int(userid))


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm(request.form)
    users = User.query.filter( User.is_active == True).all()
    if form.validate_on_submit():
        print("validating form")
        user = User.query.filter(or_(User.username == form.userid.data, User.userid == form.userid.data, User.email == form.userid.data)).first()

        print('user')
        if user and bcrypt.check_password_hash(user.password, request.form["password"]):
            login_user(user)
            is_admin = user.is_admin
            return redirect(url_for("homepage.index"))
        else:
            flash("Invalid email and/or password.", "danger")
            return render_template("authentication/login.html", form=form,users=users)
    return render_template("authentication/login.html", form=form,users=users)


@auth_bp.route("/logout")
@login_required
def logout():
    logout_user()
    flash("You were logged out.", "success")
    return redirect(url_for("authentication.login"))


@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    # if current_user.is_authenticated:
    #    flash("You are already registered.", "info")
    #    print("current user authenticate")
    #    return redirect(url_for("homepage.index"))

    if request.method == 'GET':
        form = RegisterForm(request.form)
        # flash("Add User", "success")
        return render_template("authentication/register.html", form=form)

    if request.method == 'POST':
        form = RegisterForm(request.form)

        if form.validate():
            users = User.query.filter().all()
            if users:

                user = User(password=form.password.data, username=form.username.data,
                            mobile=form.mobile.data,
                            email=form.email.data, is_active=True, is_admin=False)
            else:
                # if no users, attach admin rights to first user created in the system
                # is Admin column in db is set to 1
                user = User(password=form.password.data, username=form.username.data,
                            mobile=form.mobile.data,
                            email=form.email.data, is_active=True, is_admin=True)

            try:
                db.session.add(user)
                db.session.commit()
                # login_user(user)
                flash("The user registration is complete with member id  :  " + str(user.userid) + "    ", "success")
            except:
                flash("Unable to save", "success")

            return redirect(url_for("authentication.register"))
        print(" validation failed")
        print(form.errors)
        print(form)

        return render_template("authentication/register.html", form=form)


@auth_bp.route("/updateuser", methods=["GET", "POST"])
def updateuser():

    if request.method == 'POST':
        form = UpdateForm(request.form)

        if form.validate():
            user = User.query.filter_by(userid=form.userid.data).first()
            user.email = form.email.data
            user.username = form.username.data
            user.mobile = form.mobile.data
            user.password = bcrypt.generate_password_hash(form.password.data )

            try:
                db.session.add(user)
                db.session.commit()
                # login_user(user)
                flash("The user updation is complete for member id  :  " + str(user.userid) + "    ", "success")
            except:
                flash("Unable to update", "success")

            return redirect(url_for("lms.listmembers"))
        print(" validation failed")
        print(form.errors)
        print(form)

        return render_template("authentication/updateuser.html", form=form)








