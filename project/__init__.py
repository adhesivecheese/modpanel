from flask import Flask
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy
from loguru import logger
import logging
from flask.logging import default_handler


# init SQLAlchemy so we can use it later in our models
db = SQLAlchemy()


class InterceptHandler(logging.Handler):
	def emit(self, record):
		logger_opt = logger.opt(depth=6, exception=record.exc_info)
		logger_opt.log(record.levelno, record.getMessage())


def create_app():
	app = Flask(__name__)

	app.config.from_pyfile('config.cfg')
	db.init_app(app)

	logger.remove()
	logger.start(
		f"logs/{app.config['LOG_NAME']}",
		level=app.config['LOG_LEVEL'],
		format=app.config['LOG_FORMAT'],
		backtrace=app.config['LOG_BACKTRACE'],
		retention=app.config['LOG_RETENTION']
	)
	# register loguru as handler
	app.logger.addHandler(InterceptHandler())


	login_manager = LoginManager()
	login_manager.login_view = 'auth.login'
	login_manager.init_app(app)
	
	if app.config['SINGLE_USER_MODE']:
		login_manager.anonymous_user.is_authenticated = True
		login_manager.anonymous_user.active = True
		login_manager.anonymous_user.name = "Single-User Mode"
		login_manager.anonymous_user.is_admin = True
		

	from .models import User

	@login_manager.user_loader
	def load_user(user_id):
		# since the user_id is just the primary key of our user table,
		# use it in the query for the user
		return User.query.get(int(user_id))

	# blueprint for auth routes of app
	from .auth import auth as auth_blueprint
	app.register_blueprint(auth_blueprint)

	# blueprint for admin pages
	from .admin import admins as admin_blueprint
	app.register_blueprint(admin_blueprint)

	# blueprint for non-auth parts of app
	from .main import main as main_blueprint
	app.register_blueprint(main_blueprint)

	from .queue import queue as queue_blueprint
	app.register_blueprint(queue_blueprint)

	# blueprint for settings
	from .settings import settings as settings_blueprint
	app.register_blueprint(settings_blueprint)

	# blueprint for settings
	from .diff import diff as diff_blueprint
	app.register_blueprint(diff_blueprint)

	# blueprint for user pages
	from .user import user as user_blueprint
	app.register_blueprint(user_blueprint)

	return app

db.create_all(app=create_app())
