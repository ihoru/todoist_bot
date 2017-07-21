#!/usr/bin/env python3

from flask_migrate import MigrateCommand
from flask_script import Manager

from app import app
from app.telegram.command import BotCommand

manager = Manager(app)
manager.add_command('db', MigrateCommand)
manager.add_command('bot', BotCommand)

if __name__ == '__main__':
    manager.run()
