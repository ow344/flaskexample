from flask import Blueprint
from models import db, User, School, UserSchool, Staff
from forms import LoginForm, RegistrationForm
from flask import render_template, redirect, url_for, flash, session, request
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash
from sqlalchemy import and_

################################  Main  ################################
main = Blueprint('main', __name__)

@main.route('/')
def hello_world():
    if current_user.is_authenticated:
        if current_user.is_admin:
            home = url_for('admin.home')
        else:
            home = url_for('user.home')
        return redirect(home)

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
    if not current_user.is_admin:
        session.pop('active_school_id')
        session.pop('active_school_name')
    logout_user()
    return redirect(url_for('main.hello_world'))

################################  Admin  ################################
admin = Blueprint('admin', __name__)
@admin.before_request
@login_required
def handle_route_permissions():
    pass

@admin.route('/admin')
def home():
    return render_template('admin/self.html')

@admin.route('/admin/userpermissions')
def userpermissions():
    return render_template('admin/userpermissions/self.html', users=User.query.all())


@admin.route('/admin/userpermissions/user/<int:user_id>', methods=['GET', 'POST'])
def userpermissions_user(user_id):
    user=db.session.get(User,user_id)
    schools = School.query.all()
    if request.method == 'POST':
        for school in schools:
            default_value = 0
            primary_B = str(school.id) == request.form.get("default", default_value)
            basic_B = request.form.get(f"basic-{school.id}", default_value) == "on"
            finance_B = request.form.get(f"finance-{school.id}", default_value) == "on"
            user_school_entry = UserSchool.query.filter_by(user_id=user.id,school_id=school.id).first()
            if any([basic_B,primary_B,finance_B]):
                if user_school_entry:
                    user_school_entry.primary = primary_B
                    user_school_entry.finance = finance_B
                else:
                    user_school_entry = UserSchool(user_id=user.id,school_id=school.id,
                                                   primary=primary_B,finance=finance_B)
                    db.session.add(user_school_entry)
            elif user_school_entry:
                db.session.delete(user_school_entry)
        db.session.commit()
        flash("Permissions confirmed", "success")
        return redirect(url_for('admin.userpermissions'))
        
    primary = [i.school_id for i in UserSchool.query.filter_by(user_id=user.id, primary=True).all()]
    basic = [i.school_id for i in UserSchool.query.filter_by(user_id=user.id).all()]
    finance = [i.school_id for i in UserSchool.query.filter_by(user_id=user.id, finance=True).all()]
    return render_template('admin/userpermissions/user.html', user=user, schools=schools, primary=primary, basic=basic, finance=finance)



@admin.route('/admin/userpermissions/register', methods=['GET', 'POST'])
def userpermissions_register():
    form = RegistrationForm()
    if form.validate_on_submit():
        hash = generate_password_hash(form.password.data)
        newU = User(username=form.username.data, hashed_password=hash, is_admin = form.is_admin.data)
        db.session.add(newU)
        db.session.commit()
        flash("Register successful, new user created", "success")
        return redirect(url_for('admin.userpermissions'))

    return render_template('admin/userpermissions/register.html', form=form)

################################  User  ################################
user = Blueprint('user', __name__)


@user.before_request
@login_required
def run_code_once_per_session():
    if 'active_school_id' not in session and current_user.is_authenticated:
        userschools = UserSchool.query.filter(and_(UserSchool.user_id==current_user.id, UserSchool.primary==True)).first()    
        session['active_school_id'] = userschools.school.id
        print(userschools.school.id)
        print(session['active_school_id'])
        session['active_school_name'] = userschools.school.name





@user.route('/user')
def home():
    return render_template('user/self.html')


@user.route('/user/changeschool', methods=['GET', 'POST'])
def changeschool():
    if request.method =='POST':
        school = db.session.get(School,int(request.form['school']))
        session['active_school_id'] = school.id
        session['active_school_name'] = school.name
        return redirect(url_for('user.home'))
    available_schools = [i.school for i in UserSchool.query.filter(UserSchool.user_id==current_user.id).all()]
    return render_template('user/changeschool.html',available_schools=available_schools)



@user.route('/user/stafflist', methods=['GET', 'POST'])
def stafflist():
    staff = Staff.query.filter_by(school_id=session['active_school_id']).all()
    print(staff)
    return render_template('user/stafflist/self.html', staff=staff)






################################  Staff  ################################
staff = Blueprint('staff', __name__)

@staff.before_request
@login_required
def handle_route_permissions():
    pass

def check_permission(staff_id):
    if not current_user.is_admin:
        available_school_ids = [i.school_id for i in UserSchool.query.filter(UserSchool.user_id==current_user.id).all()]
        staff = db.session.get(Staff,staff_id)
        if not staff.school_id in available_school_ids:
            flash('No Permission to view this entry', "error")
            return False
    return True
            






@staff.route('/staff/<int:staff_id>')
def staffentry(staff_id):
    if not check_permission(staff_id):
        return redirect(url_for('main.hello_world'))
    print(staff_id)
    return render_template('staff/self.html', staff=db.session.get(Staff,staff_id))