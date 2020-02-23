#!/usr/bin/env python3

from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import check_password_hash

db = SQLAlchemy()

class MailingList(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String, unique=True)

    def add(self):
        db.session.add(self)
        db.session.commit()

class TempWebsite(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'), nullable=False, unique=True)
    domain = db.Column(db.String, db.ForeignKey('user.domain', ondelete='CASCADE'), nullable=False, unique=True)
    activation_date = db.Column(db.DateTime)
    created_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow())
    expiration_date = db.Column(db.DateTime)
    active = db.Column(db.Boolean, nullable=False, default=False)
    site_props = db.Column(db.String)

    def add(self):
        db.session.add(self)
        db.session.commit()

    def site_activation(self):
        self.active = not self.active
        if self.active:
              self.activation_date = datetime.utcnow()
        db.session.commit()

    def update_site(self, newValue):
        self.site_props = newValue
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

class Website(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'), nullable=False, unique=True)
    domain = db.Column(db.String, db.ForeignKey('user.domain', ondelete='CASCADE'), nullable=False, unique=True)
    activation_date = db.Column(db.DateTime)
    created_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow())
    active = db.Column(db.Boolean, nullable=False, default=False)
    site_props = db.Column(db.String)

    def add(self):
        db.session.add(self)
        db.session.commit()

    def site_activation(self):
        self.active = not self.active
        if self.active:
            self.activation_date = datetime.utcnow()
        db.session.commit()

    def screenshot_activation(self):
        self.active = True
        db.session.commit()

    def screenshot_deactivation(self):
        self.active = False
        db.session.commit()

    def update_site(self, newValue):
        self.site_props = newValue
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

class Upload(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    url = db.Column(db.String, nullable=False)
    size = db.Column(db.Integer, nullable=False)
    type = db.Column(db.String, nullable=False)
    name = db.Column(db.String, nullable=False)
    upload_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow())
    ext = db.Column(db.String)
    label = db.Column(db.String, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'), nullable=False)

    def add(self):
        db.session.add(self)
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    def update(self, new_values):
        self.size = new_values['size']
        self.type = new_values['type']
        self.name = new_values['name']
        self.url = new_values['url']
        self.ext = new_values['ext']
        db.session.commit()

class WebsiteStats(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    domain = db.Column(db.String, db.ForeignKey('website.domain', ondelete='CASCADE'), nullable=False)
    cta_inter = db.Column(db.Boolean, default=False)
    visit_date_time = db.Column(db.DateTime, nullable=False)

    def add(self):
        db.session.add(self)
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    domain = db.Column(db.String(20), nullable=False, unique=True)
    email = db.Column(db.String, nullable=False, unique=True)
    email_confirmed = db.Column(db.Boolean, nullable=False, default=False)
    skip_tutorial = db.Column(db.Boolean, nullable=False, default=False)
    creation_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow())
    f_name = db.Column(db.String, nullable=False)
    s_name = db.Column(db.String, nullable=False)
    password = db.Column(db.String, nullable=False)
    account_type = db.Column(db.Integer, nullable=False, default=0)
    storage_space = db.Column(db.Integer, nullable=False, default=100000000)
    dark_mode = db.Column(db.Boolean, nullable=False, default=False)
    uploads = db.relationship('Upload', backref='user', lazy=True)

    def add(self):
        db.session.add(self)
        db.session.commit()

    def update_email(self, new_email):
        self.email = new_email
        self.email_confirmed = True
        db.session.commit()

    def update_password(self, new_password):
        self.password = new_password
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    def updateStorageSpace(self, op, size_to_update):
        if op == '+':
            self.storage_space += size_to_update
        elif op == '-':
            self.storage_space -= size_to_update
        db.session.commit()

    def toggle_dark_mode(self):
        self.dark_mode = not self.dark_mode
        db.session.commit()

    @classmethod
    def authenticate(cls, email, password):
        if not email or not password:
            return None
        
        user = cls.query.filter_by(email=email).first()
        if not user or not check_password_hash(user.password, password):
            return None

        return user

class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    support_ticket_id = db.Column(db.Integer, db.ForeignKey('support_message.id', ondelete='CASCADE'))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'), nullable=False)
    sender_name = db.Column(db.String, nullable=False)
    sender_address = db.Column(db.String, nullable=False)
    subject = db.Column(db.String, nullable=False)
    body = db.Column(db.String, nullable=False)
    read = db.Column(db.Boolean, nullable=False, default=False)
    user_sent = db.Column(db.Boolean, default=False)
    time_sent = db.Column(db.DateTime, nullable=False, default=datetime.utcnow())

    def add(self):
        db.session.add(self)
        db.session.commit()

    def set_read(self):
      self.read = True
      db.session.commit()

class SupportMessage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'), nullable=False)
    subject = db.Column(db.String, nullable=False)
    body = db.Column(db.String, nullable=False)
    time_sent = db.Column(db.DateTime, nullable=False, default=datetime.utcnow())

    def add(self):
        db.session.add(self)
        db.session.commit()

