# cars.py (Modified)

import os
from flask import Blueprint, render_template, url_for, redirect, flash, request, current_app, session
from forms.car_forms import CarForm
from forms.interested_forms import InterestedForm
from models import Car, InterestedBuyers, Wishlist, Appointment, Image, ReportedAds
from app import db, app
from flask_login import current_user, login_required
from werkzeug.utils import secure_filename
import secrets
from PIL import Image as PILImage
import os
from datetime import datetime, timezone
from sqlalchemy.orm import joinedload
from sqlalchemy.exc import IntegrityError
import logging
from forms.report_forms import ReportForm
from sqlalchemy import or_
from forms.appointment_forms import AppointmentForm
from models.payment import PaymentStatus, BuyerPayments
import requests  # For Imgur upload


try:
    from locations import indian_states_districts
    indian_states = list(indian_states_districts.keys())
except ImportError as e:
    print(f"ImportError: Could not import indian_states_districts from locations.py: {e}")
    indian_states = []
    indian_states_districts = {}

cars_bp = Blueprint('cars', __name__, __name__, url_prefix='/cars')

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
UPLOAD_FOLDER = os.path.join('static', 'images')  # Use os.path.join
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER  # Important: Set in app config!

# Imgur Configuration
IMGUR_CLIENT_ID = os.environ.get("IMGUR_CLIENT_ID")  # Retrieve from environment
if not IMGUR_CLIENT_ID:
    raise ValueError("IMGUR_CLIENT_ID environment variable not set.")

logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def populate_filters():
    """Helper function to fetch distinct makes and models from the database."""
    with app.app_context():
        makes = db.session.query(Car.make).distinct().order_by(Car.make).all()
        models = db.session.query(Car.model).distinct().order_by(Car.model).all()
        return makes, models


def upload_to_imgur(image):
    """Uploads an image file to Imgur and returns the image URL"""
    url = "https://api.imgur.com/3/upload"
    headers = {"Authorization": f"Client-ID {IMGUR_CLIENT_ID}"}

    try:
        response = requests.post(url, headers=headers, files={"image": image})
        response.raise_for_status()  # Raise HTTPError for bad responses (4xx or 5xx)

        return response.json()["data"]["link"]  # Returns Imgur URL

    except requests.exceptions.RequestException as e:
        print(f"Error during Imgur upload: {e}")
        return None


@cars_bp.route("/", methods=['GET', 'POST'])
def home():
    """Displays the homepage with car listings."""
    state = request.args.get('state')
    district = request.args.get('district')

    if state:
        session['selected_state'] = state
    if district:
        session['selected_district'] = district
    elif 'selected_state' in session and 'selected_district' in session:  # If location is not available in args, read it from session
        state = session['selected_state']
        district = session['selected_district']

    try:
        with app.app_context():
            makes, models = populate_filters()
            cars_query = Car.query.filter_by(is_approved=True).options(joinedload(Car.images))

            if state:
                cars_query = cars_query.filter_by(state=state)
            if district:
                cars_query = cars_query.filter_by(city=district)

            cars = cars_query.all()
            featured_cars = Car.query.filter_by(is_featured=True).options(joinedload(Car.images)).limit(4).all()

            return render_template('home.html', cars=cars,
                                   featured_cars=featured_cars, makes=makes, models=models,
                                   datetime=datetime, timezone=timezone,
                                   indian_states_districts=indian_states_districts,
                                   selected_state=state,
                                   selected_district=district
                                   )
    except Exception as e:
        logging.exception("Error in home route: %s", e)
        flash(f"Error displaying listings: {e}", "error")
        return render_template("error.html", error=str(e))


@cars_bp.route("/listings", methods=['GET', 'POST'])
def listings():
    """Displays the car listings page with filters."""

    makes = db.session.query(Car.make).distinct().order_by(Car.make).all()
    models = db.session.query(Car.model).distinct().order_by(Car.model).all()
    cars_query = Car.query.filter_by(is_approved=True).options(joinedload(Car.images))

    # 1. Location Filters:
    state = request.args.get('state')
    city = request.args.get('city')
    if state:
        cars_query = cars_query.filter(Car.state == state)
    if city:
        cars_query = cars_query.filter(Car.city.ilike(f"%{city}%"))

    # 2. Price Filters:
    min_price = request.args.get('min_price')
    max_price = request.args.get('max_price')

    if min_price:
        try:
            min_price = float(min_price)
            cars_query = cars_query.filter(Car.price >= min_price)
        except ValueError:
            flash("Invalid Min Price", "error")  # Proper error handling
    if max_price:
        try:
            max_price = float(max_price)
            cars_query = cars_query.filter(Car.price <= max_price)
        except ValueError:
            flash("Invalid Max Price", "error")

    # 3. Year Filters:
    min_year = request.args.get('min_year')
    max_year = request.args.get('max_year')

    if min_year:
        try:
            min_year = int(min_year)
            cars_query = cars_query.filter(Car.year >= min_year)
        except ValueError:
            flash("Invalid Min Year", "error")
    if max_year:
        try:
            max_year = int(max_year)
            cars_query = cars_query.filter(Car.year <= max_year)
        except ValueError:
            flash("Invalid Max Year", "error")

    # 4. Brand and Model Filter:
    make = request.args.get('make')
    if make:
        cars_query = cars_query.filter(Car.make == make)

    # 5. KM Driven Filter:
    min_km = request.args.get('min_km')
    max_km = request.args.get('max_km')

    if min_km:
        try:
            min_km = int(min_km)
            cars_query = cars_query.filter(Car.kilometers >= min_km)
        except ValueError:
            flash("Invalid Min KM", "error")
    if max_km:
        try:
            max_km = int(max_km)
            cars_query = cars_query.filter(Car.kilometers <= max_km)
        except ValueError:
            flash("Invalid Max KM", "error")

    # 6. Search Filter:
    search_query = request.args.get('search')
    if search_query:
        cars_query = cars_query.filter(
            or_(Car.title.ilike(f"%{search_query}%"), Car.description.ilike(f"%{search_query}%"),
                Car.model.ilike(f"%{search_query}%"), Car.make.ilike(f"%{search_query}%"))
        )

    cars = cars_query.all()

    now_utc = datetime.now(timezone.utc)
    return render_template(
        "listings.html",
        cars=cars,
        makes=makes,
        models=models,
        now_utc=now_utc,
        datetime=datetime,
        indian_states=indian_states,  # Pass indian_states to the template
        request=request
    )


@cars_bp.route("/car/new", methods=['GET', 'POST'])
@login_required
def new_car():
    form = CarForm(request.form)

    if request.method == 'POST':
        state = request.form.get('state')
        if state and state in indian_states_districts:
            form.district.choices = [(d, d) for d in indian_states_districts[state]]
        else:
            form.district.choices = []

    if form.validate_on_submit():
        logging.info("Form is valid. Processing car data...")

        car = Car(
            title=form.title.data,
            description=form.description.data,
            price=form.price.data,
            year=form.year.data,
            make=form.make.data,
            model=form.model.data,
            transmission=form.transmission.data,
            state=form.state.data,
            city=form.district.data,
            seller=current_user,
            is_approved=False,
            kilometers=form.kilometers.data,
            no_of_owners=form.no_of_owners.data,
            registration_expiry=datetime.now().date(),
            vin="",
            body_type=form.body_type.data,
            fuel_type=form.fuel_type.data,
            engine_type=form.engine_type.data,
            engine_capacity=form.engine_capacity.data,
        )

        with app.app_context():
            db.session.add(car)
            try:
                db.session.commit()

                for image in request.files.getlist(form.images.name):
                    if image and allowed_file(image.filename):
                        try:
                           # image_url = save_picture(image) # Saves images locally.
                           image_url = upload_to_imgur(image) # Saves the image in Imgur server
                           if image_url:
                               image_db = Image(url=image_url, car_id=car.id)
                               db.session.add(image_db)
                               db.session.commit()  # Commit each image immediately
                           else:
                               db.session.rollback()
                               logging.error("Imgur upload failed for one of the images.")
                               flash("Imgur upload failed for one of the images.", "error")
                               return render_template("error.html", error="Imgur upload failed.")


                        except Exception as image_err:
                            db.session.rollback()
                            logging.error(f"Error saving image: {image_err}")
                            flash(f"Error saving image: {image_err}", "error")
                            return render_template("error.html", error=str(image_err))

                flash('Your car ad has been created! It is pending approval.', 'success')
                return redirect(url_for('cars.home'))

            except IntegrityError as e:
                db.session.rollback()
                logging.exception("Error creating car ad (IntegrityError): %s", e)
                flash(f'Database error creating car ad: {e}', 'error')
                return render_template("error.html", error=str(e))

            except Exception as e:
                db.session.rollback()
                logging.exception("Error creating car ad: %s", e)
                flash(f'Error creating car ad: {e}', 'error')
                return render_template("error.html", error=str(e))

    print(form.errors)
    return render_template('create_car.html',
                           title='New Car',
                           form=form,
                           legend='New Car Ad')


def save_picture(form_image):
    """Saves the uploaded picture and returns the filename."""
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_image.filename)
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(app.config['UPLOAD_FOLDER'], picture_fn)  # Use app.config

    try:
        output_size = (800, 600)
        i = PILImage.open(form_image)
        i.thumbnail(output_size)
        i.save(picture_path)
        return picture_fn
    except Exception as e:
        logging.error(f"Error saving picture: {e}")
        raise  # Re-raise the exception after logging


@cars_bp.route("/car/<int:car_id>")
def car(car_id):
    """Displays a specific car's details."""
    car = Car.query.options(joinedload(Car.seller), joinedload(Car.images)).get_or_404(car_id)
    report_form = ReportForm()
    buyer_can_view_contact = False
    wishlist_status = False

    if current_user.is_authenticated:
        with app.app_context():
            payment = BuyerPayments.query.filter_by(
                buyer_id=current_user.id,
                car_id=car_id,
                payment_status=PaymentStatus.PAYMENT_SUCCESSFUL,
                is_contact_unlocked=True
            ).first()

            buyer_can_view_contact = bool(payment)

        wishlist_status = is_car_in_wishlist(current_user.id, car_id)

    return render_template('car_detail.html',
                           title=car.title,
                           car=car,
                           report_form=report_form,
                           buyer_can_view_contact=buyer_can_view_contact,
                           wishlist_status=wishlist_status)


@cars_bp.route("/car/<int:car_id>/interested", methods=['GET', 'POST'])
@login_required
def interested(car_id):
    """Handles buyer interest in a car."""
    car = Car.query.get_or_404(car_id)
    form = InterestedForm(request.form)

    if form.validate_on_submit():
        with app.app_context():
            interested_buyer = InterestedBuyers(car_id=car_id,
                                                 buyer_name=form.name.data,
                                                 buyer_phone=form.phone.data,
                                                 buyer_id=current_user.id)
            db.session.add(interested_buyer)
            try:
                db.session.commit()
                flash('Your interest has been noted! The seller may contact you.', 'success')
            except Exception as e:
                db.session.rollback()
                logging.exception("Error saving interest: %s", e)
                flash('Error noting your interest. Please try again.', 'error')
                return render_template("error.html", error=str(e))

    elif request.method == 'POST':
        for field, errors in form.errors.items():
            for error in errors:
                flash(f"Error in {getattr(form, field).label.text}: {error}", 'danger')

    return redirect(url_for('cars.car', car_id=car_id))


def is_car_in_wishlist(user_id, car_id):
    """Checks if a car is in the user's wishlist."""
    with app.app_context():
        wishlist_item = Wishlist.query.filter_by(user_id=user_id, car_id=car_id).first()
    return bool(wishlist_item)


@cars_bp.route("/car/<int:car_id>/wishlist/add", methods=['POST'])
@login_required
def add_to_wishlist(car_id):
    """Adds a car to the user's wishlist."""
    car = Car.query.get_or_404(car_id)

    if is_car_in_wishlist(current_user.id, car_id):
        flash('Car is already in your wishlist.', 'info')
    else:
        with app.app_context():
            wishlist_item = Wishlist(user_id=current_user.id, car_id=car_id)
            db.session.add(wishlist_item)
            try:
                db.session.commit()
                flash('Car added to wishlist!', 'success')
            except Exception as e:
                db.session.rollback()
                flash('Error adding to wishlist.', 'error')
                return render_template("error.html", error=str(e))
    return redirect(url_for('cars.car', car_id=car_id))


@cars_bp.route("/car/<int:car_id>/wishlist/remove", methods=['POST'])
@login_required
def remove_from_wishlist(car_id):
    """Removes a car from the user's wishlist."""
    car = Car.query.get_or_404(car_id)
    with app.app_context():
        wishlist_item = Wishlist.query.filter_by(user_id=current_user.id,
                                                   car_id=car_id).first()
    if wishlist_item:
        db.session.delete(wishlist_item)
        try:
            db.session.commit()
            flash('Car removed from wishlist.', 'success')
        except Exception as e:
            db.session.rollback()
            flash('Error removing from wishlist.', 'error')
            return render_template("error.html", error=str(e))
    elif not wishlist_item:
        flash('Car is not in your wishlist.', 'info')

    return redirect(url_for('cars.car', car_id=car_id))


@cars_bp.route("/wishlist")
@login_required
def show_wishlist():
    """Displays the user's wishlist."""
    with app.app_context():
        wishlist_items = Wishlist.query.filter_by(user_id=current_user.id).all()
    return render_template('wishlist.html', wishlist_items=wishlist_items)


@cars_bp.route("/about")
def about():
    """Displays the about page."""
    return render_template('about.html')


@cars_bp.route("/car/<int:car_id>/request_appointment",
           methods=['GET', 'POST'])
@login_required
def request_appointment(car_id):
    """Handles appointment requests for a car."""
    car = Car.query.get_or_404(car_id)
    form = AppointmentForm()

    if form.validate_on_submit():
        if current_user.id == car.seller_id:
            flash("You cannot request an appointment for your own car.", "warning")
            return redirect(url_for('cars.car', car_id=car_id))

        with app.app_context():
            appointment = Appointment(
                buyer_id=current_user.id,
                seller_id=car.seller_id,
                car_id=car_id,
                appointment_time=form.appointment_time.data,
                notes=form.notes.data)
            db.session.add(appointment)
            try:
                db.session.commit()
                flash('Your appointment request has been submitted.', 'success')
                return redirect(url_for('cars.car', car_id=car_id))
            except Exception as e:
                db.session.rollback()
                flash(f'Error submitting appointment request: {e}', 'error')
                return render_template("error.html", error=str(e))

    return render_template('appointment.html', form=form, car=car)


@cars_bp.route("/car/<int:car_id>/report", methods=['GET', 'POST'])
@login_required
def report_ad(car_id):
    """Handles reporting of car ads."""
    car = Car.query.get_or_404(car_id)
    form = ReportForm()

    if form.validate_on_submit():
        try:
            report = ReportedAds(
                car_id=car.id,
                reported_by=current_user.id,
                reason=form.reason.data
            )
            db.session.add(report)
            db.session.commit()
            flash('Ad reported. Thank you!', 'success')
            return redirect(url_for('cars.car', car_id=car.id))
        except Exception as e:
            db.session.rollback()
            flash(f"Error Reporting Ad:{e}", "error")
            return render_template("error.html", error=str(e))

    return render_template('report_ad.html', form=form, car=car)


@cars_bp.route("/delete_car/<int:car_id>", methods=['POST'])
@login_required
def delete_car(car_id):
    """Deletes a car listing."""
    car = Car.query.get_or_404(car_id)

    if car.seller_id != current_user.id:
        flash("You are not authorized to delete this listing.", "error")
        return redirect(url_for('cars.home'))  # Or appropriate error page

    try:
        db.session.delete(car)
        db.session.commit()
        flash("Listing deleted successfully.", "success")
    except Exception as e:
        db.session.rollback()
        logging.exception("Error deleting car: %s", e)
        flash(f"Error deleting listing: {e}", "error")
        return render_template("error.html", error=str(e))

    return redirect(url_for('users.seller_dashboard'))  # Redirect to seller dashboard


@cars_bp.route("/pause_car/<int:car_id>", methods=['POST'])
@login_required
def pause_car(car_id):
    """Pauses a car listing (sets is_active to False)."""
    car = Car.query.get_or_404(car_id)

    if car.seller_id != current_user.id:
        flash("You are not authorized to pause this listing.", "error")
        return redirect(url_for('cars.home'))  # Or appropriate error page

    car.is_active = False #Set Car model to active or inactive
    try:
        db.session.commit()
        flash("Listing paused successfully.", "success")
    except Exception as e:
        db.session.rollback()
        logging.exception("Error pausing car: %s", e)
        flash(f"Error pausing listing: {e}", "error")
        return render_template("error.html", error=str(e))

    return redirect(url_for('users.seller_dashboard'))  # Redirect to seller dashboard

@cars_bp.route("/unpause_car/<int:car_id>", methods=['POST'])
@login_required
def unpause_car(car_id):
    """Unpauses a car listing (sets is_active to True)."""
    car = Car.query.get_or_404(car_id)

    if car.seller_id != current_user.id:
        flash("You are not authorized to unpause this listing.", "error")
        return redirect(url_for('cars.home'))  # Or appropriate error page

    car.is_active = True
    try:
        db.session.commit()
        flash("Listing unpaused successfully.", "success")
    except Exception as e:
        db.session.rollback()
        logging.exception("Error unpausing car: %s", e)
        flash(f"Error unpausing listing: {e}", "error")
        return render_template("error.html", error=str(e))

    return redirect(url_for('users.seller_dashboard'))  # Redirect to seller dashboard
