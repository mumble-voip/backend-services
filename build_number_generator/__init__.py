from flask import Flask
import os

def create_app() -> None:
	app_path = os.path.dirname(__file__)
	app = Flask(__name__, root_path=app_path, instance_path=os.path.join(app_path, "instance"), instance_relative_config=True)

	app.config.from_pyfile("config.py")

	app.app_context()

	with app.app_context():
		from . import database
		database.init()

		from .controller import build_number

	return app
