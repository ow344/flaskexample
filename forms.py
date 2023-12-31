from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, PasswordField, BooleanField, SelectField, SubmitField, TextAreaField, FileField, DateField, EmailField, RadioField, FloatField
from wtforms.validators import InputRequired, Email, EqualTo, Length, ValidationError, DataRequired, Optional
from werkzeug.security import check_password_hash
from models import User, Department, School
from wtforms.widgets import NumberInput


class LoginForm(FlaskForm):
    username = StringField('Username', validators=[InputRequired()])
    password = PasswordField('Password', validators=[InputRequired()])
    submit = SubmitField('Login')
    next_page = StringField('Next')
    def validate_username(self, field):
        user = User.query.filter_by(username=field.data).first()
        if user is None:
            raise ValidationError('Username not found.')
    def validate_password(self, field):
        user = User.query.filter_by(username=self.username.data).first()
        if user and not check_password_hash(user.hashed_password, field.data) :
            raise ValidationError('Password incorrect.')
        
class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[InputRequired(), Length(min=4, max=20)])
    password = StringField('Temporary Password', validators=[InputRequired(), Length(min=5)])
    is_admin = BooleanField('Admin?')
    submit = SubmitField('Register')
    def validate_username(self, field):
        user = User.query.filter_by(username=field.data).first()
        if not user is None:
            raise ValidationError('Username already exists.')
        


class RequestForm(FlaskForm):
    justification = TextAreaField('Justification')
    budgeted = BooleanField('Budgeted?')
    effect_date = DateField('Date to go into effect')



class RoleForm(FlaskForm):
    school_id = SelectField("School", coerce=int, validators=[Optional()])
    department_id = SelectField("Department", coerce=int)
    role =  StringField('Role Title')

    salary = FloatField('Salary', widget=NumberInput(), render_kw={"step": "0.01"})
    pension = SelectField('Pension')
    ftpt = SelectField('Full/Part Time')
    weekhours = FloatField('Hours per week', widget=NumberInput(), render_kw={"step": "0.25"})
    contract = SelectField('Contract')
    holiday = StringField('Holiday')
    notice = StringField('Notice')

    def __init__(self, *args, **kwargs):
        super(RoleForm, self).__init__(*args, **kwargs)
        schools = School.query.all()
        departments = Department.query.all()
        self.school_id.choices = [(school.id, school.name) for school in schools]
        self.department_id.choices = [(department.id, department.name) for department in departments]
        self.pension.choices = ['PEN0','PEN3','PEN5','PEN7']
        self.ftpt.choices = ['Full Time','Part Time']
        self.contract.choices = ['Term Time','Term Time + 4 Weeks','Term Time + 6 Weeks','All Year Round']


class PersonForm(FlaskForm):
    firstname = StringField('First Name')
    lastname = StringField('Last Name')
    dob = DateField('Date of birth')
    gender = StringField('Gender')
    nino = StringField('National Insurance Number')
    nic = SelectField('nic')
    marital = StringField('marital')
    home_address = StringField('home_address')
    postcode = StringField('postcode')
    email = EmailField('email')

    startdate = DateField('Start Date')

    def __init__(self, *args, **kwargs):
        super(PersonForm, self).__init__(*args, **kwargs)
        self.nic.choices = ['A','B','C','H','J','M','V','Z','X']

class ApprovalForm(FlaskForm):
    status = SelectField('Decision', choices=['Pending','Approved','Denied'])


class CommentForm(FlaskForm):
    content = TextAreaField('Comment')
