from flask import Blueprint, render_template, request, flash, redirect, url_for
from sqlalchemy.exc import IntegrityError
from stock_control_app.app import db # Relative import for db
from ..models import Operator, StockMovement # Relative import for models
from .forms import OperatorForm # Relative import for forms

operator_bp = Blueprint('operators',
                        __name__,
                        template_folder='templates')

@operator_bp.route('/')
def list_operators():
    operators = Operator.query.order_by(Operator.name).all()
    return render_template('operators_list.html', operators=operators, title="Operators")

@operator_bp.route('/add', methods=['GET', 'POST'])
def add_operator():
    form = OperatorForm()
    if form.validate_on_submit():
        new_operator = Operator(name=form.name.data, dni=form.dni.data)
        db.session.add(new_operator)
        try:
            db.session.commit()
            flash(f'Operator "{new_operator.name}" has been successfully added.', 'success')
            return redirect(url_for('operators.list_operators'))
        except IntegrityError as e:
            db.session.rollback()
            if "operator.dni" in str(e.orig).lower():
                 form.dni.errors.append("This DNI already exists in the database.")
            else:
                flash(f"Error adding operator: Database integrity error. {str(e)}", 'danger')
        except Exception as e:
            db.session.rollback()
            flash(f"An unexpected error occurred: {str(e)}", 'danger')

    return render_template('operator_form.html', form=form, title="Add New Operator", legend="Add New Operator")

@operator_bp.route('/edit/<int:operator_id>', methods=['GET', 'POST'])
def edit_operator(operator_id):
    operator = Operator.query.get_or_404(operator_id)
    form = OperatorForm(obj=operator) # Pass operator object for pre-population and validation context

    if form.validate_on_submit():
        operator.name = form.name.data
        operator.dni = form.dni.data
        try:
            db.session.commit()
            flash(f'Operator "{operator.name}" has been successfully updated.', 'success')
            return redirect(url_for('operators.list_operators'))
        except IntegrityError as e:
            db.session.rollback()
            if "operator.dni" in str(e.orig).lower():
                 form.dni.errors.append("This DNI already exists in the database.")
            else:
                flash(f"Error updating operator: Database integrity error. {str(e)}", 'danger')
        except Exception as e:
            db.session.rollback()
            flash(f"An unexpected error occurred: {str(e)}", 'danger')

    return render_template('operator_form.html', form=form, title=f"Edit Operator: {operator.name}", legend=f"Edit Operator: {operator.name}", operator=operator)

@operator_bp.route('/delete/<int:operator_id>', methods=['POST'])
def delete_operator(operator_id):
    operator = Operator.query.get_or_404(operator_id)
    operator_name = operator.name

    if StockMovement.query.filter_by(operator_id=operator.id).first():
        flash(f'Operator "{operator_name}" cannot be deleted because they have associated stock movements. Please remove or reassign these movements first.', 'danger')
        return redirect(url_for('operators.list_operators'))

    db.session.delete(operator)
    try:
        db.session.commit()
        flash(f'Operator "{operator_name}" has been successfully deleted.', 'success')
    except IntegrityError as e:
        db.session.rollback()
        flash(f"Error deleting operator: Database integrity error. {str(e)}", 'danger')
    except Exception as e:
        db.session.rollback()
        flash(f"An unexpected error occurred: {str(e)}", 'danger')

    return redirect(url_for('operators.list_operators'))
