from datetime import datetime, timedelta, timezone

from flask import Flask, request, session, render_template, redirect, url_for, flash, Blueprint
from flask_login import current_user, logout_user, login_required, login_user
from app import db
from app.models import *
from app.forms import LoginForm, RegistrationForm, AddMonitorForm, ZipKeyForm

bp = Blueprint("main", __name__)

@bp.after_request
def after_request(response):
    
    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, post-check=0, pre-check=0, max-age=0'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '-1'

    return response

@bp.route("/")
def index():
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
    session.clear()
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

    monitors: list[Monitor] = db.session.scalars(
        current_user.monitors.select()
    ).all()

    most_recent_statuses: list[Status] = []
    for m in monitors:
        most_recent = db.session.scalars(
            m.status_checks.select().order_by(sa.desc(Status.timestamp))
        ).first()
        most_recent_statuses.append(most_recent)

    monitor_and_status = list(zip(monitors, most_recent_statuses))
    return render_template("dashboard.html", monitor_and_status=monitor_and_status)

@bp.route("/dashboard/add_monitor", methods=["GET", "POST"])
@login_required
def add_monitor():

    form = AddMonitorForm()

    if form.validate_on_submit():

        existing_monitor = db.session.scalar(
            sa.select(Monitor).where(sa.and_(Monitor.user_id == current_user.id, Monitor.url == form.url.data))
        )

        if existing_monitor is not None:
            flash("Monitor already exists")
            return redirect(url_for("main.add_monitor"))

        seconds_to_next_ping = 60*form.minutes_between_pings.data
        time_next_ping = datetime.now(timezone.utc) + timedelta(seconds=seconds_to_next_ping)

        monitor = Monitor(url=form.url.data, time_next_ping=time_next_ping, seconds_to_next_ping=seconds_to_next_ping, user=current_user)

        db.session.add(monitor)
        db.session.commit()

        return redirect(url_for("main.dashboard"))

    return render_template("add_monitor.html", form=form)

@bp.route("/dashboard/remove_monitor/<monitor_id>")
@login_required
def remove_monitor(monitor_id):

    to_delete = db.session.get(Monitor, monitor_id)

    # if monitor belongs to user
    if (to_delete is not None) and to_delete.user_id == current_user.id:
        db.session.delete(to_delete)
        db.session.commit()

    return redirect(url_for("main.dashboard"))

@bp.route("/account_settings")
@login_required
def account_settings():

    form = ZipKeyForm()

    return render_template("settings.html", form=form)

@bp.route("/account_settings/set_zip_key", methods=["POST"])
@login_required
def set_zip_key():
    
    zip_key = request.form.get("zip_key")

    if zip_key is None:
        current_user.zip_key = None
    else:
        if not zip_key.isspace():
            current_user.zip_key = zip_key

    db.session.commit()
    
    return redirect(url_for("main.account_settings"))