from flask import Blueprint
from models import db, User, School, UserSchool, Staff, Variation, R2R, R2RMessage, Onboard
from forms import RegistrationForm, PersonForm, RoleForm, ApporovalForm, CommentForm
from flask import render_template, redirect, url_for, flash, request
from flask_login import login_required
from werkzeug.security import generate_password_hash

################################  Admin  ################################
from . import admin
@admin.before_request
@login_required
def handle_route_permissions():
    pass

@admin.route('/admin')
def home():
    return render_template('admin/self.html')

@admin.route('/admin/reviewrequests/r2r')
def reviewrequests_r2r():
    r2rs= R2R.query.all()
    return render_template('admin/reviewrequests/r2r/self.html',r2rs=r2rs)

@admin.route('/admin/reviewrequests/r2r/entry/<int:r2r_id>', methods=['GET','POST'])
def reviewrequests_r2r_entry(r2r_id):
    form = ApporovalForm()
    r2r = db.session.get(R2R,r2r_id)
    if r2r.request.status == 'Linked':
        flash(f'Cannot change request with status {r2r.request.status}', 'error')
        return redirect(url_for('admin.reviewrequests_r2r'))
    if form.validate_on_submit():
        r2r.request.status = form.decision.data
        flash(f'Status set to {form.decision.data}', 'success')
        db.session.commit()
        return redirect(url_for('admin.reviewrequests_r2r'))
    cform = CommentForm()
    comments = R2RMessage.query.filter_by(r2r_id=r2r.id).order_by(R2RMessage.id.desc()).all()
    return render_template('admin/reviewrequests/r2r/entry.html',r2r=r2r, form=form, cform=cform,comments=comments)

@admin.route('/sendcomment/<int:r2r_id>', methods=['POST'])
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
        flash("Comment sent", "success")
    return redirect(url_for('admin.reviewrequests_r2r_entry',r2r_id=r2r.id))

@admin.route('/admin/reviewrequests/onboard')
def reviewrequests_onboard():
    onboards = Onboard.query.all()
    return render_template('admin/reviewrequests/onboard/self.html',onboards=onboards)

@admin.route('/admin/reviewrequests/onboard/entry/<int:onboard_id>', methods=['GET','POST'])
def reviewrequests_onboard_entry(onboard_id):
    form = ApporovalForm()
    onboard = db.session.get(Onboard,onboard_id)
    if onboard.request.status != 'Pending':
        flash(f'Cannot change request with status {onboard.request.status}', 'error')
        return redirect(url_for('admin.reviewrequests_onboard'))
    if form.validate_on_submit():
        onboard.request.status = form.decision.data
        flash(f'Status set to {form.decision.data}', 'success')
        if onboard.request.status == "Approved":
            staff = Staff()           
            for attr in ['firstname','lastname','dob','gender','nino','nic','marital','home_address','postcode','email','startdate']: 
                setattr(staff, attr, getattr(onboard, attr))
            for attr in ['school_id','department_id','role','salary','pension','ftpt','weekhours','contract','holiday','notice']:
                setattr(staff, attr, getattr(onboard.r2r, attr))
            db.session.add(staff)
        db.session.commit()
        return redirect(url_for('admin.reviewrequests_onboard'))
    return render_template('admin/reviewrequests/onboard/entry.html',onboard=onboard, form=form)

@admin.route('/admin/reviewrequests/variation')
def reviewrequests_variation():
    variations = Variation.query.all()
    return render_template('admin/reviewrequests/variation/self.html',variations=variations)

@admin.route('/admin/reviewrequests/variation/entry/<int:variation_id>', methods=['GET','POST'])
def reviewrequests_variation_entry(variation_id):
    form = ApporovalForm()
    variation = db.session.get(Variation,variation_id)
    staff = variation.staff
    if variation.request.status != 'Pending':
        flash(f'Cannot change request with status {variation.request.status}', 'error')
        return redirect(url_for('admin.reviewrequests_variation'))
    if form.validate_on_submit():
        variation.request.status = form.decision.data
        if variation.request.status == 'Approved':
            attributes_to_copy = ['department_id','role','salary','pension','ftpt','weekhours','contract','holiday','notice']
            for attr in attributes_to_copy:             
                setattr(staff, attr, getattr(variation, attr))
        flash(f'Successfuly transitioned to {variation.request.status}', 'success')
        db.session.commit()
        return redirect(url_for('admin.reviewrequests_variation'))
    return render_template('admin/reviewrequests/variation/entry.html',variation=variation, staff=staff, form=form)

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

@admin.route('/admin/stafflist/staff/edit/<int:staff_id>', methods=['GET', 'POST'])
def stafflist_staff_edit(staff_id):
    staff = db.session.get(Staff,staff_id)
    pform = PersonForm(obj=staff)
    rform = RoleForm(obj=staff)
    if pform.validate_on_submit() and rform.validate_on_submit():
        pform.populate_obj(staff)
        rform.populate_obj(staff)
        db.session.commit()
        return redirect(url_for('admin.stafflist_staff',staff_id=staff.id))
    return render_template('admin/stafflist/staff/edit.html', staff=staff, pform=pform, rform=rform)
