from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
db = SQLAlchemy()

from datetime import date
from flask_login import current_user
from flask import session

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    hashed_password = db.Column(db.String(200), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    def __repr__(self):
        return f'{self.username}'

class School(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    def __repr__(self):
        return f'{self.name}'

class UserSchool(db.Model):
    __tablename__ = 'user_school'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    school_id = db.Column(db.Integer, db.ForeignKey('school.id'))
    primary = db.Column(db.Boolean, default=False)
    finance = db.Column(db.Boolean, default=False)
    user = db.relationship('User', backref=db.backref('user_schools'))
    school = db.relationship('School', backref=db.backref('user_schools'))

class Department(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    def __repr__(self):
        return f'{self.name}'


class Staff(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    firstname = db.Column(db.String(80))
    lastname = db.Column(db.String(80))
    dob = db.Column(db.Date)
    gender = db.Column(db.String(20))
    nino = db.Column(db.String(12))
    nic = db.Column(db.String(12))
    marital = db.Column(db.String(20))
    home_address = db.Column(db.String(120))
    postcode = db.Column(db.String(20))
    email = db.Column(db.String(80))

    startdate = db.Column(db.Date)

    role_id = db.Column(db.Integer, db.ForeignKey('role.id'))
    role = db.relationship('Role', backref='staff')

    def __repr__(self):
        return f'{self.firstname} {self.lastname}'


class Variation(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    staff_id = db.Column(db.Integer, db.ForeignKey('staff.id'))
    staff = db.relationship('Staff', backref='variation')
    
    new_role_id = db.Column(db.Integer, db.ForeignKey('role.id'))
    new_role = db.relationship('Role', backref='variation_new', foreign_keys=[new_role_id])

    old_role_id = db.Column(db.Integer, db.ForeignKey('role.id'))
    old_role = db.relationship('Role', backref='variation_old', foreign_keys=[old_role_id])



    justification = db.Column(db.Text)
    budgeted = db.Column(db.Boolean, default=False)
    effect_date = db.Column(db.Date)

    request_id = db.Column(db.Integer, db.ForeignKey('request.id'))
    request = db.relationship('Request', backref='variation')
    


class R2R(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    
    role_id = db.Column(db.Integer, db.ForeignKey('role.id'))
    role = db.relationship('Role', backref='r2r')

    justification = db.Column(db.Text)
    budgeted = db.Column(db.Boolean, default=False)
    effect_date = db.Column(db.Date)

    request_id = db.Column(db.Integer, db.ForeignKey('request.id'))
    request = db.relationship('Request', backref='r2r')



class R2RMessage(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    r2r_id = db.Column(db.Integer, db.ForeignKey('r2_r.id'))
    r2r = db.relationship('R2R', backref='r2rmessage')

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), default=lambda: current_user.id if current_user.is_authenticated else None)
    user = db.relationship('User', backref='r2rmessage')

    content = db.Column(db.Text)


class Onboard(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    firstname = db.Column(db.String(80))
    lastname = db.Column(db.String(80))
    dob = db.Column(db.Date)
    gender = db.Column(db.String(20))
    nino = db.Column(db.String(12))
    nic = db.Column(db.String(12))
    marital = db.Column(db.String(20))
    home_address = db.Column(db.String(120))
    postcode = db.Column(db.String(20))
    email = db.Column(db.String(80))
    
    startdate = db.Column(db.Date)

    # Remodel to link to R2R
    r2r_id = db.Column(db.Integer, db.ForeignKey('r2_r.id'))
    r2r = db.relationship('R2R', backref='onboard')
   
    request_id = db.Column(db.Integer, db.ForeignKey('request.id'))
    request = db.relationship('Request', backref='onboard')

  
    def __repr__(self):
        return f'{self.firstname} {self.lastname}'
    

class Request(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    status = db.Column(db.String(20), default='Pending')
    request_date = db.Column(db.Date, default=date.today)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), default=lambda: current_user.id if current_user.is_authenticated else None)
    user = db.relationship('User', backref='request')

class Role(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    school_id = db.Column(db.Integer, db.ForeignKey('school.id'), default=lambda: session.get("active_school_id", None))
    school = db.relationship('School', backref='role')
    department_id = db.Column(db.Integer, db.ForeignKey('department.id'))
    department = db.relationship('Department', backref='role')
    role = db.Column(db.String(120))
    salary = db.Column(db.Float())
    pension = db.Column(db.String(12))
    ftpt = db.Column(db.String(20))
    weekhours = db.Column(db.Float())
    contract = db.Column(db.String(80))
    holiday = db.Column(db.String(80))
    notice = db.Column(db.String(20))
    def __repr__(self):
        return f'{self.role}'