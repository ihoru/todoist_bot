from datetime import datetime

from flask import current_app as app
from telegram import Message, Update
from telegram.error import Unauthorized
from todoist import TodoistAPI
from todoist.api import SyncError

from app import db


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    tg_id = db.Column(db.BigInteger, unique=True)
    first_name = db.Column(db.String(255))
    last_name = db.Column(db.String(255))
    username = db.Column(db.String(100))
    todoist_id = db.Column(db.BigInteger, nullable=True, index=True)
    state = db.Column(db.String(36), default='', index=True)
    auth = db.Column(db.String(255), default='')
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, nullable=False)
    last_active_at = db.Column(db.DateTime, nullable=True)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.update = None  # type: Update
        self.message = None  # type: Message
        self.api = None  # type: TodoistAPI
        self.now = None  # type: datetime

    def first_init_api(self):
        self.init_api()
        if not self.auth:
            return
        projects = ' '.join(['#' + project['name'] for project in self.api.projects.all()])
        labels = ' '.join(['@' + label['name'] for label in self.api.labels.all()])
        # TODO: say welcome
        if not projects and not labels:
            return
        text = ''
        if projects:
            text += '\nProjects: ' + projects
        if labels:
            text += '\nLabels: ' + labels
        self.send_message(text)

    def init_api(self):
        if not self.auth:
            return
        try:
            with app.app_context():
                self.api = TodoistAPI(self.auth, cache=app.config['TODOIST']['CACHE'])
            result = self.api.sync()
            if 'error' in result:
                raise SyncError
            if 'user' in result and not self.todoist_id:
                self.todoist_id = result['user']['id']
        except SyncError:
            self.auth = ''
            self.todoist_id = None
            self.api = None

    def send_message(self, text, **kwargs):
        from app.telegram.handlers import bot
        try:
            return bot().send_message(self.tg_id, text, **kwargs)
        except Unauthorized:
            self.is_active = False
            db.session.commit()
        return False
