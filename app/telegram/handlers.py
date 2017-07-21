from datetime import datetime
from uuid import uuid4

from flask import Blueprint, url_for
from sqlalchemy.orm import Query
from telegram import Bot, Message
from telegram import User as TgUser
from telegram.ext import *

from app.telegram.models import User, db

app = None
handlers = Blueprint('handlers', __name__)


@handlers.record
def init_app(state):
    global app
    app = state.app


def handler_wrapper(func):
    def wrap(self, _, update):
        assert isinstance(User.query, Query)
        assert isinstance(update.message, Message)
        tguser = update.message.from_user
        assert isinstance(tguser, TgUser)
        user = User.query.filter(User.tg_id == tguser.id).one_or_none()
        now = datetime.now()
        if not user:
            user = User(
                tg_id=tguser.id,
                first_name=tguser.first_name,
                last_name=tguser.last_name or '',
                username=tguser.username,
                created_at=now,
                last_active_at=now,
            )
            db.session.add(user)
            db.session.commit()
        else:
            user.first_name = tguser.first_name
            user.last_name = tguser.last_name or ''
            user.username = tguser.username
            user.last_active_at = now
            user.is_active = True
        user.update = update
        user.message = update.message
        try:
            func(self, user)
        except Flow:
            pass
        db.session.commit()

    return wrap


def check_auth(func):
    def wrap(self, user: User):
        user.init_api()
        if not user.auth:
            assert isinstance(self, MyBot), self
            user.state = str(uuid4())
            db.session.commit()
            with app.app_context():
                url = url_for('todoist.need_auth', state=user.state, _external=True)
                user.send_message('You need to authorize: {}'.format(url))
                raise Stop
        func(self, user)

    return wrap


class Flow(Exception):
    pass


class Stop(Flow):
    pass


class MyBot(Bot):
    def __init__(self, token):
        super().__init__(token)
        # noinspection PyTypeChecker
        self.dispatcher = Dispatcher(self, None)
        self.process_dispatcher()

    def link(self):
        return 'https://t.me/{}'.format(self.username)

    @handler_wrapper
    @check_auth
    def start(self, user: User):
        user.send_message('Started')

    @handler_wrapper
    @check_auth
    def echo(self, user: User):
        item = user.api.quick.add(user.message.text)
        if not item:
            user.send_message('Could not create task')
            return
        labels = item['labels']
        if labels:
            labels = ['@' + label.data['name'] for label in user.api.labels.all() if label.data['id'] in labels]
        answer = 'Task added:\n{} {} {}'.format(item['content'], ' '.join(labels), item['date_string'] or '')
        user.send_message(answer)

    @handler_wrapper
    def error(self, user: User):
        user.send_message('Error accured')

    def process_dispatcher(self):
        self.dispatcher.add_handler(CommandHandler('start', self.start))
        self.dispatcher.add_handler(MessageHandler(Filters.text, self.echo))
        self.dispatcher.add_error_handler(self.error)


def bot() -> MyBot:
    return app.bot
