from models import R2R, Role, Request, Onboard, db
from flask import render_template, session, redirect, url_for, flash
from flask_login import current_user
from forms import PersonForm, ApporovalForm
from sqlalchemy import and_
from . import models

@models.route('/onboard')
def onboard_list():
    if current_user.is_admin:
        onb = Onboard.query.all()
    else:
        onb = Onboard.query.join(R2R).join(Role).filter(Role.school_id == session['active_school_id']).all()
    return render_template('models/onboard/list.html', onb=onb)

@models.route('/onboard/select-r2r')
def onboard_select_r2r():
    r2rs = R2R.query.join(Request).join(Role).filter(and_(Request.status=='Approved', Role.school_id == session['active_school_id'])).all()
    return render_template('models/onboard/select_r2r.html', r2rs=r2rs)

@models.route('/onboard/create/<int:r2r_id>', methods=['GET', 'POST'])
def onboard_create(r2r_id):
    r2r = R2R.query.get_or_404(r2r_id)
    if not perm_check_r2r(r2r):
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
    if not perm_check_onboard(onboard):
        return redirect(url_for('models.onboard_list'))
    aform = ApporovalForm()
    if aform.validate_on_submit():
        aform.populate_obj(onboard.request)
        db.session.commit()
        flash(f'Status updated to {onboard.request.status}', 'success')
        return redirect(url_for('models.onboard_list'))
    return render_template('models/onboard/read.html', onboard=onboard, aform=aform)

@models.route('/onboard/update/<int:onboard_id>', methods=['GET', 'POST'])
def onboard_update(onboard_id):
    onboard = Onboard.query.get_or_404(onboard_id)
    if not perm_check_onboard(onboard):
        return redirect(url_for('models.onboard_list'))
    pform = PersonForm(obj=onboard)
    if pform.validate_on_submit():
        pform.populate_obj(onboard)
        db.session.commit()
        return redirect(url_for('models.onboard_list'))
    return render_template('models/onboard/credit.html', pform=pform, r2r=onboard.r2r)

@models.route('/onboard/delete/<int:onboard_id>', methods=['POST'])
def onboard_delete(onboard_id):
    onboard = Onboard.query.get_or_404(onboard_id)
    onboard.r2r.request.status = 'Approved'
    db.session.delete(onboard.request)
    db.session.delete(onboard)
    db.session.commit()
    return redirect(url_for('models.onboard_list'))

def perm_check_r2r(r2r):
    if not current_user.is_admin:
        cond1 = r2r.role.school_id != session['active_school_id']
        cond2 = r2r.request.status != 'Approved'
        if cond1 or cond2:
            flash('You do not have permissions to make changes here', 'error')
            return False     
    return True

def perm_check_onboard(onboard):
    if not current_user.is_admin:
        cond1 = onboard.r2r.role.school_id != session['active_school_id']
        cond2 = onboard.request.status != 'Pending'
        if cond1 or cond2:
            flash('You do not have permissions to make changes here', 'error')
            return False     
    return True