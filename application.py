from flask import Flask
from config import Config
from models import db
from views import main

application = Flask(__name__)
application.config.from_object(Config)
db.init_app(application)
application.register_blueprint(main)


from flask_login import LoginManager
login_manager = LoginManager()
login_manager.login_view = 'login'
login_manager.login_message = "User needs to be logged in to view this page"
login_manager.login_message_category = "error"
login_manager.init_app(application)






from models import User


@login_manager.user_loader
def load_user(user_id):
    # since the user_id is just the primary key of our user table, use it in the query for the user
    return db.session.get(User,int(user_id))








from flask import render_template, redirect, url_for, flash, session, request
from flask_login import login_user, logout_user, login_required, current_user

from models import User
from forms import LoginForm






@application.route('/home')
@login_required
def home():
    return render_template('base.html')


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
    return redirect(url_for('main.hello_world'))