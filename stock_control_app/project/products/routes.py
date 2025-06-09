from flask import Blueprint, render_template, request, flash, redirect, url_for
from sqlalchemy.exc import IntegrityError
from stock_control_app.app import db  # Corrected relative import for db
from ..models import Product, StockMovement  # Corrected relative import for models
from .forms import ProductForm # Corrected relative import for forms

product_bp = Blueprint('products',
                       __name__,
                       template_folder='templates')
                       # static_folder='static', # Not typically needed for blueprint specific static files here
                       # static_url_path='/project/products/static')

@product_bp.route('/')
def list_products():
    products = Product.query.order_by(Product.name).all()
    return render_template('products_list.html', products=products, title="Products")

@product_bp.route('/add', methods=['GET', 'POST'])
def add_product():
    form = ProductForm()
    if form.validate_on_submit():
        new_product = Product(
            name=form.name.data,
            unit_of_measure=form.unit_of_measure.data,
            category=form.category.data,
            minimum_stock=form.minimum_stock.data
        )
        db.session.add(new_product)
        try:
            db.session.commit()
            flash(f'Product "{new_product.name}" has been successfully added.', 'success')
            return redirect(url_for('products.list_products'))
        except IntegrityError as e:
            db.session.rollback()
            if "product.name" in str(e.orig).lower(): # Check if error is due to name uniqueness
                 form.name.errors.append("This product name already exists. Please choose a different name.")
            else:
                flash(f"Error adding product: Database integrity error. {str(e)}", 'danger')
        except Exception as e:
            db.session.rollback()
            flash(f"An unexpected error occurred: {str(e)}", 'danger')

    return render_template('product_form.html', form=form, title="Add New Product", legend="Add New Product")

@product_bp.route('/edit/<int:product_id>', methods=['GET', 'POST'])
def edit_product(product_id):
    product = Product.query.get_or_404(product_id)
    form = ProductForm(obj=product) # Pass product object to pre-populate and for validation context

    if form.validate_on_submit():
        product.name = form.name.data
        product.unit_of_measure = form.unit_of_measure.data
        product.category = form.category.data
        product.minimum_stock = form.minimum_stock.data
        try:
            db.session.commit()
            flash(f'Product "{product.name}" has been successfully updated.', 'success')
            return redirect(url_for('products.list_products'))
        except IntegrityError as e:
            db.session.rollback()
            if "product.name" in str(e.orig).lower():
                 form.name.errors.append("This product name already exists. Please choose a different name.")
            else:
                flash(f"Error updating product: Database integrity error. {str(e)}", 'danger')
        except Exception as e:
            db.session.rollback()
            flash(f"An unexpected error occurred: {str(e)}", 'danger')

    return render_template('product_form.html', form=form, title=f"Edit Product: {product.name}", legend=f"Edit Product: {product.name}", product=product)

@product_bp.route('/delete/<int:product_id>', methods=['POST'])
def delete_product(product_id):
    product = Product.query.get_or_404(product_id)
    product_name = product.name

    # Check for related StockMovements or StockLevels before deleting
    if StockMovement.query.filter_by(product_id=product.id).first():
        flash(f'Product "{product_name}" cannot be deleted because it has associated stock movements. Please remove or reassign these movements first.', 'danger')
        return redirect(url_for('products.list_products'))
    # Add similar check for StockLevel if direct deletion of product should be prevented if stock levels exist
    # if StockLevel.query.filter_by(product_id=product.id).first():
    #     flash(f'Product "{product_name}" cannot be deleted because it has existing stock level records.', 'danger')
    #     return redirect(url_for('products.list_products'))

    db.session.delete(product)
    try:
        db.session.commit()
        flash(f'Product "{product_name}" has been successfully deleted.', 'success')
    except IntegrityError as e: # Should be rare if checks above are comprehensive
        db.session.rollback()
        flash(f"Error deleting product: Database integrity error. {str(e)}", 'danger')
    except Exception as e:
        db.session.rollback()
        flash(f"An unexpected error occurred: {str(e)}", 'danger')

    return redirect(url_for('products.list_products'))
