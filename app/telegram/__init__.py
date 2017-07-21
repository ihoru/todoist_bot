from flask import Blueprint, abort, request
from flask import current_app as app
from telegram import Update

telegram = Blueprint('telegram', __name__)


@telegram.route('/')
def main():
    return '<a href="{}">Go to the bot!</a>'.format(app.bot.link())


@telegram.route('/bot/<string:hashsum>', methods=['POST'])
def webhook(hashsum):
    if hashsum != app.config['BOT_HASHSUM']:
        abort(403)
    from app.telegram.handlers import bot
    update = Update.de_json(request.json, bot())
    bot().dispatcher.process_update(update)
    return 'Ok'
