from sqlalchemy import Enum, UniqueConstraint # Keep Enum and UniqueConstraint from sqlalchemy
from stock_control_app.app import db # Import db from app.py

# Base = declarative_base() # Removed

class Product(db.Model): # Changed Base to db.Model
    __tablename__ = "product"

    id = db.Column(db.Integer, primary_key=True, index=True) # Changed Column, Integer
    name = db.Column(db.String, nullable=False, unique=True) # Changed Column, String
    unit_of_measure = db.Column(db.String) # Changed Column, String
    category = db.Column(db.String) # Changed Column, String
    minimum_stock = db.Column(db.Integer, default=0) # Changed Column, Integer

    stock_movements = db.relationship("StockMovement", back_populates="product") # Changed relationship
    stock_levels = db.relationship("StockLevel", back_populates="product") # Changed relationship

class Deposit(db.Model): # Changed Base to db.Model
    __tablename__ = "deposit"

    id = db.Column(db.Integer, primary_key=True, index=True) # Changed Column, Integer
    name = db.Column(db.String, nullable=False, unique=True) # Changed Column, String

    stock_movements = db.relationship("StockMovement", back_populates="deposit") # Changed relationship
    stock_levels = db.relationship("StockLevel", back_populates="deposit") # Changed relationship

class Operator(db.Model): # Changed Base to db.Model
    __tablename__ = "operator"

    id = db.Column(db.Integer, primary_key=True, index=True) # Changed Column, Integer
    name = db.Column(db.String, nullable=False) # Changed Column, String
    dni = db.Column(db.String, unique=True) # Changed Column, String

    stock_movements = db.relationship("StockMovement", back_populates="operator") # Changed relationship

class Client(db.Model): # Changed Base to db.Model
    __tablename__ = "client"

    id = db.Column(db.Integer, primary_key=True, index=True) # Changed Column, Integer
    name = db.Column(db.String, nullable=False) # Changed Column, String
    address = db.Column(db.String) # Changed Column, String
    locality = db.Column(db.String) # Changed Column, String

    stock_movements = db.relationship("StockMovement", back_populates="client") # Changed relationship

class StockMovement(db.Model): # Changed Base to db.Model
    __tablename__ = "stock_movement"

    id = db.Column(db.Integer, primary_key=True, index=True) # Changed Column, Integer
    product_id = db.Column(db.Integer, db.ForeignKey("product.id"), nullable=False) # Changed Column, Integer, ForeignKey
    deposit_id = db.Column(db.Integer, db.ForeignKey("deposit.id"), nullable=False) # Changed Column, Integer, ForeignKey
    operator_id = db.Column(db.Integer, db.ForeignKey("operator.id"), nullable=True) # Changed Column, Integer, ForeignKey
    client_id = db.Column(db.Integer, db.ForeignKey("client.id"), nullable=True) # Changed Column, Integer, ForeignKey
    type = db.Column(Enum('Compra', 'Pedido operario', 'Entrega cliente', 'Ajuste', name='movement_types'), nullable=False) # Changed Column, kept Enum
    quantity = db.Column(db.Float, nullable=False) # Changed Column, Float
    timestamp = db.Column(db.DateTime, server_default=db.func.now()) # Changed Column, DateTime, func

    product = db.relationship("Product", back_populates="stock_movements") # Changed relationship
    deposit = db.relationship("Deposit", back_populates="stock_movements") # Changed relationship
    operator = db.relationship("Operator", back_populates="stock_movements") # Changed relationship
    client = db.relationship("Client", back_populates="stock_movements") # Changed relationship

class StockLevel(db.Model): # Changed Base to db.Model
    __tablename__ = "stock_level"

    id = db.Column(db.Integer, primary_key=True, index=True) # Changed Column, Integer
    product_id = db.Column(db.Integer, db.ForeignKey("product.id"), nullable=False) # Changed Column, Integer, ForeignKey
    deposit_id = db.Column(db.Integer, db.ForeignKey("deposit.id"), nullable=False) # Changed Column, Integer, ForeignKey
    current_stock = db.Column(db.Float, nullable=False, default=0.0) # Changed Column, Float

    product = db.relationship("Product", back_populates="stock_levels") # Changed relationship
    deposit = db.relationship("Deposit", back_populates="stock_levels") # Changed relationship

    __table_args__ = (UniqueConstraint('product_id', 'deposit_id', name='_product_deposit_uc'),)
