#!/usr/bin/env python3
import os
import shutil
import pytest
from flask_migrate import Migrate, MigrateCommand
from flask_script import Manager

from API import create_app
from API.models import db

app = create_app(os.environ['APP_ENV'])
db.init_app(app)

migrate = Migrate(app, db)
manager = Manager(app)

manager.add_command('db', MigrateCommand)

@manager.command
def test():
  '''
  Run Tests
  Create test upload folders if they do not exist.
  Remove folders after tests finished running.
  '''

  test_upload_folder = '/home/fareed/Documents/Kreoh/test_kreoh_user_site_images'
  if not os.path.exists(test_upload_folder):
    os.makedirs(test_upload_folder)

  pytest.main(['-s', 'tests/test_auth.py', 'tests/test_site_creation.py', 'tests/test_helpers.py', 'tests/test_uploads.py'])

  shutil.rmtree(test_upload_folder, ignore_errors=True)



if __name__ == '__main__':
    manager.run()