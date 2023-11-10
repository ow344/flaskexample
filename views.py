from flask import Blueprint
from models import db, User
from forms import LoginForm
from flask import render_template, redirect, url_for, flash, session, request
from flask_login import login_user, logout_user, login_required, current_user


main = Blueprint('main', __name__)



@main.route('/')
def hello_world():
    u = db.session.get(User,1)
    return f"Sup {u.username}, hello world"


@main.route('/home')
@login_required
def home():
    return render_template('base.html')

@main.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    form.next_page.data = request.args.get('next')
    if form.validate_on_submit():
        flash("Login successful", "success")
        user = User.query.filter_by(username=form.username.data).first()
        login_user(user, remember=True)

        return redirect(form.next_page.data or url_for('main.hello_world'))
    
    return render_template('user/login.html', form=form)

@main.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('main.hello_world'))