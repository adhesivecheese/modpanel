from .redditManager import get_instance
from flask import (Blueprint, render_template, request)
import markdown
import urllib
import json
from html_diff import diff as df
from urllib.parse import quote

diff = Blueprint('diff', __name__)


class Submission:
	def __init__(self, author, id, selftext, title, url, subreddit, created_utc):
		self.author = author
		self.id = id
		self.selftext = selftext
		self.html = markdown.markdown(selftext)
		self.title = title
		self.subreddit = subreddit
		self.created_utc = created_utc
		self.url = url


@diff.route('/postdiff/<post_id>', methods=('GET', 'POST'))
def displaySettings(post_id):
	r = get_instance()
	with urllib.request.urlopen(f"https://api.pushshift.io/reddit/search/submission/?ids={post_id}") as url:
		data = json.loads(url.read().decode())
		pushshift = data['data'][0]
		pushshift = Submission(
			author=pushshift['author'],
			id=pushshift['id'],
			selftext=pushshift['selftext'],
			title=pushshift['title'],
			url=pushshift['url'],
			subreddit=pushshift['subreddit'],
			created_utc=pushshift['created_utc']
		)
	reddit = r.submission(id=post_id)
	live_html = markdown.markdown(reddit.selftext)
	diff_html = df(pushshift.html, live_html)

	setattr(reddit, "diff", diff_html)
	setattr(reddit, "pushshift", pushshift.html)
	setattr(reddit, "current", live_html)
	base = request.base_url
	base = base.rsplit("/",1)[0] + "/"
	base = quote(base, safe='')
	return render_template('postdiff.jinja2', post=reddit, url=base)
