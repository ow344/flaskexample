from models import Department
from flask import render_template
from . import models

@models.route('/departments')
def departments():
    return render_template('models/department/list.html', departments=Department.query.all())
