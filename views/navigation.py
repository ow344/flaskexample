from . import nav
from flask import render_template
from models import User, School, UserSchool, db
from forms import LoginForm
from flask import render_template, redirect, url_for, flash, session, request
from flask_login import login_user, logout_user, current_user


@nav.route('/')
def index():
    if current_user.is_authenticated:
        home = url_for('nav.home')
        return redirect(home)
    return redirect(url_for('nav.login'))

@nav.route('/home')
def home():
    return render_template('navigation/home.html')

@nav.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    form.next_page.data = request.args.get('next')
    if form.validate_on_submit():
        flash("Login successful", "success")
        user = User.query.filter_by(username=form.username.data).first()
        login_user(user, remember=True)
        return redirect(form.next_page.data or url_for('nav.index'))
    return render_template('navigation/login.html', form=form)

@nav.route('/logout')
def logout():
    if not current_user.is_admin:
        session.pop('active_school_id')
        session.pop('active_school_name')
    logout_user()
    return redirect(url_for('nav.index'))


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