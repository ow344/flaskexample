from flask import Blueprint
from models import db, User, School, UserSchool, Staff, Department, Variation
from forms import LoginForm, RegistrationForm, VariationForm, StaffForm
from flask import render_template, redirect, url_for, flash, session, request, jsonify
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash
from sqlalchemy import and_

################################  Main  ################################
main = Blueprint('main', __name__)

@main.route('/')
def index():
    if current_user.is_authenticated:
        if current_user.is_admin:
            home = url_for('admin.home')
        else:
            home = url_for('user.home')
        return redirect(home)
    return redirect(url_for('main.login'))

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
    return redirect(url_for('main.index'))

################################  Admin  ################################
admin = Blueprint('admin', __name__)
@admin.before_request
@login_required
def handle_route_permissions():
    pass

@admin.route('/admin')
def home():
    return render_template('admin/self.html')

@admin.route('/admin/reviewrequests/variation')
def reviewrequests_variation():
    variations = Variation.query.all()
    return render_template('admin/reviewrequests/variation/self.html',variations=variations)

@admin.route('/admin/reviewrequests/variation/entry/<int:variation_id>', methods=['GET','POST'])
def reviewrequests_variation_entry(variation_id):
    variation = db.session.get(Variation,variation_id)
    staff = variation.staff
    if request.method=='POST':
        if request.form['decision'] == 'Approve':
            attributes_to_copy = ['department_id','role','salary','pension','ftpt','weekhours','contract','holiday','notice']
            for attr in attributes_to_copy:             
                if not getattr(staff, attr) == getattr(variation, attr):
                    setattr(staff, attr, getattr(variation, attr))
            flash('Successfuly Approved', 'success')
        else:
            flash('Successfuly Denied', 'success')
        db.session.delete(variation)
        db.session.commit()
        return redirect(url_for('admin.reviewrequests_variation'))
 
    return render_template('admin/reviewrequests/variation/entry.html',variation=variation, staff=staff)

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
        newU = User()
        form.populate_obj(newU)
        newU.hashed_password = generate_password_hash(form.password.data)
        db.session.add(newU)
        db.session.commit()
        flash("Register successful, new user created", "success")
        return redirect(url_for('admin.userpermissions'))

    return render_template('admin/userpermissions/register.html', form=form)

@admin.route('/admin/stafflist', methods=['GET', 'POST'])
def stafflist():
    staff = Staff.query.all()
    return render_template('admin/stafflist/self.html', staff=staff)

@admin.route('/admin/stafflist/staff/<int:staff_id>')
def stafflist_staff(staff_id):
    staff = db.session.get(Staff,staff_id)
    return render_template('admin/stafflist/staff/self.html', staff=staff)

@admin.route('/admin/stafflist/staff/edit/<int:staff_id>')
def stafflist_staff_edit(staff_id):
    staff = db.session.get(Staff,staff_id)
    form = StaffForm(obj=staff)
    return render_template('admin/stafflist/staff/edit.html', staff=staff, form=form)



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
    return render_template('user/stafflist/self.html', staff=staff)

@user.route('/user/stafflist/staff/<int:staff_id>')
def stafflist_staff(staff_id):
    if not check_permission(staff_id):
        return redirect(url_for('user.stafflist'))
    
    staff = db.session.get(Staff,staff_id)
    return render_template('user/stafflist/staff/self.html', staff=staff)

@user.route('/user/requestforms/variation/pending', methods=['GET', 'POST'])
def requestforms_variation_pending():
    variations = Variation.query.join(Staff).filter(Staff.school_id == session['active_school_id']).all()
    return render_template(f'user/requestforms/variation/pending.html', variations=variations)

@user.route('/user/requestforms/variation/form', methods=['GET', 'POST'])
def requestforms_variation_form():
    if request.method=='POST':
        return redirect(url_for('user.requestforms_variation_form2', staff_id=request.form['employee']))
    return render_template('user/requestforms/variation/form.html')

@user.route('/user/requestforms/variation/form/<int:staff_id>', methods=['GET', 'POST'])
def requestforms_variation_form2(staff_id):
    if not check_permission(staff_id):
        return redirect(url_for('user.requestforms_pending', form='variation'))
    
    staff = db.session.get(Staff,staff_id)
    form = VariationForm(obj=staff)

    if form.validate_on_submit():
        new_variation = Variation()
        form.populate_obj(new_variation)
        new_variation.staff_id = int(staff_id)
        new_variation.user_id = current_user.id
        db.session.add(new_variation)
        db.session.commit()
   

        flash("Varition to Contract request submitted", "success")
        return redirect(url_for('user.requestforms_pending', form='variation'))
    
    return render_template('user/requestforms/variation/form2.html', staff=staff, form=form)

@user.route('/update_text', methods=['POST'])
def update_text():
    text = request.get_json().get('text')
    school = session['active_school_id']
    results = Staff.query.filter(and_(Staff.school_id == school, Staff.firstname.like(f"%{text}%"))).all()
    staff_list = [{'id': member.id, 'firstname': str(member.firstname + " " + member.lastname)} for member in results]
    return jsonify(staff_list)

################################  Functions  ################################

def check_permission(staff_id):
    staff = db.session.get(Staff,staff_id)
    if staff.school_id == session['active_school_id']:
        return True
    flash('No Permission to view this entry', "error")
    return False
            


