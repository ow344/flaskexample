from models import R2R, Role, Request, R2RMessage
from flask import render_template, session, redirect, url_for, flash, request
from flask_login import current_user
from forms import RequestForm, RoleForm, CommentForm, PersonForm, ApporovalForm
from models import db


from . import models

@models.route('/r2rs')
def r2r_list():
    if current_user.is_admin:
        r2rs = R2R.query.all()
    else:
        r2rs = R2R.query.join(Role).filter(Role.school_id == session['active_school_id']).all()
    return render_template('models/r2r/list.html', r2rs=r2rs)
    
@models.route('/r2r/create', methods=['GET', 'POST'])
def r2r_create():
    rform = RoleForm()
    rqform = RequestForm()
    if rform.validate_on_submit() and rqform.validate_on_submit():
        r2r = R2R()
        r2r.role = Role()
        r2r.request = Request()
        rform.populate_obj(r2r.role)
        rqform.populate_obj(r2r)
        db.session.add(r2r)
        db.session.commit()
        return redirect(url_for('models.r2r_list'))

    return render_template('models/r2r/credit.html', rform=rform, rqform=rqform)

@models.route('/r2r/read/<int:r2r_id>', methods=['GET', 'POST'])
def r2r_read(r2r_id):
    r2r = R2R.query.get_or_404(r2r_id)
    rform = RoleForm(obj=r2r.role)
    rqform = RequestForm(obj=r2r)
    aform = ApporovalForm()
    cform = CommentForm()
    comments = R2RMessage.query.filter(R2RMessage.r2r_id==r2r_id).order_by(R2RMessage.id.desc()).all()
    if aform.validate_on_submit():
        aform.populate_obj(r2r.request)
        db.session.commit()
        flash(f'Status updated to {r2r.request.status}', 'success')
        return redirect(url_for('models.r2r_list'))
    return render_template('models/r2r/read.html', r2r=r2r, rform=rform, rqform=rqform, aform=aform, cform=cform, comments=comments)


@models.route('/r2r/update/<int:r2r_id>', methods=['GET', 'POST'])
def r2r_update(r2r_id):
    r2r = R2R.query.get_or_404(r2r_id)
    if r2r.request.status != 'Pending' and not current_user.is_admin:
        flash(f'Request has been progressed and can no longer be changed', 'error')
        return redirect(url_for('models.r2r_list'))
    rform = RoleForm(obj=r2r.role)
    rqform = RequestForm(obj=r2r)
    if rform.validate_on_submit() and rqform.validate_on_submit():
        rform.populate_obj(r2r.role)
        rqform.populate_obj(r2r)
        # db.session.add(r2r)
        db.session.commit()
        return redirect(url_for('models.r2r_list'))

    return render_template('models/r2r/credit.html', r2r=r2r, rform=rform, rqform=rqform)

@models.route('/r2r/delete/<int:r2r_id>', methods=['POST'])
def r2r_delete(r2r_id):
    r2r = R2R.query.get_or_404(r2r_id)
    db.session.delete(r2r)
    db.session.commit()
    return redirect(url_for('models.r2r_list'))


@models.route('/r2r/sendcomment/<int:r2r_id>', methods=['POST'])
def r2r_sendcomment(r2r_id):
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
    return redirect(url_for('models.r2r_read',r2r_id=r2r.id))