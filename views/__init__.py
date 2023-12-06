from flask import Blueprint
from flask_login import login_required

# Defining blueprints
main = Blueprint('main', __name__)
admin = Blueprint('admin', __name__)
user1 = Blueprint('user', __name__)
models = Blueprint('models', __name__)
admin_models = Blueprint('admin_models', __name__)
nav = Blueprint('nav', __name__)

# Rules for blueprints
@admin_models.before_request
@login_required
def handle_route_permissions():
    if not current_user.is_admin:
        flash("Log in as admin to access", "error")
        return redirect(url_for("main.index"))





@models.before_request
@login_required
def handle_route_permissions():
    if current_user.is_admin or 'active_school_id' in session:
        pass
    else:
        userschools = UserSchool.query.filter(and_(UserSchool.user_id==current_user.id, UserSchool.primary==True)).first()    
        session['active_school_id'] = userschools.school.id
        session['active_school_name'] = userschools.school.name

@nav.before_request
@login_required
def handle_route_permissions():
    if current_user.is_admin or 'active_school_id' in session:
        pass
    else:
        userschools = UserSchool.query.filter(and_(UserSchool.user_id==current_user.id, UserSchool.primary==True)).first()    
        session['active_school_id'] = userschools.school.id
        session['active_school_name'] = userschools.school.name


# Importing views here to avoid circular import
from .main import *
from .admin import *
from .user1 import *

from .staff import *
from .departments import *
from .r2r import *
from .onboard import *
from .variation import *

from .user import *

from .navigation import *
