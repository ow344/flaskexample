from . import nav
from flask import render_template
from models import User, School, UserSchool, db
from forms import LoginForm
from flask import render_template, redirect, url_for, flash, session, request
from flask_login import login_user, logout_user, current_user

@nav.route('/home')
def home():
    return render_template('navigation/home.html')

@nav.route('/settings1')
def settings():
    return render_template('navigation/settings.html')

@nav.route('/changeschool', methods=['GET', 'POST'])
def changeschool():
    if request.method =='POST':
        school = db.session.get(School,int(request.form['school']))
        session['active_school_id'] = school.id
        session['active_school_name'] = school.name
        return redirect(url_for('main.index'))
    available_schools = [i.school for i in UserSchool.query.filter(UserSchool.user_id==current_user.id).all()]
    return render_template('navigation/changeschool.html',available_schools=available_schools)