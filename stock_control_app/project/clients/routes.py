from flask import Blueprint, render_template, request, flash, redirect, url_for
from sqlalchemy.exc import IntegrityError
from stock_control_app.app import db # Relative import for db
from ..models import Client, StockMovement # Relative import for models
from .forms import ClientForm # Relative import for forms

client_bp = Blueprint('clients',
                      __name__,
                      template_folder='templates')

@client_bp.route('/')
def list_clients():
    clients = Client.query.order_by(Client.name).all()
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
        except IntegrityError: # Assuming client name might need to be unique based on model, though not specified
            db.session.rollback()
            form.name.errors.append("This client name might already exist or another integrity issue occurred.")
        except Exception as e:
            db.session.rollback()
            flash(f"An unexpected error occurred: {str(e)}", 'danger')

    return render_template('client_form.html', form=form, title="Add New Client", legend="Add New Client")

@client_bp.route('/edit/<int:client_id>', methods=['GET', 'POST'])
def edit_client(client_id):
    client = Client.query.get_or_404(client_id)
    form = ClientForm(obj=client) # Pass client object for pre-population

    if form.validate_on_submit():
        client.name = form.name.data
        client.address = form.address.data
        client.locality = form.locality.data
        try:
            db.session.commit()
            flash(f'Client "{client.name}" has been successfully updated.', 'success')
            return redirect(url_for('clients.list_clients'))
        except IntegrityError:
            db.session.rollback()
            form.name.errors.append("This client name might already exist or another integrity issue occurred.")
        except Exception as e:
            db.session.rollback()
            flash(f"An unexpected error occurred: {str(e)}", 'danger')

    return render_template('client_form.html', form=form, title=f"Edit Client: {client.name}", legend=f"Edit Client: {client.name}", client=client)

@client_bp.route('/delete/<int:client_id>', methods=['POST'])
def delete_client(client_id):
    client = Client.query.get_or_404(client_id)
    client_name = client.name

    if client.stock_movements.first(): # Efficiently check if any related movements exist
        flash(f'Client "{client_name}" cannot be deleted because they have associated stock movements. Please remove or reassign these movements first.', 'danger')
        return redirect(url_for('clients.list_clients'))

    db.session.delete(client)
    try:
        db.session.commit()
        flash(f'Client "{client_name}" has been successfully deleted.', 'success')
    except IntegrityError as e: # Should be rare if checks above are comprehensive
        db.session.rollback()
        flash(f"Error deleting client: Database integrity error. {str(e)}", 'danger')
    except Exception as e:
        db.session.rollback()
        flash(f"An unexpected error occurred: {str(e)}", 'danger')

    return redirect(url_for('clients.list_clients'))
