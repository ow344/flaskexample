from flask import Blueprint
from models import db, School, UserSchool, Staff, Variation, R2R, R2RMessage, Onboard, Request, Role
from forms import RequestForm, RoleForm, CommentForm, PersonForm
from flask import render_template, redirect, url_for, flash, session, request, jsonify
from flask_login import login_required, current_user
from sqlalchemy import and_

user = Blueprint('user', __name__)

@user.before_request
@login_required
def run_code_once_per_session():
    if 'active_school_id' not in session and current_user.is_authenticated:
        if current_user.is_admin:
            flash("Log in as non-admin to access", "error")
            return redirect(url_for("admin.home"))
        userschools = UserSchool.query.filter(and_(UserSchool.user_id==current_user.id, UserSchool.primary==True)).first()    
        session['active_school_id'] = userschools.school.id
        session['active_school_name'] = userschools.school.name

##################### Home #####################
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

##################### Staff #####################
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

##################### Request Forms #####################
##################### R2R #####################
@user.route('/user/requestforms/r2r/pending', methods=['GET', 'POST'])
def requestforms_r2r_pending():
    r2rs = R2R.query.join(Role).filter(Role.school_id == session['active_school_id']).all()
    return render_template('user/requestforms/r2r/pending.html', r2rs=r2rs)

@user.route('/user/requestforms/r2r/form', methods=['GET', 'POST'])
def requestforms_r2r_form():
    r2r = R2R()
    rform = RoleForm(obj=r2r.role)
    rqform = RequestForm(obj=r2r)
    if rform.validate_on_submit() and rqform.validate_on_submit():
        r2r.role = Role()
        rform.populate_obj(r2r.role)
        rqform.populate_obj(r2r)
        r2r.request = Request()
        db.session.add(r2r)
        db.session.commit()
        return redirect(url_for('user.requestforms_r2r_pending'))
    return render_template('user/requestforms/r2r/form.html', rform=rform, rqform=rqform)

@user.route('/user/requestforms/r2r/edit/<int:r2r_id>', methods=['GET', 'POST'])
def requestforms_r2r_edit(r2r_id):
    r2r = db.session.get(R2R,r2r_id)
    if r2r.request.status != 'Pending':
        flash("Decision already made, not editable", "error")
        return redirect(url_for('user.requestforms_r2r_pending'))
    
    rform = RoleForm(obj=r2r.role)
    rqform = RequestForm(obj=r2r)
    if rform.validate_on_submit() and rqform.validate_on_submit():
        rform.populate_obj(r2r.role)
        rqform.populate_obj(r2r)
        # db.session.add(r2r)
        db.session.commit()
        return redirect(url_for('user.requestforms_r2r_pending'))
    
    cform = CommentForm()
    comments = R2RMessage.query.filter_by(r2r_id=r2r.id).order_by(R2RMessage.id.desc()).all()

    return render_template('user/requestforms/r2r/edit.html', rform=rform, rqform=rqform, cform=cform,comments=comments,r2r=r2r)

@user.route('/sendcomment1/<int:r2r_id>', methods=['POST'])
def sendcomment(r2r_id):
    r2r = db.session.get(R2R,r2r_id)
    cform = CommentForm()
    if cform.validate_on_submit():
        print(cform.content.data)
        r2rm = R2RMessage()
        cform.populate_obj(r2rm)
        r2rm.r2r_id=r2r_id
        db.session.add(r2rm)
        db.session.commit()

    return redirect(url_for('user.requestforms_r2r_edit',r2r_id=r2r.id))

##################### Onboard #####################
@user.route('/user/requestforms/onboard/pending', methods=['GET', 'POST'])
def requestforms_onboard_pending():
    onboards = Onboard.query.join(R2R).join(Role).filter(and_(
        Role.school_id == session['active_school_id']
    )).all()

    return render_template('user/requestforms/onboard/pending.html', onboards=onboards)

@user.route('/user/requestforms/onboard/form', methods=['GET', 'POST'])
def requestforms_onboard_form():
    approved_r2rs = R2R.query.join(Role).join(Request).filter(Role.school_id == session['active_school_id'], Request.status == 'Approved').all()
    pform = PersonForm()
    if pform.validate_on_submit():
        onboard = Onboard()
        pform.populate_obj(onboard)
        onboard.r2r_id = pform.r2r_id.data
        onboard.startdate = pform.startdate.data
        onboard.request = Request()
        db.session.add(onboard)
        db.session.commit()
        return redirect(url_for('user.requestforms_onboard_pending'))
    return render_template('user/requestforms/onboard/form.html', approved_r2rs=approved_r2rs, pform=pform)

@user.route('/user/requestforms/onboard/form2/<int:r2r_id>', methods=['GET', 'POST'])
def requestforms_onboard_form2(r2r_id):
    r2r = db.session.get(R2R,r2r_id)
    if r2r.request.status != 'Approved':
        flash("R2R not approved", "error")
        return redirect(url_for('user.requestforms_onboard_pending'))
    
    onboard = Onboard()
    pform = PersonForm(obj=onboard)
    if pform.validate_on_submit():
        pform.populate_obj(onboard)
        onboard.r2r_id = r2r_id
        onboard.startdate = request.form['startdate']
        onboard.request = Request()
        db.session.add(onboard)
        r2r.request.status = 'Linked'
        db.session.commit()
        return redirect(url_for('user.requestforms_onboard_pending'))
    
    return render_template('user/requestforms/onboard/form2.html', pform=pform, r2r=r2r)

@user.route('/user/requestforms/onboard/edit/<int:onboard_id>', methods=['GET', 'POST'])
def requestforms_onboard_edit(onboard_id):
    onboard = db.session.get(Onboard,onboard_id)
    if onboard.request.status != 'Pending':
        flash("Decision already made, not editable", "error")
        return redirect(url_for('user.requestforms_onboard_pending'))
    if onboard.r2r.role.school_id != session['active_school_id']:
        flash("No Permission to view this entry", "error")
        return redirect(url_for('user.requestforms_onboard_pending'))
    pform = PersonForm(obj=onboard)
    if pform.validate_on_submit():
        pform.populate_obj(onboard)
        db.session.commit()
        return redirect(url_for('user.requestforms_onboard_pending'))
    return render_template('user/requestforms/onboard/edit.html', pform=pform, onboard=onboard, r2r=onboard.r2r)

##################### Variation #####################
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
        return redirect(url_for('user.requestforms_variation_pending'))
    
    staff = db.session.get(Staff,staff_id)
    rform= RoleForm(obj=staff)
    rqform = RequestForm(obj=staff)


    if rform.validate_on_submit() and rqform.validate_on_submit():
        new_variation = Variation()
        rform.populate_obj(new_variation)
        rqform.populate_obj(new_variation)
        new_variation.staff_id = int(staff_id)
        new_variation.request = Request()
        db.session.add(new_variation)
        db.session.commit()
   

        flash("Variation to Contract request submitted", "success")
        return redirect(url_for('user.requestforms_variation_pending'))
    
    return render_template('user/requestforms/variation/form2.html', staff=staff, rform=rform, rqform=rqform)

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
            