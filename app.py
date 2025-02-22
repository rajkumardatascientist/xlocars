# app.py
from flask import Flask, render_template, url_for, redirect
from flask_login import LoginManager, current_user
from datetime import datetime, timezone
from jinja2 import Environment
import os
import sys  # Import sys

# Import db and migrate from extensions.py
from extensions import db, migrate

# Import all necessary models AFTER creating the app instance
from models import User, Car, InterestedBuyers, Wishlist, Appointment, FeaturedPayments, BuyerPayments, ReportedAds
try:
    from locations import indian_states_districts  # Try this import style
except ImportError as e:
    print(f"ImportError: Could not import indian_states_districts from locations.py.  Please verify the file exists and is in the correct directory. {e}") # ADDED THIS LINE FOR DIAGNOSTICS
    indian_states_districts = {}  # Fallback, so the app doesn't crash during development. REMOVE in production!


app = Flask(__name__)

# Load configurations from config.py
app.config.from_object('config')

# Initialize Extensions
db.init_app(app)
migrate.init_app(app, db)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'auth.login'

from routes import auth_bp, cars_bp, admin_bp, payments_bp, about_bp, dashboard_bp #ADD THIS LINE

app.register_blueprint(auth_bp)
app.register_blueprint(cars_bp)
app.register_blueprint(admin_bp)
app.register_blueprint(payments_bp)
app.register_blueprint(about_bp)
app.register_blueprint(dashboard_bp) #ADD THIS LINE

# Define Indian states (moved here to be accessible globally within the app)
indian_states = ["Andhra Pradesh", "Arunachal Pradesh", "Assam", "Bihar", "Chhattisgarh", "Goa", "Gujarat", "Haryana", "Himachal Pradesh", "Jharkhand", "Karnataka", "Kerala", "Madhya Pradesh", "Maharashtra", "Manipur", "Meghalaya", "Mizoram", "Nagaland", "Odisha", "Punjab", "Rajasthan", "Sikkim", "Tamil Nadu", "Telangana", "Tripura", "Uttar Pradesh", "Uttarakhand", "West Bengal"]

# Load user callback
@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))

# Context Processors to provide access to states and admin status in templates
@app.context_processor
def inject_template_globals():
    return dict(
        indian_states=indian_states,
        current_user=current_user,
        indian_states_districts = indian_states_districts,  # ADD THIS LINE
        datetime=datetime, # ADD THIS LINE
        timezone=timezone
       )

# Define a Jinja2 filter to get the current date and time

# Default Route
@app.route('/')
def index():
    return redirect(url_for('cars.home'))

# Routes that Require indian_states
@app.route('/hello')
def hello():
    return "Hello, World! (from Flask)"

@app.route('/about')
def about():
    return render_template('about.html')

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

# Create database tables within the application context
with app.app_context():
    db.create_all()  # Create the database tables

if __name__ == '__main__':
    app.run(debug=True)