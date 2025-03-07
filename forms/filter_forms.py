# forms/filter_forms.py
from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, SubmitField
from wtforms.validators import Optional
from locations import indian_states_districts  # Import at the top


class CarFilterForm(FlaskForm):
    make = SelectField('Make', choices=[('', 'All Makes')], validators=[Optional()])
    model = SelectField('Model', choices=[('', 'All Models')], validators=[Optional()])
    state = SelectField("State", choices=[('', 'All States')], validators=[Optional()])
    district = SelectField("District", choices=[('', 'All Districts')], validators=[Optional()])
    owner_type = SelectField('Owner Type', choices=[('', 'Any'), ('1', 'First Owner'), ('2', 'Second Owner')], validators=[Optional()])
    submit = SubmitField('Apply Filters')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        try: #Try adding this, if this does not work it still should continue to render page.
            self.state.choices = [('', 'All States')] + [(state, state) for state in indian_states_districts.keys()]
        except:
            self.state.choices = [('', 'All States')] # Default State
        self.district.choices = [('', 'All Districts')]
