import praw
from praw.util.token_manager import BaseTokenManager
from flask_login import current_user
from loguru import logger
from . import create_app

from . import db
from .models import User


class customTokenManager(BaseTokenManager):
	def __init__(self, name):
		self.name = name
		BaseTokenManager.__init__(self)

	def post_refresh_callback(self, authorizer):
		User.query.filter_by(name=self.name).update(
			{User.token: authorizer.refresh_token},
			synchronize_session=False
		)
		db.session.commit()

	def pre_refresh_callback(self, authorizer):
		if authorizer.refresh_token is None:
			user = User.query.filter_by(name=self.name).first()
			authorizer.refresh_token = user.token


@logger.catch
def get_instance():
	app = create_app()
	if app.config['SINGLE_USER_MODE']:
		return praw.Reddit(
			client_id=app.config['CLIENT_ID'],
			client_secret=app.config['CLIENT_SECRET'],
			password=app.config['REDDIT_PASSWORD'],
			user_agent=app.config['USER_AGENT'],
			username=app.config['REDDIT_USERNAME']
		)
	else:
		refresh_token_manager = customTokenManager(current_user.name)
		return praw.Reddit(
			client_id=app.config['CLIENT_ID'],
			client_secret=app.config['CLIENT_SECRET'],
			token_manager=refresh_token_manager,
			user_agent=app.config['USER_AGENT']
		)


@logger.catch
def get_auth_instance():
	app = create_app()
	return praw.Reddit(
		client_id=app.config['CLIENT_ID'],
		client_secret=app.config['CLIENT_SECRET'],
		redirect_uri=app.config['REDIRECT_URI'],
		user_agent=app.config['USER_AGENT']
	)
