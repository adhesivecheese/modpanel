from flask_login import UserMixin

from . import db


class User(UserMixin, db.Model):
	id = db.Column(db.Integer, primary_key=True)
	password = db.Column(db.String(100))
	name = db.Column(db.String(20))
	active = db.Column(db.Boolean)
	admin = db.Column(db.Boolean)
	token = db.Column(db.String(1000))
	state = db.Column(db.String(1000))

	@property
	def is_admin(self):
		return self.admin

	@property
	def is_active(self):
		return self.active