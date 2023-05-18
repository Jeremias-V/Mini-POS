from datetime import datetime
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Users(db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    public_id = db.Column(db.Integer)
    username = db.Column(db.String(50))
    password = db.Column(db.String(50))
    admin = db.Column(db.Boolean, default=False)

class Product(db.Model):
    __tablename__ = "product"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    price = db.Column(db.Integer, nullable=False)
    weight = db.Column(db.Float, nullable=False)
    unit = db.Column(db.String(3), nullable=False)

class Product_Quantity(db.Model):
    """
    TODO: Implement logic when creating products, and adding them to invoice.
    Table to relate a product to its available quantity.
    """
    __tablename__ = "product_quantity"
    id = db.Column(db.Integer, primary_key=True)
    quantity = db.Column(db.Integer, default=0)
    product_id = db.Column(db.Integer, db.ForeignKey("product.id"))
    
class Invoice(db.Model):
    """
    The invoice has a creation time and an user who
    created it, the products of an invoice is selected
    from the invoice_product table.
    """
    __tablename__ = "invoice"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    date = db.Column(db.DateTime, default=datetime.utcnow().date())

class Invoice_Product(db.Model):
    """
    This table is to relate an invoice with its products,
    it contains the product information because the info
    might change or the product can be deleted from the
    database but its sale still be recorded.
    """
    __tablename__ = "invoice_product"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    weight = db.Column(db.String(20), nullable=False)
    price = db.Column(db.String(50), nullable=False)
    unit = db.Column(db.String(3), nullable=False)
    quantity = db.Column(db.Integer, default=1)
    invoice_id = db.Column(db.Integer, db.ForeignKey("invoice.id"))

class CurrentInvoice(db.Model):
    """
    This is for the current products in an invoice 
    before the purchase is completed.
    """
    __tablename__ = "currentinvoice"
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"))

class CurrentInvoice_Product(db.Model):
    __tablename__ = "currentinvoice_product"
    id = db.Column(db.Integer, primary_key=True)
    currentinvoice_id = db.Column(db.Integer, db.ForeignKey("currentinvoice.id"))
    product_id = db.Column(db.Integer, db.ForeignKey("product.id"))
