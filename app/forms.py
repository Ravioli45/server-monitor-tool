from urllib.parse import urlparse

from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, IntegerField
from wtforms.validators import ValidationError, EqualTo, Email, \
    Length, InputRequired, URL, NumberRange, DataRequired

from app import db
import sqlalchemy as sa
from app.models import User

class LoginForm(FlaskForm):

    username = StringField("Username", validators=[InputRequired()])
    password = PasswordField("Password", validators=[InputRequired()])

    submit = SubmitField("Sign In")


class RegistrationForm(FlaskForm):
    username = StringField("Username", validators=[InputRequired()])
    email = StringField("Email", validators=[InputRequired(), Email()])

    password = PasswordField("Password", validators=[InputRequired(), Length(8)])
    password2 = PasswordField("Repeat Password", validators=[EqualTo("password"), InputRequired(), Length(8)])

    submit = SubmitField("Register")

    # validate_<field_name> is automatically called by wtforms
    def validate_username(self, username):
        user = db.session.scalar(sa.select(User).where(User.username == username.data))
        if user is not None:
            raise ValidationError("Please use a different username.")
        
    def validate_email(self, email):
        user = db.session.scalar(sa.select(User).where(User.email == email.data))
        if user is not None:
            raise ValidationError("Please use a different email.")
        
class AddMonitorForm(FlaskForm):
    url = StringField("Website URL", validators=[InputRequired(), URL("Message")])
    minutes_between_pings = IntegerField("Minutes between pings", validators=[InputRequired(), NumberRange(30, 300)])

    submit = SubmitField("Start Monitoring")

    def validate_url(self, url):
        parsed = urlparse(url.data)
        if parsed.scheme != "https":
            raise ValidationError("Make sure to include HTTPS at beginning of url.")

class ZipKeyForm(FlaskForm):
    zip_key = StringField("Zip Key", validators=[DataRequired()])

    submit_key = SubmitField("Set Zip Key")
    reset_key = SubmitField("Reset Zip Key")
