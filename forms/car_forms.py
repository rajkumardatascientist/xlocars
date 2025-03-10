# forms/car_forms.py

from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, IntegerField, FloatField, TextAreaField, SubmitField, SelectField
from wtforms.validators import DataRequired, Length, NumberRange, ValidationError, Optional
from datetime import datetime
from locations import indian_states_districts  # Import at the top


class CarForm(FlaskForm):
    title = StringField("Title", validators=[DataRequired(), Length(max=100)])
    description = TextAreaField("Description", validators=[DataRequired()])
    price = IntegerField("Price (INR)", validators=[DataRequired(), NumberRange(min=1)])
    year = IntegerField(
        "Year", validators=[DataRequired(), NumberRange(min=1900, max=datetime.now().year)] #Modify to allow 1900 years and up
    )
    make = StringField("Make", validators=[DataRequired()])
    model = StringField("Model", validators=[DataRequired()])
    transmission = SelectField(
        "Transmission",
        choices=[("Automatic", "Automatic"), ("Manual", "Manual")],
        validators=[DataRequired()],
    )
    images = FileField(
        "Car Images",
        validators=[FileAllowed(["jpg", "jpeg", "png", "gif"])],  # Include GIF
        render_kw={"multiple": True},
    )  # Allow multiple files

    kilometers = IntegerField("Kilometers Driven", validators=[Optional()])
    no_of_owners = IntegerField(
        "Number of Previous Owners", validators=[DataRequired(), NumberRange(min=1, max=10)]
    )
    state = SelectField("State", choices=[(state, state) for state in indian_states_districts.keys()], validators=[DataRequired()])
    district = SelectField("District", choices=[], validators=[DataRequired()])
    body_type = SelectField("Body Type", choices=[
        ('Sedan', 'Sedan'), ('SUV', 'SUV'), ('Hatchback', 'Hatchback'),
        ('Convertible', 'Convertible'), ('Coupe', 'Coupe'), ('Van', 'Van'),
        ('Truck', 'Truck'), ('Wagon', 'Wagon'), ('Other', 'Other')], validators=[Optional()])  # Added Body Type
    fuel_type = SelectField(
        "Fuel Type",
        choices=[("Petrol", "Petrol"), ("Diesel", "Diesel"), ("CNG", "CNG"), ("Electric", "Electric"), ("Hybrid", "Hybrid")],
        validators=[Optional()],
    )  # Added Fuel Type
    engine_type = StringField("Engine Type", validators=[Optional()])
    engine_capacity = FloatField("Engine Capacity (CC)", validators=[Optional()])
    exterior_color = StringField("Exterior Color", validators=[Optional()])
    interior_color = StringField("Interior Color", validators=[Optional()])
    vin = StringField("VIN", validators=[Optional(), Length(max=17)])
    license_plate = StringField("License Plate", validators=[Optional()])
    registration_expiry = StringField("Registration Expiry", validators=[Optional()])
    seller_phone = StringField("Seller Phone Number", validators=[Optional(), Length(max=20)])  #Added Phone Number

    submit = SubmitField("Post Ad")

    def __init__(self, *args, **kwargs):
        super(CarForm, self).__init__(*args, **kwargs)
        # Populate state choices.  This needs to happen *after* the form is instantiated
        try:
            self.state.choices = [(state, state) for state in indian_states_districts.keys()]  # State selection
            self.district.choices = []
        except ImportError:
            self.state.choices = [("No Locations", "No Locations")]  # if can't find location file
            self.district.choices = [("No Locations", "No Locations")]  # if can't find location file

    # Delete this Validate_Year to allow any year
    # def validate_year(self, year):
    #    if year.data < 2015:
    #        raise ValidationError("Year must be 2015 or later.")
