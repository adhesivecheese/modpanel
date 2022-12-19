from typing import List, Any
from dataclasses import dataclass
import json
from prawcore.exceptions import NotFound


@dataclass
class DefaultNote:
	index: str
	note: str

	@staticmethod
	def from_dict(obj: Any) -> 'DefaultNote':
		_index = str(obj.get("index"))
		_note = str(obj.get("note"))
		return DefaultNote(_index, _note)


@dataclass
class NoteAction:
	key: str
	action: str

	@staticmethod
	def from_dict(obj: Any) -> 'NoteAction':
		_key = str(obj.get("key"))
		_action = str(obj.get("action"))
		return NoteAction(_key, _action)


@dataclass
class Root:
	schema: int
	tempBan: int
	noNoteAction: str
	noteActions: List[NoteAction]
	defaultNotes: List[DefaultNote]

	def __str__(self):
		return self.to_json()

	@staticmethod
	def from_dict(obj: Any) -> 'Root':
		_schema = int(obj.get("schema"))
		_tempBan = int(obj.get("tempBan"))
		_noNoteAction = str(obj.get("noNoteAction"))
		_noteActions = [NoteAction.from_dict(y) for y in obj.get("noteActions")]
		_defaultNotes = [DefaultNote.from_dict(y) for y in obj.get("defaultNotes")]
		return Root(_schema, _tempBan, _noNoteAction, _noteActions, _defaultNotes)

	def to_json(self):
		return json.dumps(self.__dict__, default=lambda o: o.__dict__)


class Modpanel:
	def __init__(self, sub, json="""{"schema":1,"tempBan":7,"noNoteAction":"none","noteActions":[{"key":"gooduser","action":"hidden"},{"key":"spamwatch","action":"remove"},{"key":"spamwarn","action":"remove"},{"key":"abusewarn","action":"remove"},{"key":"ban","action":"tempban"},{"key":"permban","action":"permban"},{"key":"botban","action":"hidden"}],"defaultNotes":[]}"""):
		self.sub = sub
		self.json = json

		self.settings = Root.from_dict(self.load())

	def load(self):
		try:
			page = self.sub.wiki["modpanel"].content_md
		except NotFound:
			page = self.sub.wiki.create(name="modpanel", content=self.json)
			self.sub.wiki["modpanel"].mod.update(listed=False, permlevel=2)
			page = self.settings
		return json.loads(page)

	def save(self):
			self.sub.wiki["modpanel"].edit(content=self.settings)
