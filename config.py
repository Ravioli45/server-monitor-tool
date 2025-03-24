import os
from datetime import timedelta

class Config:
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Strict'
    SECRET_KEY = os.environ.get("APPSETTING_FLASK_SECRET_KEY") or "test"
    PERMANENT_SESSION_LIFETIME = timedelta(hours=1)

