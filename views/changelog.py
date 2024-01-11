from models import Department, Changelog
from flask import render_template
from . import models

@models.route('/changelog')
def changelog():
    return render_template('models/changelog/list.html', changes=Changelog.query.all())
