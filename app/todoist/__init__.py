import base64
import hashlib
import logging

import requests
from flask import Blueprint, redirect, request
from flask import current_app as app
from todoist import TodoistAPI

from app import db
from app.telegram.models import User

todoist = Blueprint('todoist', __name__)


@todoist.route('/need_auth/<string:state>')
def need_auth(state):
    scope = 'data:read_write,data:delete'
    url = 'https://todoist.com/oauth/authorize?client_id={CLIENT_ID}&scope={scope}&state={state}'.format(**app.config['TODOIST'], scope=scope, state=state)
    return redirect(url)


@todoist.route('/auth')
def auth():
    error = request.args.get('error')
    if error:
        return error
    code = request.args.get('code')
    state = request.args.get('state')
    if not code:
        return 'code was not passed'
    if not state:
        return 'state was not passed'
    user = User.query.filter(User.state == state, User.is_active == True).one_or_none()
    if not user:
        return 'user was not found'
    data = dict(
        client_id=app.config['TODOIST']['CLIENT_ID'],
        client_secret=app.config['TODOIST']['CLIENT_SECRET'],
        code=code,
    )
    response = requests.post(app.config['TODOIST']['URL'], data=data)
    if response.status_code != 200:
        return response.text
    result = response.json()
    if 'error' in result and result['error']:
        return result['error']
    user.auth = result['access_token']
    user.state = ''
    user.first_init_api()
    db.session.commit()
    return redirect(app.bot.link())


@todoist.route('/callback/<string:client_id>', methods=['POST'])
def callback(client_id):
    if client_id != app.config['TODOIST']['CLIENT_ID']:
        return 'wrong client_id'
    if 'X-Todoist-Hmac-SHA256' not in request.headers:
        return 'no signature'
    signature = request.headers['X-Todoist-Hmac-SHA256']
    password = request.data
    salt = app.config['TODOIST']['CLIENT_SECRET'].encode()
    my_signature = base64.encodebytes(hashlib.pbkdf2_hmac('sha256', password, salt, 100000)).decode()
    if signature != my_signature:
        logging.warning('wrong signature')
        # return 'wrong signature'
    data = request.json
    if not data:
        return 'empty json'
    if data['event_name'] != 'reminder:fired':
        return 'wrong event_name'
    user = User.query.filter(User.todoist_id == data['user_id'], User.is_active == True).one_or_none()
    if not user:
        return 'user was not found'
    user.init_api()
    assert isinstance(user.api, TodoistAPI)
    item = user.api.items.get_by_id(data['event_data']['item_id'])
    if not item:
        return 'item not found'
    from app.telegram.handlers import bot
    result = bot().notification(user, item)
    if not result:
        return 'bot was blocked'
    return 'Ok!'
