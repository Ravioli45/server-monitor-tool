from flask import Flask
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from argon2 import PasswordHasher
from sqlalchemy import event

#app = Flask(__name__)
#app.config.from_object(Config)

#login = LoginManager(app)
login = LoginManager()
login.login_view = "login"
ph = PasswordHasher()
#db = SQLAlchemy(app)
db = SQLAlchemy()
#migrate = Migrate(app, db)
migrate = Migrate()

def create_app(config=Config):
    app = Flask(__name__)
    app.config.from_object(config)

    login.init_app(app)
    db.init_app(app)
    migrate.init_app(app, db)

    from app.routes import bp as main_bp
    app.register_blueprint(main_bp)

    # sqlite is used when testing the app locally
    # 
    # sqlite does not enforce foreign keys by default, so it
    # has to be enabled
    with app.app_context():
        #print("h")
        if db.engine.url.drivername == "sqlite":
            @event.listens_for(db.engine, "connect")
            def set_sqlite_pragma(dbapi_connection, connection_record):
                #print("g")
                cursor = dbapi_connection.cursor()
                cursor.execute("PRAGMA foreign_keys=ON")
                cursor.close()

    return app

from app import routes, models
