#!/usr/bin/env python3
import os
from flask import Flask
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from API import site_creation, auth, helpers
from API.models import db

app = Flask(__name__, instance_relative_config=True)
app.config.from_pyfile('config.py')
CORS(app, supports_credentials=True, origins=['http://localhost:3000/*', 'http://localhost:8080', 'https?://([a-z0-9]+[.])*localhost:3000', 'https?://([a-z0-9]+[.])*localhost:8080'])
# https?://([a-z0-9]+[.])*sub[12]domain[.]com
jwt = JWTManager(app)

with app.app_context():
    db.init_app(app)
    print('Initialized Database')

app.register_blueprint(site_creation.bp)
app.register_blueprint(auth.bp)
app.register_blueprint(helpers.bp)
