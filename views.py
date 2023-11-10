from flask import Blueprint
from models import db, User
from forms import LoginForm
from flask import render_template, redirect, url_for, flash, session, request
from flask_login import login_user, logout_user, login_required, current_user


################################  Main  ################################
main = Blueprint('main', __name__)

@main.route('/')
def hello_world():
    return render_template('welcome.html')

@main.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    form.next_page.data = request.args.get('next')
    if form.validate_on_submit():
        flash("Login successful", "success")
        user = User.query.filter_by(username=form.username.data).first()
        login_user(user, remember=True)
        if current_user.is_admin:
            home = url_for('admin.home')
        else:
            home = url_for('user.home')
        return redirect(form.next_page.data or home)
    return render_template('login.html', form=form)

@main.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('main.hello_world'))

################################  Admin  ################################
admin = Blueprint('admin', __name__)

@admin.route('/admin')
@login_required
def home():
    return render_template('admin/self.html')

@admin.route('/admin/userpermissions')
@login_required
def userpermissions():
    return render_template('admin/userpermissions/self.html', users=User.query.all())

################################  User  ################################
user = Blueprint('user', __name__)

@user.route('/user')
@login_required
def home():
    return render_template('user/self.html')

################################  Next  ################################


