import re
from datetime import datetime
from urllib.parse import unquote
from time import mktime, time

import markdown
import pmtw
from flask import Blueprint, Response, render_template, request
from flask_login import login_required
from loguru import logger
from urlextract import URLExtract
from psaw import PushshiftAPI

from . import create_app
from .redditManager import get_instance
from .wikihandler import Modpanel
from .auth import authorize

queue = Blueprint('queue', __name__)


def add_hyperlinks(text):
	extractor = URLExtract()
	for url in extractor.gen_urls(text):
		if "http" not in url:
			prefixedurl = "http://" + url
		else:
			prefixedurl = url
		prefixedurl = prefixedurl.strip("'")
		text = text.replace(url, f"<a href='{prefixedurl}'>{url}</a>", 1)
	return text


def get_settings(r, sub):
	removalReasons = []
	noteTypes = []
	noteActions = {}
	mpSettings = Modpanel(sub).settings
	tbSettings = pmtw.Settings(r, sub)
	if tbSettings.settingsJSON["ver"] != 1:
		return f"Toolbox Schema Version Mismatch. Required is 1, got version {tbSettings.settingsJSON['ver']}"
	notes = pmtw.Usernotes(r, sub)
	if notes.usernotesJSON["ver"] != 6:
		return f"Toolbox Usernotes Schema Mismatch. Required is 6, got version {notes.usernotesJSON['ver']}"
	count = 0
	for reason in tbSettings.get_reasons():
		setattr(reason, "html", "")
		setattr(reason, "count", count)
		reason.html = reason.text.replace(
			"<select ",
			f"<select style='width:100%' name='r{count}_subr'"
		)
		subcount = 0
		for x in reason.html:
			reason.html = reason.html.replace("<option", f"< option value='{subcount}'", 1)
			subcount += 1
		reason.html = reason.html.replace("< option", "<option")
		reason.html = reason.html.replace("<textarea ", f"<textarea name='r{count}-custom'")
		reason.html = reason.html.replace("\[", "[")
		reason.html = reason.html.replace("\]", "]")
		reason.html = reason.html.replace("\(", "(")
		reason.html = reason.html.replace("\)", ")")

		reason.html = markdown.markdown(reason.html)
		matches = re.findall("<select(?s).*<\/select>", reason.text)
		if len(matches) > 0:
			for match in matches:
				reason.text = reason.text.replace(match, "")
				submatches = re.findall("<option>.*</option>", match)
				subcount = 0
				for submatch in submatches:
					submatch = submatch.replace("<option>", "").replace("</option>", "")
					setattr(reason, f"r{count}s{subcount}", submatch)
					subcount += 1
		setattr(reason, "index", count)
		if reason not in removalReasons:
			removalReasons.append(reason)
		count += 1

	for type in tbSettings.get_usernoteColors():
		if type not in noteTypes:
			noteTypes.append(type)
	if noteActions == {}:
		noteDisplay = mpSettings.noteActions
		for n in noteDisplay:
			noteActions[n.key] = n.action

	return {
		"noteTypes": noteTypes,
		"removalReasons": removalReasons,
		"mpSettings": mpSettings,
		"notes": notes
	}


@logger.catch
def handle_HTTPPOST_request(r, request, removalReasons, notes):
	action = request.form["action"]
	postID = request.form["postID"]


	try:
		actionItem = r.comment(postID)
		body = actionItem.body  # only comments have a body field
		actionItem.kind = "comment"
	except:
		actionItem = r.submission(postID)
		actionItem.kind = "submission"

	if action == "approve":
		actionItem.mod.approve()
	elif action == "quickRemove":
		remove_post(request, actionItem)
	elif action == "remove":
		remove_post(request, actionItem)
		send_notice(request, removalReasons, actionItem)
		add_note(request, actionItem, notes)
		if ("ban", "true") in request.form.items():
			ban_user(request, actionItem)
	elif action == "addNote":
		add_note(request, actionItem, notes)
	elif action == "deleteNote":
		delete_note(request, notes)
	elif action == "banuser":
		remove_post(request, actionItem)
		ban_user(request, actionItem)
		if ("wipe", "on") in request.form.items():
			wipe_history(actionItem)


@logger.catch
def send_notice(request, removalReasons, actionItem):
	r = actionItem._reddit
	sub = actionItem.subreddit
	settings = pmtw.Settings(r, sub)
	removals_info = settings.get_removalReasons()
	removalIndex = []

	for key in request.form.keys():
		if key.startswith("removal-"):
			if int(key.split("removal-")[1]) not in removalIndex:
				removalIndex.append(int(key.split("removal-")[1]))

	header = removals_info.header
	header = header.format(author=actionItem.author.name, kind=actionItem.kind, url=actionItem.permalink)

	removalText = ""
	for reason in removalReasons:
		if reason.index in removalIndex:
			if reason.text.startswith("<textarea"):
				removalText += request.form[f"r{reason.index}-custom"] + "\n"
			else:
				removalText += reason.text + "\n"
			try:
				subreason = str(request.form[f'r{reason.index}_subr'])
				subrule = f"r{reason.index}s{subreason}"
				removalText += getattr(reason, subrule) + "\n\n"
			except:
				continue

	removalMessage = f"""{header}\n\n{removalText}\n\n{removals_info.footer}\n\n---\n\n[[link to your {actionItem.kind}]({actionItem.permalink})]"""

	try:
		if removals_info.typeReply == "pm":
			typeAsSub = removals_info.typeAsSub
			conversation = sub.modmail.create(str(removals_info.pmsubject), removalMessage, str(actionItem.author), typeAsSub)
			if removals_info.autoArchive is True:
				conversation.archive()
		elif removals_info.typeReply == "reply":
			actionItem.reply(removalMessage)
		elif removals_info.typeReply == "both":
			typeAsSub = removals_info.typeAsSub
			sub.modmail.create(str(removals_info.pmsubject), removalMessage, str(actionItem.author), typeAsSub)
			actionItem.reply(removalMessage)
	except:
		logger.warning("failed to send removal notice")


@logger.catch
def remove_post(request, actionItem):
	spamPost = False
	if ("type", "spam") in request.form.items():
		spamPost = True
	try:
		actionItem.mod.remove(spam=spamPost)
		logger.debug(f"removed post {actionItem}")
	except:
		logger.warning("failed to remove Item")


@logger.catch
def add_note(request, actionItem, notes):
	warnType = request.form['warnType']
	noteText = unquote(request.form['noteText'])
	try:
		n = pmtw.Note(user=actionItem.author.name, note=noteText, link=f"https://reddit.com/{actionItem.id}", warning=warnType)
		notes.add_note(n)
		logger.debug(f"Added {n} on user {actionItem.author.name}")
	except:
		logger.warning(f"failed to add note '{noteText}' on user {actionItem.author.name}")


@logger.catch
def delete_note(request, notes):
	try:
		user = request.form["user"]
		timestamp = int(request.form["timestamp"])
		notes.delete_note(user, timestamp)
		logger.info(f"Deleted note on {user} timestamped {timestamp}")
	except:
		logger.warning(f"Failed to delete note on {user} timestamped {timestamp}")

@logger.catch
def ban_user(request, actionItem):
	if "banlength" in request.form.keys():
		banLength = int(request.form["banlength"])
	else:
		banLength = "permban"
	sub = actionItem.subreddit
	if 'noteText' in request.form.keys():
		banNote = unquote(request.form['noteText'])
	else:
		banNote = ""
	if 'banmessage' in request.form.keys():
		banMessage = unquote(request.form['banmessage'])
	else:
		banMessage = ""

	try:
		if banLength == "permban":
			if banMessage == "":
				sub.banned.add(actionItem.author.name, note=banNote)
			else:
				sub.banned.add(actionItem.author.name, note=banNote, ban_message=banMessage)
			logger.debug(f"Banned user {actionItem.author.name} - permanent")
		else:
			if banMessage == "":
				sub.banned.add(actionItem.author.name, note=banNote, duration=banLength)
			else:
				sub.banned.add(actionItem.author.name, note=banNote, ban_message=banMessage, duration=banLength)
			logger.debug(f"Banned user {actionItem.author.name} - {banLength} days")
	except:
		logger.warning(f"Failed to ban user {actionItem.author.name}")


@logger.catch
def wipe_history(actionItem):
	sub = actionItem.subreddit
	user = actionItem.author
	for post in user.submissions.new(limit=None):
		if post.subreddit == sub:
			if not post.removed:
				post.mod.remove(spam=False)
				logger.debug(f"Wipe History: Removed post {post.id}")
	for comment in user.comments.new(limit=None):
		if comment.subreddit == sub:
			if not comment.removed:
				comment.mod.remove(spam=False)
				logger.debug(f"Wipe History: Removed comment {comment.id}")


@logger.catch
def populate_queue(queue, notes, sub, limit=None, params={}):
	queueItems = []
	if queue == "modqueue":
		selectedQueue = sub.mod.modqueue(limit=None)
	elif queue == "hot":
		selectedQueue = sub.hot(limit=limit, params=params)
	elif queue == "rising":
		selectedQueue = sub.rising(limit=limit, params=params)
	elif queue == "new":
		selectedQueue = sub.new(limit=limit, params=params)
	elif queue == "unmoderated":
		selectedQueue = sub.mod.unmoderated(limit=limit, params=params)
	elif isinstance(queue, list):
		selectedQueue = queue
	else:
		return

	for item in selectedQueue:
		highlightTerm = None
		for report in item.mod_reports:
			try:
				if "[" in report[0]:
					highlightTerm = report[0].split("[")[1].split("]")[0]
				report[0] = add_hyperlinks(report[0])
			except:
				continue
		try:
			if highlightTerm:
				selftext = item.selftext_html.replace(highlightTerm, f"<mark>{highlightTerm}</mark>")
			else:
				selftext = item.selftext_html
			setattr(item, "html", selftext)
			setattr(item, "link", f"https://redd.it/{item.id}")
		except:
			setattr(item, "html", item.body_html)
			setattr(item, "title", f"Comment on: {item.submission.title}")
			setattr(item, "link", f"https://reddit.com/r/{item.subreddit}/comments/{item.submission.id}/-/{item.id}")

		try:
			if item.removed_by_category == "automod_filtered":
				for log in sub.mod.log(limit=200, mod="Automoderator", action="removelink"):
					if item.id == log.target_fullname[3:]:
						setattr(item, "amRemovalReason", add_hyperlinks(log.details))
		except:
			pass

		item_usernotes = []
		try:
			for note in notes.get_user_notes(item.author.name):
				item_usernotes.append(note)
		except:
			pass
		setattr(item, "usernotes", item_usernotes)

		try: setattr(item, "name", item.author.name)
		except: setattr(item, "name", "[deleted]")
		queueItems.append(item)
	return queueItems


@queue.route('/<moderatedSub>/queue/<queue>', methods=['GET', 'POST'])
@queue.errorhandler(500)
@login_required
def arbitrary_queue(moderatedSub, queue):
	queue = queue.split('?')[0]
	r = get_instance()
	try: moderatedSub = r.subreddit(moderatedSub)
	except: return authorize()
	try:
		settings = get_settings(r, moderatedSub)
		if isinstance(settings, str): return render_template('error.jinja2', error=settings),500
	except Exception as e: return render_template('error.jinja2', error=e),500
	limit = request.args.get('limit', default=25, type=int)
	if request.method == "POST":
		handle_HTTPPOST_request(r, request, settings["removalReasons"], settings["notes"])
		return ""
	queueItems = populate_queue(queue, settings["notes"], moderatedSub, limit)
	return render_template(
		'queue.jinja2',
		queueItems=queueItems,
		removalReasons=settings["removalReasons"],
		noteTypes=settings["noteTypes"],
		mpSettings=settings["mpSettings"],
		moderatedSub=moderatedSub,
		queue=queue,
		mod=r.user.me().name
	)


@queue.route('/<moderatedSub>/queue/<queue>/more', methods=['GET', 'POST'])
@login_required
def load_more_queue(moderatedSub, queue):
	thingID = request.form["thingID"]
	try:
		queue = queue.split('?')[0]
		r = get_instance()
		moderatedSub = r.subreddit(moderatedSub)
		settings = get_settings(r, moderatedSub)
		notes = pmtw.Usernotes(r, moderatedSub)
		limit = request.args.get('limit', default=25, type=int)
		queueItems = populate_queue(queue, notes, moderatedSub, limit=limit, params={"after": thingID})
		return render_template('queue_items.jinja2', queueItems=queueItems, noteTypes=settings["noteTypes"])
	except:
		return '<button type="button" class="button is-link is-fullwidth" disabled>no more</button>'


@queue.route('/<moderatedSub>/search', methods=['GET', 'POST'])
@queue.errorhandler(500)
@login_required
def search_queue(moderatedSub):
	r = get_instance()
	try: moderatedSub = r.subreddit(moderatedSub)
	except: return authorize()
	try:
		settings = get_settings(r, moderatedSub)
		if isinstance(settings, str): return render_template('error.jinja2', error=settings),500
	except Exception as e: return render_template('error.jinja2', error=e),500
	if request.method == "POST":
		if request.form["action"] == "search":
			query = unquote(request.form["searchField"])
			if request.form["backend"] == "pushshift":
				authors = unquote(request.form["authors"])
				authors.replace(" ","")
				score = unquote(request.form["score"])
				before = unquote(request.form["before"])
				if before == "": before = int(time())
				else: before = int(mktime(datetime.strptime(before, '%Y-%m-%dT%H:%M').timetuple()))
				after = unquote(request.form["after"])
				if after == "": after = 0
				else: after = int(mktime(datetime.strptime(after, '%Y-%m-%dT%H:%M').timetuple()))
				try:
					p = PushshiftAPI(r)
					if request.form["search-kind"] == "comment": gen = p.search_comments(limit=100,subreddit=moderatedSub.display_name,after=after,before=before,q=query,score=score,author=authors)
					else: gen = p.search_submissions(limit=100,subreddit=moderatedSub.display_name,after=after,before=before,q=query,score=score,author=authors)
					queue = list(gen)
				except: return "Pushshift may be down"
			else:
				queue = []
				for item in moderatedSub.search(query=query, sort="new"): queue.append(item)

			queueItems = populate_queue(queue, settings["notes"], moderatedSub, limit=None)

			for item in queueItems:
				item.html = item.html.replace(query, f"<mark>{query}</mark>")
				item.title = item.title.replace(query, f"<mark>{query}</mark>")

			return render_template(
				'queue_items.jinja2',
				queueItems=queueItems,
				removalReasons=settings["removalReasons"],
				noteTypes=settings["noteTypes"],
				mpSettings=settings["mpSettings"],
				moderatedSub=moderatedSub,
				queue="Search"
			)
		else:
			handle_HTTPPOST_request(r, request, settings["removalReasons"], settings["notes"])
			return ""
	else:
		return render_template(
			'search.jinja2',
			removalReasons=settings["removalReasons"],
			noteTypes=settings["noteTypes"],
			mpSettings=settings["mpSettings"],
			moderatedSub=moderatedSub,
			mod=r.user.me().name
		)


@queue.route("/log")
@login_required
def streamSessionEvents():
	try:
		r = get_instance()
		sub = request.args.get('sub', type=str)
		sub = r.subreddit(sub)
		return Response(stream(sub), mimetype="text/event-stream")
	except:
		logger.error(f"Something's wrong with the log stream")


def stream(sub):
	app = create_app()
	app.app_context().push()
	for log in sub.mod.stream.log():
		actions = [
			"removelink",
			"approvelink",
			"removecomment",
			"approvecomment",
			"spamlink",
			"spamcomment"
		]
		if log.action in actions:
			yield(f"data: {log.created_utc} |-| {log.mod} |-| {log.target_fullname} |-| {log.action}\n\n")
