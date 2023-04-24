from flask import Blueprint, render_template, session
from flask_login import login_required

from sqlalchemy.exc import OperationalError
from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import login_required, login_user, logout_user, current_user
from app import bcrypt, db
from app.auth.forms import LoginForm, RegisterForm
from app.auth.models import User
from app import login_manager  # the variable from Flask-login

auth_bp = Blueprint("authentication", __name__)


## fixing issue with key -- userid instead of id
@login_manager.user_loader
def load_user(userid):
    return User.query.get(int(userid))


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        flash("You are already logged in.", "info")
        return redirect(url_for("homepage.index"))
    form = LoginForm(request.form)
    if form.validate_on_submit():
        print("validating form")
        user = User.query.filter_by(userid=form.userid.data).first()
        print('user')
        if user and bcrypt.check_password_hash(user.password, request.form["password"]):
            login_user(user)

            ## check user role,
            ## if its admin user show role selection screen or take to  admin view
            ## admin view can only be accessed by admin users
            return redirect(url_for("homepage.index"))
        else:
            flash("Invalid email and/or password.", "danger")
            return render_template("authentication/login.html", form=form)
    return render_template("authentication/login.html", form=form)


@auth_bp.route("/logout")
@login_required
def logout():
    logout_user()
    flash("You were logged out.", "success")
    return redirect(url_for("authentication.login"))


@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        flash("You are already registered.", "info")
        print("current user authenticate")
        return redirect(url_for("homepage.index"))
    form = RegisterForm(request.form)
    if form.validate_on_submit():
        user = User(password=form.password.data, username=form.username.data,
                    mobile=form.mobile.data,
                    email=form.email.data, is_admin=form.is_admin.data, is_active=form.is_active.data)

        try:
            db.session.add(user)
            db.session.commit()
        except:
            flash("Unable to commit", "success")

        # https://devpress.csdn.net/python/63044f1f7e6682346619974b.html
        print("u r registered")

        login_user(user)
        flash("You registered and are now logged in. Welcome!", "success")

        return redirect(url_for("homepage.index"))
    print("not validated")
    print(form.errors)
    print(form)

    return render_template("authentication/register.html", form=form)
