from . import nav
from flask import render_template, render_template, redirect, url_for, flash, session, request
from models import User, School, UserSchool, db
from forms import LoginForm
from flask_login import login_user, logout_user, current_user
from werkzeug.security import generate_password_hash

@nav.route('/')
def index():
    if current_user.is_authenticated:
        home = url_for('nav.home')
        return redirect(home)
    return redirect(url_for('log.login'))

@nav.route('/home')
def home():
    return render_template('navigation/home.html')


@nav.route('/logout')
def logout():
    if not current_user.is_admin:
        session.pop('active_school_id')
        session.pop('active_school_name')
    logout_user()
    return redirect(url_for('log.login'))

@nav.route('/settings')
def settings():
    return render_template('navigation/settings.html')

@nav.route('/changeschool', methods=['GET', 'POST'])
def changeschool():
    if request.method =='POST':
        school = db.session.get(School,int(request.form['school']))
        session['active_school_id'] = school.id
        session['active_school_name'] = school.name
        return redirect(url_for('nav.index'))
    available_schools = [i.school for i in UserSchool.query.filter(UserSchool.user_id==current_user.id).all()]
    return render_template('navigation/changeschool.html',available_schools=available_schools)

@nav.route('/changepassword', methods=['GET', 'POST'])
def changepassword():
    if request.method =='POST':
        if request.form['password'] != request.form['password2']:
            flash("Passwords do not match", "error")
            return redirect(url_for('nav.changepassword'))
        current_user.hashed_password = generate_password_hash(request.form['password'])
        db.session.commit()
        flash("Password changed successfully", "success")
        return redirect(url_for('nav.index'))
    return render_template('navigation/changepassword.html')

@nav.route('/newfromupdate')
def newfromupdate():
    return render_template('navigation/newfromupdate.html')