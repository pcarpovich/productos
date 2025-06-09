from flask import Blueprint, render_template, request, flash, redirect, url_for
from sqlalchemy.exc import IntegrityError
from stock_control_app.app import db # Relative import for db
from ..models import Deposit, StockMovement # Relative import for models
from .forms import DepositForm # Relative import for forms

deposit_bp = Blueprint('deposits',
                       __name__,
                       template_folder='templates')

@deposit_bp.route('/')
def list_deposits():
    deposits = Deposit.query.order_by(Deposit.name).all()
    return render_template('deposits_list.html', deposits=deposits, title="Deposits")

@deposit_bp.route('/add', methods=['GET', 'POST'])
def add_deposit():
    form = DepositForm()
    if form.validate_on_submit():
        new_deposit = Deposit(name=form.name.data)
        db.session.add(new_deposit)
        try:
            db.session.commit()
            flash(f'Deposit "{new_deposit.name}" has been successfully added.', 'success')
            return redirect(url_for('deposits.list_deposits'))
        except IntegrityError as e:
            db.session.rollback()
            if "deposit.name" in str(e.orig).lower():
                 form.name.errors.append("This deposit name already exists.")
            else:
                flash(f"Error adding deposit: Database integrity error. {str(e)}", 'danger')
        except Exception as e:
            db.session.rollback()
            flash(f"An unexpected error occurred: {str(e)}", 'danger')

    return render_template('deposit_form.html', form=form, title="Add New Deposit", legend="Add New Deposit")

@deposit_bp.route('/edit/<int:deposit_id>', methods=['GET', 'POST'])
def edit_deposit(deposit_id):
    deposit = Deposit.query.get_or_404(deposit_id)
    form = DepositForm(obj=deposit) # Pass deposit object for pre-population and validation context

    if form.validate_on_submit():
        deposit.name = form.name.data
        try:
            db.session.commit()
            flash(f'Deposit "{deposit.name}" has been successfully updated.', 'success')
            return redirect(url_for('deposits.list_deposits'))
        except IntegrityError as e:
            db.session.rollback()
            if "deposit.name" in str(e.orig).lower():
                 form.name.errors.append("This deposit name already exists.")
            else:
                flash(f"Error updating deposit: Database integrity error. {str(e)}", 'danger')
        except Exception as e:
            db.session.rollback()
            flash(f"An unexpected error occurred: {str(e)}", 'danger')

    return render_template('deposit_form.html', form=form, title=f"Edit Deposit: {deposit.name}", legend=f"Edit Deposit: {deposit.name}", deposit=deposit)

@deposit_bp.route('/delete/<int:deposit_id>', methods=['POST'])
def delete_deposit(deposit_id):
    deposit = Deposit.query.get_or_404(deposit_id)
    deposit_name = deposit.name

    if StockMovement.query.filter_by(deposit_id=deposit.id).first():
        flash(f'Deposit "{deposit_name}" cannot be deleted because it has associated stock movements. Please remove or reassign these movements first.', 'danger')
        return redirect(url_for('deposits.list_deposits'))

    db.session.delete(deposit)
    try:
        db.session.commit()
        flash(f'Deposit "{deposit_name}" has been successfully deleted.', 'success')
    except IntegrityError as e:
        db.session.rollback()
        flash(f"Error deleting deposit: Database integrity error. {str(e)}", 'danger')
    except Exception as e:
        db.session.rollback()
        flash(f"An unexpected error occurred: {str(e)}", 'danger')

    return redirect(url_for('deposits.list_deposits'))
