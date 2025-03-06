# forms/filter_forms.py
from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, SelectField, SubmitField, FieldList, FloatField
from wtforms.validators import Optional
from locations import indian_states_districts  # Import at the top

class CarFilterForm(FlaskForm):
    make = SelectField('Make', choices=[('', 'All Makes')], validators=[Optional()])
    model = SelectField('Model', choices=[('', 'All Models')], validators=[Optional()])
    year_min = IntegerField('Min Year', validators=[Optional()])
    year_max = IntegerField('Max Year', validators=[Optional()])
    price_min = FloatField('Min Price', validators=[Optional()])
    price_max = FloatField('Max Price', validators=[Optional()])
    state = SelectField("State", choices=[('', 'All States')], validators=[Optional()])
    district = SelectField("District", choices=[('', 'All Districts')], validators=[Optional()])

    submit = SubmitField('Apply Filters')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        #Dynamic updates based on the India states list
        self.state.choices = [('', 'All States')] + [(state, state) for state in indian_states_districts.keys()]
        self.district.choices = [('', 'All Districts')] #Ensure this is reset to empty state on initialization as well
