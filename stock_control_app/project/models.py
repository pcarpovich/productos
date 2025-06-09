from sqlalchemy import Enum as SQLAlchemyEnum, UniqueConstraint, event
# from sqlalchemy.orm import relationship # Not needed if using db.relationship directly
# from sqlalchemy.sql import func # db.func is available via SQLAlchemy instance
from stock_control_app.app import db # Import db from the main app module

class Product(db.Model):
    __tablename__ = "product"

    id = db.Column(db.Integer, primary_key=True, index=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    unit_of_measure = db.Column(db.String(50))
    category = db.Column(db.String(100))
    minimum_stock = db.Column(db.Integer, default=0, nullable=False)

    stock_movements = db.relationship("StockMovement", back_populates="product", lazy='dynamic')
    stock_levels = db.relationship("StockLevel", back_populates="product", lazy='dynamic')

    def __repr__(self):
        return f"<Product {self.name}>"

class Deposit(db.Model):
    __tablename__ = "deposit"

    id = db.Column(db.Integer, primary_key=True, index=True)
    name = db.Column(db.String(100), nullable=False, unique=True)

    stock_movements = db.relationship("StockMovement", back_populates="deposit", lazy='dynamic')
    stock_levels = db.relationship("StockLevel", back_populates="deposit", lazy='dynamic')

    def __repr__(self):
        return f"<Deposit {self.name}>"

class Operator(db.Model):
    __tablename__ = "operator"

    id = db.Column(db.Integer, primary_key=True, index=True)
    name = db.Column(db.String(100), nullable=False)
    dni = db.Column(db.String(20), unique=True, nullable=False)

    stock_movements = db.relationship("StockMovement", back_populates="operator", lazy='dynamic')

    def __repr__(self):
        return f"<Operator {self.name}>"

class Client(db.Model):
    __tablename__ = "client"

    id = db.Column(db.Integer, primary_key=True, index=True)
    name = db.Column(db.String(100), nullable=False)
    address = db.Column(db.String(250))
    locality = db.Column(db.String(100))

    stock_movements = db.relationship("StockMovement", back_populates="client", lazy='dynamic')

    def __repr__(self):
        return f"<Client {self.name}>"

class StockMovement(db.Model):
    __tablename__ = "stock_movement"

    id = db.Column(db.Integer, primary_key=True, index=True)
    product_id = db.Column(db.Integer, db.ForeignKey("product.id"), nullable=False)
    deposit_id = db.Column(db.Integer, db.ForeignKey("deposit.id"), nullable=False)
    operator_id = db.Column(db.Integer, db.ForeignKey("operator.id"), nullable=True)
    client_id = db.Column(db.Integer, db.ForeignKey("client.id"), nullable=True)

    TYPE_CHOICES = [('Compra', 'Compra'), ('Pedido operario', 'Pedido operario'), ('Entrega cliente', 'Entrega cliente'), ('Ajuste', 'Ajuste')]
    # Ensure the Enum uses values from TYPE_CHOICES correctly for the database constraint
    type = db.Column(SQLAlchemyEnum(*[choice[0] for choice in TYPE_CHOICES], name='movement_types_enum'), nullable=False)

    quantity = db.Column(db.Float, nullable=False)
    timestamp = db.Column(db.DateTime, server_default=db.func.now(), nullable=False)

    product = db.relationship("Product", back_populates="stock_movements")
    deposit = db.relationship("Deposit", back_populates="stock_movements")
    operator = db.relationship("Operator", back_populates="stock_movements")
    client = db.relationship("Client", back_populates="stock_movements")

    def __repr__(self):
        return f"<StockMovement ID: {self.id} Product: {self.product.name if self.product else 'N/A'} Type: {self.type} Qty: {self.quantity}>"

class StockLevel(db.Model):
    __tablename__ = "stock_level"

    id = db.Column(db.Integer, primary_key=True, index=True)
    product_id = db.Column(db.Integer, db.ForeignKey("product.id"), nullable=False)
    deposit_id = db.Column(db.Integer, db.ForeignKey("deposit.id"), nullable=False)
    current_stock = db.Column(db.Float, nullable=False, default=0.0)

    product = db.relationship("Product", back_populates="stock_levels")
    deposit = db.relationship("Deposit", back_populates="stock_levels")

    __table_args__ = (UniqueConstraint('product_id', 'deposit_id', name='_product_deposit_uc'),)

    def __repr__(self):
        return f"<StockLevel Product: {self.product.name if self.product else 'N/A'} Deposit: {self.deposit.name if self.deposit else 'N/A'} Stock: {self.current_stock}>"

# Event listener function for StockMovement
def update_stock_level_after_movement(mapper, connection, target_movement):
    Session = db.object_session(target_movement)
    if not Session:
        print("Warning: Could not obtain session from target_movement for StockLevel update.")
        return

    stock_level = Session.query(StockLevel).filter_by(
        product_id=target_movement.product_id,
        deposit_id=target_movement.deposit_id
    ).with_for_update().first()

    if not stock_level:
        stock_level = StockLevel(
            product_id=target_movement.product_id,
            deposit_id=target_movement.deposit_id,
            current_stock=0.0
        )
        Session.add(stock_level)

    if target_movement.type == 'Compra':
        stock_level.current_stock += target_movement.quantity
    elif target_movement.type in ['Pedido operario', 'Entrega cliente']:
        stock_level.current_stock -= target_movement.quantity
    elif target_movement.type == 'Ajuste':
        stock_level.current_stock += target_movement.quantity

# Register the event listener
event.listen(StockMovement, 'after_insert', update_stock_level_after_movement)
