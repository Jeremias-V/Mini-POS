from src.models import Users

def test_init(client):
    response = client.get("/")
    assert b"Not Found" in response.data

def test_registration(client, app):

    data = {"username": "TestUser1", "password": "testpass"}
    headers = {"Content-Type": "application/json"}

    response = client.post("/register", data=data, headers=headers)

    print(response.text)

    with app.app_context():
        assert Users.query.count() == 1
        assert Users.query.first().username == "TestUser1"
    