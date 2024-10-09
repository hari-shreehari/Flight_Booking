# app/__init__.py
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

# Create the SQLAlchemy instance
db = SQLAlchemy()

# Function to create the Flask app
def create_app():
    app = Flask(__name__)
    
    # Set up the secret key for the app
    app.config['SECRET_KEY'] = 'Voldemart'
    
    # Set up the database URI (SQLite in this example)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///flight_booking.db'
    
    # Initialize the app with SQLAlchemy
    db.init_app(app)
    
    return app

# Create the app instance
app = create_app()

