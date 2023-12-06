from models import User
from forms import LoginForm
from flask import render_template, redirect, url_for, flash, session, request
from flask_login import login_user, logout_user, current_user

################################  Main  ################################
from . import main

@main.route('/')
def index():
    if current_user.is_authenticated:
        if current_user.is_admin:
            home = url_for('admin.home')
        else:
            home = url_for('user.home')
        # Override to new home page
        home = url_for('nav.home')
        return redirect(home)
    return redirect(url_for('main.login'))


@main.route('/settings')
def settings():
    return render_template('main/settings.html')


@main.route('/test1')
def test():
    return render_template('main/test.html')


@main.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    form.next_page.data = request.args.get('next')
    if form.validate_on_submit():
        flash("Login successful", "success")
        user = User.query.filter_by(username=form.username.data).first()
        login_user(user, remember=True)
        return redirect(form.next_page.data or url_for('main.index'))
    return render_template('main/login.html', form=form)

@main.route('/logout')
def logout():
    if not current_user.is_admin:
        session.pop('active_school_id')
        session.pop('active_school_name')
    logout_user()
    return redirect(url_for('main.index'))


