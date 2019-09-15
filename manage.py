#!/usr/bin/env python3
import os
from flask_migrate import Migrate, MigrateCommand
from flask_script import Manager

from API import app
from API.models import db

db.init_app(app)

migrate = Migrate(app, db)
manager = Manager(app)

manager.add_command('db', MigrateCommand)


if __name__ == '__main__':
    manager.run()