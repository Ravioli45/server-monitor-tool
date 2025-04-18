from app.models import User
from app import db

def test_home(client):
    response = client.get("/")
    assert response.status_code == 200



def test_registration(client, app):
    response = client.post("/", data={"email": "test@test.com", "password": "testpassword"})
    
    with app.app_context():
        user = db.session.get(User, 1)

        assert User.query.count() == 1
        assert User.query.first().email == "viktorjohansen@outlook.com"
