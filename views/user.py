from flask import Blueprint
from models import db, User, School, UserSchool, Staff, Department, Variation, R2R
from forms import LoginForm, RegistrationForm, VariationForm, StaffForm, R2RForm
from flask import render_template, redirect, url_for, flash, session, request, jsonify
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash
from sqlalchemy import and_


################################  User  ################################
user = Blueprint('user', __name__)

@user.before_request
@login_required
def run_code_once_per_session():
    if 'active_school_id' not in session and current_user.is_authenticated:
        userschools = UserSchool.query.filter(and_(UserSchool.user_id==current_user.id, UserSchool.primary==True)).first()    
        session['active_school_id'] = userschools.school.id
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

@user.route('/user/requestforms/r2r/pending', methods=['GET', 'POST'])
def requestforms_r2r_pending():
    r2rs= R2R.query.filter(R2R.school_id == session['active_school_id']).all()
    return render_template('user/requestforms/r2r/pending.html',r2rs=r2rs)

@user.route('/user/requestforms/r2r/form', methods=['GET', 'POST'])
def requestforms_r2r_form():
    form = R2RForm()
    if form.validate_on_submit():
        new_request = R2R()
        form.populate_obj(new_request)
        db.session.add(new_request)
        db.session.commit()
        return redirect(url_for('user.requestforms_r2r_pending'))
    return render_template('user/requestforms/r2r/form.html', form=form)

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
            


