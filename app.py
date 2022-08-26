from flask import Flask, request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from dotenv import load_dotenv
from functools import wraps
from os import environ
from models import db, Users, Product, User_Token
import uuid
import jwt
import datetime

load_dotenv()

app = Flask(__name__)

app.config["SECRET_KEY"] = environ.get("SECRET_KEY")
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:////" + environ.get("DB_PATH")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = True

db.init_app(app)

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):

        token = None

        if 'x-access-tokens' in request.headers:
            token = request.headers['x-access-tokens']

        if not token:
            return jsonify({'message': 'a valid token is missing'}), 401

        try:
            data = jwt.decode(token, app.config['SECRET_KEY'], algorithms="HS256")
            current_user = Users.query.filter_by(public_id=data['public_id']).first()
        except Exception as e:
            print("Exception: ", e)
            return jsonify({'message': 'token is invalid'}), 401

        return f(current_user, *args, **kwargs)
        
    return decorated


@app.route('/register', methods=['GET', 'POST'])
def signup_user():

    data = request.get_json()

    user = Users.query.filter_by(name=data['name']).first()

    if user is not None:
        return jsonify({'message': 'user already exists'}), 409

    hashed_password = generate_password_hash(data['password'], method='sha256')

    new_user = Users(public_id=str(uuid.uuid4()), name=data['name'], password=hashed_password, admin=False)
    db.session.add(new_user)
    db.session.commit()

    return jsonify({'message': 'registered successfully'})
    

@app.route('/login', methods=['GET', 'POST'])
def login_user():
 
    auth = request.authorization

    if not auth or not auth.username or not auth.password:
        return jsonify({'message': 'could not verify'}), 401

    user = Users.query.filter_by(name=auth.username).first()
        
    if user is not None and check_password_hash(user.password, auth.password):
        token = jwt.encode({'public_id': user.public_id, 'exp' :\
                datetime.datetime.utcnow() + datetime.timedelta(minutes=10)}, app.config['SECRET_KEY'])

        user_token = User_Token.query.filter_by(name=auth.username).first()

        if user_token is not None:
            user_token.token = token
        else:
            new_user_token = User_Token(name=auth.username, token=token)
            db.session.add(new_user_token)

        db.session.commit()

        return jsonify({'token' : token})

    return jsonify({'message': 'could not verify'}), 401


@app.route('/product', methods=['POST', 'GET'])
@token_required
def create_product(current_user):
    
    data = request.get_json()
    product = Product.query.filter_by(name=data['name']).first()

    if product is not None:
        return jsonify({'message': 'product already exists'}), 409


    new_product = Product(name=data['name'], weight=data['weight'], price=data['price'])
    db.session.add(new_product)
    db.session.commit()

    return jsonify({'message' : 'new product created'})


@app.route('/products', methods=['GET'])
@token_required
def get_products(current_user):

    products = Product.query.filter_by().all()

    output = []
    for product in products:

        product_data = {}
        product_data['name'] = product.name
        product_data['weight'] = product.weight
        product_data['price'] = product.price
        output.append(product_data)

    return jsonify({'list_of_products' : output})

@app.route('/products/<product_id>', methods=['DELETE'])
@token_required
def delete_product(current_user, product_id):
    product = Product.query.filter_by(id=product_id).first()

    if product is None:
       return jsonify({'message': 'product does not exist'}), 404

    db.session.delete(product)
    db.session.commit()

    return jsonify({'message': 'Product deleted'})

if  __name__ == '__main__':  
    app.run()
