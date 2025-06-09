from flask import Blueprint, render_template, request, flash, redirect, url_for
from sqlalchemy.exc import IntegrityError
from stock_control_app.app import db # Relative import for db
from ..models import StockMovement, Product, Deposit, Operator, Client # Relative import for models
from .forms import StockMovementForm # Relative import for forms
from datetime import datetime

stock_movement_bp = Blueprint('stock_movements',
                              __name__,
                              template_folder='templates')

@stock_movement_bp.route('/add', methods=['GET', 'POST'])
def add_movement():
    form = StockMovementForm(request.form if request.method == 'POST' else None)

    if form.validate_on_submit():
        product = form.product_id.data
        deposit = form.deposit_id.data
        movement_type = form.type.data
        quantity = form.quantity.data
        operator = form.operator_id.data
        client = form.client_id.data
        # Ensure timestamp from form is used, or default to now if not provided/empty
        timestamp_data = form.timestamp.data
        if timestamp_data is None: # Check if DateTimeLocalField was empty
            timestamp_to_save = datetime.utcnow()
        else:
            timestamp_to_save = timestamp_data

        new_movement = StockMovement(
            product_id=product.id,
            deposit_id=deposit.id,
            type=movement_type,
            quantity=quantity,
            operator_id=operator.id if operator else None,
            client_id=client.id if client else None,
            timestamp=timestamp_to_save
        )

        db.session.add(new_movement)
        try:
            db.session.commit() # This will trigger the SQLAlchemy event to update StockLevel
            flash(f'Stock movement of {quantity} x "{product.name}" for "{deposit.name}" as "{movement_type}" recorded successfully.', 'success')
            # Redirect to a new form to allow multiple entries, or to a list page if one exists
            return redirect(url_for('stock_movements.add_movement'))
        except IntegrityError as e:
            db.session.rollback()
            flash(f'Error recording stock movement: Database integrity error. {str(e)}', 'danger')
        except Exception as e:
            db.session.rollback()
            flash(f'An unexpected error occurred: {str(e)}', 'danger')

    return render_template('stock_movement_form.html', form=form, title="Record New Stock Movement", legend="Record New Stock Movement")
