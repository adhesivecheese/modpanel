from uuid import uuid4
from flask import (Blueprint, abort, flash, redirect, render_template,
				   request, url_for, current_app)
from flask_login import current_user, login_required, login_user, logout_user
from werkzeug.security import check_password_hash, generate_password_hash

from .redditManager import get_auth_instance

from . import db
from .models import User


auth = Blueprint('auth', __name__)


@auth.route('/login', methods=('GET', 'POST'))
def login():
	allUsers = User.query.all()
	if len(allUsers) == 0: signup()

	"""Handles Logging in a user"""
	if request.method == 'POST':
		name = request.form.get('name')
		password = request.form.get('password')
		remember = True if request.form.get('remember') else False
		user = User.query.filter_by(name=name).first()
		if not user or not check_password_hash(user.password, password):
			flash('Please check your login details and try again.')
			return redirect(url_for('auth.login'))
		login_user(user, remember=remember)
		return redirect(url_for('auth.authorize'))
	else:
		return render_template('login.jinja2')


@auth.route('/authorize')
def authorize():
	"""Generates the Authorize with Reddit template"""
	user = User.query.filter_by(name=current_user.name).first()
	try:
		if user.token:
			return redirect(url_for('main.index'))
		state = str(uuid4())
		User.query.filter_by(name=current_user.name).update(
			{User.state: state},
			synchronize_session=False
		)
		db.session.commit()
		return render_template(
			'authorize.jinja2',
			auth_link=get_auth_instance().auth.url(
				current_app.config['SCOPE'],
				state,
				"permanent"
			)
		)
	except: return render_template('error.jinja2', error="Your account is not activated. Please contact your modpanel admin for account activation")


@auth.route('/authorize_callback')
def authorized_callback():
	"""Post-Authorization function. Assuming state matches what was sent,
	Saves the OAuth token for the user.
	"""
	state = request.args.get('state', '')
	code = request.args.get('code', '')
	# Return a 403 error if state doesn't match
	saved_state = User.query.filter_by(
		name=current_user.name
	).first().state
	if saved_state != state:
		abort(403)
	refresh_token = get_auth_instance().auth.authorize(code)
	User.query.filter_by(
		name=current_user.name
	).update(
		{User.token: refresh_token},
		synchronize_session=False
	)
	db.session.commit()
	return redirect(url_for('main.index'))


@auth.route('/signup', methods=('GET', 'POST'))
def signup():
	"""Handles Signup"""
	if request.method == 'POST':
		name = request.form.get('name')
		password = request.form.get('password')
		password_confirm = request.form.get('password_confirm')
		if password != password_confirm:
			flash('Passwords do not match')
			return redirect(url_for('auth.signup'))
		user = User.query.filter_by(name=name).first()
		if user:
			flash(f'Username "{user}" already exists')
			return redirect(url_for('auth.signup'))

		allUsers = User.query.all()
		if len(allUsers) == 0:
			isAdmin = True
			isActive = True
		else:
			isAdmin = False
			isActive = current_app.config['NEW_ACCOUNTS_ACTIVE']

		new_user = User(
			name=name,
			password=generate_password_hash(password, method='sha256'),
			active=isActive,
			admin=isAdmin
		)
		db.session.add(new_user)
		db.session.commit()
		return redirect(url_for('auth.login'))
	else:
		return render_template('signup.jinja2')


@auth.route('/logout')
@login_required
def logout():
	"""Log out the currently logged in user"""
	logout_user()
	return redirect(url_for('main.index'))
