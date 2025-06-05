from flask_wtf import FlaskForm
from wtforms import SelectField, SubmitField
from wtforms.fields import DateField # Using DateField from wtforms
from wtforms.validators import Optional
from wtforms_sqlalchemy.fields import QuerySelectField
from stock_control_app.project.models import Product, Deposit, Operator, Client, StockMovement

# Query factories for QuerySelectFields
def product_query():
    return Product.query.order_by(Product.name).all()

def deposit_query():
    return Deposit.query.order_by(Deposit.name).all()

def operator_query():
    return Operator.query.order_by(Operator.name).all()

def client_query():
    return Client.query.order_by(Client.name).all()

class MovementHistoryFilterForm(FlaskForm):
    product_id = QuerySelectField(
        "Product",
        query_factory=product_query,
        get_label='name',
        allow_blank=True,
        blank_text='-- All Products --',
        validators=[Optional()]
    )
    deposit_id = QuerySelectField(
        "Deposit",
        query_factory=deposit_query,
        get_label='name',
        allow_blank=True,
        blank_text='-- All Deposits --',
        validators=[Optional()]
    )
    movement_type = SelectField(
        "Movement Type",
        choices=[('', '-- All Types --')] + StockMovement.TYPE_CHOICES, # Using TYPE_CHOICES from model
        validators=[Optional()]
    )
    operator_id = QuerySelectField(
        "Operator",
        query_factory=operator_query,
        get_label='name',
        allow_blank=True,
        blank_text='-- All Operators --',
        validators=[Optional()]
    )
    client_id = QuerySelectField(
        "Client",
        query_factory=client_query,
        get_label='name',
        allow_blank=True,
        blank_text='-- All Clients --',
        validators=[Optional()]
    )
    start_date = DateField(
        "Start Date",
        format='%Y-%m-%d',
        validators=[Optional()]
    )
    end_date = DateField(
        "End Date",
        format='%Y-%m-%d',
        validators=[Optional()]
    )
    submit = SubmitField("Filter Movements")
