
import pmtw
from flask import (Blueprint, render_template, request)
from loguru import logger

from .redditManager import get_instance
from .wikihandler import NoteAction, DefaultNote, Modpanel
from .auth import authorize

settings = Blueprint('settings', __name__)


@logger.catch
def get_settings(r, sub):
	tbSettings = pmtw.Settings(r, sub)
	mp = Modpanel(sub)

	removal_Reasons = []
	note_Types = []
	count = 0
	for reason in tbSettings.get_reasons():
		setattr(reason, "index", count)
		removal_Reasons.append(reason)
		count += 1
	noteValues = mp.settings.noteActions
	for type in tbSettings.get_usernoteColors():
		for key in noteValues:
			if type.key == key.key:
				setattr(type, "action", key.action)
				break
			else:
				setattr(type, "action", "none")
		note_Types.append(type)

	return {"removal_Reasons": removal_Reasons, "note_Types": note_Types, "mpSettings": mp}


@settings.route('/<modSub>/settings', methods=('GET', 'POST'))
def displaySettings(modSub):
	r = get_instance()
	try:
		sub = r.subreddit(modSub)
	except:
		return authorize()
	settings = get_settings(r, sub)
	mp = settings["mpSettings"]

	if request.method == 'POST':
		settingType = ""
		for key in request.form.keys():
			if key == "type":
				settingType = request.form[key]
				break
		if settingType != "":
			if settingType == "removalTypes":
				newTypes = []
				for key in request.form.keys():
					if key == "type" or key == "noNote" or key == "banLength":
						continue
					newTypes.append(NoteAction(key=key, action=request.form[key]))
				mp.settings.noteActions = newTypes
				mp.settings.tempBan = request.form["banLength"]
				mp.settings.noNoteAction = request.form["noNote"]
			elif settingType == "defaultNotes":
				defaults = []
				for key in request.form.keys():
					defaults.append(DefaultNote(index=key, note=request.form[key]))
				mp.settings.defaultNotes = defaults
		mp.save()

	return render_template(
		'settings.jinja2',
		removalReasons=settings["removal_Reasons"],
		notes=mp.settings.defaultNotes,
		noteTypes=settings["note_Types"],
		mpSettings=mp.settings,
		modSub=modSub
	)
