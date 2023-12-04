from models import Department, R2R, Role
from flask import render_template, session
from flask_login import current_user, login_required
from flask import render_template
from models import Department, R2R
from . import models

@models.before_request
@login_required
def handle_route_permissions():
    pass


@models.route('/departments')
def departments():
    return render_template('models/department/list.html', departments=Department.query.all())

@models.route('/r2rs')
def r2rs():
    if current_user.is_admin:
        r2rs = R2R.query.all()
    else:
        r2rs = R2R.query.join(Role).filter(Role.school_id == session['active_school_id']).all()
    return render_template('models/r2r/list.html', r2rs=r2rs)
    
