# routes/cars.py
import os
from dotenv import load_dotenv  # 1. Load dotenv at the top

load_dotenv()  # Load environment variables from .env file

from flask import Blueprint, render_template, url_for, redirect, flash, request, current_app, session, jsonify
from forms.car_forms import CarForm
from forms.interested_forms import InterestedForm
from models import Car, InterestedBuyers, Wishlist, Appointment, Image, ReportedAds
from app import db, app
from flask_login import current_user, login_required
from werkzeug.utils import secure_filename
import secrets
from PIL import Image as PILImage
from datetime import datetime, timezone
from sqlalchemy.orm import joinedload
from sqlalchemy.exc import IntegrityError
import logging
from forms.report_forms import ReportForm
from sqlalchemy import or_
from forms.appointment_forms import AppointmentForm
from models.payment import PaymentStatus, BuyerPayments
import requests  # For Imgur upload REMOVE LATER
from models.car import CarStatus  # Import the CarStatus Enum
from forms.home_forms import MinimalForm  # Import MinimalForm
from forms.filter_forms import CarFilterForm  # Import filter form
import pytz  # Import pytz for timezone
import base64  # BASE 64 load file as type
import cloudinary
import cloudinary.uploader
import cloudinary.api

try:
    from locations import indian_states_districts

    indian_states = list(indian_states_districts.keys())
    indian_states_districts = indian_states_districts
except ImportError as e:
    print(f"ImportError: Could not import indian_states_districts from locations.py: {e}")
    indian_states = []
    indian_states_districts = {}

cars_bp = Blueprint('cars', __name__, url_prefix='/cars')

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
UPLOAD_FOLDER = os.path.join('static', 'images')  # Use os.path.join
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER  # Important: Set in app config!

# Cloudinary Configuration Retrieve from environment variables
CLOUDINARY_CLOUD_NAME = os.environ.get('CLOUDINARY_CLOUD_NAME')  # Use os.environ.get
CLOUDINARY_API_KEY = os.environ.get('CLOUDINARY_API_KEY')  # Use os.environ.get
CLOUDINARY_API_SECRET = os.environ.get('CLOUDINARY_API_SECRET')  # Use os.environ.get

cloudinary.config(
    cloud_name=CLOUDINARY_CLOUD_NAME,
    api_key=CLOUDINARY_API_KEY,
    api_secret=CLOUDINARY_API_SECRET,
    secure=True
)

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


# CLOUDINARY FUNCTION
def upload_to_cloudinary(image):
    """Uploads an image file to Cloudinary and returns the image URL."""
    try:
        upload_result = cloudinary.uploader.upload(image)  # Directly upload the file object
        return upload_result['secure_url']  # Return the secure URL of the uploaded image
    except Exception as e:
        print(f"Error during Cloudinary upload: {e}")
        return None


@cars_bp.route("/", methods=['GET', 'POST'])
def home():
    """Displays the homepage with car listings."""
    # Pre-populate based on URL query parameters
    state = request.args.get('state')
    district = request.args.get('district')

    # Corrected the syntax error here:
    filter_form = CarFilterForm(request.form, state=state, district=district)  # Populate it

    # Initialise State (from the FilterForm first)
    if state:
        if state in indian_states_districts:
            filter_form.district.choices = [('', 'All Districts')] + [(d, d) for d in
                                                                        indian_states_districts[state]]  # Set state if state
        else:
            filter_form.district.choices = [('', 'All Districts')]  # No State

    # Handle storing the selection into the session
    if state:
        session['selected_state'] = state
    if district:
        session['selected_district'] = district

    elif 'selected_state' in session and 'selected_district' in session:  # If location is not available in args, read it from session
        state = session['selected_state']
        district = session['selected_district']

    try:
        with app.app_context():
            # Populate filter form choices (for display)
            makes, models = populate_filters()
            filter_form.make.choices = [('', 'All Makes')] + [(m.make, m.make) for m in
                                                               makes]  # Populate 'make' choices
            filter_form.model.choices = [('', 'All Models')] + [(m.model, m.model) for m in
                                                                 models]  # Populate 'model' choices

            cars_query = Car.query.filter_by(status=CarStatus.ACTIVE).options(joinedload(Car.images))

            if filter_form.validate_on_submit():  # Apply filters if the forms is submitted
                print("validated")
                # Apply filters if the forms is submitted
                if filter_form.state.data:
                    cars_query = cars_query.filter_by(state=filter_form.state.data)
                if filter_form.district.data:
                    cars_query = cars_query.filter_by(district=filter_form.district.data)
                if filter_form.make.data:
                    cars_query = cars_query.filter_by(make=filter_form.make.data)
                if filter_form.model.data:
                    cars_query = cars_query.filter_by(model=filter_form.model.data)

                # New filters
                if filter_form.owner_type.data:
                    if filter_form.owner_type.data == '1':
                        cars_query = cars_query.filter(Car.no_of_owners == 1)  # Filter for first owner
                    elif filter_form.owner_type.data == '2':
                        cars_query = cars_query.filter(
                            Car.no_of_owners == 2)  # Adjust based on how owner numbers are modeled

            elif state:
                cars_query = cars_query.filter_by(state=state)
            if district:
                cars_query = cars_query.filter_by(district=district)

            cars = cars_query.all()
            featured_cars = Car.query.filter_by(is_featured=True, status=CarStatus.ACTIVE).options(
                joinedload(Car.images)).limit(4).all()

            # Add owner type to each car object
            def get_owner_string(no_of_owners):
                if no_of_owners == 1:
                    return "First Owner"
                elif no_of_owners == 2:
                    return "Second Owner"
                elif no_of_owners == 3:
                    return "Third Owner"
                else:
                    return f"{no_of_owners}th Owner"  # For 4th, 5th, etc.

            for car in cars:
                car.owner_type_string = get_owner_string(car.no_of_owners)

            for car in featured_cars:
                car.owner_type_string = get_owner_string(car.no_of_owners)

            # Timezone setup
            tz = pytz.timezone('Asia/Kolkata')  # India timezone
            now = datetime.now(tz)

            return render_template('home.html', cars=cars,
                                   featured_cars=featured_cars, makes=makes, models=models,
                                   datetime=datetime, timezone=timezone,
                                   indian_states_districts=indian_states_districts,
                                   selected_state=state,
                                   selected_district=district,
                                   filter_form=filter_form
                                   )
    except Exception as e:
        logging.exception("Error in home route: %s", e)
        flash(f"Error displaying listings: {e}", "error")
        return render_template("error.html", error=str(e))


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
            district=form.district.data,
            seller=current_user,
            kilometers=form.kilometers.data,
            no_of_owners=form.no_of_owners.data,
            registration_expiry=datetime.now().date(),
            vin="",
            body_type=form.body_type.data,
            fuel_type=form.fuel_type.data,
            engine_type=form.engine_type.data,
            engine_capacity=form.engine_capacity.data,
            seller_phone=form.seller_phone.data
        )
        #  car.status will default to PENDING

        with app.app_context():
            db.session.add(car)
            try:
                db.session.commit()

                for image in request.files.getlist(form.images.name):
                    if image and allowed_file(image.filename):
                        try:
                            # image_url = save_picture(image) # Saves images locally.
                            image_url = upload_to_cloudinary(image)  # Saves the image in Cloudinary server # CHANGE FUNCTION
                            if image_url:
                                image_db = Image(url=image_url, car_id=car.id)
                                db.session.add(image_db)
                                db.session.commit()  # Commit each image immediately
                            else:
                                db.session.rollback()
                                logging.error("Cloudinary upload failed for one of the images.")  # CHANGER OR ERRORS with Cloudinary or IMG UPLOAD NAME!
                                flash("Cloudinary upload failed for one of the images.", "error")
                                return render_template("error.html",
                                                       error="Cloudinary upload failed.")  # CHANGER OR ERRORS with Cloudinary or IMG UPLOAD NAME!


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


@cars_bp.route("/get-districts", methods=["GET"])
def get_districts():
    state = request.args.get("state")
    try:
        districts = indian_states_districts.get(state, [])
    except NameError:
        districts = []
    return jsonify({"districts": districts})


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

    # Only display to public when these are meet!
    # if car.is_sold or not car.is_active or not car.is_approved:
    if car.status == CarStatus.SOLD or car.status != CarStatus.ACTIVE:
        flash("This car listing is no longer available.", "info")
        return redirect(url_for('cars.home'))

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

    # if car.is_sold or not car.is_active or not car.is_approved:
    if car.status == CarStatus.SOLD or car.status != CarStatus.ACTIVE:
        flash("This car listing is no longer available.", "info")
        return redirect(url_for('cars.home'))

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

    # if car.is_sold or not car.is_active or not car.is_approved:
    if car.status == CarStatus.SOLD or car.status != CarStatus.ACTIVE:
        flash("This car listing is no longer available.", "info")
        return redirect(url_for('cars.home'))

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

    # if car.is_sold or not car.is_active or not car.is_approved:
    if car.status == CarStatus.SOLD or car.status != CarStatus.ACTIVE:
        flash("This car listing is no longer available.", "info")
        return redirect(url_for('cars.home'))

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

    # if car.is_sold or not car.is_active or not car.is_approved:
    if car.status == CarStatus.SOLD or car.status != CarStatus.ACTIVE:
        flash("This car listing is no longer available.", "info")
        return redirect(url_for('cars.home'))

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

    # if car.is_sold or not car.is_active or not car.is_approved:
    if car.status == CarStatus.SOLD or car.status != CarStatus.ACTIVE:
        flash("This car listing is no longer available.", "info")
        return redirect(url_for('cars.home'))

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

    return redirect(url_for('dashboard.seller'))  # Redirect to seller dashboard


@cars_bp.route("/pause_car/<int:car_id>", methods=['POST'])
@login_required
def pause_car(car_id):
    """Pauses a car listing (sets is_active to False)."""
    car = Car.query.get_or_404(car_id)

    if car.seller_id != current_user.id:
        flash("You are not authorized to pause this listing.", "error")
        return redirect(url_for('cars.home'))  # Or appropriate error page

    # car.is_active = False #Set Car model to active or inactive
    car.status = CarStatus.PENDING
    try:
        db.session.commit()
        flash("Listing paused successfully.", "success")
    except Exception as e:
        db.session.rollback()
        logging.exception("Error pausing car: %s", e)
        flash(f"Error pausing listing: {e}", "error")
        return render_template("error.html", error=str(e))

    return redirect(url_for('dashboard.seller'))  # Redirect to seller dashboard


@cars_bp.route("/unpause_car/<int:car_id>", methods=['POST'])
@login_required
def unpause_car(car_id):
    """Unpauses a car listing (sets is_active to True)."""
    car = Car.query.get_or_404(car_id)

    if car.seller_id != current_user.id:
        flash("You are not authorized to unpause this listing.", "error")
        return redirect(url_for('cars.home'))  # Or appropriate error page

    # car.is_active = True
    car.status = CarStatus.ACTIVE
    try:
        db.session.commit()
        flash("Listing unpaused successfully.", "success")
    except Exception as e:
        db.session.rollback()
        logging.exception("Error unpausing car: %s", e)
        flash(f"Error unpausing listing: {e}", "error")
        return render_template("error.html", error=str(e))

    return redirect(url_for('dashboard.seller'))  # Redirect to seller dashboard


@cars_bp.route("/car/<int:car_id>/update", methods=['GET', 'POST'])
@login_required
def update_car(car_id):
    """Updates a specific car's details."""
    car = Car.query.get_or_404(car_id)

    if car.seller_id != current_user.id:
        flash("You are not authorized to update this listing.", "error")
        return redirect(url_for('cars.car', car_id=car_id))

    form = CarForm(obj=car)  # Populate form with car data

    if request.method == 'POST':
        state = request.form.get('state')
        if state and state in indian_states_districts:
            form.district.choices = [(d, d) for d in indian_states_districts[state]]
        else:
            form.district.choices = []

    if form.validate_on_submit():
        # Update car attributes
        car.title = form.title.data
        car.description = form.description.data
        car.price = form.price.data
        car.year = form.year.data
        car.make = form.make.data
        car.model = form.model.data
        car.transmission = form.transmission.data
        car.state = form.state.data
        car.district = form.district.data
        car.kilometers = form.kilometers.data
        car.no_of_owners = form.no_of_owners.data
        car.body_type = form.body_type.data
        car.fuel_type = form.fuel_type.data
        car.engine_type = form.engine_type.data
        car.seller_phone = form.seller_phone.data

        # Image Handling
        for image in request.files.getlist(form.images.name):
            if image and allowed_file(image.filename):
                try:
                    image_url = upload_to_cloudinary(image)  # Or save_picture #changed IMGUR
                    if image_url:
                        image_db = Image(url=image_url, car_id=car.id)
                        db.session.add(image_db)
                    else:
                        flash("Cloudinary upload failed for one of the images.",
                              "error")  # Imgur error with UPLOAD or UPLOAD issues on images!!
                        return render_template("error.html",
                                               error="Cloudinary upload failed.")  # Upload to IMG BB
                except Exception as image_err:
                    db.session.rollback()
                    logging.error(f"Error saving image: {image_err}")
                    flash(f"Error saving image: {image_err}", "error")
                    return render_template("error.html", error=str(image_err))

        try:
            db.session.commit()
            flash('Your car ad has been updated!', 'success')
            return redirect(url_for('cars.car', car_id=car.id))
        except Exception as e:
            db.session.rollback()
            logging.exception("Error updating car ad: %s", e)
            flash(f'Error updating car ad: {e}', 'error')
            return render_template("error.html", error=str(e))

    # Pre-populate state and district choices for GET requests
    form.state.choices = [(state, state) for state in indian_states_districts.keys()]
    if car.state in indian_states_districts:
        form.district.choices = [(d, d) for d in indian_states_districts[car.state]]

    return render_template('create_car.html',
                           title='Update Car',
                           form=form,
                           legend='Update Car Ad', car=car)
