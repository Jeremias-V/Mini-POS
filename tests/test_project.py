from src.models import Users
from os import environ
from dotenv import load_dotenv
from werkzeug.security import generate_password_hash

load_dotenv()

# TEST CONSTANTS

DEFAULT_USERNAME = "TestUser1"
DEFAULT_PASSWORD = "testpass"


ADMIN_USERNAME = "TestAdmin1"
ADMIN_PASSWORD = "adminpass"
ADMIN_KEY = environ.get('ADMIN_KEY')

# TESTS

def test_init(client):

    response = client.get("/")
    assert b"Not Found" in response.data

def test_registration(client, app):

    username = "TestUser1"
    password = "testpass"

    data = {"username": username, "password": password}
    headers = {"Content-Type": "application/json"}

    response = client.post("/register", json=data, headers=headers)

    assert response.status_code == 200

    with app.app_context():
        assert Users.query.count() == 1
        assert Users.query.first().username == "TestUser1"
    
def test_login_with_mock_data(client, app, mocker):
    with app.test_request_context():
        username = "TestUser1"
        password = "testpass"
        auth = (username, password)

        # Mock the Users.query.filter_by().first() method
        mocked_user = mocker.Mock()
        mocked_user.username = username
        mocked_user.password = generate_password_hash(password, method='sha256')

        # Patch the Users.query.filter_by method
        mock_filter_by = mocker.patch('src.models.Users.query.filter_by')

        # Patch the return value of Users.query.filter_by().first() to return the mocked user
        mock_filter_by.return_value.first.return_value = mocked_user

        # Perform the login request
        response = client.post("/login", auth=auth)

        assert response.status_code == 200
        assert 'token' in response.json

        token = response.json['token']
        print(token)

