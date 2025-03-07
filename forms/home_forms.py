# forms/home_forms.py
from flask_wtf import FlaskForm
from wtforms import SubmitField

class MinimalForm(FlaskForm):
    submit = SubmitField('Apply Filters')
