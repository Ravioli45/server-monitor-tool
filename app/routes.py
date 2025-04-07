from flask import Flask, request, session, render_template, redirect, url_for, flash
from flask_login import current_user, logout_user, login_required, login_user
from app import app, db
from app.models import *
from app.forms import LoginForm, RegistrationForm

@app.route("/")
def index():
    #session.permanent = True
    #session['test'] = 52

    return render_template("index.html")

@app.route("/login", methods=['GET', 'POST'])
def login():
    session.permanent = True

    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))

    form = LoginForm()
    if form.validate_on_submit():

        user = db.session.scalar(sa.select(User).where(User.username == form.username.data))
        if user is None or not user.check_password(form.password.data):
            flash("Invalid username or password")
            return redirect(url_for("login"))
        
        login_user(user)
    
        return redirect(url_for("dashboard"))
    

    return render_template("login.html", form=form)

@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for("index"))

@app.route("/register", methods=["GET", "POST"])
def register():

    if current_user.is_authenticated:
        return redirect(url_for("dashboard"))
    
    form = RegistrationForm()

    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)

        db.session.add(user)
        db.session.commit()

        flash("You can now log in")

        return redirect(url_for("login"))

    return render_template("register.html", form=form)

@app.route("/dashboard")
@login_required
def dashboard():
    
    return render_template("dashboard.html")
