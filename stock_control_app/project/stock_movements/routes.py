from flask import Blueprint, render_template, request, flash, redirect, url_for
from stock_control_app.project.models import StockMovement, Product, Deposit, Operator, Client
from stock_control_app.project.stock_movements.forms import StockMovementForm
from stock_control_app.app import db
from datetime import datetime

stock_movement_bp = Blueprint('stock_movements',
                              __name__,
                              template_folder='templates')

@stock_movement_bp.route('/add', methods=['GET', 'POST'])
def add_movement():
    form = StockMovementForm(request.form if request.method == 'POST' else None)

    if form.validate_on_submit():
        # Extract data from form
        product = form.product_id.data
        deposit = form.deposit_id.data
        movement_type = form.type.data
        quantity = form.quantity.data
        operator = form.operator_id.data
        client = form.client_id.data
        timestamp = form.timestamp.data or datetime.utcnow() # Use provided or default to now

        # Create new StockMovement object
        new_movement = StockMovement(
            product_id=product.id,
            deposit_id=deposit.id,
            type=movement_type,
            quantity=quantity, # The actual quantity, directionality handled by type
            operator_id=operator.id if operator else None,
            client_id=client.id if client else None,
            timestamp=timestamp
        )

        # Logic to update StockLevel will be handled by a listener or a subsequent subtask.
        # For now, just save the movement.

        db.session.add(new_movement)
        try:
            db.session.commit()
            flash(f'Stock movement of {quantity} x "{product.name}" for "{deposit.name}" as "{movement_type}" recorded successfully.', 'success')
            return redirect(url_for('stock_movements.add_movement')) # Redirect back to the form
        except Exception as e:
            db.session.rollback()
            flash(f'Error recording stock movement: {str(e)}', 'danger')

    return render_template('stock_movement_form.html', form=form, title="Record New Stock Movement", legend="Record New Stock Movement")
