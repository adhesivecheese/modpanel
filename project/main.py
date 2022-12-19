from flask import Blueprint, render_template
from flask_login import login_required

from .redditManager import get_instance
from .auth import authorize

main = Blueprint('main', __name__)


@main.route('/', methods=['GET', 'POST'])
@login_required
def index():
	r = get_instance()
	moderated = r.user.me().moderated()
	#try:
	#	moderated = r.user.me().moderated()
	#except:
	#	return authorize()
	modsubs = []
	for sub in moderated:
		count = 0
		for _ in sub.mod.modqueue():
			count += 1
		modsubs.append([sub, count])
	return render_template('index.jinja2', subreddits=modsubs, mod=r.user.me().name)


@main.route('/about')
def about():
	return render_template('about.jinja2')