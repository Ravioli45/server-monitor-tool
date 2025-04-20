from app.models import User, Monitor
from app import db
import sqlalchemy as sa
from flask import Flask, request, render_template
from bs4 import BeautifulSoup

def test_home(client):
    response = client.get("/")
    assert response.status_code == 200

def test_registration(client, app):
    app.config['WTF_CSRF_ENABLED'] = False 

    # response = client.get('/register')
    # soup = BeautifulSoup(response.data, 'html.parser')
    # csrf_token = soup.find('input', {'name': csrf_token})['value']
    data = {
    #   "csrf_token": csrf_token,
        "username": "test",
        "email": "test@test.com",
        "password": "testpassword",
        "password2":"testpassword"
    }
    response = client.post("/register", data=data)
    print(response)

    with app.app_context():
        print(db.session.scalars(sa.select(User)).all())

        u = db.session.scalar(sa.select(User).where(User.username == "test"))
        print(u)
        
        assert u.email == "test@test.com"
        db.session.delete(u)
        db.session.commit()

    app.config['WTF_CSRF_ENABLED'] = True 

def test_invalid_login(client, app):
    app.config['WTF_CSRF_ENABLED'] = False 

    data = {
        "username": "test",
        "email": "test@test.com",
        "password": "testpassword",
        "password2":"testpassword"
    }

    response = client.post("/login", data=data)

    assert response.status_code == 302
    app.config['WTF_CSRF_ENABLED'] = True 


def test_no_login(client, app):
    response = client.get("/dashboard/add_monitor")

    assert response.status_code == 302

def test_log_out(client, app):
    app.config['WTF_CSRF_ENABLED'] = False 

    data = {
        "username": "test",
        "email": "test@test.com",
        "password": "testpassword",
        "password2":"testpassword"
    }

    client.post("/register", data=data)
    client.post("/login", data=data)
    
    response = client.get("/logout")

    with app.app_context():
        assert response.status_code == 302

        u = db.session.scalar(sa.select(User).where(User.username == "test"))
        db.session.delete(u)
        db.session.commit()

    app.config['WTF_CSRF_ENABLED'] = True 



def test_setzipkey(client, app):
    app.config['WTF_CSRF_ENABLED'] = False 

    data = {
        "username": "test",
        "email": "test@test.com",
        "password": "testpassword",
        "password2":"testpassword"
    }

    client.post("/register", data=data)
    client.post("/login", data=data)

    response = client.post("/account_settings/set_zip_key", data = {"zip_key": "123456"})

    assert response.status_code == 302

    with app.app_context():
        u = db.session.scalar(sa.select(User).where(User.username == "test"))
        db.session.delete(u)
        db.session.commit()

    app.config['WTF_CSRF_ENABLED'] = True 

def test_monitor_add(client, app):
    app.config['WTF_CSRF_ENABLED'] = False 

    data = {
        "username": "test",
        "email": "test@test.com",
        "password": "testpassword",
        "password2":"testpassword"
    }

    client.post("/register", data=data)
    client.post("/login", data=data)

    with app.app_context():
        monitor_data = {
        "url": "https://www.youtube.com",
        "minutes_between_pings": "30",
        }
        response = client.post("/dashboard/add_monitor", data=monitor_data)

        assert response.status_code == 302

        u = db.session.scalar(sa.select(User).where(User.username == "test"))
        db.session.delete(u)
        db.session.commit()

    app.config['WTF_CSRF_ENABLED'] = True 

def test_monitor_remove(client, app):
    app.config['WTF_CSRF_ENABLED'] = False 

    data = {
        "username": "test",
        "email": "test@test.com",
        "password": "testpassword",
        "password2":"testpassword"
    }

    client.post("/register", data=data)
    client.post("/login", data=data)

    with app.app_context():
        monitor_data = {
            "url": "https://www.youtube.com",
            "minutes_between_pings": "30",
        }
        response1 = client.post("/dashboard/add_monitor", data=monitor_data)
        assert response1.status_code == 302

        l = db.session.scalar(sa.select(Monitor).where(Monitor.url == "https://www.youtube.com"))
        m = l.id
        n = str(m)
        print (n)
        response = client.get("/dashboard/remove_monitor/" + n)
        assert response.status_code == 302

        u = db.session.scalar(sa.select(User).where(User.username == "test"))

        db.session.delete(u)
        db.session.commit()

    app.config['WTF_CSRF_ENABLED'] = True 