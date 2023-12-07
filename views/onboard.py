from models import R2R, Role, Request, Onboard, db, Staff
from flask import render_template, session, redirect, url_for, flash
from flask_login import current_user
from forms import PersonForm, ApporovalForm
from sqlalchemy import and_
from . import models
from . import permissions


@models.route('/onboard')
def onboard_list():
    if current_user.is_admin:
        onb = Onboard.query.all()
    else:
        onb = Onboard.query.join(R2R).join(Role).filter(Role.school_id == session['active_school_id']).all()
    return render_template('models/onboard/list.html', onb=onb)

@models.route('/onboard/select-r2r')
def onboard_select_r2r():
    if current_user.is_admin:
        r2rs = R2R.query.join(Request).join(Role).filter(Request.status=='Approved').all()
    else:
        r2rs = R2R.query.join(Request).join(Role).filter(and_(Request.status=='Approved', Role.school_id == session['active_school_id'])).all()
    return render_template('models/onboard/select_r2r.html', r2rs=r2rs)

@models.route('/onboard/create/<int:r2r_id>', methods=['GET', 'POST'])
def onboard_create(r2r_id):
    r2r = R2R.query.get_or_404(r2r_id)
    if not permissions.onboard_create(r2r):
        return redirect(url_for('models.onboard_list'))
    pform = PersonForm()
    if pform.validate_on_submit():
        onboard = Onboard()
        pform.populate_obj(onboard)
        r2r.request.status = 'Linked'
        onboard.r2r = r2r
        onboard.request = Request()
        db.session.add(onboard)
        db.session.commit()
        return redirect(url_for('models.onboard_list'))
    return render_template('models/onboard/credit.html', pform=pform, r2r=r2r)

@models.route('/onboard/read/<int:onboard_id>', methods=['GET', 'POST'])
def onboard_read(onboard_id):
    onboard = Onboard.query.get_or_404(onboard_id)
    if not permissions.onboard_read(onboard):
        return redirect(url_for('models.onboard_list'))
    aform = ApporovalForm(obj=onboard.request)
    if aform.validate_on_submit():
        if not permissions.onboard_change(onboard):
            return render_template('models/onboard/read.html', onboard=onboard, aform=aform)


        aform.populate_obj(onboard.request)
        flash(f'Status updated to {onboard.request.status}', 'success')
        if onboard.request.status == 'Approved':
            staff = Staff()
            staff.role = onboard.r2r.role
            for attribute in ['firstname','lastname','dob','gender','nino','nic','marital','home_address','postcode','email','startdate']:
                setattr(staff, attribute, getattr(onboard, attribute))
            db.session.add(staff)
            flash(f"{staff} added to staff list", "success")
        db.session.commit()
        return redirect(url_for('models.onboard_list'))
    return render_template('models/onboard/read.html', onboard=onboard, aform=aform)

@models.route('/onboard/update/<int:onboard_id>', methods=['GET', 'POST'])
def onboard_update(onboard_id):
    onboard = Onboard.query.get_or_404(onboard_id)
    if not permissions.onboard_change(onboard):
        return redirect(url_for('models.onboard_list'))
    pform = PersonForm(obj=onboard)
    if pform.validate_on_submit():
        pform.populate_obj(onboard)
        db.session.commit()
        return redirect(url_for('models.onboard_list'))
    return render_template('models/onboard/credit.html', pform=pform, r2r=onboard.r2r)

@models.route('/onboard/delete/<int:onboard_id>', methods=['POST'])
def onboard_delete(onboard_id):
    onboard = db.session.get(Onboard,onboard_id)
    if not permissions.onboard_change(onboard):
        return redirect(url_for('models.onboard_list'))
    db.session.delete(onboard.request)
    db.session.delete(onboard.role)
    db.session.delete(onboard)
    db.session.commit()
    return redirect(url_for('models.onboard_list'))

