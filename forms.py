from flask_wtf import FlaskForm
from wtforms import EmailField, PasswordField, SubmitField
from wtforms.validators import DataRequired

class LoginForm(FlaskForm):

    email = EmailField("E-Mail", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])


