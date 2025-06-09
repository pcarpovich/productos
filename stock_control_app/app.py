import os
from flask import Flask, render_template, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_wtf.csrf import CSRFProtect

# Initialize extensions without app context first
db = SQLAlchemy()
migrate = Migrate()
csrf = CSRFProtect()

def create_app(config_class=None):
    app = Flask(__name__, instance_relative_config=True)

    # Configuration
    # Use environment variable for secret key if available, otherwise use a default
    app.config.from_mapping(
        SECRET_KEY=os.environ.get('SECRET_KEY', 'a_very_temporary_and_insecure_secret_key_dev'),
        # Database URI - default to SQLite in the instance folder parent (project root)
        SQLALCHEMY_DATABASE_URI=os.environ.get('DATABASE_URL', 'sqlite:///../stock_control.db'),
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
        WTF_CSRF_ENABLED=True # Explicitly enable CSRF, though default in recent Flask-WTF
    )

    if config_class:
        app.config.from_object(config_class)

    # Ensure instance folder exists for SQLite db if it's placed there
    # However, our current path 'sqlite:///../stock_control.db' places it outside instance.
    try:
        os.makedirs(app.instance_path, exist_ok=True)
    except OSError:
        pass # Potentially handle error if instance path creation fails

    # Initialize extensions with app context
    db.init_app(app)
    migrate.init_app(app, db)
    csrf.init_app(app) # Initialize CSRF protection

    # Import models here, after db is initialized and associated with app
    from .project import models # Relative import

    # Register Blueprints
    from .project.products.routes import product_bp
    app.register_blueprint(product_bp, url_prefix='/products')

    from .project.deposits.routes import deposit_bp
    app.register_blueprint(deposit_bp, url_prefix='/deposits')

    from .project.operators.routes import operator_bp
    app.register_blueprint(operator_bp, url_prefix='/operators')

    from .project.clients.routes import client_bp
    app.register_blueprint(client_bp, url_prefix='/clients')

    from .project.stock_movements.routes import stock_movement_bp
    app.register_blueprint(stock_movement_bp, url_prefix='/movements')

    from .project.reports.routes import reports_bp
    app.register_blueprint(reports_bp) # url_prefix is in blueprint definition (/reports)


    @app.route('/')
    def home():
        # Links for easy navigation during development / testing
        # These will appear on the home page.
        nav_links = {
            "Products": url_for('products.list_products'),
            "Deposits": url_for('deposits.list_deposits'),
            "Operators": url_for('operators.list_operators'),
            "Clients": url_for('clients.list_clients'),
            "Record Movement": url_for('stock_movements.add_movement'),
            "Movement History": url_for('reports.view_movement_history'),
            "Current Stock Report": url_for('reports.view_current_stock'),
            "Low Stock Alerts": url_for('reports.view_low_stock_alerts'),
            "Client Consumption": url_for('reports.view_client_consumption'),
            "Operator Consumption": url_for('reports.view_operator_consumption'),
        }
        return render_template('home.html', title="Home", nav_links=nav_links)

    return app
