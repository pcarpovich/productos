from flask import Blueprint, render_template, request, flash, redirect, url_for
from stock_control_app.project.models import Deposit
from stock_control_app.project.deposits.forms import DepositForm
from stock_control_app.app import db

deposit_bp = Blueprint('deposits',
                       __name__,
                       template_folder='templates')

@deposit_bp.route('/')
def list_deposits():
    deposits = Deposit.query.all()
    return render_template('deposits_list.html', deposits=deposits, title="Deposits")

@deposit_bp.route('/add', methods=['GET', 'POST'])
def add_deposit():
    form = DepositForm()
    if form.validate_on_submit():
        new_deposit = Deposit(name=form.name.data)
        db.session.add(new_deposit)
        db.session.commit()
        flash(f'Deposit "{new_deposit.name}" has been successfully added.', 'success')
        return redirect(url_for('deposits.list_deposits'))
    return render_template('deposit_form.html', form=form, title="Add New Deposit", legend="Add New Deposit")

@deposit_bp.route('/edit/<int:deposit_id>', methods=['GET', 'POST'])
def edit_deposit(deposit_id):
    deposit = Deposit.query.get_or_404(deposit_id)
    form = DepositForm(obj=deposit) # Pre-populate form

    if form.validate_on_submit():
        deposit.name = form.name.data
        db.session.commit()
        flash(f'Deposit "{deposit.name}" has been successfully updated.', 'success')
        return redirect(url_for('deposits.list_deposits'))

    return render_template('deposit_form.html', form=form, title=f"Edit Deposit: {deposit.name}", legend=f"Edit Deposit: {deposit.name}", deposit=deposit)

@deposit_bp.route('/delete/<int:deposit_id>', methods=['POST'])
def delete_deposit(deposit_id):
    deposit = Deposit.query.get_or_404(deposit_id)
    deposit_name = deposit.name
    db.session.delete(deposit)
    db.session.commit()
    flash(f'Deposit "{deposit_name}" has been successfully deleted.', 'success')
    return redirect(url_for('deposits.list_deposits'))
