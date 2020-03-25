import os
from datetime import timedelta

class Config(object):
  SECRET_KEY = os.environ['KREOH_SECRET_KEY']
  SECURITY_PASSWORD_SALT = os.environ['KREOH_SECURITY_PASSWORD_SALT']
  JWT_SECRET_KEY = os.environ['JWT_SECRET_KEY']
  ALLOWED_EXTENSIONS = {'ico'}
  MAIL_SERVER = 'smtp.eu.mailgun.org'
  MAIL_PORT = 587
  MAIL_USERNAME = os.environ['KREOH_SUPPORT_MAIL_ADDRESS']
  MAIL_PASSWORD = os.environ['KREOH_SUPPORT_MAIL_PASSWORD']
  MAIL_USE_TLS = True
  MAIL_USE_SSL = False
  S3_BUCKET_NAME = os.environ['BUCKETEER_BUCKET_NAME']
  SQLALCHEMY_TRACK_MODIFICATIONS = False
  SECURITY_CONFIRMABLE = True
  SECURITY_TRACKABLE = True
  JWT_BLACKLIST_ENABLED = True
  JWT_BLACKLIST_TOKEN_CHECKS = ['access', 'refresh']

class TestConfig(Config):
  TESTING = True
  ENV = 'test'
  PRESERVE_CONTEXT_ON_EXCEPTION = False
  SQLALCHEMY_DATABASE_URI = os.environ['TEST_KREOH_DATABASE_URL']
  SQLALCHEMY_TRACK_MODIFICATIONS = False
  EMAIL = 'fareedidris20@gmail.com'
  PASSWORD = 'testing123'

class ProdConfig(Config):
  DEBUG = False
  SQLALCHEMY_DATABASE_URI = os.environ['DATABASE_URL']


class DevConfig(Config):
  DEBUG = True
  SQLALCHEMY_DATABASE_URI = os.environ['KREOH_DATABASE_URL']  