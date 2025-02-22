# forms/report_forms.py

from flask_wtf import FlaskForm
from wtforms import TextAreaField, SubmitField
from wtforms.validators import DataRequired

class ReportForm(FlaskForm):
    reason = TextAreaField('Reason', validators=[DataRequired()])
    submit = SubmitField('Report')