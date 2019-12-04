#!/usr/bin/env python3
import os
from flask import Flask
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from API import site_creation, auth, helpers, uploads, stats
from API.models import db

def create_app(config='dev'):
  app = Flask(__name__, instance_relative_config=True)
  if config == 'dev':
    app.config.from_pyfile('dev_config.py')
  elif config == 'test':
    app.config.from_pyfile('test_config.py')
  elif config == 'prod':
    app.config.from_pyfile('prod_config.py')

  try:
    os.makedirs(app.instance_path)
  except OSError:
    pass
  
  CORS(app, supports_credentials=True, origins=[
    'https?://localhost:3000',
    'https?://localhost:8080',
    'https?://([a-z0-9]+[.])*localhost:3000',
    'https?://([a-z0-9]+[.])*localhost:8080',
    'https?://kreoh-client.herokuapp.com',
    'https?://([a-z0-9]+[.])*kreoh-client.herokuapp.com'
  ])
  # https?://([a-z0-9]+[.])*sub[12]domain[.]com
  jwt = JWTManager(app)

  with app.app_context():
    db.init_app(app)
    print('Initialized Database')

  app.register_blueprint(site_creation.bp)
  app.register_blueprint(auth.bp)
  app.register_blueprint(helpers.bp)
  app.register_blueprint(uploads.bp)
  app.register_blueprint(stats.bp)

  @app.teardown_request
  def teardown_request(exception):
    if exception:
      db.session.rollback()
    db.session.remove()

  return app