from . import models
from flask import render_template, flash, redirect, url_for, session
from flask_login import current_user
from models import Staff, db, Role
from forms import PersonForm, RoleForm
from . import permissions
from flask import request
from utils import ChangeService

@models.route('/staff')
def staff_list():
    school_condition = True
    department_condition = True
    per_page = 50

    page = request.args.get('page', 1, type=int)
    schoolid = request.args.get('schoolid', 0, type=int)
    departmentid = request.args.get('departmentid', 0, type=int)

    if not current_user.is_admin:
        schoolid = session['active_school_id']
    if schoolid > 0:
        school_condition = Role.school_id == schoolid
    if departmentid > 0:
        department_condition = Role.department_id == departmentid

    staff = Staff.query.join(Role).filter(school_condition,department_condition).paginate(page=page, per_page=per_page)

    return render_template('models/staff/list.html', staff=staff, schoolid=schoolid, departmentid=departmentid)

@models.route('/staff/<int:staff_id>', methods=['GET'])
def staff(staff_id):
    staff = db.session.get(Staff,staff_id)

    if not permissions.staff_read(staff):
        return redirect(url_for('models.staff_list'))
    
    return render_template('models/staff/read.html', staff=staff)

@models.route('/staff/edit/<int:staff_id>', methods=['GET', 'POST'])
def staff_edit(staff_id):
    staff = db.session.get(Staff,staff_id)
    if not permissions.staff_read(staff):
        return redirect(url_for('models.staff_list'))
    pform = PersonForm(obj=staff)
    rform = RoleForm(obj=staff.role)
    if pform.validate_on_submit() and rform.validate_on_submit():
        with ChangeService(staff):
            pform.populate_obj(staff)
            rform.populate_obj(staff.role)
        # db.session.commit()
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


