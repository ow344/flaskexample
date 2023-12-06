from models import R2R, Role, Request, R2RMessage, Onboard, Variation, Staff, School, UserSchool, User, db
from flask import render_template, session, redirect, url_for, flash, request, jsonify
from flask_login import current_user
from forms import RequestForm, RoleForm, CommentForm, PersonForm, ApporovalForm
from sqlalchemy import and_, or_


from . import models

@models.route('/variation')
def variation_list():
    if current_user.is_admin:
        variations = Variation.query.all()
    else:
        variations = Variation.query.join(Role, onclause=Variation.new_role_id == Role.id).filter(Role.school_id == session['active_school_id']).all()
    return render_template('models/variation/list.html', variations=variations)

@models.route('/variation/select-employee', methods=['GET', 'POST'])
def variation_select_employee():
    if request.method == 'POST':
        return redirect(url_for('models.variation_create', staff_id=request.form['staff_id']))
    return render_template('models/variation/selectemployee.html')

@models.route('/variation/create/<int:staff_id>', methods=['GET', 'POST'])
def variation_create(staff_id):
    staff = db.session.get(Staff, staff_id)
    rform = RoleForm(obj=staff.role)
    rqform = RequestForm()
    if rform.validate_on_submit() and rqform.validate_on_submit():

        new_role = Role()
        rform.populate_obj(new_role)
        new_role.school_id = staff.role.school_id
        
        variation = Variation()
        rqform.populate_obj(variation)
        variation.request = Request()
        variation.old_role = staff.role
        variation.new_role = new_role
        variation.staff_id = staff_id

        db.session.add(variation)
        db.session.commit()

        flash("Variation created successfully", "success")
        return redirect(url_for('models.variation_list'))
    return render_template('models/variation/create.html', rform=rform, staff=staff, rqform=rqform)

@models.route('/variation/read/<int:variation_id>', methods=['GET', 'POST'])
def variation_read(variation_id):
    variation = db.session.get(Variation, variation_id)
    staff = variation.staff
    aform = ApporovalForm()
    if aform.validate_on_submit():
        if variation.request.status == 'Approved':
            flash(f'Variation already approved', 'error')
            return redirect(url_for('models.variation_list'))
        aform.populate_obj(variation.request)
        flash(f'Status updated to {variation.request.status}', 'success')
        if variation.request.status == 'Approved':
            staff.role = variation.new_role
            flash(f'Variation applied to {staff.firstname} {staff.lastname}', 'success')
        db.session.commit()
        return redirect(url_for('models.variation_list'))
    return render_template('models/variation/read.html', variation=variation, staff=staff, aform=aform)






@models.route('/variation/update/<int:variation_id>', methods=['GET', 'POST'])
def variation_update(variation_id):
    variation = db.session.get(Variation, variation_id)
    if not current_user.is_admin or variation.request.status != 'Pending':
        flash(f'Request has been progressed and can no longer be changed', 'error')
        return redirect(url_for('models.variation_list'))
    staff = variation.staff
    rform = RoleForm(obj=variation.new_role)
    rqform = RequestForm(obj=variation)
    if rform.validate_on_submit() and rqform.validate_on_submit():
        rform.populate_obj(variation.new_role)
        rqform.populate_obj(variation)
        db.session.commit()
        flash("Variation updated successfully", "success")
        return redirect(url_for('models.variation_list'))
    return render_template('models/variation/create.html', rform=rform, rqform=rqform, staff=staff)











@models.route('/variation/delete/<int:variation_id>', methods=['POST'])
def variation_delete(variation_id):
    variation = db.session.get(Variation, variation_id)
    if not current_user.is_admin or variation.request.status != 'Pending':
        flash(f'Request has been progressed and can no longer be changed', 'error')
        return redirect(url_for('models.variation_list'))
    request = variation.request
    role = variation.new_role

    db.session.delete(request)
    db.session.delete(role)
    db.session.delete(variation)
    db.session.commit()
    flash("Variation deleted successfully", "success")
    return redirect(url_for('models.variation_list'))











@models.route('/update_text1', methods=['POST'])
def update_text():
    text = request.get_json().get('text').split(" ")
    if len(text) == 1:
        text.append("")
    if current_user.is_admin:
        results = Staff.query.filter(or_(
            and_(Staff.firstname.like(f"%{text[0]}%"), Staff.lastname.like(f"%{text[1]}%")),
            and_(Staff.firstname.like(f"%{text[1]}%"), Staff.lastname.like(f"%{text[0]}%"))
        )).all()
        staff_list = [{'id': member.id, 'firstname': str(f"{member.firstname} {member.lastname} ({member.school.name})")} for member in results]
    else:
        results = Staff.query.filter(and_(
            Staff.school_id == session['active_school_id'],
            or_(
            and_(Staff.firstname.like(f"%{text[0]}%"), Staff.lastname.like(f"%{text[1]}%")),
            and_(Staff.firstname.like(f"%{text[1]}%"), Staff.lastname.like(f"%{text[0]}%"))
        )
            )).all()
        staff_list = [{'id': member.id, 'firstname': str(member.firstname + " " + member.lastname)} for member in results]


    return jsonify(staff_list)