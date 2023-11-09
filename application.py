from os import environ, path
from dotenv import load_dotenv
basedir = path.abspath(path.dirname(__file__))
load_dotenv(path.join(basedir, '.env'))
from flask import Flask, render_template, redirect, url_for, flash, session, request
from flask_sqlalchemy import SQLAlchemy





db = SQLAlchemy()
application = Flask(__name__)
application.config["SQLALCHEMY_DATABASE_URI"] = environ.get('MYSQLCREDS')
db.init_app(application)

application.secret_key = environ.get('SECKEY')




from flask_login import UserMixin



class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    hashed_password = db.Column(db.String(200), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    def __repr__(self):
        return f'{self.username}'






from flask_login import login_user, logout_user, login_required, current_user
from flask_login import LoginManager


login_manager = LoginManager()
login_manager.login_view = 'login'
login_manager.login_message = "User needs to be logged in to view this page"
login_manager.login_message_category = "error"
login_manager.init_app(application)




@login_manager.user_loader
def load_user(user_id):
    # since the user_id is just the primary key of our user table, use it in the query for the user
    return db.session.get(User,int(user_id))





@application.route('/')
def hello_world():
    u = db.session.get(User,1)
    return f"Sup {u.username}, hello world"




@application.route('/home')
@login_required
def home():
    return render_template('base.html')




from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import InputRequired, ValidationError
from werkzeug.security import check_password_hash




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




@application.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    form.next_page.data = request.args.get('next')
    if form.validate_on_submit():
        flash("Login successful", "success")
        user = User.query.filter_by(username=form.username.data).first()
        login_user(user, remember=True)

        return redirect(form.next_page.data or url_for('hello_world'))
    
    return render_template('user/login.html', form=form)

@application.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('hello_world'))