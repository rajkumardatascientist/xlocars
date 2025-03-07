from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired

class MinimalForm(FlaskForm):
    make = StringField('Make', validators=[DataRequired()])
    model = StringField('Model')
    state = StringField('State')
    district = StringField('District')
    owner_type = StringField('Owner Type')
    submit = SubmitField('Apply Filters')
