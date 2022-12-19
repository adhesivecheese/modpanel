from flask import Blueprint, render_template, request
from flask_login import login_required

from .redditManager import get_instance

user = Blueprint('user', __name__)


@user.route('/user/<user>', methods=['GET', 'POST'])
@login_required
def load_user(user):
	r = get_instance()
	user = r.redditor(user)
	modSubs = []
	for sub in r.user.me().moderated():
		modSubs.append(sub.display_name.lower())
	new = []
	for item in user.new(limit=50):
		try:
			if item.pinned:
				setattr(item, "pin", True)
		except:
			...
		new.append([type(item).__name__, item])

	return render_template('user.jinja2', user=user, new=new, modSubs=modSubs)


@user.route('/user/<user>/more', methods=['GET', 'POST'])
@login_required
def load_more_user(user):
	thingID = request.form["thingID"]
	new = []
	for item in get_instance().redditor(user).new(limit=50, params={"after": thingID}):
		new.append([type(item).__name__, item])
	try:
		return render_template('user_more.jinja2', new=new)
	except:
		return '<button type="button" class="button is-link is-fullwidth" disabled>no more</button>'
