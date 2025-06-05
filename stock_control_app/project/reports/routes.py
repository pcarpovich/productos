from flask import Blueprint, render_template
from stock_control_app.project.models import StockLevel, Product, Deposit
from stock_control_app.app import db

reports_bp = Blueprint('reports',
                       __name__,
                       template_folder='templates',
                       url_prefix='/reports')

@reports_bp.route('/current_stock')
def view_current_stock():
    """
    Displays the current stock levels for each product in each deposit.
    """
    stock_data = db.session.query(
        StockLevel.current_stock,
        Product.name.label('product_name'),
        Product.unit_of_measure.label('unit_of_measure'),
        Deposit.name.label('deposit_name')
    ).join(Product, StockLevel.product_id == Product.id)\
     .join(Deposit, StockLevel.deposit_id == Deposit.id)\
     .order_by(Product.name, Deposit.name).all()

    # Each item in stock_data will be a Row object (similar to a named tuple)
    # e.g., item.current_stock, item.product_name, item.deposit_name

    return render_template('current_stock.html',
                           stock_data=stock_data,
                           title="Current Stock by Product and Deposit")

@reports_bp.route('/low_stock_alerts')
def view_low_stock_alerts():
    """
    Displays products that are below their minimum stock level in specific deposits.
    """
    low_stock_items = db.session.query(
        Product.name.label('product_name'),
        Deposit.name.label('deposit_name'),
        StockLevel.current_stock,
        Product.minimum_stock,
        Product.unit_of_measure
    ).join(StockLevel, Product.id == StockLevel.product_id)\
     .join(Deposit, Deposit.id == StockLevel.deposit_id)\
     .filter(StockLevel.current_stock < Product.minimum_stock)\
     .filter(Product.minimum_stock > 0)\
     .order_by(Product.name, Deposit.name).all()

    return render_template('low_stock_alerts.html',
                           low_stock_items=low_stock_items,
                           title="Low Stock Alerts")

from sqlalchemy.sql import func # Import func for db.func.sum

@reports_bp.route('/client_consumption')
def view_client_consumption():
    """
    Displays the total quantity of each product consumed by each client.
    Consumption is based on 'Entrega cliente' movement type.
    """
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

from stock_control_app.project.models import Operator # Import Operator

@reports_bp.route('/operator_consumption')
def view_operator_consumption():
    """
    Displays the total quantity of each product requested by each operator.
    Based on 'Pedido operario' movement type.
    """
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

from flask import request # Import request
from datetime import datetime, time # Import datetime and time
from stock_control_app.project.reports.forms import MovementHistoryFilterForm
from stock_control_app.project.models import StockMovement # StockMovement already imported

@reports_bp.route('/movement_history', methods=['GET'])
def view_movement_history():
    form = MovementHistoryFilterForm(request.args) # Populate form from query args

    query = StockMovement.query.options(
        db.joinedload(StockMovement.product),
        db.joinedload(StockMovement.deposit),
        db.joinedload(StockMovement.operator),
        db.joinedload(StockMovement.client)
    ).order_by(StockMovement.timestamp.desc())

    # Apply filters based on form data.
    # Using request.args directly for filtering if form isn't "submitted" in GET context
    # but fields are present in URL. form.validate() not typically used for GET filters.

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
        query = query.filter(StockMovement.timestamp >= form.start_date.data)
    if form.end_date.data:
        # To include the whole end day, set time to 23:59:59 or use datetime.combine with time.max
        end_datetime = datetime.combine(form.end_date.data, time.max)
        query = query.filter(StockMovement.timestamp <= end_datetime)

    page = request.args.get('page', 1, type=int)
    per_page = 20 # Items per page
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    movements = pagination.items

    return render_template('movement_history.html',
                           form=form,
                           movements=movements,
                           pagination=pagination,
                           title="Movement History")

import io
import csv
from flask import Response

@reports_bp.route('/movement_history/export_csv', methods=['GET'])
def export_movement_history_csv():
    form = MovementHistoryFilterForm(request.args) # Populate form from query args

    query = StockMovement.query.options(
        db.joinedload(StockMovement.product),
        db.joinedload(StockMovement.deposit),
        db.joinedload(StockMovement.operator),
        db.joinedload(StockMovement.client)
    ).order_by(StockMovement.timestamp.desc()) # Order is good for consistency, though not strictly needed for CSV

    # Apply filters - same logic as in view_movement_history
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
        query = query.filter(StockMovement.timestamp >= form.start_date.data)
    if form.end_date.data:
        end_datetime = datetime.combine(form.end_date.data, time.max)
        query = query.filter(StockMovement.timestamp <= end_datetime)

    movements = query.all() # Get all matching movements

    si = io.StringIO()
    writer = csv.writer(si)

    # Write header row
    writer.writerow([
        'Timestamp', 'Product', 'Unit', 'Deposit', 'Type',
        'Quantity', 'Operator DNI', 'Operator Name', 'Client Name'
    ])

    # Write data rows
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
        headers={"Content-disposition":
                 "attachment; filename=movement_history.csv"}
    )
