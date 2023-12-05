from flask import Blueprint
from flask_login import login_required

# Defining blueprints
main = Blueprint('main', __name__)
admin = Blueprint('admin', __name__)
user = Blueprint('user', __name__)
models = Blueprint('models', __name__)

# Rules for blueprints
@models.before_request
@login_required
def handle_route_permissions():
    pass

# Importing views here to avoid circular import
from .main import *
from .admin import *
from .user import *

from .staff import *
from .departments import *
from .r2r import *
from .onboard import *
