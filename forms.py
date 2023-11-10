

from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import InputRequired, ValidationError
from werkzeug.security import check_password_hash
from models import User




class LoginForm(FlaskForm):
    username = StringField('Username', validators=[InputRequired()])
    password = PasswordField('Password', validators=[InputRequired()])
    submit = SubmitField('Login')
    next_page = StringField('Next')
    def validate_username(self, field):
        user = User.query.filter_by(username=field.data).first()
        if user is None:
            raise ValidationError('Username not found. Please register or enter a valid username.')
    def validate_password(self, field):
        user = User.query.filter_by(username=self.username.data).first()
        if user and user.hashed_password != field.data:
            raise ValidationError('Password incorrect.')  
