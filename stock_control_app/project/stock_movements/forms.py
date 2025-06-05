from flask_wtf import FlaskForm
from wtforms import SelectField, FloatField, SubmitField
from wtforms.fields import DateTimeLocalField # Using DateTimeLocalField for better browser support with format
from wtforms.validators import DataRequired, Optional, ValidationError, NumberRange
from wtforms_sqlalchemy.fields import QuerySelectField
from stock_control_app.project.models import Product, Deposit, Operator, Client
from datetime import datetime

def product_query():
    return Product.query.order_by(Product.name).all()

def deposit_query():
    return Deposit.query.order_by(Deposit.name).all()

def operator_query():
    return Operator.query.order_by(Operator.name).all()

def client_query():
    return Client.query.order_by(Client.name).all()

class StockMovementForm(FlaskForm):
    product_id = QuerySelectField('Product',
                                  query_factory=product_query,
                                  get_label='name',
                                  allow_blank=False, # Must select a product
                                  validators=[DataRequired(message="Please select a product.")])
    deposit_id = QuerySelectField('Deposit',
                                  query_factory=deposit_query,
                                  get_label='name',
                                  allow_blank=False, # Must select a deposit
                                  validators=[DataRequired(message="Please select a deposit.")])
    type = SelectField('Movement Type',
                       choices=[
                           ('', '-- Select Type --'), # Placeholder
                           ('Compra', 'Compra (Incoming)'),
                           ('Pedido operario', 'Pedido operario (Outgoing)'),
                           ('Entrega cliente', 'Entrega cliente (Outgoing)'),
                           ('Ajuste', 'Ajuste (Manual Correction)')
                       ],
                       validators=[DataRequired(message="Please select a movement type.")])
    quantity = FloatField('Quantity',
                          validators=[DataRequired(message="Quantity is required.")])
                          # NumberRange will be added in custom validation based on type
    operator_id = QuerySelectField('Operator',
                                   query_factory=operator_query,
                                   get_label='name',
                                   allow_blank=True, # Operator can be blank
                                   blank_text='-- Optional: Select Operator --')
    client_id = QuerySelectField('Client',
                                 query_factory=client_query,
                                 get_label='name',
                                 allow_blank=True, # Client can be blank
                                 blank_text='-- Optional: Select Client --')
    timestamp = DateTimeLocalField('Timestamp (Optional)',
                                 format='%Y-%m-%dT%H:%M',
                                 default=datetime.utcnow,
                                 validators=[Optional()])
    submit = SubmitField('Record Movement')

    def validate(self, extra_validators=None):
        # Standard validation
        if not super(StockMovementForm, self).validate(extra_validators):
            return False

        # Custom logic
        movement_type = self.type.data
        quantity_val = self.quantity.data
        operator = self.operator_id.data
        client = self.client_id.data

        valid = True

        if movement_type == 'Pedido operario':
            if not operator:
                self.operator_id.errors.append('Operator is required for "Pedido operario".')
                valid = False
            # client_id should be None for Pedido operario - handled by allowing blank and not requiring
        elif movement_type == 'Entrega cliente':
            if not client:
                self.client_id.errors.append('Client is required for "Entrega cliente".')
                valid = False
        # For 'Compra' and 'Ajuste', operator_id and client_id are optional.

        # Quantity validation based on type
        if quantity_val is not None: # DataRequired should ensure it's not None
            if movement_type == 'Compra':
                if quantity_val <= 0:
                    self.quantity.errors.append('Quantity must be greater than zero for "Compra".')
                    valid = False
            elif movement_type in ['Pedido operario', 'Entrega cliente']:
                if quantity_val <= 0:
                    self.quantity.errors.append('Quantity must be greater than zero for outgoing movements (it represents the amount taken).')
                    valid = False
            elif movement_type == 'Ajuste':
                if quantity_val == 0:
                    self.quantity.errors.append('Quantity cannot be zero for "Ajuste". Use positive for additions or negative for subtractions.')
                    valid = False
            # No specific validation for quantity sign on Ajuste other than non-zero, as it can be positive or negative.

        return valid
