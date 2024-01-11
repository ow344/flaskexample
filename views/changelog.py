from models import Department
from flask import render_template
from . import models

@models.route('/changelog')
def changelog():
    return render_template('models/changelog/list.html', departments=Department.query.all())
