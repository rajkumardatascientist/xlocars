# forms/appointment_forms.py
from flask_wtf import FlaskForm
from wtforms import DateTimeField, TextAreaField, SubmitField
from wtforms.validators import DataRequired
from datetime import datetime

class AppointmentForm(FlaskForm):
    appointment_time = DateTimeField('Appointment Time', validators=[DataRequired()], default=datetime.now)
    notes = TextAreaField('Additional Notes')
    submit = SubmitField('Request Appointment')