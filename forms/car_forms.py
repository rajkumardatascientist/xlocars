# forms/car_forms.py

from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, IntegerField, FloatField, TextAreaField, SubmitField, SelectField
from wtforms.validators import DataRequired, Length, NumberRange, ValidationError, Optional
from datetime import datetime


class CarForm(FlaskForm):
    title = StringField("Title", validators=[DataRequired(), Length(max=100)])
    description = TextAreaField("Description", validators=[DataRequired()])
    price = IntegerField("Price (INR)", validators=[DataRequired(), NumberRange(min=1)])
    year = IntegerField(
        "Year", validators=[DataRequired(), NumberRange(min=2015, max=datetime.now().year)]
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
    state = SelectField("State", choices=[], validators=[DataRequired()])
    district = SelectField("District", choices=[], validators=[DataRequired()])
    body_type = StringField("Body Type", validators=[Optional()])
    fuel_type = SelectField(
        "Fuel Type",
        choices=[("Petrol", "Petrol"), ("Diesel", "Diesel"), ("CNG", "CNG"), ("Electric", "Electric"), ("Hybrid", "Hybrid")],
        validators=[Optional()],
    )
    engine_type = StringField("Engine Type", validators=[Optional()])
    engine_capacity = FloatField("Engine Capacity (CC)", validators=[Optional()])
    exterior_color = StringField("Exterior Color", validators=[Optional()])
    interior_color = StringField("Interior Color", validators=[Optional()])
    vin = StringField("VIN", validators=[Optional(), Length(max=17)])
    license_plate = StringField("License Plate", validators=[Optional()])
    registration_expiry = StringField("Registration Expiry", validators=[Optional()])


    submit = SubmitField("Post Ad")

    def __init__(self, *args, **kwargs):
        super(CarForm, self).__init__(*args, **kwargs)
        # Populate state choices.  This needs to happen *after* the form is instantiated
        try:
            from locations import indian_states_districts

            self.state.choices = [(state, state) for state in indian_states_districts.keys()]  # State selection
            self.district.choices = []
        except ImportError:
            self.state.choices = [("No Locations", "No Locations")]  # if can't find location file
            self.district.choices = [("No Locations", "No Locations")]  # if can't find location file

    def validate_year(self, year):
        if year.data < 2015:
            raise ValidationError("Year must be 2015 or later.")
