#!/usr/bin/env python3
from datetime import timedelta
import re
from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import (
    jwt_required, create_access_token, get_jwt_identity,
    jwt_refresh_token_required, create_refresh_token
)
from werkzeug.security import check_password_hash, generate_password_hash
from API.models import User, Website
from API.mail_service import MailService
from API.token import generate_confirmation_token, confirm_token

bp = Blueprint('auth', __name__, url_prefix="/auth")

@bp.route('/register', methods=('POST',))
def register():
  data = request.get_json()
  f_name = data['f_name']
  s_name = data['s_name']
  email = data['email']
  password = data['password']
  domain = data['domain']

  if not re.fullmatch(r'[^@]+@[^@]+\.[^@]+', email):
    return jsonify(msg='Email is in wrong format!'), 401
  if not domain.isalnum():
    return jsonify(msg='Your domain can only contain letters and numbers!'), 406
  if len(password) < 8 or len(password) > 25:
    return jsonify(msg='Invalid password.'), 401

  user = User.query.filter_by(domain=domain).first()
  if user is None:
    users = User.query.all()
    if len(users) < 25:
      user = User(domain=domain, email=email, f_name=f_name, s_name=s_name, password=generate_password_hash(password), account_type=4)
      user.add()

      user = User.query.filter_by(domain=domain).first()
      mailer = MailService(current_app, ('Fareed From Kreoh', current_app.config['MAIL_USERNAME']), user.id)
      mailer.send_welcome_message()

      access_token = create_access_token(user.id, fresh=True, expires_delta=timedelta(minutes=30))
      refresh_token = create_refresh_token(user.id)
      return jsonify(access_token=access_token, refresh_token=refresh_token, message=email + ' user created.'), 201
    else:
      return jsonify(msg="You've just missed out! The early access is currently full!"), 401
  else:
    return jsonify(msg="unable to create user"), 401

@bp.route('/login', methods=('POST',))
def login():
  data = request.get_json()
  email = data['email']
  password = data['password']
  user = User.authenticate(email, password)
  if user:
    access_token = create_access_token(user.id, fresh=True, expires_delta=timedelta(minutes=30))
    refresh_token = create_refresh_token(user.id)
    return jsonify(access_token=access_token, refresh_token=refresh_token), 200
  else:
    return jsonify(msg="Invalid Email or Password."), 401

@bp.route('/user', methods=('GET',))
@jwt_required
def get_user():
    user_id = get_jwt_identity()
    user = User.query.filter_by(id=user_id).first()
    if user is None:
      return jsonify(id=None, f_name=None, s_name=None, domain=None, email=None, account_type=None, site_created=False, site_active=False, email_confirmed=None, skip_tutorial=None, dark_mode=None), 200
    else:
      website = Website.query.filter_by(user_id=user.id).first()
      if website is None:
        return jsonify(id=user.id, f_name=user.f_name, s_name=user.s_name, domain=user.domain, email=user.email, account_type=user.account_type, site_created=False, site_active=False, email_confirmed=user.email_confirmed, skip_tutorial=user.skip_tutorial, dark_mode=user.dark_mode), 200
      else:
        return jsonify(id=user.id, f_name=user.f_name, s_name=user.s_name, domain=user.domain, email=user.email, account_type=user.account_type, site_created=True, site_active=website.active, email_confirmed=user.email_confirmed, skip_tutorial=user.skip_tutorial, dark_mode=user.dark_mode), 200

@bp.route('/refresh_token', methods=('POST',))
@jwt_refresh_token_required
def refresh():
  user = get_jwt_identity()
  new_token = create_access_token(identity=user, fresh=False, expires_delta=timedelta(minutes=30))
  return jsonify(access_token=new_token), 201