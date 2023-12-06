from . import admin_models
from flask import render_template, flash, redirect, url_for, session, request
from flask_login import current_user
from models import Staff, db, User, UserSchool, School
from forms import PersonForm, RoleForm, RegistrationForm
from werkzeug.security import generate_password_hash

@admin_models.route('/user')
def user_list():
    users = User.query.all()
    return render_template('models/user/list.html', users=users)


@admin_models.route('/user/edit/<int:user_id>', methods=['GET', 'POST'])
def user_update(user_id):
    user = User.query.get_or_404(user_id)
    schools = School.query.all()

    if request.method == 'POST':
        if request.form.get('admin'):
            user.is_admin = True
            for usl in user.user_schools:
                db.session.delete(usl)
        else:
            user.is_admin = False
            for school in schools:
                default_value = 0
                primary_B = str(school.id) == request.form.get("default", default_value)
                basic_B = request.form.get(f"basic-{school.id}", default_value) == "on"
                finance_B = request.form.get(f"finance-{school.id}", default_value) == "on"
                user_school_entry = UserSchool.query.filter_by(user_id=user.id,school_id=school.id).first()
                if any([basic_B,primary_B,finance_B]):
                    if user_school_entry:
                        user_school_entry.primary = primary_B
                        user_school_entry.finance = finance_B
                    else:
                        user_school_entry = UserSchool(user_id=user.id,school_id=school.id,
                                                    primary=primary_B,finance=finance_B)
                        db.session.add(user_school_entry)
                elif user_school_entry:
                    db.session.delete(user_school_entry)

        db.session.commit()
        flash("User updated", "success")
        return redirect(url_for('admin_models.user_list'))


    primary = [i.school_id for i in UserSchool.query.filter_by(user_id=user.id, primary=True).all()]
    basic = [i.school_id for i in UserSchool.query.filter_by(user_id=user.id).all()]
    finance = [i.school_id for i in UserSchool.query.filter_by(user_id=user.id, finance=True).all()]
    return render_template('models/user/update.html', user=user, schools=schools, primary=primary, basic=basic, finance=finance)

@admin_models.route('/user/create', methods=['GET', 'POST'])
def user_create():
    form = RegistrationForm()
    if form.validate_on_submit():
        newU = User()
        form.populate_obj(newU)
        newU.hashed_password = generate_password_hash(form.password.data)
        db.session.add(newU)
        db.session.commit()
        flash("New user created", "success")
        return redirect(url_for('admin_models.user_list'))
    return render_template('models/user/create.html', form=form)

@admin_models.route('/user/delete/<int:user_id>', methods=['POST'])
def user_delete(user_id):
    user = User.query.get_or_404(user_id)
    db.session.delete(user)
    db.session.commit()
    flash("User deleted", "success")
    return redirect(url_for('admin_models.user_list'))