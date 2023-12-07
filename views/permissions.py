from flask_login import current_user
from flask import render_template, session, redirect, url_for, flash
from models import R2R, Role, Request, Onboard, db, Staff



##### Multiple ######
def school_perm(school_id):
	return current_user.is_admin or school_id == session['active_school_id']
	
##### R2R #####
def r2r_read(r2r):
	if school_perm(r2r.role.school_id):
		return True
	flash("No permission to access Request to Recruit", "error")
	return False

def r2r_change(r2r):
	if r2r.request.status == "Pending":
		return True
	flash("Decision already made for Request to Recruit", "error")
	return False

##### Onboard #####
def onboard_create(r2r):
	con1 = r2r_read(r2r)
	con2 = r2r.request.status == 'Approved'
	if con1 and con2:
		return True
	if not con2:
		flash("Request to Recruit not approved to onboard", "error")
	return False

def onboard_read(onboard):
	if school_perm(onboard.r2r.role.school_id):
		return True
	flash("No permission to access Onboard Request", "error")
	return False

def onboard_change(onboard):
	if onboard.request.status == "Pending":
		return True
	flash("Decision already made for Onboarding Request", "error")
	return False


##### Variation #####
def variation_read(variation):
	if school_perm(variation.old_role.school_id):
		return True
	flash("No permission to access Variation", "error")
	return False

def variation_change(variation):
	if variation.request.status == "Pending":
		return True
	flash("Decision already made for Variation", "error")
	return False


##### Staff #####
def staff_read(staff):
	if school_perm(staff.role.school_id):
		return True
	flash("No permission to access Staff", "error")
	return False