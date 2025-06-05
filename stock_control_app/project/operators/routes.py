from flask import Blueprint, render_template, request, flash, redirect, url_for
from stock_control_app.project.models import Operator
from stock_control_app.project.operators.forms import OperatorForm
from stock_control_app.app import db

operator_bp = Blueprint('operators',
                        __name__,
                        template_folder='templates')

@operator_bp.route('/')
def list_operators():
    operators = Operator.query.all()
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
        except Exception as e: # Catching potential integrity errors if DB constraint is hit before form validation
            db.session.rollback()
            if 'UNIQUE constraint failed: operator.dni' in str(e).lower():
                form.dni.errors.append('This DNI is already registered in the database.')
            else:
                flash('Error saving operator: ' + str(e), 'danger')
    return render_template('operator_form.html', form=form, title="Add New Operator", legend="Add New Operator")

@operator_bp.route('/edit/<int:operator_id>', methods=['GET', 'POST'])
def edit_operator(operator_id):
    operator = Operator.query.get_or_404(operator_id)
    form = OperatorForm(obj=operator) # Pre-populate form, passing 'obj' for uniqueness validator

    if request.method == 'POST': # Ensure _obj is set for POST validation
        form._obj = operator

    if form.validate_on_submit():
        operator.name = form.name.data
        operator.dni = form.dni.data
        try:
            db.session.commit()
            flash(f'Operator "{operator.name}" has been successfully updated.', 'success')
            return redirect(url_for('operators.list_operators'))
        except Exception as e:
            db.session.rollback()
            if 'UNIQUE constraint failed: operator.dni' in str(e).lower():
                form.dni.errors.append('This DNI is already registered in the database.')
            else:
                flash('Error updating operator: ' + str(e), 'danger')

    return render_template('operator_form.html', form=form, title=f"Edit Operator: {operator.name}", legend=f"Edit Operator: {operator.name}", operator=operator)

@operator_bp.route('/delete/<int:operator_id>', methods=['POST'])
def delete_operator(operator_id):
    operator = Operator.query.get_or_404(operator_id)
    operator_name = operator.name
    db.session.delete(operator)
    db.session.commit()
    flash(f'Operator "{operator_name}" has been successfully deleted.', 'success')
    return redirect(url_for('operators.list_operators'))
