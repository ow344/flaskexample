from . import models
from flask import render_template, flash, redirect, url_for, session
from flask_login import current_user
from models import Staff, db
from forms import PersonForm, RoleForm

@models.route('/staff')
def staff_list():
    if current_user.is_admin:
        staff=Staff.query.all()
    else:
        staff=Staff.query.filter_by(school_id=session['active_school_id']).all()
    return render_template('models/staff/list.html', staff=staff)

@models.route('/staff/<int:staff_id>', methods=['GET'])
def staff(staff_id):
    if not access_to_staff(staff_id):
        flash('You do not have permission to access this staff record.', 'error')
        return redirect(url_for('models.staff_list'))
    
    staff = db.session.get(Staff,staff_id)
    return render_template('models/staff/read.html', staff=staff)

@models.route('/staff/edit/<int:staff_id>', methods=['GET', 'POST'])
def staff_edit(staff_id):
    staff = db.session.get(Staff,staff_id)
    pform = PersonForm(obj=staff)
    rform = RoleForm(obj=staff.role)
    if pform.validate_on_submit() and rform.validate_on_submit():
        pform.populate_obj(staff)
        rform.populate_obj(staff.role)
        db.session.commit()
        flash('Staff record updated successfully.', 'success')
        return redirect(url_for('models.staff_list'))
    return render_template('models/staff/edit.html', staff=staff, pform=pform, rform=rform)


@models.route('/staff/delete/<int:staff_id>', methods=['GET','POST'])
def staff_delete(staff_id):
    if not current_user.is_admin:
        flash('You do not have permission to edit this staff record.', 'error')
        return redirect(url_for('models.staff_list'))
    staff = db.session.get(Staff,staff_id)
    db.session.delete(staff)
    db.session.commit()
    flash("Successfully deleted staff record", "success")
    return redirect(url_for('models.staff_list'))



def access_to_staff(staff_id):
    if current_user.is_admin:
        return True
    staff = db.session.get(Staff,staff_id)
    if staff.role.school_id == session['active_school_id']:
        return True
    return False