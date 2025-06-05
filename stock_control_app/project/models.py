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

    TYPE_CHOICES = [('Compra', 'Compra'), ('Pedido operario', 'Pedido operario'), ('Entrega cliente', 'Entrega cliente'), ('Ajuste', 'Ajuste')]

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

from sqlalchemy import event
from stock_control_app.app import db # Required for db.object_session

# Event listener function
def update_stock_level_after_movement(mapper, connection, target_movement):
    Session = db.object_session(target_movement)
    if not Session:
        # This can happen if the event is triggered in a context where the object is not session-bound,
        # though for after_insert via Flask-SQLAlchemy, it should be.
        # Fallback or error if necessary, or acquire session differently if standalone script.
        # For Flask app, this should generally work.
        # If issues, could try: from flask_sqlalchemy import get_state
        # Session = get_state(db.get_app()).db.session
        print("Warning: Could not obtain session from target_movement. Stock level may not be updated.")
        return

    # Find existing StockLevel or create a new one
    stock_level = Session.query(StockLevel).filter_by(
        product_id=target_movement.product_id,
        deposit_id=target_movement.deposit_id
    ).with_for_update().first() # with_for_update() for pessimistic locking if concurrent updates are a concern

    if not stock_level:
        stock_level = StockLevel(
            product_id=target_movement.product_id,
            deposit_id=target_movement.deposit_id,
            current_stock=0.0 # Initialize stock
        )
        Session.add(stock_level)
        # If we add a new stock_level, we might need to flush to get its ID if other parts of the transaction need it.
        # Session.flush()

    # Adjust stock based on movement type
    if target_movement.type == 'Compra':
        stock_level.current_stock += target_movement.quantity
    elif target_movement.type in ['Pedido operario', 'Entrega cliente']:
        stock_level.current_stock -= target_movement.quantity
    elif target_movement.type == 'Ajuste':
        stock_level.current_stock += target_movement.quantity

    # The session commit is handled by the route that created the StockMovement.
    # If stock_level was newly created, it will be persisted along with the movement.
    # If it was existing, its change will also be part of the same transaction.
    # print(f"StockLevel updated for Product ID {stock_level.product_id} in Deposit ID {stock_level.deposit_id} to {stock_level.current_stock}") # For debugging

# Register the event listener for StockMovement after_insert events
event.listen(StockMovement, 'after_insert', update_stock_level_after_movement)
