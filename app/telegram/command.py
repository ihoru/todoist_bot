from flask import Blueprint, url_for
from flask import current_app as app
from flask_script import Manager
from telegram.ext import Updater

from app.telegram.handlers import bot
from app.telegram.models import User

allowed_updates = ['message']
BotCommand = Manager(usage='Bot manipulation commands')

bot_command = Blueprint('bot_command', __name__)


@BotCommand.command
def get_updates():
    updater = Updater(bot=bot(), workers=1)
    for attr in ('handlers', 'groups', 'error_handlers'):
        setattr(updater.dispatcher, attr, getattr(bot().dispatcher, attr))
    updater.start_polling(timeout=60, allowed_updates=allowed_updates)
    updater.idle()


@BotCommand.command
def set_webhook():
    url = url_for('telegram.webhook', hashsum=app.config['BOT_HASHSUM'], _external=True, _scheme='https')
    return bot().set_webhook(url, allowed_updates=allowed_updates)


@BotCommand.command
def delete_webhook():
    return bot().delete_webhook()


@BotCommand.command
def get_webhook_info():
    return bot().get_webhook_info()


@BotCommand.command
def set_all(text):
    users = User.query.all()
    for user in users:
        print(user.id)
        result = user.send_message(text)
        print(bool(result))
    return 'ok'
