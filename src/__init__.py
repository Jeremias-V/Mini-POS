from flask import Flask
from dotenv import load_dotenv
from os import environ
from flask_cors import CORS
from .models import db
from .routes import main
from sqlalchemy import create_engine
from sqlalchemy_utils import database_exists, create_database

def validate_database(DB_URI):

    status = False

    engine = create_engine(DB_URI)

    if not database_exists(engine.url): 
        create_database(engine.url)
        print("Created new database " + DB_URI)
        status = False

    else:
        print("Database loaded from " + DB_URI)
        status = True
        
    return status

def create_app(db_uri=None):

    load_dotenv()

    app = Flask(__name__)
    CORS(app)

    app.config["SECRET_KEY"] = environ.get("SECRET_KEY")
    
    if db_uri is None:
        app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:////" + environ.get("DB_PATH")
    else:
        app.config["SQLALCHEMY_DATABASE_URI"] = db_uri

    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = True
    app.config["ADMIN_KEY"] = environ.get("ADMIN_KEY")


    app.register_blueprint(main)

    db.init_app(app)
    if not validate_database(app.config["SQLALCHEMY_DATABASE_URI"]):
        db.create_all(app=app)

    return app
