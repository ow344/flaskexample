from flask import Blueprint
from flask_login import login_required
############################################## Models ##############################################
models = Blueprint('models', __name__)
@models.before_request
@login_required
def handle_route_permissions():
    if current_user.is_admin or 'active_school_id' in session:
        pass
    else:
        userschools = UserSchool.query.filter(and_(UserSchool.user_id==current_user.id, UserSchool.primary==True)).first()    
        session['active_school_id'] = userschools.school.id
        session['active_school_name'] = userschools.school.name

from .staff import *
from .departments import *
from .r2r import *
from .onboard import *
from .variation import *
############################################## Admin Models ##############################################
admin_models = Blueprint('admin_models', __name__)
@admin_models.before_request
@login_required
def handle_route_permissions():
    if not current_user.is_admin:
        flash("Log in as admin to access", "error")
        return redirect(url_for("main.index"))
    
from .user import *
############################################## Nav ##############################################
nav = Blueprint('nav', __name__)
@nav.before_request
@login_required
def handle_route_permissions():
    if current_user.is_admin or 'active_school_id' in session:
        pass
    else:
        userschools = UserSchool.query.filter(and_(UserSchool.user_id==current_user.id, UserSchool.primary==True)).first()    
        session['active_school_id'] = userschools.school.id
        session['active_school_name'] = userschools.school.name

from .navigation import *
############################################## Log ##############################################
log = Blueprint('log', __name__)
@log.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    form.next_page.data = request.args.get('next')
    if form.validate_on_submit():
        flash("Login successful", "success")
        user = User.query.filter_by(username=form.username.data).first()
        login_user(user, remember=True)
        return redirect(form.next_page.data or url_for('nav.index'))
    return render_template('navigation/login.html', form=form)
