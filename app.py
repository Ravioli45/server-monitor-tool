import os
from datetime import timedelta
from flask import Flask, request, session, render_template

from config import Config
from forms import LoginForm

app = Flask(__name__)

app.config.from_object(Config)
#app.config['WTF_CSRF_TIME_LIMIT'] = 30
#app.permanent_session_lifetime = timedelta(minutes=1)

#print(app.config['WTF_CSRF_TIME_LIMIT'])

@app.route("/")
def home_get():
    #session.permanent = True
    #session['test'] = 52
    header_dict = dict(request.headers)
    return header_dict
    #return "<p>Hello world!</p>"

@app.route("/login", methods=['GET', 'POST'])
def login():
    session.permanent = True

    form = LoginForm()
    if form.validate_on_submit():
        return {form.email.label.text: form.email.data, form.password.label.text: form.password.data}

    return render_template("login.html", form=form)
