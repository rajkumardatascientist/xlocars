# forms/user_forms.py
from flask_wtf import FlaskForm
from wtforms import StringField, BooleanField, SubmitField, SelectField
from wtforms.validators import DataRequired, Length, Email, ValidationError

from models import UserRole #Import to update the forms

class EditUserForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=2, max=80)])
    email = StringField('Email', validators=[DataRequired(), Email(), Length(max=120)])
    first_name = StringField('First Name', validators=[Length(max=50)])
    last_name = StringField('Last Name', validators=[Length(max=50)])
    phone_number = StringField('Phone Number', validators=[Length(max=20)])
    role = SelectField('Role', choices=[(role.value, role.name.title()) for role in UserRole], validators=[DataRequired()])
    is_banned = BooleanField('Banned')
    submit = SubmitField('Update User')

    def __init__(self, user=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = user #Used for form validation

    #User validation for the username if it's edited.
    def validate_username(self, username):
        if self.user and self.user.username != username.data:
            user = User.query.filter_by(username=username.data).first()
            if user:
                raise ValidationError('That username is taken. Please choose a different one.')

    #User validation for the email if it's edited.
    def validate_email(self, email):
         if self.user and self.user.email != email.data:
            user = User.query.filter_by(email=email.data).first()
            if user:
                raise ValidationError('That email is taken. Please choose a different one.')
