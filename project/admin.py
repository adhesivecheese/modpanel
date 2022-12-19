from flask import Blueprint, abort, render_template, request
from flask_login import current_user, login_required

from . import db
from .models import User

admins = Blueprint('admin', __name__)


def handle_HTTPPOST_request(request):
	for key in request.form.keys():
		username = key.split("-")[0]
		action = key.split("-")[1]
		value = request.form[key]
		user = User.query.filter_by(name=username).first()
		if action == "role":
			if value == "admin": user.admin = True
			else: user.admin = False
		if action == "active":
			if value == "active": user.active = True
			else: user.active = False
		if action == "deleteToken":	user.token = None
		if action == "deleteUser": db.session.delete(user)
		db.session.commit()


@admins.route('/admin', methods=('GET', 'POST'))
@login_required
def admin():
	if not current_user.is_admin:
		abort(403)
	if request.method == "POST":
		handle_HTTPPOST_request(request)
	all = User.query.all()
	users = []

	for user in all:
		users.append({
			"name": user.name,
			"active": user.active,
			"admin": user.admin
		})

	return render_template('admin.jinja2', users=users)
