#!/usr/bin/env python3
import os
from flask import Flask
from flask_cors import CORS
from API.extensions import jwt, mail
from API import site_creation, auth, helpers, uploads, stats, user, mailer, support
from API.models import db

def create_app():
  app = Flask(__name__)
  if os.environ['FLASK_ENV'] == "development":
    app.config.from_object('API.config.DevConfig')
  else:
    app.config.from_object('API.config.ProdConfig')
  
  CORS(app, send_wildcard=True)

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
