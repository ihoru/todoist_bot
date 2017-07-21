import logging

from flask import Flask
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy

from app.utils import md5

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
app = Flask(__name__)

app.config.from_object('settings')
app.config['BOT_HASHSUM'] = md5(app.config['BOT_TOKEN'])

db = SQLAlchemy(app)

from app.telegram import telegram
from app.telegram import handlers
from app.todoist import todoist

app.register_blueprint(telegram)
app.register_blueprint(handlers.handlers)
app.register_blueprint(todoist)
app.bot = handlers.MyBot(app.config['BOT_TOKEN'])

migrate = Migrate(app, db)
db.create_all()
