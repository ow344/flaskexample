from models import R2R, Role
from flask import render_template, session
from flask_login import current_user
from . import models

@models.route('/r2rs')
def r2rs():
    if current_user.is_admin:
        r2rs = R2R.query.all()
    else:
        r2rs = R2R.query.join(Role).filter(Role.school_id == session['active_school_id']).all()
    return render_template('models/r2r/list.html', r2rs=r2rs)
    
