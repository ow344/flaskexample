from flask import Blueprint

# Defining blueprints
main = Blueprint('main', __name__)
admin = Blueprint('admin', __name__)
user = Blueprint('user', __name__)
models = Blueprint('models', __name__)
sample_blueprint = Blueprint('sample_blueprint', __name__)

# Importing views here to avoid circular import
from .staff import *
from .main import *
from .admin import *
from .user import *
from .models import *
