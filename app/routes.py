from flask import Flask, request, session, render_template, redirect, url_for, flash, Blueprint
from flask_login import current_user, logout_user, login_required, login_user
from app import db
from app.models import *
from app.forms import LoginForm, RegistrationForm

bp = Blueprint("main", __name__)

@bp.route("/")
def index():
    #session.permanent = True
    #session['test'] = 52

    return render_template("index.html")

@bp.route("/login", methods=['GET', 'POST'])
def login():
    session.permanent = True

    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))

    form = LoginForm()
    if form.validate_on_submit():

        user = db.session.scalar(sa.select(User).where(User.username == form.username.data))
        if user is None or not user.check_password(form.password.data):
            flash("Invalid username or password")
            return redirect(url_for("main.login"))
        
        login_user(user)
    
        return redirect(url_for("main.dashboard"))
    

    return render_template("login.html", form=form)

@bp.route("/logout")
def logout():
    logout_user()
    return redirect(url_for("main.index"))

@bp.route("/register", methods=["GET", "POST"])
def register():

    if current_user.is_authenticated:
        return redirect(url_for("main.dashboard"))
    
    form = RegistrationForm()

    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)

        db.session.add(user)
        db.session.commit()

        flash("You can now log in")

        return redirect(url_for("main.login"))

    return render_template("register.html", form=form)

@bp.route("/dashboard")
@login_required
def dashboard():
    
    return render_template("dashboard.html")
