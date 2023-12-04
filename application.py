from flask import Flask
from config import Config
from models import db
from views import main, admin, user, models
from flask_migrate import Migrate
from flask_login import LoginManager
from models import User


application = Flask(__name__)
application.config.from_object(Config)
db.init_app(application)
application.register_blueprint(main)
application.register_blueprint(admin)
application.register_blueprint(user)
application.register_blueprint(models)

migrate = Migrate(application, db)


login_manager = LoginManager()
login_manager.login_view = 'main.login'
login_manager.login_message = "User needs to be logged in to view this page"
login_manager.login_message_category = "error"
login_manager.init_app(application)


@login_manager.user_loader
def load_user(user_id):
    # since the user_id is just the primary key of our user table, use it in the query for the user
    return db.session.get(User,int(user_id))