from flask import Blueprint, render_template, request, flash, redirect, url_for
from stock_control_app.project.models import Client
from stock_control_app.project.clients.forms import ClientForm
from stock_control_app.app import db

client_bp = Blueprint('clients',
                      __name__,
                      template_folder='templates')

@client_bp.route('/')
def list_clients():
    clients = Client.query.order_by(Client.name).all() # Ordered by name
    return render_template('clients_list.html', clients=clients, title="Clients")

@client_bp.route('/add', methods=['GET', 'POST'])
def add_client():
    form = ClientForm()
    if form.validate_on_submit():
        new_client = Client(
            name=form.name.data,
            address=form.address.data,
            locality=form.locality.data
        )
        db.session.add(new_client)
        try:
            db.session.commit()
            flash(f'Client "{new_client.name}" has been successfully added.', 'success')
            return redirect(url_for('clients.list_clients'))
        except Exception as e:
            db.session.rollback()
            # A more specific error check could be added if there are unique constraints on Client model
            flash(f'Error saving client: {str(e)}', 'danger')

    return render_template('client_form.html', form=form, title="Add New Client", legend="Add New Client")

@client_bp.route('/edit/<int:client_id>', methods=['GET', 'POST'])
def edit_client(client_id):
    client = Client.query.get_or_404(client_id)
    form = ClientForm(obj=client) # Pre-populate form

    if form.validate_on_submit():
        client.name = form.name.data
        client.address = form.address.data
        client.locality = form.locality.data
        try:
            db.session.commit()
            flash(f'Client "{client.name}" has been successfully updated.', 'success')
            return redirect(url_for('clients.list_clients'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error updating client: {str(e)}', 'danger')

    return render_template('client_form.html', form=form, title=f"Edit Client: {client.name}", legend=f"Edit Client: {client.name}", client=client)

@client_bp.route('/delete/<int:client_id>', methods=['POST'])
def delete_client(client_id):
    client = Client.query.get_or_404(client_id)
    client_name = client.name

    # Check for related StockMovements before deleting
    if client.stock_movements:
        flash(f'Client "{client_name}" cannot be deleted because they have associated stock movements. Please remove or reassign these movements first.', 'danger')
        return redirect(url_for('clients.list_clients'))

    db.session.delete(client)
    try:
        db.session.commit()
        flash(f'Client "{client_name}" has been successfully deleted.', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error deleting client: {str(e)}', 'danger')

    return redirect(url_for('clients.list_clients'))
