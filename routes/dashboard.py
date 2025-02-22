# create routes/dashboard.py and add below code

from flask import Blueprint, render_template
from flask_login import login_required, current_user
from models import Car, Appointment, Wishlist  # Import your models

dashboard_bp = Blueprint('dashboard', __name__, url_prefix='/dashboard')


@dashboard_bp.route("/buyer")
@login_required
def buyer():
    """Displays the buyer dashboard with relevant information."""
    buying_appointments = Appointment.query.filter_by(buyer_id=current_user.id).all()
    wishlist_items = Wishlist.query.filter_by(user_id=current_user.id).all()
    return render_template('buyer_dashboard.html', buying_appointments=buying_appointments, wishlist_items=wishlist_items)


@dashboard_bp.route("/seller")
@login_required
def seller():
    """Displays the seller dashboard with relevant information."""
    selling_appointments = Appointment.query.filter_by(seller_id=current_user.id).all()
    cars = Car.query.filter_by(seller_id=current_user.id).all()
    return render_template('seller_dashboard.html', selling_appointments=selling_appointments, cars=cars)