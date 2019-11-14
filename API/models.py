#!/usr/bin/env python3

from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import check_password_hash

db = SQLAlchemy()

class Website(db.Model):
  w_id = db.Column(db.Integer, primary_key=True)
  user_id = db.Column(db.Integer, db.ForeignKey('user.u_id'), nullable=False)
  domain = db.Column(db.String, db.ForeignKey('user.domain'), nullable=False)
  activation_date = db.Column(db.DateTime)
  active = db.Column(db.Boolean, nullable=False, default=False)
  site_props = db.Column(db.String)

  def add(self):
    db.session.add(self)
    db.session.commit()

  def site_activation(self):
    self.active = not self.active
    if self.active:
        print('active')
        self.activation_date = datetime.utcnow()
    db.session.commit()

  def update_site(self, newValue):
    self.site_props = newValue
    db.session.commit()

  def delete(self):
    db.session.delete(self)
    db.session.commit()

class User(db.Model):
  u_id = db.Column(db.Integer, primary_key=True)
  domain = db.Column(db.String(20), nullable=False, unique=True)
  email = db.Column(db.String, nullable=False, unique=True)
  creation_date = db.Column(db.DateTime, default=datetime.utcnow())
  f_name = db.Column(db.String, nullable=False)
  s_name = db.Column(db.String, nullable=False)
  password = db.Column(db.String, nullable=False)
  account_type = db.Column(db.String, nullable=False, default='Free')

  def add(self):
    db.session.add(self)
    db.session.commit()

  @classmethod
  def authenticate(cls, email, password):
    if not email or not password:
      return None
      
    user = cls.query.filter_by(email=email).first()
    if not user or not check_password_hash(user.password, password):
      return None

    return user