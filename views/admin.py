from flask import Blueprint
from models import db, User, School, UserSchool, Staff, Variation
from forms import RegistrationForm, PersonForm, RoleForm
from flask import render_template, redirect, url_for, flash, request
from flask_login import login_required
from werkzeug.security import generate_password_hash

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


