import logging
from datetime import datetime
from uuid import uuid4

from flask import Blueprint, url_for
from sqlalchemy.orm import Query
from telegram import Bot, Message
from telegram import User as TgUser
from telegram.ext import *
from todoist.models import Item

from app.telegram import emoji
from app.telegram.models import User, db

app = None
handlers = Blueprint('handlers', __name__)


@handlers.record
def init_app(state):
    global app
    app = state.app


def handler_wrapper(func):
    def wrap(self, _, update, *args, **kwargs):
        with app.app_context():
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
                func(self, user, *args, **kwargs)
            except Flow:
                pass
            db.session.add(user)
            db.session.commit()

    return wrap


def check_auth(func):
    def wrap(self, user: User):
        user.init_api()
        if not user.is_authorized():
            assert isinstance(self, MyBot), self
            user.state = str(uuid4())
            with app.app_context():
                url = url_for('todoist.need_auth', state=user.state, _external=True)
                user.send_message(
                    'You need to authorize: {}\n'.format(url) +
                    'We promise, that we will not share you private information with anyone, or look at it by ourselves.\n'
                    'You can check it open source code of this bot: {}'.format(app.config['PROJECT_REPOSITORY_LINK']),
                    disable_web_page_preview=True,
                )
                raise Stop
        func(self, user)

    return wrap


def check_start_param(func):
    def wrap(self, user: User):
        while True:
            if not user.message or not user.message.text or not str(user.message.text).startswith('/start '):
                break
            param = str(user.message.text).split(' ', 1)[1]
            if not param.startswith('error_'):
                break
            with app.app_context():
                if not user.state:
                    user.state = str(uuid4())
                url = url_for('todoist.need_auth', state=user.state, _external=True)
                if param == 'error_access_denied':
                    user.send_message(
                        'If you want to use bot you have to grant us access to your Todoist account: {}\n'.format(url) +
                        'We care about your privacy!'
                    )
                elif param == 'error_invalid_scope':
                    user.send_message(
                        'Shit happens...\n'
                        'Please, try again: {}\n'.format(url)
                    )
                raise Stop
            break
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

    def link(self, start=''):
        if start:
            start = '?start={}'.format(start)
        return 'https://t.me/{}{}'.format(self.username, start)

    @handler_wrapper
    @check_start_param
    @check_auth
    def start(self, user: User):
        user.send_message(
            'You are authorized! Everything is good!\n'
            'Now you can create new task just by writing it to me...'
        )

    @handler_wrapper
    def stop(self, user: User):
        user.send_message('We will not send you anything again until you send a message me.')
        user.is_active = False

    @handler_wrapper
    @check_auth
    def labels(self, user: User):
        labels = ' '.join(['@' + label['name'] for label in user.api.labels.all()])
        if labels:
            user.send_message('Your labels: ' + labels)
        else:
            user.send_message('You don\'t have any labels!')

    @handler_wrapper
    @check_auth
    def projects(self, user: User):
        projects = ' '.join(['#' + project['name'] for project in user.api.projects.all()])
        if projects:
            user.send_message('Your projects: ' + projects)
        else:
            user.send_message('You don\'t have any projects!')

    @handler_wrapper
    @check_auth
    def any_text(self, user: User):
        item = user.api.quick.add(user.message.text)
        if not item:
            user.send_message('Could not create task')
            return
        labels = item['labels']
        if labels:
            labels = ['@' + label.data['name'] for label in user.api.labels.all() if label.data['id'] in labels]
        answer = 'Task added:\n{} {} {}'.format(item['content'], ' '.join(labels), item['due'] or '')
        user.send_message(answer)

    @handler_wrapper
    def any_other(self, user: User):
        user.send_message('This type of content is not supported.')

    @handler_wrapper
    def group(self, user: User):
        user.message.reply_text(
            'Bot is not available in group chat yet!\n'
            'You can talk to me in private dialog: @{username}'.format(username=self.username)
        )

    @handler_wrapper
    def error(self, user: User, error):
        user.send_message('Error occurred')
        logging.warning('Error occurred: {}'.format(error))

    @handler_wrapper
    @check_auth
    def welcome(self, user: User):
        self.base_welcome(user)

    def base_welcome(self, user: User):
        projects = ' '.join(['#' + project['name'] for project in user.api.projects.all()])
        labels = ' '.join(['@' + label['name'] for label in user.api.labels.all()])
        text = 'You were successfully authorized!'
        if projects or labels:
            text += '\n'
        if projects:
            text += '\nProjects: ' + projects
        if labels:
            text += '\nLabels: ' + labels
        text += '\n\nNow you can send me a task that you want to save for later...'
        user.send_message(text)

    @handler_wrapper
    @check_auth
    def test_notification(self, user: User):
        import random
        items = user.api.items.all()
        item = random.choice(items)
        self.notification(user, item)

    def notification(self, user: User, item: Item):
        text = '{} {}'.format(emoji.DOUBLE_RED_EXCLAMATION, item.data['content'])
        return user.send_message(text)

    def process_dispatcher(self):
        self.dispatcher.add_handler(MessageHandler(Filters.group, self.group))
        self.dispatcher.add_handler(CommandHandler('start', self.start))
        self.dispatcher.add_handler(CommandHandler(['stop', 'off'], self.stop))
        self.dispatcher.add_handler(CommandHandler('labels', self.labels))
        self.dispatcher.add_handler(CommandHandler('projects', self.projects))
        self.dispatcher.add_handler(CommandHandler('welcome', self.welcome))  # for debug
        self.dispatcher.add_handler(CommandHandler('test_notification', self.test_notification))  # for debug
        self.dispatcher.add_handler(MessageHandler(Filters.text, self.any_text))
        self.dispatcher.add_handler(MessageHandler(Filters.all, self.any_other))
        self.dispatcher.add_error_handler(self.error)


def bot() -> MyBot:
    return app.bot
