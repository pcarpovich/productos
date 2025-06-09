from flask_wtf import FlaskForm
from wtforms import SelectField, FloatField, SubmitField
from wtforms.fields import DateTimeLocalField
from wtforms.validators import DataRequired, Optional, ValidationError
from wtforms_sqlalchemy.fields import QuerySelectField
from stock_control_app.project.models import Product, Deposit, Operator, Client, StockMovement # Import StockMovement for TYPE_CHOICES
from datetime import datetime

# Query factories
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
                                  allow_blank=False,
                                  validators=[DataRequired(message="Please select a product.")])
    deposit_id = QuerySelectField('Deposit',
                                  query_factory=deposit_query,
                                  get_label='name',
                                  allow_blank=False,
                                  validators=[DataRequired(message="Please select a deposit.")])
    type = SelectField('Movement Type',
                       choices=[('', '-- Select Type --')] + StockMovement.TYPE_CHOICES,
                       validators=[DataRequired(message="Please select a movement type.")])
    quantity = FloatField('Quantity',
                          validators=[DataRequired(message="Quantity is required.")])
    operator_id = QuerySelectField('Operator',
                                   query_factory=operator_query,
                                   get_label='name',
                                   allow_blank=True,
                                   blank_text='-- Optional: Select Operator --',
                                   validators=[Optional()])
    client_id = QuerySelectField('Client',
                                 query_factory=client_query,
                                 get_label='name',
                                 allow_blank=True,
                                 blank_text='-- Optional: Select Client --',
                                 validators=[Optional()])
    timestamp = DateTimeLocalField('Timestamp (Optional, defaults to now)',
                                 format='%Y-%m-%dT%H:%M',
                                 default=datetime.utcnow,
                                 validators=[Optional()])
    submit = SubmitField('Record Movement')

    def validate(self, extra_validators=None):
        if not super(StockMovementForm, self).validate(extra_validators):
            return False

        movement_type = self.type.data
        quantity_val = self.quantity.data # Already checked for None by DataRequired
        operator = self.operator_id.data
        client = self.client_id.data

        valid = True

        if movement_type == 'Pedido operario':
            if not operator:
                self.operator_id.errors.append('Operator is required for "Pedido operario".')
                valid = False
        elif movement_type == 'Entrega cliente':
            if not client:
                self.client_id.errors.append('Client is required for "Entrega cliente".')
                valid = False

        if quantity_val is not None:
            if movement_type == 'Compra':
                if quantity_val <= 0:
                    self.quantity.errors.append('Quantity must be greater than zero for "Compra".')
                    valid = False
            elif movement_type in ['Pedido operario', 'Entrega cliente']:
                if quantity_val <= 0:
                    self.quantity.errors.append('Quantity must be greater than zero for outgoing movements.')
                    valid = False
            elif movement_type == 'Ajuste':
                if quantity_val == 0:
                    self.quantity.errors.append('Quantity cannot be zero for "Ajuste".')
                    valid = False

        return valid
