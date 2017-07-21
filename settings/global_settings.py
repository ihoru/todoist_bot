import os

BASE_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), '')
SQLALCHEMY_DATABASE_URI = 'sqlite:///' + BASE_DIR + 'app.db'
SQLALCHEMY_TRACK_MODIFICATIONS = True

PROJECT_REPOSITORY_LINK = 'https://github.com/ihoru/todoist_bot'

TODOIST = {
    'URL': 'https://todoist.com/oauth/access_token',
    'CLIENT_ID': '',
    'CLIENT_SECRET': '',
    'CACHE': os.path.join(BASE_DIR, 'sync', ''),
}

BOT_TOKEN = ''
