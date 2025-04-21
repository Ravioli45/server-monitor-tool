from flask import Flask
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from argon2 import PasswordHasher
from sqlalchemy import event

login = LoginManager()
login.login_view = "main.login"
ph = PasswordHasher()
db = SQLAlchemy()
migrate = Migrate()

def create_app(config=Config):
    app = Flask(__name__)
    app.config.from_object(config)

    # initialize all extensions with flask app
    login.init_app(app)
    db.init_app(app)
    migrate.init_app(app, db)

    # add blueprint to app
    from app.routes import bp as main_bp
    app.register_blueprint(main_bp)

    # sqlite is used when testing the app locally
    # 
    # sqlite does not enforce foreign keys by default, so it
    # has to be enabled
    with app.app_context():
        if db.engine.url.drivername == "sqlite":
            @event.listens_for(db.engine, "connect")
            def set_sqlite_pragma(dbapi_connection, connection_record):
                cursor = dbapi_connection.cursor()
                cursor.execute("PRAGMA foreign_keys=ON")
                cursor.close()

    return app

from app import routes, models
