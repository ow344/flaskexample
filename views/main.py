from flask import Blueprint
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
    """
    Handle the login functionality.

    This function renders the login form, validates the form data,
    logs in the user, and redirects them to the appropriate page
    based on their role (admin or user).

    Returns:
        If the form is valid and the login is successful, the function
        redirects the user to the next page or the home page based on
        their role. Otherwise, it renders the login template with the form.
    """
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
    return render_template('main/login.html', form=form)

@main.route('/logout')
def logout():
    if not current_user.is_admin:
        session.pop('active_school_id')
        session.pop('active_school_name')
    logout_user()
    return redirect(url_for('main.index'))