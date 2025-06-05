from flask import Blueprint, render_template, request, flash, redirect, url_for
from stock_control_app.project.models import Product
from stock_control_app.project.products.forms import ProductForm
from stock_control_app.app import db

product_bp = Blueprint('products',
                       __name__,
                       template_folder='templates',
                       static_folder='static', # Though likely not used for this blueprint
                       static_url_path='/project/products/static') # If static assets were specific to this blueprint

@product_bp.route('/')
def list_products():
    products = Product.query.all()
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
        db.session.commit()
        flash(f'Product "{new_product.name}" has been successfully added.', 'success')
        return redirect(url_for('products.list_products'))
    return render_template('product_form.html', form=form, title="Add New Product", legend="Add New Product")

@product_bp.route('/edit/<int:product_id>', methods=['GET', 'POST'])
def edit_product(product_id):
    product = Product.query.get_or_404(product_id)
    form = ProductForm(obj=product) # Pre-populate form with product data on GET

    if form.validate_on_submit():
        product.name = form.name.data
        product.unit_of_measure = form.unit_of_measure.data
        product.category = form.category.data
        product.minimum_stock = form.minimum_stock.data
        db.session.commit()
        flash(f'Product "{product.name}" has been successfully updated.', 'success')
        return redirect(url_for('products.list_products'))

    # For GET request or if form validation fails on POST
    return render_template('product_form.html', form=form, title=f"Edit Product: {product.name}", legend=f"Edit Product: {product.name}", product=product)

@product_bp.route('/delete/<int:product_id>', methods=['POST'])
def delete_product(product_id):
    product = Product.query.get_or_404(product_id)
    product_name = product.name # Store name for flash message before deleting
    db.session.delete(product)
    db.session.commit()
    flash(f'Product "{product_name}" has been successfully deleted.', 'success')
    return redirect(url_for('products.list_products'))
