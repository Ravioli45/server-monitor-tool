from flask import Flask
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from argon2 import PasswordHasher

app = Flask(__name__)
app.config.from_object(Config)

login = LoginManager(app)
login.login_view = "login"
ph = PasswordHasher()
db = SQLAlchemy(app)
migrate = Migrate(app, db)

from app import routes, models
