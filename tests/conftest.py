import pytest
import json
import os

from API import create_app, db

@pytest.fixture(scope='session')
def app():
  test_app = create_app(test_config=True)
  with test_app.app_context():   
    # alternative pattern to app.app_context().push()
    # all commands indented under 'with' are run in the app context 
    db.create_all()
    yield test_app
    db.session.remove()
    db.drop_all()

@pytest.fixture(scope='session')
def user_1_auth_tokens():
  tokens = {'access_token': None, 'refresh_token': None}
  return tokens

@pytest.fixture(scope='session')
def user_2_auth_tokens():
  tokens = {'access_token': None, 'refresh_token': None}
  return tokens

@pytest.fixture(scope='session')
def site_props():
  props = {
    'test': True
  }
  return json.dumps(props)