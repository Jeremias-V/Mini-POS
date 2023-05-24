"""
This 'unit' tests are not following all the unit test rules.
They depend on each other, so they aren't strictly unit tests.
This was configured like that because of compatibility problems
of mocking data in pytest @ the current versions.
"""
from src.models import Users, Product, Product_Quantity, CurrentInvoice, CurrentInvoice_Product
from os import environ
from dotenv import load_dotenv
import src.utils

load_dotenv()

# TEST CONSTANTS

DEFAULT_USERNAME = "TestUser1"
DEFAULT_PASSWORD = "testpass"


ADMIN_USERNAME = "TestAdmin1"
ADMIN_PASSWORD = "adminpass"
ADMIN_KEY = environ.get('ADMIN_KEY')

DEFAULT_PRODUCT = {"name": "Rice",
                   "price": "21500",
                   "weight": "2.5",
                   "unit": "kg"}

# HELPER FUNCTIONS
def register(client, is_admin=False):

    headers = {"Content-Type": "application/json"}

    if is_admin:
        data = {"username": ADMIN_USERNAME,
                "password": ADMIN_PASSWORD,
                "admin_key": ADMIN_KEY}
    
    else:
        data = {"username": DEFAULT_USERNAME,
                "password": DEFAULT_PASSWORD}

    response = client.post("/register", json=data, headers=headers)

    return response


def login(client, is_admin=False):

    if is_admin:

        user = (ADMIN_USERNAME,
                ADMIN_PASSWORD)
        
    else:

        user = (DEFAULT_USERNAME,
                DEFAULT_PASSWORD)

    response = client.post("/login", auth=user)

    return response


def get_token(client, is_admin=False):

    return login(client, is_admin).json['token']


def create_product(client, token):

    headers = {"Content-Type": "application/json",
               "x-access-tokens": token}
    
    data = DEFAULT_PRODUCT
    
    response = client.post("/product/create", json=data, headers=headers)
    
    return response

def get_products(client, token):

    headers = {"Content-Type": "application/json",
               "x-access-tokens": token}
    
    response = client.get("/products", headers=headers)

    return response


def add_product(client, token):

    headers = {"Content-Type": "application/json",
               "x-access-tokens": token}
    
    data = {"name": DEFAULT_PRODUCT["name"],
            "quantity": "1"}
    
    response = client.post("/product/add", json=data, headers=headers)

    return response


def delete_product(client, token):

    headers = {"Content-Type": "application/json",
               "x-access-tokens": token}
    
    response = client.delete("/products/1", headers=headers)

    return response

def add_to_invoice(client, token):

    headers = {"Content-Type": "application/json",
               "x-access-tokens": token}
    
    response = client.get("/add/1", headers=headers)

    return response

# TESTS

def test_init(client):

    response = client.get("/")
    assert b"Not Found" in response.data


def test_registration(client, app):

    response = register(client)

    assert response.status_code == 200

    with app.app_context():
        assert Users.query.count() == 1
        assert Users.query.first().username == DEFAULT_USERNAME
        assert Users.query.first().admin == 0


def test_registration_admin(client, app):

    response = register(client, is_admin=True)

    assert response.status_code == 200

    with app.app_context():
        assert Users.query.count() == 1
        assert Users.query.first().username == ADMIN_USERNAME
        assert Users.query.first().admin == 1
    

def test_login_user(client):

    register(client)

    user = (DEFAULT_USERNAME,
            DEFAULT_PASSWORD)

    # Perform the login request
    response = login(client)

    assert response.status_code == 200
    assert 'token' in response.json


def test_login_admin(client):

    register(client, is_admin=True)

    user = (DEFAULT_USERNAME,
            DEFAULT_PASSWORD)

    # Perform the login request
    response = login(client, is_admin=True)

    assert response.status_code == 200
    assert 'token' in response.json


def test_util():

    assert src.utils.is_float("0.01") == True
    assert src.utils.is_float("a.01") == False

def test_create_product_not_admin(client, app):
    
    register(client)
    token = get_token(client)

    response = create_product(client, token)

    print(response.json)

    assert response.status_code == 401


def test_create_product_admin(client, app):
    
    register(client, is_admin=True)
    token = get_token(client, is_admin=True)

    response = create_product(client, token)

    print(response.json)

    assert response.status_code == 200

    with app.app_context():
        assert Product.query.count() == 1
        assert Product.query.first().name == DEFAULT_PRODUCT["name"]
        assert Product.query.first().unit == DEFAULT_PRODUCT["unit"]
        assert Product_Quantity.query.first().product_id == Product.query.first().id
        assert Product_Quantity.query.first().quantity == 0

def test_add_product_quantity(client, app):

    register(client, is_admin=True)
    token = get_token(client, is_admin=True)
    create_product(client, token)

    N = 10

    for _ in range(N):
        response = add_product(client, token)
        assert response.status_code == 200


    with app.app_context():
        assert Product_Quantity.query.count() == 1
        assert Product_Quantity.query.first().quantity == N

def test_view_products_and_delete(client, app):

    # Create product to view with admin
    register(client, is_admin=True)
    token_admin = get_token(client, is_admin=True)
    create_product(client, token_admin)
    add_product(client, token_admin)

    # Create non admin user to view products
    register(client)
    token = get_token(client)

    # Get all current products
    response = get_products(client, token)

    assert response.status_code == 200

    data = response.json["list_of_products"][0]

    assert data["id"] == 1
    assert data["name"] == DEFAULT_PRODUCT["name"]
    assert data["quantity"] == 1

    response = delete_product(client, token_admin)

    assert response.status_code == 200

    with app.app_context():
        assert Product.query.count() == 0


def test_add_to_invoice(client, app):

    N = 5
    M = 3

    # Create and add products quantity with admin
    register(client, is_admin=True)
    token_admin = get_token(client, is_admin=True)
    create_product(client, token_admin)

    for _ in range(N):
        add_product(client, token_admin)

    # Create normal user to add to invoices
    register(client)
    token = get_token(client)

    for _ in range(M):
        response = add_to_invoice(client, token)
        assert response.status_code == 200

    with app.app_context():
        assert Product_Quantity.query.first().quantity == (N-M)
        assert CurrentInvoice_Product.query.count() == M
        assert CurrentInvoice.query.count() == 1
