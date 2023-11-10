from flask import Blueprint
from models import db, User

main = Blueprint('main', __name__)



@main.route('/')
def hello_world():
    u = db.session.get(User,1)
    return f"Sup {u.username}, hello world"
