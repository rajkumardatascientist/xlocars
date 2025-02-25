# routes/admin.py
from flask import Blueprint, render_template, redirect, url_for, flash, request
from models import Car, FeaturedPayments, BuyerPayments, User, Appointment, ReportedAds
from app import db
from flask_login import login_required, current_user
from sqlalchemy import or_
from forms import ReportForm
from models.payment import PaymentStatus
from forms.user_forms import EditUserForm

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')


@admin_bp.route("/dashboard")
@login_required
def dashboard():
    if not current_user.is_admin:
        flash("You don't have permission to access this page.", "danger")
        return redirect(url_for('cars.home'))

    pending_cars = Car.query.filter_by(is_approved=False).all()
    cars = Car.query.all()

    featured_payments = FeaturedPayments.query.filter(FeaturedPayments.payment_status.in_(
        [PaymentStatus.PENDING_PAYMENT, PaymentStatus.PAYMENT_FAILED, PaymentStatus.PAYMENT_REFUNDED])).all()

    buyer_payments = BuyerPayments.query.filter(BuyerPayments.payment_status.in_(
        [PaymentStatus.PENDING_PAYMENT, PaymentStatus.PAYMENT_FAILED, PaymentStatus.PAYMENT_REFUNDED])).all()

    appointments = Appointment.query.filter(Appointment.status == "pending").all()
    reports = ReportedAds.query.all()
    return render_template('admin_dashboard.html', pending_cars=pending_cars, cars=cars, featured_payments=featured_payments,
                           buyer_payments=buyer_payments, appointments=appointments, reports=reports)


@admin_bp.route("/approve_car/<int:car_id>")
@login_required
def approve_car(car_id):
    if not current_user.is_admin:
        flash("You don't have permission to access this page.", "danger")
        return redirect(url_for('cars.home'))
    car = Car.query.get_or_404(car_id)
    car.is_approved = True
    db.session.commit()
    flash(f"Car '{car.title}' approved!", 'success')
    return redirect(url_for('admin.dashboard'))


@admin_bp.route("/reject_car/<int:car_id>")
@login_required
def reject_car(car_id):
    if not current_user.is_admin:
        flash("You don't have permission to access this page.", "danger")
        return redirect(url_for('cars.home'))
    car = Car.query.get_or_404(car_id)
    db.session.delete(car)
    try:
        db.session.commit()
        flash(f"Car '{car.title}' rejected and deleted.", 'success')
    except Exception as e:
        db.session.rollback()
        flash(f"Error deleting car: {e}", "danger")
        return redirect(url_for('admin.dashboard'))

    return redirect(url_for('admin.dashboard'))


@admin_bp.route("/activate_feature_payment/<int:payment_id>")
@login_required
def activate_feature_payment(payment_id):
    if not current_user.is_admin:
        flash("You don't have permission to access this page.", "danger")
        return redirect(url_for('cars.home'))
    payment = FeaturedPayments.query.get_or_404(payment_id)
    payment.payment_status = PaymentStatus.PAYMENT_SUCCESSFUL
    payment.is_featured = True
    car = Car.query.get_or_404(payment.car_id)
    car.is_featured = True
    db.session.commit()
    flash(f"Featured Payment ID '{payment.id}' activated!", 'success')
    return redirect(url_for('admin.dashboard'))


@admin_bp.route("/activate_buyer_payment/<int:payment_id>")
@login_required
def activate_buyer_payment(payment_id):
    if not current_user.is_admin:
        flash("You don't have permission to access this page.", "danger")
        return redirect(url_for('cars.home'))
    payment = BuyerPayments.query.get_or_404(payment_id)
    payment.payment_status = PaymentStatus.PAYMENT_SUCCESSFUL
    payment.is_contact_unlocked = True
    db.session.commit()
    flash(f"Buyer Payment ID '{payment.id}' activated!", 'success')
    return redirect(url_for('admin.dashboard'))


@admin_bp.route("/deactivate_feature_payment/<int:payment_id>")
@login_required
def deactivate_feature_payment(payment_id):
    if not current_user.is_admin:
        flash("You don't have permission to access this page.", "danger")
        return redirect(url_for('cars.home'))
    payment = FeaturedPayments.query.get_or_404(payment_id)
    payment.payment_status = PaymentStatus.PAYMENT_FAILED
    payment.is_featured = False
    car = Car.query.get_or_404(payment.car_id)
    car.is_featured = False
    db.session.commit()
    flash(f"Featured Payment ID '{payment.id}' deactivated!", 'success')
    return redirect(url_for('admin.dashboard'))


@admin_bp.route("/deactivate_buyer_payment/<int:payment_id>")
@login_required
def deactivate_buyer_payment(payment_id):
    if not current_user.is_admin:
        flash("You don't have permission to access this page.", "danger")
        return redirect(url_for('cars.home'))
    payment = BuyerPayments.query.get_or_404(payment_id)
    payment.payment_status = PaymentStatus.PAYMENT_FAILED
    payment.is_contact_unlocked = False
    db.session.commit()
    flash(f"Buyer Payment ID '{payment.id}' deactivated!", 'success')
    return redirect(url_for('admin.dashboard'))


@admin_bp.route("/approve_appointment/<int:appointment_id>")
@login_required
def approve_appointment(appointment_id):
    if not current_user.is_admin:
        flash("You don't have permission to access this page.", "danger")
        return redirect(url_for('cars.home'))
    appointment = Appointment.query.get_or_404(appointment_id)
    appointment.status = "Confirmed"
    db.session.commit()
    flash(f"Appointment ID '{appointment.id}' approved!", 'success')
    return redirect(url_for('admin.dashboard'))


@admin_bp.route("/reject_appointment/<int:appointment_id>")
@login_required
def reject_appointment(appointment_id):
    if not current_user.is_admin:
        flash("You don't have permission to access this page.", "danger")
        return redirect(url_for('cars.home'))
    appointment = Appointment.query.get_or_404(appointment_id)
    appointment.status = "Rejected"
    db.session.commit()
    flash(f"Appointment ID '{appointment.id}' Rejected!", 'success')
    return redirect(url_for('admin.dashboard'))


@admin_bp.route("/search", methods=['GET'])
@login_required
def search():
    if not current_user.is_admin:
        flash("You don't have permission to access this page.", "danger")
        return redirect(url_for('cars.home'))

    search_query = request.args.get('query')
    results = {'users': [], 'cars': []}

    if search_query:
        results['users'] = User.query.filter(
            or_(User.username.ilike(f'%{search_query}%'),
                User.email.ilike(f'%{search_query}%'))
        ).all()

        results['cars'] = Car.query.filter(
            or_(Car.title.ilike(f'%{search_query}%'),
                Car.model.ilike(f'%{search_query}%'),
                Car.registration_number.ilike(f'%{search_query}%'))
        ).all()

    return render_template('admin_dashboard.html',
                           pending_cars=Car.query.filter_by(is_approved=False).all(),
                           cars=Car.query.all(),
                           featured_payments=FeaturedPayments.query.filter(FeaturedPayments.payment_status.in_(
                               [PaymentStatus.PENDING_PAYMENT, PaymentStatus.PAYMENT_FAILED,
                                PaymentStatus.PAYMENT_REFUNDED])).all(),
                           buyer_payments=BuyerPayments.query.filter(BuyerPayments.payment_status.in_(
                               [PaymentStatus.PENDING_PAYMENT, PaymentStatus.PAYMENT_FAILED,
                                PaymentStatus.PAYMENT_REFUNDED])).all(),
                           appointments=Appointment.query.filter(Appointment.status == "pending").all(),
                           results=results,
                           search_query=search_query, reports=ReportedAds.query.all())


# User Management
@admin_bp.route("/users")
@login_required
def list_users():
    if not current_user.is_admin:
        flash("You don't have permission to access this page.", "danger")
        return redirect(url_for('cars.home'))

    users = User.query.all()
    return render_template('admin/list_users.html', users=users)


@admin_bp.route("/users/edit/<int:user_id>", methods=['GET', 'POST'])
@login_required
def edit_user(user_id):
    if not current_user.is_admin:
        flash("You don't have permission to access this page.", "danger")
        return redirect(url_for('cars.home'))

    user = User.query.get_or_404(user_id)
    form = EditUserForm(obj=user, user=user)  # Pass user to the form for validation

    if form.validate_on_submit():
        user.username = form.username.data
        user.email = form.email.data
        user.first_name = form.first_name.data
        user.last_name = form.last_name.data
        user.phone_number = form.phone_number.data
        user.role = form.role.data
        user.is_banned = form.is_banned.data  # Update banned status

        try:
            db.session.commit()
            flash(f"User '{user.username}' updated.", 'success')
            return redirect(url_for('admin.list_users'))
        except Exception as e:
            db.session.rollback()
            flash(f"Error updating user: {e}", 'danger')

    return render_template('admin/edit_user.html', form=form, user=user)


@admin_bp.route("/users/ban/<int:user_id>")
@login_required
def ban_user(user_id):
    if not current_user.is_admin:
        flash("You don't have permission to access this page.", "danger")
        return redirect(url_for('cars.home'))

    user = User.query.get_or_404(user_id)
    user.is_banned = True
    try:
        db.session.commit()
        flash(f"User '{user.username}' banned.", 'success')
    except Exception as e:
        db.session.rollback()
        flash(f"Error banning user: {e}", 'danger')
    return redirect(url_for('admin.list_users'))


@admin_bp.route("/users/unban/<int:user_id>")
@login_required
def unban_user(user_id):
    if not current_user.is_admin:
        flash("You don't have permission to access this page.", "danger")
        return redirect(url_for('cars.home'))

    user = User.query.get_or_404(user_id)
    user.is_banned = False
    try:
        db.session.commit()
        flash(f"User '{user.username}' unbanned.", 'success')
    except Exception as e:
        db.session.rollback()
        flash(f"Error unbanning user: {e}", 'danger')
    return redirect(url_for('admin.list_users'))


@admin_bp.route("/users/deactivate/<int:user_id>")
@login_required
def deactivate_user(user_id):
    if not current_user.is_admin:
        flash("You don't have permission to access this page.", "danger")
        return redirect(url_for('cars.home'))

    user = User.query.get_or_404(user_id)
    # check if the user has is_active column or not.
    if hasattr(user, 'is_active'):
        user.is_active = False  # Or a similar flag you define
    try:
        db.session.commit()
        flash(f"User '{user.username}' deactivated.", 'success')
    except Exception as e:
        db.session.rollback()
        flash(f"Error deactivating user: {e}", 'danger')
    return redirect(url_for('admin.list_users'))


@admin_bp.route("/users/delete/<int:user_id>")
@login_required
def delete_user(user_id):
    if not current_user.is_admin:
        flash("You don't have permission to access this page.", "danger")
        return redirect(url_for('cars.home'))

    user = User.query.get_or_404(user_id)
    try:
        db.session.delete(user)
        db.session.commit()
        flash(f"User '{user.username}' deleted.", 'success')
    except Exception as e:
        db.session.rollback()
        flash(f"Error deleting user: {e}", 'danger')
    return redirect(url_for('admin.list_users'))


@admin_bp.route("/cars/mark_sold/<int:car_id>")
@login_required
def mark_car_sold(car_id):
    if not current_user.is_admin:
        flash("You don't have permission to access this page.", "danger")
        return redirect(url_for('cars.home'))

    car = Car.query.get_or_404(car_id)
    car.is_sold = True
    car.is_active = False
    try:
        db.session.commit()
        flash(f"Car '{car.title}' marked as sold.", 'success')
    except Exception as e:
        db.session.rollback()
        flash(f"Error marking car as sold: {e}", 'danger')
    return redirect(url_for('admin.dashboard'))


@admin_bp.route("/cars/mark_available/<int:car_id>")
@login_required
def mark_car_available(car_id):
    if not current_user.is_admin:
        flash("You don't have permission to access this page.", "danger")
        return redirect(url_for('cars.home'))

    car = Car.query.get_or_404(car_id)
    car.is_sold = False
    car.is_active = True
    try:
        db.session.commit()
        flash(f"Car '{car.title}' marked as available.", 'success')
    except Exception as e:
        db.session.rollback()
        flash(f"Error marking car as available: {e}", 'danger')
    return redirect(url_for('admin.dashboard'))


# Report Management
@admin_bp.route("/reports")
@login_required
def list_reports():
    if not current_user.is_admin:
        flash("You don't have permission to access this page.", "danger")
        return redirect(url_for('cars.home'))

    reports = ReportedAds.query.all()
    return render_template('admin/list_reports.html', reports=reports)


@admin_bp.route("/reports/delete/<int:report_id>")
@login_required
def delete_report(report_id):
    if not current_user.is_admin:
        flash("You don't have permission to access this page.", "danger")
        return redirect(url_for('cars.home'))

    report = ReportedAds.query.get_or_404(report_id)
    try:
        db.session.delete(report)
        db.session.commit()
        flash("Report deleted.", 'success')
    except Exception as e:
        db.session.rollback()
        flash(f"Error deleting report: {e}", 'danger')
    return redirect(url_for('admin.list_reports'))
