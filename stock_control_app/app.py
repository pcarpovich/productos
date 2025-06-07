from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

# Initialize extensions without app context first
db = SQLAlchemy()
migrate = Migrate()

def create_app():
    app = Flask(__name__)
    # ../ goes one level up from 'instance' folder if it exists, or from app.py location.
    # To ensure it's always relative to the app's root (stock_control_app),
    # we might need to adjust this if app is run from outside its directory.
    # For now, assuming app is run from stock_control_app directory or instance folder is not used.
    app.config['SECRET_KEY'] = 'a_temporary_secret_key_for_development' # Added secret key
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////home/pcarpovich/productos/stock_control.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # Initialize extensions with app context
    db.init_app(app)
    migrate.init_app(app, db)

    # Import models here, after db is initialized and associated with app
    # This ensures models can correctly inherit from db.Model
    # Also, ensure this import path is correct based on your project structure
    from stock_control_app.project import models

    # Register Blueprints
    from stock_control_app.project.products.routes import product_bp
    app.register_blueprint(product_bp, url_prefix='/products')

    from stock_control_app.project.deposits.routes import deposit_bp
    app.register_blueprint(deposit_bp, url_prefix='/deposits')

    from stock_control_app.project.operators.routes import operator_bp
    app.register_blueprint(operator_bp, url_prefix='/operators')

    from stock_control_app.project.clients.routes import client_bp
    app.register_blueprint(client_bp, url_prefix='/clients')

    from stock_control_app.project.stock_movements.routes import stock_movement_bp
    app.register_blueprint(stock_movement_bp, url_prefix='/movements')

    @app.route('/')
    def hello_world():
        return 'Hello, World! <a href="/products/">View Products</a> | <a href="/deposits/">View Deposits</a> | <a href="/operators/">View Operators</a> | <a href="/clients/">View Clients</a> | <a href="/movements/add">Record Movement</a>' # Added a link for easy testing

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)
