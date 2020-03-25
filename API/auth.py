#!/usr/bin/env python3
from datetime import timedelta
import re
from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import (
    jwt_required, create_access_token, get_jwt_identity,
    jwt_refresh_token_required, create_refresh_token, get_jti, get_raw_jwt
)
from werkzeug.security import check_password_hash, generate_password_hash
from API.models import KreohUser, Website
from API.mail_service import MailService
from API.token import generate_confirmation_token, confirm_token
from API.extensions import jwt_revoked_store

bp = Blueprint('auth', __name__, url_prefix="/auth")

ACCESS_EXPIRES = timedelta(minutes=15)
REFRESH_EXPIRES = timedelta(days=30)

@bp.route('/register', methods=('POST',))
def register():
  data = request.get_json()
  f_name = data['f_name']
  s_name = data['s_name']
  email = data['email'].lower()
  password = data['password']
  domain = data['domain'].lower()

  if not re.fullmatch(r'[^@]+@[^@]+\.[^@]+', email) or \
    len(password) < 8 or \
    len(password) > 25 or \
    not f_name.isalnum() or \
    not s_name.isalnum() or \
    not re.search(r'\d+', password) or \
    not re.search(r'[A-Z]+', password):
    return jsonify(error=True, message='Invalid Details. Please Try again'), 400
  if not domain.isalnum():
    return jsonify(error=True, message='Your domain can only contain letters and numbers!'), 400

  user = KreohUser.query.filter_by(domain=domain).first()
  if user is None:
    users = KreohUser.query.all()
    if len(users) < 25:
      user = KreohUser(domain=domain, email=email, f_name=f_name, s_name=s_name, password=generate_password_hash(password), account_type=4)
      user.add()

      user = KreohUser.query.filter_by(domain=domain).first()
      mailer = MailService(current_app, ('Fareed From Kreoh', current_app.config['MAIL_USERNAME']), user.id)
      mailer.send_welcome_message()

      access_token = create_access_token(user.id, fresh=True, expires_delta=timedelta(seconds=900))
      refresh_token = create_refresh_token(user.id)

      access_jti = get_jti(encoded_token=access_token)
      refresh_jti = get_jti(encoded_token=refresh_token)
      jwt_revoked_store.set(access_jti, 'false', ACCESS_EXPIRES * 1.2)
      jwt_revoked_store.set(refresh_jti, 'false', REFRESH_EXPIRES * 1.2)

      return jsonify(error=False, access_token=access_token, refresh_token=refresh_token), 201
    else:
      return jsonify(error=True, message="You've just missed out! The early access is currently full!"), 400
  else:
    return jsonify(error=True, message="unable to create user"), 400

@bp.route('/login', methods=('POST',))
def login():
  data = request.get_json()
  email = data['email']
  password = data['password']
  user = KreohUser.authenticate(email, password)
  if user:
    access_token = create_access_token(user.id, fresh=True, expires_delta=timedelta(seconds=900))
    refresh_token = create_refresh_token(user.id)
    access_jti = get_jti(encoded_token=access_token)
    refresh_jti = get_jti(encoded_token=refresh_token)
    jwt_revoked_store.set(access_jti, 'false', ACCESS_EXPIRES * 1.2)
    jwt_revoked_store.set(refresh_jti, 'false', REFRESH_EXPIRES * 1.2)
    return jsonify(error=False, access_token=access_token, refresh_token=refresh_token), 201
  else:
    return jsonify(error=True, message="Invalid Details."), 401

@bp.route('/logout', methods=('POST',))
@jwt_required
def logout():
  jti = get_raw_jwt()['jti']
  jwt_revoked_store.set(jti, 'true', ACCESS_EXPIRES * 1.2)
  return jsonify(error=False, message='Access JWT revoked'), 200

@bp.route('/logout_refresh', methods=('POST',))
@jwt_refresh_token_required
def logout_refresh():
  jti = get_raw_jwt()['jti']
  jwt_revoked_store.set(jti, 'true', REFRESH_EXPIRES * 1.2)
  return jsonify(error=False, message='Refresh JWT revoked'), 200

@bp.route('/user', methods=('GET',))
@jwt_required
def get_user():
  user_id = get_jwt_identity()
  user = KreohUser.query.filter_by(id=user_id).first()
  if user is None:
    return jsonify(id=None, f_name=None, s_name=None, domain=None, email=None, account_type=None, site_created=False, site_active=False, email_confirmed=None, site_props={}, dark_mode=None), 200
  else:
    website = Website.query.filter_by(user_id=user.id).first()
    if website is None:
      return jsonify(id=user.id, f_name=user.f_name, s_name=user.s_name, domain=user.domain, email=user.email, account_type=user.account_type, site_created=False, site_active=False, email_confirmed=user.email_confirmed, site_props={}, dark_mode=user.dark_mode), 200
    else:
      return jsonify(id=user.id, f_name=user.f_name, s_name=user.s_name, domain=user.domain, email=user.email, account_type=user.account_type, site_created=True, site_active=website.active, email_confirmed=user.email_confirmed, site_props=website.site_props, dark_mode=user.dark_mode), 200

@bp.route('/refresh_token', methods=('POST',))
@jwt_refresh_token_required
def refresh():
  user = get_jwt_identity()
  access_token = create_access_token(identity=user, fresh=False, expires_delta=timedelta(seconds=900))
  access_jti = get_jti(encoded_token=access_token)
  jwt_revoked_store.set(access_jti, 'false', ACCESS_EXPIRES * 1.2)
  return jsonify(access_token=access_token), 201