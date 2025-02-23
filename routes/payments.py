from flask import Blueprint, render_template, redirect, url_for, flash
from flask_login import current_user, login_required
from app import db
from models.payment import BuyerPayments, FeaturedPayments, PaymentStatus  # ✅ Import ENUM
from models.car import Car
from datetime import datetime  # ✅ Import datetime

payments_bp = Blueprint('payments', __name__, url_prefix='/payments')

@payments_bp.route("/unlock_contact/<int:car_id>")
@login_required
def unlock_contact_request(car_id):
    car = Car.query.get_or_404(car_id)

    # ✅ Check if payment record already exists
    existing_payment = BuyerPayments.query.filter_by(
        buyer_id=current_user.id, car_id=car_id
    ).first()

    if existing_payment:
        flash("You have already requested to unlock contact info. Please wait for admin approval.", "info")
        return redirect(url_for("cars.car", car_id=car_id))

    # ✅ Create a new BuyerPayments record with correct ENUM usage
    new_payment = BuyerPayments(
        buyer_id=current_user.id,
        seller_id=car.seller_id,
        car_id=car_id,
        payment_date=datetime.utcnow(),
        payment_status=PaymentStatus.PENDING_PAYMENT,  # ✅ Use ENUM instead of False
        is_contact_unlocked=False
    )
    db.session.add(new_payment)
    db.session.commit()

    flash("Contact unlock payment requested. Admin will verify and approve it.", "info")
    return redirect(url_for("cars.car", car_id=car_id))

@payments_bp.route("/request_feature/<int:car_id>")
@login_required
def request_feature_payment(car_id):
    car = Car.query.get_or_404(car_id)

    # ✅ Check if payment record already exists
    existing_payment = FeaturedPayments.query.filter_by(
        seller_id=current_user.id, car_id=car_id
    ).first()

    if existing_payment:
        flash("You have already requested to feature this car. Please wait for admin approval.", "info")
        return redirect(url_for("cars.car", car_id=car_id))

    # ✅ Create a new FeaturedPayments record with correct ENUM usage
    new_payment = FeaturedPayments(
        seller_id=current_user.id,
        car_id=car_id,
        payment_date=datetime.utcnow(),
        payment_status=PaymentStatus.PENDING_PAYMENT,  # ✅ Use ENUM instead of False
        is_featured=False
    )
    db.session.add(new_payment)
    db.session.commit()

    flash("Request to feature this car has been submitted. Admin will verify and approve it.", "info")
    return redirect(url_for("cars.car", car_id=car_id))
