#!/usr/bin/env python3
import os
from flask import Flask
from flask_cors import CORS
from API.extensions import jwt, mail
from API import site_creation, auth, helpers, uploads, stats, user, mailer, support
from API.models import db

def create_app(config='DevConfig'):
  app = Flask(__name__)
  app.config.from_object('API.config.' + config)
  
  CORS(app, supports_credentials=True, origins=[
    'https?://localhost:3000',
    'https?://localhost:8080',
    'https?://([a-z0-9]+[.])*localhost:3000',
    'https?://([a-z0-9]+[.])*localhost:3001',
    'https?://([a-z0-9]+[.])*localhost:8080',
    'https?://kreoh-client.herokuapp.com',
    'https?://([a-z0-9]+[.])*kreoh-client.herokuapp.com'
  ])

  with app.app_context():
    db.init_app(app)
    print('Initialized Database')

  register_extensions(app)
  register_endpoints(app)

  @app.teardown_request
  def teardown_request(exception):
    if exception:
      db.session.rollback()
    db.session.remove()

  return app

def register_extensions(app):
  jwt.init_app(app)
  mail.init_app(app)

def register_endpoints(app):
  app.register_blueprint(site_creation.bp)
  app.register_blueprint(auth.bp)
  app.register_blueprint(helpers.bp)
  app.register_blueprint(uploads.bp)
  app.register_blueprint(stats.bp)
  app.register_blueprint(user.bp)
  app.register_blueprint(mailer.bp)
  app.register_blueprint(support.bp)
