from flask import Blueprint, render_template, request, Response
from sqlalchemy.sql import func
from sqlalchemy.orm import joinedload # Explicit import for clarity
from datetime import datetime, time
import io
import csv

from stock_control_app.app import db # Relative import for db
from ..models import StockLevel, Product, Deposit, StockMovement, Operator, Client # Relative import for models
from .forms import MovementHistoryFilterForm # Relative import for forms

reports_bp = Blueprint('reports',
                       __name__,
                       template_folder='templates',
                       url_prefix='/reports') # url_prefix defined here

@reports_bp.route('/current_stock')
def view_current_stock():
    stock_data = db.session.query(
        Product.name.label('product_name'),
        Deposit.name.label('deposit_name'),
        StockLevel.current_stock,
        Product.unit_of_measure
    ).select_from(StockLevel)\
     .join(Product, StockLevel.product_id == Product.id)\
     .join(Deposit, StockLevel.deposit_id == Deposit.id)\
     .order_by(Product.name, Deposit.name).all()

    return render_template('current_stock.html',
                           stock_data=stock_data,
                           title="Current Stock by Product and Deposit")

@reports_bp.route('/low_stock_alerts')
def view_low_stock_alerts():
    low_stock_items = db.session.query(
        Product.name.label('product_name'),
        Deposit.name.label('deposit_name'),
        StockLevel.current_stock,
        Product.minimum_stock,
        Product.unit_of_measure
    ).select_from(StockLevel)\
     .join(Product, Product.id == StockLevel.product_id)\
     .join(Deposit, Deposit.id == StockLevel.deposit_id)\
     .filter(StockLevel.current_stock < Product.minimum_stock)\
     .filter(Product.minimum_stock > 0)\
     .order_by(Product.name, Deposit.name).all()

    return render_template('low_stock_alerts.html',
                           low_stock_items=low_stock_items,
                           title="Low Stock Alerts")

@reports_bp.route('/client_consumption')
def view_client_consumption():
    client_consumption_data = db.session.query(
        Client.name.label('client_name'),
        Product.name.label('product_name'),
        Product.unit_of_measure,
        db.func.sum(StockMovement.quantity).label('total_consumed')
    ).select_from(StockMovement)\
     .join(Product, StockMovement.product_id == Product.id)\
     .join(Client, StockMovement.client_id == Client.id)\
     .filter(StockMovement.type == 'Entrega cliente')\
     .group_by(Client.name, Product.name, Product.unit_of_measure)\
     .order_by(Client.name, Product.name).all()

    return render_template('client_consumption.html',
                           client_consumption_data=client_consumption_data,
                           title="Total Consumption by Client")

@reports_bp.route('/operator_consumption')
def view_operator_consumption():
    operator_consumption_data = db.session.query(
        Operator.name.label('operator_name'),
        Product.name.label('product_name'),
        Product.unit_of_measure,
        db.func.sum(StockMovement.quantity).label('total_requested')
    ).select_from(StockMovement)\
     .join(Product, StockMovement.product_id == Product.id)\
     .join(Operator, StockMovement.operator_id == Operator.id)\
     .filter(StockMovement.type == 'Pedido operario')\
     .group_by(Operator.name, Product.name, Product.unit_of_measure)\
     .order_by(Operator.name, Product.name).all()

    return render_template('operator_consumption.html',
                           operator_consumption_data=operator_consumption_data,
                           title="Total Requested by Operator")

@reports_bp.route('/movement_history', methods=['GET'])
def view_movement_history():
    form = MovementHistoryFilterForm(request.args)

    query = StockMovement.query.options(
        joinedload(StockMovement.product),
        joinedload(StockMovement.deposit),
        joinedload(StockMovement.operator),
        joinedload(StockMovement.client)
    ).order_by(StockMovement.timestamp.desc())

    if form.product_id.data:
        query = query.filter(StockMovement.product_id == form.product_id.data.id)
    if form.deposit_id.data:
        query = query.filter(StockMovement.deposit_id == form.deposit_id.data.id)
    if form.movement_type.data: # Ensure this checks for non-empty string
        query = query.filter(StockMovement.type == form.movement_type.data)
    if form.operator_id.data:
        query = query.filter(StockMovement.operator_id == form.operator_id.data.id)
    if form.client_id.data:
        query = query.filter(StockMovement.client_id == form.client_id.data.id)
    if form.start_date.data:
        query = query.filter(StockMovement.timestamp >= datetime.combine(form.start_date.data, time.min))
    if form.end_date.data:
        query = query.filter(StockMovement.timestamp <= datetime.combine(form.end_date.data, time.max))

    page = request.args.get('page', 1, type=int)
    per_page = 20
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    movements = pagination.items

    return render_template('movement_history.html',
                           form=form,
                           movements=movements,
                           pagination=pagination,
                           title="Movement History")

@reports_bp.route('/movement_history/export_csv', methods=['GET'])
def export_movement_history_csv():
    form = MovementHistoryFilterForm(request.args)

    query = StockMovement.query.options(
        joinedload(StockMovement.product),
        joinedload(StockMovement.deposit),
        joinedload(StockMovement.operator),
        joinedload(StockMovement.client)
    ).order_by(StockMovement.timestamp.desc())

    if form.product_id.data:
        query = query.filter(StockMovement.product_id == form.product_id.data.id)
    if form.deposit_id.data:
        query = query.filter(StockMovement.deposit_id == form.deposit_id.data.id)
    if form.movement_type.data:
        query = query.filter(StockMovement.type == form.movement_type.data)
    if form.operator_id.data:
        query = query.filter(StockMovement.operator_id == form.operator_id.data.id)
    if form.client_id.data:
        query = query.filter(StockMovement.client_id == form.client_id.data.id)
    if form.start_date.data:
        query = query.filter(StockMovement.timestamp >= datetime.combine(form.start_date.data, time.min))
    if form.end_date.data:
        query = query.filter(StockMovement.timestamp <= datetime.combine(form.end_date.data, time.max))

    movements = query.all()

    si = io.StringIO()
    writer = csv.writer(si)
    writer.writerow(['Timestamp', 'Product', 'Unit', 'Deposit', 'Type', 'Quantity', 'Operator DNI', 'Operator Name', 'Client Name'])
    for movement in movements:
        row = [
            movement.timestamp.strftime('%Y-%m-%d %H:%M:%S') if movement.timestamp else '',
            movement.product.name if movement.product else '',
            movement.product.unit_of_measure if movement.product and movement.product.unit_of_measure else '',
            movement.deposit.name if movement.deposit else '',
            movement.type,
            movement.quantity,
            movement.operator.dni if movement.operator else '',
            movement.operator.name if movement.operator else '',
            movement.client.name if movement.client else ''
        ]
        writer.writerow(row)
    output = si.getvalue()

    return Response(
        output,
        mimetype="text/csv",
        headers={"Content-disposition": "attachment; filename=movement_history.csv"}
    )
