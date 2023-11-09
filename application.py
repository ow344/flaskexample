from os import environ, path
from dotenv import load_dotenv
basedir = path.abspath(path.dirname(__file__))
load_dotenv(path.join(basedir, '.env'))
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()
application = Flask(__name__)
application.config["SQLALCHEMY_DATABASE_URI"] = environ.get('MYSQLCREDS')
db.init_app(application)



class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    hashed_password = db.Column(db.String(200), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    def __repr__(self):
        return f'{self.username}'



@application.route('/')
def hello_world():
    u = db.session.get(User,1)
    return f"Sup {u.username}, hello world"



