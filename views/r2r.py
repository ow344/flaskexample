from models import R2R, Role, Request, R2RMessage, db
from flask import render_template, session, redirect, url_for, flash
from flask_login import current_user
from forms import RequestForm, RoleForm, CommentForm, ApprovalForm
from . import models
from . import permissions
from .permissions import R2RPermissions
from utils import send_email

class R2RService:
    def __init__(self):
        pass

    def get_all_r2rs(self, is_admin, school_id):
        if is_admin:
            return R2R.query.all()
        else:
            return R2R.query.join(Role).filter(Role.school_id == school_id).all()

    def create_r2r(self, rform, rqform):
        r2r = R2R()
        r2r.role = Role()
        r2r.request = Request()
        rform.populate_obj(r2r.role)
        rqform.populate_obj(r2r)
        db.session.add(r2r)
        db.session.commit()
        send_email(current_user.username, r2r.role.role, r2r.role.school.name)

    def get_r2r(self, r2r_id):
        return db.session.get(R2R,r2r_id)

    def approve_r2r(self,r2r,aform):
        aform.populate_obj(r2r.request)
        db.session.commit()

    def update_r2r(self, r2r, rform, rqform):
        rform.populate_obj(r2r.role)
        rqform.populate_obj(r2r)
        db.session.commit()

    def delete_r2r(self, r2r):
        db.session.delete(r2r.request)
        db.session.delete(r2r.role)
        db.session.delete(r2r)
        db.session.commit()

    def get_r2r_messages(self, r2r_id):
        return R2RMessage.query.filter(R2RMessage.r2r_id == r2r_id).order_by(R2RMessage.id.desc()).all()

    def create_r2r_message(self, r2r_id, cform):
        r2rm = R2RMessage()
        cform.populate_obj(r2rm)
        r2rm.r2r_id = r2r_id
        db.session.add(r2rm)
        db.session.commit()

r2r_service = R2RService()
r2r_permissions = R2RPermissions()


@models.route('/r2r')
def r2r_list():
    r2rs = r2r_service.get_all_r2rs(current_user.is_admin, session.get('active_school_id', None))
    return render_template('models/r2r/list.html', r2rs=r2rs)
 
@models.route('/r2r/create', methods=['GET', 'POST'])
def r2r_create():
    rform = RoleForm()
    rqform = RequestForm()
    if rform.validate_on_submit() and rqform.validate_on_submit():
        r2r_service.create_r2r(rform, rqform)
        return redirect(url_for('models.r2r_list'))
    return render_template('models/r2r/credit.html', rform=rform, rqform=rqform)

@models.route('/r2r/read/<int:r2r_id>', methods=['GET'])
def r2r_read(r2r_id):
    r2r = r2r_service.get_r2r(r2r_id)
    if r2r_permissions.read(r2r):
        aform = ApprovalForm()
        comments = r2r_service.get_r2r_messages(r2r_id)
        cform = CommentForm()
        return render_template('models/r2r/read.html', r2r=r2r, aform=aform, cform=cform, comments=comments)
    return redirect(url_for('models.r2r_list'))
    

@models.route('/r2r/approve/<int:r2r_id>', methods=['POST'])
def r2r_approval(r2r_id):
    r2r = r2r_service.get_r2r(r2r_id)
    if not permissions.r2r_read(r2r):
        return redirect(url_for('models.r2r_list'))
    aform = ApprovalForm()
    if aform.validate_on_submit():
        r2r_service.approve_r2r(r2r, aform)
        flash(f'Status updated to {r2r.request.status}', 'success')
        return redirect(url_for('models.r2r_list'))
    return redirect(url_for('models.r2r_read',r2r_id=r2r.id))

@models.route('/r2r/update/<int:r2r_id>', methods=['GET', 'POST'])
def r2r_update(r2r_id):
    r2r = r2r_service.get_r2r(r2r_id)
    if not permissions.r2r_change(r2r):
        return redirect(url_for('models.r2r_list'))
    rform = RoleForm(obj=r2r.role)
    rqform = RequestForm(obj=r2r)
    if rform.validate_on_submit() and rqform.validate_on_submit():
        r2r_service.update_r2r(r2r,rform,rqform)
        return redirect(url_for('models.r2r_list'))
    return render_template('models/r2r/credit.html', r2r=r2r, rform=rform, rqform=rqform)

@models.route('/r2r/delete/<int:r2r_id>', methods=['POST'])
def r2r_delete(r2r_id):
    r2r = r2r_service.get_r2r(r2r_id)
    if not permissions.r2r_change(r2r):
        return redirect(url_for('models.r2r_list'))
    r2r_service.delete_r2r(r2r)
    return redirect(url_for('models.r2r_list'))

@models.route('/r2r/sendcomment/<int:r2r_id>', methods=['POST'])
def r2r_sendcomment(r2r_id):
    r2r = r2r_service.get_r2r(r2r_id)
    cform = CommentForm()
    if cform.validate_on_submit():
        r2r_service.create_r2r_message(r2r_id, cform)
        flash("Comment sent", "success")
    return redirect(url_for('models.r2r_read',r2r_id=r2r.id))
