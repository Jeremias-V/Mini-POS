from queue import Empty
from flask import Flask, request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from dotenv import load_dotenv
from functools import wraps
from os import environ
from models import *
import uuid
import jwt
import datetime
import http_status
import utils

load_dotenv()

app = Flask(__name__)

app.config["SECRET_KEY"] = environ.get("SECRET_KEY")
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:////" + environ.get("DB_PATH")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = True

ADMIN_KEY = environ.get("ADMIN_KEY")

db.init_app(app)

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):

        token = None

        if 'x-access-tokens' in request.headers:
            token = request.headers['x-access-tokens']

        if not token:
            return jsonify({'message': 'a valid token is missing'}), http_status.UNAUTHORIZED

        try:
            data = jwt.decode(token, app.config['SECRET_KEY'], algorithms="HS256")
            current_user = Users.query.filter_by(public_id=data['public_id']).first()
        except Exception as e:
            print("Exception: ", e)
            return jsonify({'message': 'token is invalid'}), http_status.UNAUTHORIZED

        return f(current_user, *args, **kwargs)
        
    return decorated


@app.route('/register', methods=['GET', 'POST'])
def signup_user():
    """
    Register a new user, if the username already existis in DB it fails,
    if not it creates the new user and stores its password hashed with
    sha256.

    Also, if admin key is given, and it is correct, creates an admin user.
    """

    data = request.get_json()

    user = Users.query.filter_by(username=data['username']).first()

    if user is not None:
        return jsonify({'message': 'user already exists'}), http_status.CONFLICT

    hashed_password = generate_password_hash(data['password'], method='sha256')

    is_admin = False
    if 'admin_key' in data and data['admin_key'] == ADMIN_KEY:
        is_admin = True
    elif 'admin_key' in data:
        return jsonify({'message': 'Invalid key, user not created'}), http_status.FORBIDDEN

    new_user = Users(public_id=str(uuid.uuid4()),
                     username=data['username'],
                     password=hashed_password,
                     admin=is_admin)
    
    db.session.add(new_user)
    db.session.commit()

    return jsonify({'message': 'registered successfully'})
    

@app.route('/login', methods=['GET', 'POST'])
def login_user():
    """
    Sign in as a registered user, if the user doesn't exists or the
    password doesn't match, fail, else create a JWT and return the token
    to be used by other methods.
    """
 
    auth = request.authorization

    if not auth or not auth.username or not auth.password:
        return jsonify({'message': 'authorization resquest data not found'}), http_status.FORBIDDEN

    user = Users.query.filter_by(username=auth.username).first()
        
    if user is not None and check_password_hash(user.password, auth.password):
        token = jwt.encode({'public_id': user.public_id, 'exp' :\
                datetime.datetime.utcnow() + datetime.timedelta(minutes=15)}, app.config['SECRET_KEY'])

        return jsonify({'token' : token})

    return jsonify({'message': 'invalid username or password'}), http_status.UNAUTHORIZED


@app.route('/product/create', methods=['POST', 'GET'])
@token_required
def create_product(current_user):
    """
    Create a new product if the product name is not already in
    DB, also check if the user trying to create the product is
    an admin, else fail.
    """
    
    if not current_user.admin:
        return jsonify({'message': 'admin required for this action'}), http_status.UNAUTHORIZED
    
    data = request.get_json()
    product = Product.query.filter_by(name=data['name']).first()

    if product is not None:
        return jsonify({'message': 'product already exists'}), http_status.CONFLICT
    
    _name = data['name']
    if len(_name) < 3 or len(_name) > 100 or len(_name) == 0 or not _name.replace(' ', '').isalpha():
        return jsonify({'message': 'invalid name for product'}), http_status.FORBIDDEN
    
    if not data['price'].isnumeric():
        return jsonify({'message': 'invalid value for price, must be an integer'}), http_status.FORBIDDEN
    
    _price = int(data['price'])

    if _price <= 0 or _price > 10**6:
        return jsonify({'message': 'invalid value for price, 0 < price <= 1000000'}), http_status.FORBIDDEN
    
    if not utils.is_float(data['weight']):
        return jsonify({'message': 'invalid value for weight, must be a float'}), http_status.FORBIDDEN

    _weight = float(data['weight'])

    if _weight <= 0 or _weight >= 1000:
        return jsonify({'message': 'invalid value for weight, 0 < weight < 1000'}), http_status.FORBIDDEN

    _unit = data['unit']

    if not _unit.isalpha() or _unit not in ['mg', 'g', 'kg']:
        return jsonify({'message': 'invalid value for unit, must be mg, g or kg'}), http_status.FORBIDDEN

    new_product = Product(name=_name,
                          price=_price,
                          weight=_weight,
                          unit=_unit)
    
    db.session.add(new_product)

    db.session.flush()

    new_product_quantity = Product_Quantity(product_id=new_product.id)

    db.session.add(new_product_quantity)
    
    db.session.commit()

    return jsonify({'message' : 'new product created'})

@app.route('/product/add', methods=['POST', 'GET'])
@token_required
def add_product(current_user):
    """
    Sum the available quantity to an existing product.
    Must be an admin.
    """
    
    if not current_user.admin:
        return jsonify({'message': 'admin required for this action'}), http_status.UNAUTHORIZED
    
    data = request.get_json()
    product = Product.query.filter_by(name=data['name']).first()

    if product is None:
        return jsonify({'message': 'product does not exist'}), http_status.NOTFOUND
    
    if not data['quantity'].isnumeric():
        return jsonify({'message': 'invalid value for quantity'}), http_status.FORBIDDEN

    product_quantity = Product_Quantity.query.filter_by(product_id=product.id).first()

    product_quantity.quantity += int(data['quantity'])

    db.session.commit()

    return jsonify({'message' : 'new product quantity added'})

@app.route('/products', methods=['GET'])
@token_required
def get_products(current_user):
    """
    Get a json with all the products in DB (product list).
    """

    products = Product.query.filter_by().all()

    output = []
    for product in products:

        product_quantity = Product_Quantity.query.filter_by(product_id=product.id).first()

        if product_quantity is None:
            return jsonify({'message' : 'no quantity found for {}'.format(product.name)}), http_status.NOTFOUND

        product_data = {}
        product_data['id'] = product.id
        product_data['name'] = product.name
        product_data['weight'] = product.weight
        product_data['price'] = product.price
        product_data['unit'] = product.unit
        product_data['quantity'] = product_quantity.quantity
        output.append(product_data)

    return jsonify({'list_of_products' : output})


@app.route('/products/<product_id>', methods=['DELETE'])
@token_required
def delete_product(current_user, product_id):
    """
    Remove a product from the DB, if the product id is not 
    found at the DB or the user is not an admin, fail, else 
    remove the product from the DB (this is why its important
    to store the product info for each invoice).
    """

    if not current_user.admin:
        return jsonify({'message': 'admin required for this action'}), http_status.UNAUTHORIZED

    product = Product.query.filter_by(id=product_id).first()

    #TODO: Check if product is not in current invoice before deleting.

    if product is None:
       return jsonify({'message': 'product does not exist'}), http_status.NOTFOUND

    db.session.delete(product)
    db.session.commit()

    return jsonify({'message': 'Product deleted'})

if  __name__ == '__main__':  
    app.run()


@app.route('/add/<product_id>', methods=['POST', 'GET'])
@token_required
def add_to_invoice(current_user, product_id):
    """
    Add (or scan) a product by its id to an invoice,
    the invoice will be a temporary one until its confirmed
    by the confirm_purchase function. The product quantity
    doesn't matter in this representation, just add as many 
    repeated products as neeeded.
    """

    product = Product.query.filter_by(id=product_id).first()

    if product is None:
       return jsonify({'message': 'product does not exist'}), http_status.NOTFOUND


    curr_invoice = CurrentInvoice.query.filter_by(id=current_user.id).first()

    if curr_invoice is None:
        curr_invoice = CurrentInvoice(user_id=current_user.id)
        db.session.add(curr_invoice)
    
    db.session.flush()

    # TODO: When adding a product to current invoice product, the quanity must be valid.

    invoice_product = CurrentInvoice_Product(currentinvoice_id=curr_invoice.id,\
                                            product_id=product.id)
    
    # TODO: After checking if the quantity is valid, subtract the invoice quantity from the Product_Quantity

    db.session.add(invoice_product)
    db.session.commit()

    return jsonify({'message' : 'product added to your invoice'})


@app.route('/invoice', methods=['GET'])
@token_required
def get_current_invoice(current_user):
    """
    Get all the products included in the current invoice (by the current_user).
    """
    currentInv = CurrentInvoice.query.filter_by(user_id=current_user.id).first()

    if currentInv is None:
        return jsonify({'message': 'no current invoice associated to {}'.format(current_user.name)}), http_status.NOTFOUND

    currentInvProducts = CurrentInvoice_Product.query.filter_by(currentinvoice_id=currentInv.id).all()

    products = []
    for inv in currentInvProducts:
        product = Product.query.filter_by(id=inv.product_id).first()
        product_data = {}
        product_data['name'] = product.name
        product_data['weight'] = product.weight
        product_data['price'] = product.price
        products.append(product_data)

    return jsonify({'cashier' : current_user.name, 'list_of_products' : products})
    

@app.route('/confirm', methods=['GET'])
@token_required
def confirm_purchase(current_user):
    """
    Confirm a purchase with the current invoice associated
    to the current user, the product info will be stored in
    Invoice_Product as well as the quantity.
    """

    invoice = Invoice(user_id=current_user.id)
    db.session.add(invoice)
    currentInv = CurrentInvoice.query.filter_by(user_id=current_user.id).first()

    if currentInv is None:
        return jsonify({'message': 'no current invoice associated to {}'.format(current_user.name)}), http_status.NOTFOUND
    
    currentInvProducts = CurrentInvoice_Product.query.filter_by(currentinvoice_id=currentInv.id).all()

    db.session.delete(currentInv)

    allProducts = {}
    for inv in currentInvProducts:
        product = Product.query.filter_by(id=inv.product_id).first()

        if product.name not in allProducts:
            allProducts[product.name] = \
                {
                "name": product.name,
                "weight": product.weight,
                "price": product.price,
                "quantity": 1,
                "invoice_id": invoice.id
                }
        else:
            allProducts[product.name]["quantity"] += 1
        
        db.session.delete(inv)

    for products in allProducts.values():
        invProduct  = Invoice_Product(
            name = products["name"],
            weight = products["weight"],
            price = products["price"],
            quantity = products["quantity"],
            invoice_id = products["invoice_id"]
            )
        db.session.add(invProduct)

    db.session.commit()

    return jsonify({'message' : 'invoice confirmed'})

@app.route('/report', methods=['POST', 'GET'])
@token_required
def sales_report(current_user):
    """
    Generate a sales report within a given date interval.
    The report includes the date interval, the products,
    each product quantity, total price given the quantity
    and the total profits for all invoices over the date range.
    """

    if not current_user.admin:
        return jsonify({'message': 'admin required for this action'}), http_status.UNAUTHORIZED

    data = request.get_json()
    initial_date = data["from"]
    final_date = data["to"]

    # might not work because of the UTC format stored in DB
    invoices = Invoice.query.filter(Invoice.date.between(initial_date, final_date)).all()

    if invoices is None or invoices is Empty:
        return jsonify({'message': 'could not find a table entry from \
            Invoice with dates [{}, {}]'.format(initial_date, final_date)}), http_status.NOTFOUND

    report = {}
    report["date"] = {"from": initial_date, "to": final_date}
    report['total_profits'] = 0
    report['products'] = {}

    for inv in invoices:
        products = Invoice_Product.query.filter_by(invoice_id=inv.id).all()

        if products is None:
            return jsonify({'message': 'could not find a table entry from \
                Invoice_Product with invoice_id = {}'.format(inv.id)}), http_status.NOTFOUND

        for product in products:

            if product.name not in report['products']:
                report['products'][product.name] = {}
                report['products'][product.name]['quantity'] = product.quantity
                report['products'][product.name]['total_price'] = (int(product.quantity) * int(product.price))
            else:
                report['products'][product.name]['quantity'] += product.quantity
                report['products'][product.name]['total_price'] += (int(product.quantity) * int(product.price))
            report['total_profits'] += report['products'][product.name]['total_price'] 
        

    return jsonify({'report' : report})

