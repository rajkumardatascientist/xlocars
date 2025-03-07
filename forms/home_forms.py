from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired

class MinimalForm(FlaskForm):
    make = StringField('Make', validators=[DataRequired()])
    submit = SubmitField('Apply Filters')
